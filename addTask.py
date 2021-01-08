from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import style
from dataEnum import UserData


class AddTaskWindow(QWidget):
    task_confirmed = pyqtSignal()

    def __init__(self, connection, cursor):
        super().__init__()
        self.connection = connection
        self.cursor = cursor
        self.setWindowTitle("Add task")
        self.setWindowIcon(QIcon("icons/addTask.png"))
        self.setGeometry(250, 150, 400, 700)
        self.setFixedSize(self.size())
        self.create_UI()

    def create_UI(self):
        self.create_widgets()
        self.create_layouts()

    def create_widgets(self):
        # top layout widgets
        self.text = QLabel("Task")
        self.text.setAlignment(Qt.AlignCenter)
        self.img = QLabel()
        self.img.setPixmap(QPixmap('icons/addTask.png'))
        self.img.setAlignment(Qt.AlignCenter)

        # bottom layout widgets
        # name field
        self.name_entry = QLineEdit()
        self.name_entry.setFont(QFont('', 10))
        self.name_entry.setPlaceholderText("Enter task name")

        self.user_box = QComboBox()
        self.user_box.addItem("--Select--")
        for user in self.get_users():
            self.user_box.addItem(user[UserData.NAME], user[UserData.ID])

        self.status_box = QComboBox()
        self.status_box.addItems(['--Select--', 'to do', 'in progress', 'done', 'closed'])

        self.submit_btn = QPushButton("Submit")
        self.submit_btn.setStyleSheet(style.btn_style())
        self.submit_btn.clicked.connect(self.submit_task)

    def create_layouts(self):
        self.main_layout = QVBoxLayout()
        self.top_layout = QVBoxLayout()
        self.bottom_layout = QFormLayout()
        self.top_frame = QFrame()
        self.top_frame.setStyleSheet(style.window_top_frame())
        self.bottom_frame = QFrame()
        self.bottom_frame.setStyleSheet(style.window_bottom_frame())

        # top layout
        self.top_layout.addWidget(self.text)
        self.top_layout.addWidget(self.img)
        self.top_frame.setLayout(self.top_layout)

        # bottom layout
        self.bottom_layout.addRow(QLabel("Name: "), self.name_entry)
        self.bottom_layout.addRow(QLabel("Assign user: "), self.user_box)
        self.bottom_layout.addRow(QLabel("Status: "), self.status_box)
        self.bottom_layout.addRow("", self.submit_btn)
        self.bottom_frame.setLayout(self.bottom_layout)

        self.main_layout.addWidget(self.top_frame)
        self.main_layout.addWidget(self.bottom_frame)

        self.setLayout(self.main_layout)

    def submit_task(self):
        self.name = self.name_entry.text()
        self.user_id = self.user_box.currentData()
        self.user_name = self.user_box.currentText()
        self.status = self.status_box.currentText()
        if self.user_box.currentIndex() == 0 or self.status_box.currentIndex() == 0 or not self.name:
            QMessageBox.information(self, "Warning", 'Enter all fields')
        else:
            self.task_confirmed.emit()
            self.close()

    def get_users(self):
        return self.cursor.execute("SELECT * FROM users").fetchall()


class ConfirmWindow(QWidget):
    task_added = pyqtSignal()

    def __init__(self, connection, cursor, name, user_id, user_name, status):
        super().__init__()
        self.connection = connection
        self.cursor = cursor
        self.confirm_name = name
        self.confirm_user_id = user_id
        self.confirm_user_name = user_name
        self.confirm_status = status
        self.setWindowTitle("Confirm Task")
        self.setWindowIcon(QIcon("icons/addTask.png"))
        self.setGeometry(250, 150, 400, 600)
        self.setFixedSize(self.size())
        self.create_UI()

    def create_UI(self):
        self.create_widgets()
        self.create_layouts()

    def create_widgets(self):
        # top layout widgets
        self.text = QLabel("Task")
        self.text.setAlignment(Qt.AlignCenter)
        self.img = QLabel()
        self.img.setPixmap(QPixmap('icons/addTask.png'))
        self.img.setAlignment(Qt.AlignCenter)

        # bottom layout widgets
        self.name_label = QLabel()
        self.name_label.setText(self.confirm_name)

        self.user_label = QLabel()
        self.user_label.setText(self.confirm_user_name)

        self.status_label = QLabel()
        self.status_label.setText(self.confirm_status)

        self.confirm_btn = QPushButton("Confirm")
        self.confirm_btn.setStyleSheet(style.btn_style())
        self.confirm_btn.clicked.connect(self.confirm_task)

    def create_layouts(self):
        self.main_layout = QVBoxLayout()
        self.top_layout = QVBoxLayout()
        self.bottom_layout = QFormLayout()
        self.top_frame = QFrame()
        self.top_frame.setStyleSheet(style.window_top_frame())
        self.bottom_frame = QFrame()
        self.bottom_frame.setStyleSheet(style.window_bottom_frame())

        # top layout
        self.top_layout.addWidget(self.text)
        self.top_layout.addWidget(self.img)
        self.top_frame.setLayout(self.top_layout)

        # bottom layout
        self.bottom_layout.addRow(QLabel("Name: "), self.name_label)
        self.bottom_layout.addRow(QLabel("Assigned user: "), self.user_label)
        self.bottom_layout.addRow(QLabel("Status: "), self.status_label)
        self.bottom_layout.addRow("", self.confirm_btn)
        self.bottom_frame.setLayout(self.bottom_layout)

        self.main_layout.addWidget(self.top_frame)
        self.main_layout.addWidget(self.bottom_frame)

        self.setLayout(self.main_layout)

    def confirm_task(self):
        try:
            self.insert_task()
            self.task_added.emit()
            self.close()
        except:
            QMessageBox.information(self, "Warning", "Task has not been added.")

    def insert_task(self):
        query = "INSERT INTO 'tasks' (name,status,user_id) VALUES (?,?,?)"
        self.cursor.execute(query, (self.confirm_name, self.confirm_status, self.confirm_user_id))
        self.connection.commit()