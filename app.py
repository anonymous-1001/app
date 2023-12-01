import mysql.connector
from kivymd.app import App
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.filemanager import MDFileManager
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder


# Simulated in-memory user data
user_data = {"user": "password"}

# Builder string for the KV language
kv = '''
ScreenManager:
    LoginScreen:
    RegisterScreen:

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
            if ChatApp.cursor:
                # Query to check if username and password match
                query = "SELECT * FROM users WHERE username = %s AND password = %s"
                ChatApp.cursor.execute(query, (username, password))
                user = ChatApp.cursor.fetchone()
                if user:
                    print("Logged in successfully")
                else:
                    print("Invalid username or password")
            else:
                print("Cursor is not initialized.")
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

        # Check if the new username already exists
        if new_username in user_data:
            print("Username already taken")
        else:
            # Placeholder for user registration (simulated in-memory data)
            if new_username and new_password:
                user_data[new_username] = new_password
                print(f"Registered new user: {new_username}")
            else:
                print("Please enter a valid username and password")

class ChatApp(MDApp):
    
    #db = None
    #cursor = None
    def connect_to_database(self):
        try :
            self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="app"
        )
            cursor = self.db.cursor()
        except mysql.connector.Error as err:
            print(f"Error connecting to database: {err}")
            
    def build(self):
        self.layout = MDBoxLayout(orientation='vertical')

        self.username_input = MDTextField(hint_text="Enter username")
        self.password_input = MDTextField(hint_text="Enter password", password=True)

        register_button = MDFlatButton(text="Register", on_press=self.register_user)
        login_button = MDFlatButton(text="Login", on_press=self.login_user)

        self.status_label = MDLabel(text="")
        self.accounts_label = MDLabel(text="Accounts:")

        self.layout.add_widget(self.username_input)
        self.layout.add_widget(self.password_input)
        self.layout.add_widget(register_button)
        self.layout.add_widget(login_button)
        self.layout.add_widget(self.status_label)
        self.layout.add_widget(self.accounts_label)

        self.file_manager = None
        self.file_manager = MDFileManager(exit_manager=self.exit_manager_callback)  # Initialize file manager
        self.file_manager.bind(on_select=self.select_file)

        self.connect_to_database
        self.update_accounts_list()
        self.send_button = MDFlatButton(text="Send", on_press=self.send_message)
        self.layout.add_widget(self.send_button)
        self.update_accounts_list()
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.theme_style = "Dark"

        screen_manager = Builder.load_string(kv)
        return screen_manager
        return self.layout
    
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

    def create_table_if_not_exists(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE,
                    password VARCHAR(50)
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    sender VARCHAR(50),
                    receiver VARCHAR(50),
                    message TEXT,
                    FOREIGN KEY (sender) REFERENCES users(username),
                    FOREIGN KEY (receiver) REFERENCES users(username)
                )
            """)
            self.db.commit()
        except mysql.connector.Error as err:
            print(f"Error creating tables: {err}")

    def register_user(self, instance):
        username = self.username_input.text
        password = self.password_input.text

        if username and password:
            try:
                sql = "INSERT INTO users (username, password) VALUES (%s, %s)"
                self.cursor.execute(sql, (username, password))
                self.db.commit()
                self.status_label.text = f"Registered successfully: {username}"
                self.update_accounts_list()
            except mysql.connector.Error as err:
                self.status_label.text = f"Error: {err}"

    def login_user(self, instance):
        username = self.username_input.text
        password = self.password_input.text

        if username and password:
            try:
                sql = "SELECT * FROM users WHERE username = %s AND password = %s"
                self.cursor.execute(sql, (username, password))
                user = self.cursor.fetchone()
                if user:
                    self.status_label.text = f"Logged in successfully: {username}"
                    self.show_accounts_list()
                else:
                    self.status_label.text = "Invalid username or password"
            except mysql.connector.Error as err:
                self.status_label.text = f"Error: {err}"

    def show_accounts_list(self):
        self.layout.clear_widgets()
        self.layout.add_widget(self.accounts_label)

        try:
            sql = "SELECT username FROM users"
            self.cursor.execute(sql)
            accounts = self.cursor.fetchall()
            for account in accounts:
                username = account[0]
                account_button = MDFlatButton(text=username, on_press=self.select_account)
                self.layout.add_widget(account_button)
        except mysql.connector.Error as err:
            self.status_label.text = f"Error: {err}"

    def select_account(self, instance):
        selected_username = instance.text
        self.show_chat_interface(selected_username)

    def show_chat_interface(self, username):
        self.layout.clear_widgets()  # Clear previous widgets
        chat_layout = MDBoxLayout(orientation='vertical')

        self.selected_user_label = MDLabel(text=f"Chatting with: {username}", halign='center')
        chat_history_label = MDLabel(text="Chat History:", halign='center')
        self.message_history = MDLabel(text="", halign='left', valign='top', size_hint_y=None, height=200, multiline=True)

        self.user_input = MDTextField(hint_text="Type your message here")
        send_button = MDFlatButton(text="Send", on_press=self.send_message)

        chat_layout.add_widget(self.selected_user_label)
        chat_layout.add_widget(chat_history_label)
        chat_layout.add_widget(self.message_history)
        chat_layout.add_widget(self.user_input)
        chat_layout.add_widget(send_button)

        self.layout.add_widget(chat_layout)

        # Fetch message history between current user and selected username
        sender = self.username_input.text  # Current logged-in user
        receiver = username
        self.update_message_history(sender, receiver)

    def send_message(self, instance):
        receiver = self.user_input.text
        message = "Your message here"  # Replace with the actual message input
        sender = self.selected_user_label.text.split(": ")[1]  # Extract sender from the logged-in user label

        if receiver and (message or self.file_chooser.selection):
            try:
                # Handle message
                if message:
                    sql = "INSERT INTO messages (sender, receiver, message) VALUES (%s, %s, %s)"
                    self.cursor.execute(sql, (sender, receiver, message))
                    self.db.commit()

                # Handle file upload
                if self.file_chooser.selection:
                    selected_file = self.file_chooser.selection[0]
                    file_path = selected_file.replace("\\", "/")  # Normalize path for MySQL
                    file_type = "file"  # Default type if not an image or video

                    if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        file_type = "image"
                    elif file_path.lower().endswith(('.mp4', '.avi', '.mov')):
                        file_type = "video"

                    sql = "INSERT INTO files (sender, receiver, file_path, file_type) VALUES (%s, %s, %s, %s)"
                    self.cursor.execute(sql, (sender, receiver, file_path, file_type))
                    self.db.commit()

                # Update message history
                self.update_message_history(sender, receiver)
            except mysql.connector.Error as err:
                print(f"Error sending message: {err}")

        # Clear input and file chooser after sending
        self.user_input.text = ""
        self.file_chooser.selection = []

    def update_accounts_list(self):
        try:
            sql = "SELECT username FROM users"
            self.cursor.execute(sql)
            accounts =self.cursor.fetchall()

            # Assuming self.layout and self.accounts_label are properly initialized
            self.layout.clear_widgets()  # Clear previous widgets
            self.layout.add_widget(self.accounts_label)

            for account in accounts:
                username = account[0]
                account_button = MDFlatButton(text=username, on_press=self.select_account)
                self.layout.add_widget(account_button)
        except mysql.connector.Error as err:
            print(f"Error fetching accounts: {err}")
            
    def select_account(self, instance):
        try:
            if not self.cursor:
                self.connect_to_database()  # Reconnect if cursor is None
            # Reassign cursor after reconnecting
            self.cursor = self.db.cursor()

            selected_username = instance.text
            # Logic to handle account selection
            # For example, you might want to display chat history with the selected user
            self.show_chat_interface(selected_username)
        except mysql.connector.Error as err:
            print(f"Error selecting account: {err}")

    def select_file(self, instance):
        selected_file = instance.selection[0]
        # Handle selected file

    def update_message_history(self, sender, receiver):
        try:
            sql = "SELECT message FROM messages WHERE (sender = %s AND receiver = %s) OR (sender = %s AND receiver = %s)"
            self.cursor.execute(sql, (sender, receiver, receiver, sender))
            messages = self.cursor.fetchall()

            message_history_text = ""
            for msg in messages:
                message_history_text += f"{msg[0]}\n"

            self.message_history.text = message_history_text
        except mysql.connector.Error as err:
            print(f"Error updating message history: {err}")

if __name__ == "__main__":
    ChatApp().run()