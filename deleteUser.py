from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import style
from dataEnum import *


class DeleteUserWindow(QWidget):
    user_deleted = pyqtSignal(int)

    def __init__(self, connection, cursor, logged_user_id):
        super().__init__()
        self.connection = connection
        self.cursor = cursor
        self.logged_user_id = logged_user_id
        self.setWindowTitle("Delete User")
        self.setWindowIcon(QIcon("icons/deleteUser.png"))
        self.setGeometry(250, 150, 450, 350)
        self.setFixedSize(self.size())
        self.create_UI()

    def create_UI(self):
        self.create_widgets()
        self.create_layouts()

    def create_widgets(self):
        # top layout widgets
        self.title = QLabel("Delete User")
        self.img = QLabel()
        self.img.setPixmap(QPixmap('icons/deleteUser.png'))
        # bottom layout widgets
        # name field
        self.users_selecte_box = QComboBox()
        self.users_selecte_box.setFont(QFont('', 10))
        self.users_selecte_box.addItem("--Select--")
        for user in self.get_users():
            self.users_selecte_box.addItem(user[UserData.NAME], user[UserData.ID])
        self.users_selecte_box.model().sort(0)

        self.submit_btn = QPushButton("Delete")
        self.submit_btn.setStyleSheet(style.delete_btn_style())
        self.submit_btn.clicked.connect(self.delete_users)

        self.user_name = self.get_logged_user()
        if self.user_name != 'admin' or self.users_selecte_box.currentIndex() == 0:
            self.submit_btn.setEnabled(False)
        self.users_selecte_box.currentIndexChanged.connect(self.set_button_availability)

    def create_layouts(self):
        self.main_layout = QVBoxLayout()
        self.top_layout = QHBoxLayout()
        self.bottom_layout = QFormLayout()

        # frames
        self.top_frame = QFrame()
        self.top_frame.setStyleSheet(style.window_top_frame())
        self.bottom_frame = QFrame()
        self.bottom_frame.setStyleSheet(style.window_bottom_frame())

        # adding widgets to layouts
        # top layout
        self.top_layout.addWidget(self.img)
        self.top_layout.addWidget(self.title)
        self.top_frame.setLayout(self.top_layout)

        # bottom layout
        self.bottom_layout.addRow(QLabel("Select User: "), self.users_selecte_box)
        self.bottom_layout.addRow("", self.submit_btn)
        self.bottom_frame.setLayout(self.bottom_layout)

        self.main_layout.addWidget(self.top_frame)
        self.main_layout.addWidget(self.bottom_frame)

        self.setLayout(self.main_layout)

    def delete_users(self):
        mbox = QMessageBox.question(self, "Warning", "Are you sure to delete this user? "
                                                     "All assigned tasks, entries and events will be deleted too!",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if mbox == QMessageBox.Yes:
            user_id = self.users_selecte_box.currentData()
            user_index = self.users_selecte_box.currentIndex()
            if self.users_selecte_box.currentText() != 'admin':
                try:
                    self.delete_user(user_id)
                    self.delete_events(user_id)
                    self.delete_entries(user_id)
                    self.delete_tasks(user_id)
                    QMessageBox.information(self, "Information", "User has been deleted")
                    self.user_deleted.emit(user_index)
                    self.close()
                except:
                    QMessageBox.information(self, "Warning", "User has not been deleted")
            else:
                QMessageBox.information(self, "Information", "User 'Admin' can not been deleted")

    def set_button_availability(self):
        if self.user_name == 'admin' and self.users_selecte_box.currentIndex() != 0:
            self.submit_btn.setEnabled(True)
        else:
            self.submit_btn.setEnabled(False)

    def get_users(self):
        return self.cursor.execute("SELECT * FROM users").fetchall()

    def get_logged_user(self):
        user_query = self.cursor.execute(f"SELECT * FROM users WHERE id={self.logged_user_id}").fetchone()
        return user_query[UserData.NAME]

    def delete_user(self, user_id):
        query_user = "DELETE FROM users WHERE id=?"
        self.cursor.execute(query_user, (user_id,))
        self.connection.commit()

    def delete_events(self, user_id):
        query_event = "DELETE FROM events WHERE id=?"
        self.cursor.execute(query_event, (user_id,))
        self.connection.commit()

    def delete_entries(self, user_id):
        query_entry = "DELETE FROM entries WHERE user_id=?"
        self.cursor.execute(query_entry, (user_id,))
        self.connection.commit()

    def delete_tasks(self, user_id):
        query_task = "DELETE FROM tasks WHERE user_id=?"
        self.cursor.execute(query_task, (user_id,))
        self.connection.commit()
