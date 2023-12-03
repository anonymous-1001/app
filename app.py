import mysql.connector
from kivy.app import App
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.filemanager import MDFileManager
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.scrollview import ScrollView
from kivymd.uix.list import MDList
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivymd.uix.button import MDFloatingActionButton
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView

try :
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="app"
    )
    cursor = db.cursor()
except mysql.connector.Error as err:
    print(f"Error connecting to database: {err}")

# Simulated in-memory user data
user_data = {"user": "password"}

# Builder string for the KV language
kv = '''
<LoginScreen>:
    name: 'login'

    MDTextField:
        id: username_input
        hint_text: "Enter username"
        pos_hint: {'center_x': 0.5, 'center_y': 0.6}
        size_hint_x: None
        width: 300

    MDTextField:
        id: password_input
        hint_text: "Enter password"
        password: True
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        size_hint_x: None
        width: 300

    MDRectangleFlatButton:
        text: "Login"
        pos_hint: {'center_x': 0.5, 'center_y': 0.4}
        on_release: root.login()

    MDRectangleFlatButton:
        text: "Register"
        pos_hint: {'center_x': 0.5, 'center_y': 0.3}
        on_release: root.manager.current = 'register'

<RegisterScreen>:
    name: 'register'

    MDTextField:
        id: new_username_input
        hint_text: "Enter new username"
        pos_hint: {'center_x': 0.5, 'center_y': 0.6}
        size_hint_x: None
        width: 300

    MDTextField:
        id: new_password_input
        hint_text: "Enter new password"
        password: True
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        size_hint_x: None
        width: 300

    MDRectangleFlatButton:
        text: "Register"
        pos_hint: {'center_x': 0.5, 'center_y': 0.4}
        on_release: root.register()

    MDRectangleFlatButton:
        text: "Back to Login"
        pos_hint: {'center_x': 0.5, 'center_y': 0.3}
        on_release: root.manager.current = 'login'
'''
# Login Screen
class LoginScreen(Screen):
    def login(self):
        username = self.ids.username_input.text
        password = self.ids.password_input.text

        try:
                # Query to check if username and password match
            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()
            if user:
                print("Logged in successfully")
                app = MDApp.get_running_app()
                user_interface_screen = app.root.get_screen('user_interface')
                if user_interface_screen:
                    user_interface_screen.show_accounts_list()
                    app.root.current = 'user_interface'
            else:
                print("Invalid username or password")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            if 'db' in locals() and db.is_connected():
                cursor.close()
                db.close()

# Register Screen
class RegisterScreen(Screen):
     def register(self):
        new_username = self.ids.new_username_input.text
        new_password = self.ids.new_password_input.text

        if new_username and new_password:
            try:
                # Check if the new username already exists in the database
                cursor.execute("SELECT * FROM users WHERE username = %s", (new_username,))
                existing_user = cursor.fetchone()

                if existing_user:
                    print("Username already taken")
                else:
                    # Insert the new user into the 'users' table
                    insert_query = "INSERT INTO users (username, password) VALUES (%s, %s)"
                    cursor.execute(insert_query, (new_username, new_password))
                    db.commit()
                    print(f"Registered new user: {new_username}")
                    
            except mysql.connector.Error as err:
                print(f"Error: {err}")
        else:
            print("Please enter a valid username and password")

class UserInterfaceScreen(Screen):
    name = 'user_interface'
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.accounts_list = MDList()
        self.show_accounts_list()

        # Adjust the orientation and arrangement of widgets
        self.vertical_layout = BoxLayout(orientation="vertical")
        self.vertical_layout.add_widget(self.accounts_list)

        self.add_widget(self.vertical_layout)

    def show_accounts_list(self):
        self.accounts_list.clear_widgets()  # Clear previous account buttons
        try:
            sql = "SELECT username FROM users"
            cursor.execute(sql)
            accounts = cursor.fetchall()
            for account in accounts:
                username = account[0]
                account_button = MDFlatButton(text=username, on_release=self.select_account)
                self.accounts_list.add_widget(account_button)
        except mysql.connector.Error as err:
            print(f"Error fetching accounts: {err}")
            
    def select_account(self, instance):
        try:
            selected_username = instance.text
            app = App.get_running_app()
            login_screen = app.root.get_screen('login')
            if login_screen:
                username_input_text = login_screen.ids.username_input.text

                # Logic to handle account selection
                if selected_username != username_input_text:
                    # Display the chat interface only if a different account is selected
                    self.manager.current = 'chat_screen'  # Switch to the chat screen
                    chat_screen = self.manager.get_screen('chat_screen')
                    chat_screen.selected_username = selected_username  # Store selected username
                    chat_screen.update_chat_interface()  # Update chat interface
                else:
                    print("Cannot select own account for chat")
        except Exception as e:
            print(f"Error selecting account: {e}")


