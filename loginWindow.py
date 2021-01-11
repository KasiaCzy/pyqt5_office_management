from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from registerWindow import RegisterWindow
import bcrypt
import style
from dataEnum import *


class LoginWindow(QDialog):
    login_successful = pyqtSignal(str)

    def __init__(self, connection, cursor):
        super().__init__()
        self.connection = connection
        self.cursor = cursor
        self.setWindowTitle("Login")
        self.setWindowIcon(QIcon("icons/login.png"))
        self.setWindowFlags(self.windowFlags() & (~Qt.WindowContextHelpButtonHint))
        self.setGeometry(550, 150, 300, 200)
        self.setFixedSize(self.size())
        self.create_UI()

    def create_UI(self):
        self.create_widgets()
        self.create_layouts()

    def create_widgets(self):
        self.name_entry = QLineEdit()
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)

        # buttons
        self.register_btn = QPushButton('New User')
        self.register_btn.setStyleSheet(style.register_btn_style())
        self.register_btn.setAutoDefault(False)
        self.register_btn.clicked.connect(self.add_user)

        self.login_btn = QPushButton('Login')
        self.login_btn.setStyleSheet(style.btn_style())
        self.login_btn.clicked.connect(self.log_into)

    def create_layouts(self):
        self.main_layout = QFormLayout()

        self.main_layout.addRow(QLabel("User name: "), self.name_entry)
        self.main_layout.addRow(QLabel('Password: '), self.password_entry)
        self.main_layout.addRow(self.register_btn, self.login_btn)

        self.setLayout(self.main_layout)

    def log_into(self):
        username = self.name_entry.text()
        password = self.password_entry.text()

        if username and password:
            self.confirm_data(username, password)
        else:
            QMessageBox.information(self, "Warning", 'Fields: "User name" and "Password" can not be empty.')

    def confirm_data(self, username, password):
        users = self.get_users()
        users_name = self.get_users_name()

        if not any(username in user for user in users_name):
            QMessageBox.information(self, "Warning", 'Invalid username.')

        for user in users:
            if username == user[UserData.NAME]:
                if bcrypt.checkpw(password.encode(), user[UserData.PASSWORD]):
                    self.logged_user_id = user[UserData.ID]
                    self.login_successful.emit(username)
                    self.close()
                else:
                    QMessageBox.information(self, "Warning", 'Login failed. Invalid username or password.')

    def add_user(self):
        self.new_user = RegisterWindow(self.connection, self.cursor)

    def get_users(self):
        return self.cursor.execute("SELECT * FROM users").fetchall()

    def get_users_name(self):
        return self.cursor.execute("SELECT name FROM users").fetchall()
