from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from datetime import date
from dataEnum import *
import style


class DisplayTaskWindow(QWidget):
    task_updated = pyqtSignal()
    entries_updated = pyqtSignal()

    def __init__(self, connection, cursor, task_id, user_id):
        super().__init__()
        self.connection = connection
        self.cursor = cursor
        self.task_id = task_id
        self.logged_user_id = user_id
        self.setWindowTitle("Task")
        self.setWindowIcon(QIcon("icons/task.png"))
        self.setGeometry(250, 150, 500, 600)
        self.setFixedSize(self.size())
        self.create_UI()

    def create_UI(self):
        self.prepare_task_details()
        self.create_widgets()
        self.create_layouts()

    def prepare_task_details(self):
        task = self.get_task()
        self.task_name = task[TaskData.NAME]
        self.task_status = task[TaskData.STATUS]
        self.assigned_user = task[TaskData.USER_ID]
        self.entries = self.get_entries_by_task_id()

    def create_widgets(self):
        # top layouts widgets
        self.task_name_text = QLabel(f'{self.task_name}')
        self.task_name_text.setAlignment(Qt.AlignCenter)

        # bottom layouts widgets
        self.task_status_box = QComboBox()
        self.task_status_box.setFont(QFont('', 10))
        self.task_status_box.addItems(['to do', 'in progress', 'done', 'closed'])
        status_index = self.task_status_box.findText(self.task_status, Qt.MatchFixedString)
        self.task_status_box.setCurrentIndex(status_index)

        self.assigned_user_box = QComboBox()
        self.assigned_user_box.addItem("--Select--")
        users = self.get_users()
        for user in users:
            self.assigned_user_box.addItem(user[UserData.NAME], user[UserData.ID])
        user_box_index = self.assigned_user_box.findData(self.assigned_user)
        self.assigned_user_box.setCurrentIndex(user_box_index)

        self.new_entry_text = QTextEdit()
        self.new_entry_text.setMaximumHeight(50)
        self.new_entry_text.setPlaceholderText("New entry...")
        self.new_entry_text.textChanged.connect(self.activate_add_entry_button)

        user_name = ''
        self.entries_list = QListWidget()
        for entry in reversed(self.entries):
            for user in users:
                if entry[EntryData.USER_ID] == user[UserData.ID]:
                    user_name = user[UserData.NAME]
                    break
            self.entries_list.addItem(QListWidgetItem(f"{entry[EntryData.DATE]}:\n{entry[EntryData.NOTE]}"
                                                      f"\nAdded by: {user_name}\n"))
        self.entries_list.setVerticalScrollBar(QScrollBar())

        # buttons
        self.add_entry_btn = QPushButton("Add entry")
        self.add_entry_btn.setStyleSheet(style.btn_style())
        self.add_entry_btn.clicked.connect(self.add_entry)
        self.add_entry_btn.setEnabled(False)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setStyleSheet(style.delete_btn_style())
        self.delete_btn.clicked.connect(self.delete_task)

        self.update_btn = QPushButton("Update")
        self.update_btn.setStyleSheet(style.btn_style())
        self.update_btn.clicked.connect(self.update_task)

        if self.logged_user_id != self.assigned_user:
            self.delete_btn.setEnabled(False)
            self.update_btn.setEnabled(False)

    def create_layouts(self):
        self.main_layout = QVBoxLayout()
        self.top_layout = QHBoxLayout()
        self.bottom_layout = QFormLayout()

        # frames
        self.top_frame = QFrame()
        self.top_frame.setStyleSheet(style.window_top_frame())
        self.bottom_frame = QFrame()
        self.bottom_frame.setStyleSheet(style.window_bottom_frame())

        # top layout
        self.top_layout.addWidget(self.task_name_text)
        self.top_frame.setLayout(self.top_layout)

        # bottom layout
        self.bottom_layout.addRow(QLabel("Status: "), self.task_status_box)
        self.bottom_layout.addRow(QLabel("Assigned user: "), self.assigned_user_box)
        self.bottom_layout.addRow(QLabel("New entry: "), self.new_entry_text)
        self.bottom_layout.addRow("", self.add_entry_btn)
        self.bottom_layout.addWidget(self.entries_list)
        self.bottom_layout.addRow("", self.delete_btn)
        self.bottom_layout.addRow("", self.update_btn)
        self.bottom_frame.setLayout(self.bottom_layout)

        self.main_layout.addWidget(self.top_frame)
        self.main_layout.addWidget(self.bottom_frame)

        self.setLayout(self.main_layout)

    def add_entry(self):
        mbox = QMessageBox.question(self, "Confirmation", "Are you sure to add this entry?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

        if mbox == QMessageBox.Yes:
            dt = date.today().strftime("%d.%m.%Y")
            note = self.new_entry_text.toPlainText()
            try:
                self.insert_entry(dt, note)
                self.entries_updated.emit()
                self.task_updated.emit()
                self.close()
            except:
                QMessageBox.information(self, "Warning", "Entry has not been added.")

    def update_task(self):
        status = self.task_status_box.currentText()
        user_id = self.assigned_user_box.currentData()

        try:
            self.update_task_data(status, user_id)
            QMessageBox.information(self, "Success", "Task has been updated.")
            self.task_updated.emit()
            self.close()
        except:
            QMessageBox.information(self, "Warning", "Task has not been updated.")

    def delete_task(self):
        mbox = QMessageBox.question(self, "Warning", "Are you sure to delete this task?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if mbox == QMessageBox.Yes:
            try:
                self.delete_entries_data()
                self.delete_task_data()
                self.task_updated.emit()
                self.close()
            except:
                QMessageBox.information(self, "Warning", "Task has not been deleted")

    def activate_add_entry_button(self):
        if len(self.new_entry_text.toPlainText()) > 0:
            self.add_entry_btn.setEnabled(True)
        else:
            self.add_entry_btn.setEnabled(False)

    def get_task(self):
        return self.cursor.execute(f"SELECT * FROM tasks WHERE id={self.task_id}").fetchone()

    def get_entries_by_task_id(self):
        return self.cursor.execute(f"SELECT * FROM entries WHERE task_id={self.task_id}").fetchall()

    def get_users(self):
        return self.cursor.execute("SELECT * FROM users").fetchall()

    def insert_entry(self, dt, note):
        query = "INSERT INTO entries (date,note,task_id,user_id) VALUES(?,?,?,?)"
        self.cursor.execute(query, (dt, note, self.task_id, self.logged_user_id))
        self.connection.commit()

    def update_task_data(self, status, user_id):
        query = "UPDATE tasks set status=?, user_id=? WHERE id=?"
        self.cursor.execute(query, (status, user_id, self.task_id))
        self.connection.commit()

    def delete_entries_data(self):
        self.cursor.execute(f"DELETE FROM entries WHERE task_id={self.task_id}")
        self.connection.commit()

    def delete_task_data(self):
        self.cursor.execute(f"DELETE FROM tasks WHERE id={self.task_id}")
        self.connection.commit()