class ChatScreen(Screen):
    name = "chat_screen"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_file = None  # Store selected file path
        self.chat_layout = BoxLayout(orientation="vertical")
        self.chat_scroll = ScrollView()
        self.chat_box = BoxLayout(orientation="vertical", size_hint_y=None, padding=(10, 10))
        self.chat_box.bind(minimum_height=self.chat_box.setter('height'))
        self.chat_scroll.add_widget(self.chat_box)
        self.chat_layout.add_widget(self.chat_scroll)
        self.add_widget(self.chat_layout)
        # Create a BoxLayout for the message input and buttons
        self.input_box = BoxLayout(orientation="horizontal", size_hint=(1, 0.2))
        self.message_input = TextInput(hint_text="Type your message here...", multiline=False, size_hint=(0.7, 1))
        
        # Create "Send" button
        self.send_button = Button(text="Send", size_hint=(0.15, 1))
        self.send_button.bind(on_release=self.send_message)
        
        # Create "Attachments" button
        self.attach_button = Button(text="Attachments", size_hint=(0.15, 1))
        self.attach_button.bind(on_release=self.attach_file)
        
        # Add TextInput and buttons to the input_box
        self.input_box.add_widget(self.message_input)
        self.input_box.add_widget(self.send_button)
        self.input_box.add_widget(self.attach_button)
        
        # Add input_box to your layout (replace chat_layout with your appropriate layout)
        self.chat_layout.add_widget(self.input_box)


    def attach_file(self, instance):
        # Add logic to attach files
        file_popup = Popup(title="Attach File", size_hint=(0.8, 0.8))
        file_chooser = FileChooserIconView()
        file_chooser.bind(on_submit=self.select_file)
        file_popup.add_widget(file_chooser)
        file_popup.open()

    def select_file(self, instance):
        self.selected_file = instance.selection[0] if instance.selection else None

    def send_message(self, instance):  # Update the method signature to accept only 'self'
        message_text = self.message_input.text.strip()
        if message_text or self.selected_file:
            try:
                # Replace with your SQL insert query
                query = "INSERT INTO messages (sender, receiver, text, attached_file) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, ("sender_username", "receiver_username", message_text, self.selected_file))
                db.commit()
                self.update_chat_interface()
                self.message_input.text = ""  # Clear the message input field
                self.selected_file = None  # Reset selected file after sending
            except mysql.connector.Error as err:
                print(f"Error sending message: {err}")

    def update_chat_interface(self):
        chat_layout = self.ids.chat_layout  # Access the GridLayout

        try:
            query = "SELECT sender, text, attached_file FROM messages WHERE (sender = %s AND receiver = %s) OR (sender = %s AND receiver = %s) ORDER BY id ASC"
            cursor.execute(query, ("sender_username", "receiver_username", "receiver_username", "sender_username"))
            messages = cursor.fetchall()

            for sender, text, attached_file in messages:
                message_label = Label(text=f"{sender}: {text}", size_hint_y=None, height=dp(40))
                chat_layout.add_widget(message_label)
        except mysql.connector.Error as err:
            print(f"Error fetching messages: {err}")


class ChatApp(MDApp):
    file_manager = None
    def build(self):
        Builder.load_string(kv)
        screen_manager = ScreenManager()

        login_screen = LoginScreen(name='login')
        register_screen = RegisterScreen(name='register')
        user_interface_screen = UserInterfaceScreen(name='user_interface')
        chat_interface_screen = ChatScreen(name='chat_screen')  # Assuming ChatScreen is for the chat interface

        screen_manager.add_widget(login_screen)
        screen_manager.add_widget(register_screen)
        screen_manager.add_widget(user_interface_screen)
        screen_manager.add_widget(chat_interface_screen)  # Add ChatScreen for the chat interface
        screen_manager.current = 'login'  # Set the initial screen to login_screen

        return screen_manager
    
    def exit_manager_callback(self, *args):
        try:
            # Retrieve the selected file path from the args
            if args and len(args) > 1:
                selected_file = args[1][0]
                print(f"Selected file: {selected_file}")
                # Perform operations with the selected file, e.g., display it or process it further
        except Exception as e:
            import traceback
            traceback.print_exc()  # Print the stack trace for debugging
            print(f"Error: {e}")

    def on_stop(self):
        # If the app stops, close the file manager to prevent potential conflicts
        if self.file_manager:
            self.file_manager.close()

if __name__ == "__main__":
    
    ChatApp().run()
