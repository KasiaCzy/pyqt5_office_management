from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import style


class DeleteUserWindow(QWidget):

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
        query_user = "SELECT id,name FROM users"
        users = self.cursor.execute(query_user).fetchall()

        for user in users:
            self.users_selecte_box.addItem(user[1], user[0])

        self.submit_btn = QPushButton("Delete")
        self.submit_btn.setStyleSheet(style.delete_btn_style())
        self.submit_btn.clicked.connect(self.delete_user)
        user_query = self.cursor.execute(f"SELECT name FROM users WHERE id={self.logged_user_id}").fetchone()
        user_name = user_query[0]
        if user_name != 'admin':
            self.submit_btn.setEnabled(False)

    def create_layouts(self):
        self.main_layout = QVBoxLayout()
        self.top_layout = QHBoxLayout()
        self.bottom_layout = QFormLayout()
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

    def delete_user(self):
        mbox = QMessageBox.question(self, "Warning", "Are you sure to delete this user? "
                                                     "All assigned tasks, entries and events will be deleted too!",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if mbox == QMessageBox.Yes:
            user_id = self.users_selecte_box.currentData()
            if self.users_selecte_box.currentText() != 'admin':
                try:
                    query_user = "DELETE FROM users WHERE id=?"
                    self.cursor.execute(query_user, (user_id,))
                    self.connection.commit()
                    query_events = "DELETE FROM events WHERE user_id=?"
                    self.cursor.execute(query_events, (user_id,))
                    self.connection.commit()
                    query_entries = "DELETE FROM entries WHERE user_id=?"
                    self.cursor.execute(query_entries, (user_id,))
                    self.connection.commit()
                    query_task = "DELETE FROM tasks WHERE user_id=?"
                    self.cursor.execute(query_task, (user_id,))
                    self.connection.commit()
                    QMessageBox.information(self, "Information", "User has been deleted")
                    self.close()
                except:
                    QMessageBox.information(self, "Warning", "User has not been deleted")
            else:
                QMessageBox.information(self, "Information", "User 'Admin' can not been deleted")