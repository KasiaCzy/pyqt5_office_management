from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import bcrypt
import style


class RegisterWindow(QDialog):
    login_successful = pyqtSignal()

    def __init__(self, connection, cursor):
        super().__init__()
        self.connection = connection
        self.cursor = cursor
        self.setWindowTitle("New User")
        self.setWindowIcon(QIcon("icons/addUser.png"))
        self.setWindowFlags(self.windowFlags() & (~Qt.WindowContextHelpButtonHint))
        self.setGeometry(550, 150, 300, 200)
        self.setFixedSize(self.size())
        self.show()
        self.create_UI()

    def create_UI(self):
        self.create_widgets()
        self.create_layouts()

    def create_widgets(self):
        self.name_entry = QLineEdit()
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.confirm_password_entry = QLineEdit()
        self.confirm_password_entry.setEchoMode(QLineEdit.Password)

        # buttons
        self.submit_btn = QPushButton('Submit')
        self.submit_btn.setStyleSheet(style.btn_style())
        self.submit_btn.clicked.connect(self.add_user)

    def create_layouts(self):
        self.main_layout = QFormLayout()

        self.main_layout.addRow(QLabel("User name: "), self.name_entry)
        self.main_layout.addRow(QLabel('Password: '), self.password_entry)
        self.main_layout.addRow(QLabel('Confirm password: '), self.confirm_password_entry)
        self.main_layout.addRow(self.submit_btn)

        self.setLayout(self.main_layout)

    def add_user(self):
        username = self.name_entry.text()
        password = self.password_entry.text()
        cpassword = self.confirm_password_entry.text()

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        users = self.get_users_name()

        if any(username in user for user in users):
            QMessageBox.information(self, "Warning", 'User name has to be unique.')
        else:
            if username and password and password == cpassword:
                try:
                    self.insert_user(username, hashed)
                    QMessageBox.information(self, "Success", "User has been added.")
                    self.close()
                except:
                    QMessageBox.information(self, "Warning", "User has not been added.")
            else:
                QMessageBox.information(self, "Warning", 'Invalid data.')

    def get_users_name(self):
        return self.cursor.execute("SELECT name FROM users").fetchall()

    def insert_user(self, user_name, password):
        query = "INSERT INTO users (name,password) VALUES(?,?)"
        self.cursor.execute(query, (user_name, password))
        self.connection.commit()
