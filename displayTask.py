from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from datetime import date
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
        query_task = "SELECT * FROM tasks WHERE id=?"
        task = self.cursor.execute(query_task, (self.task_id,)).fetchone()
        self.task_name = task[1]
        self.task_status = task[2]
        self.assigned_user = task[3]
        query_entries = "SELECT * FROM entries WHERE task_id=?"
        self.entries = self.cursor.execute(query_entries, (self.task_id,)).fetchall()

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

        query_user = "SELECT id,name FROM users"
        users = self.cursor.execute(query_user).fetchall()

        for user in users:
            self.assigned_user_box.addItem(user[1], user[0])
        user_box_index = self.assigned_user_box.findData(self.assigned_user)
        self.assigned_user_box.setCurrentIndex(user_box_index)

        self.new_entry_text = QTextEdit()
        self.new_entry_text.setMaximumHeight(50)
        self.new_entry_text.setPlaceholderText("New entry...")

        user_name = ''
        self.entries_list = QListWidget()
        for entry in reversed(self.entries):
            for user in users:
                if entry[4] == user[0]:
                    user_name = user[1]
                    break
            self.entries_list.addItem(QListWidgetItem(f"{entry[1]}:\n{entry[2]}\nAdded by: {user_name}\n"))
        self.entries_list.setVerticalScrollBar(QScrollBar())

        self.add_entry_btn = QPushButton("Add entry")
        self.add_entry_btn.setStyleSheet(style.btn_style())
        self.add_entry_btn.clicked.connect(self.add_entry)
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
                query = "INSERT INTO entries (date,note,task_id,user_id) VALUES(?,?,?,?)"
                self.cursor.execute(query, (dt, note, self.task_id, self.logged_user_id))
                self.connection.commit()
                QMessageBox.information(self, "Success", "Entry has been added.")
                self.entries_updated.emit()
                self.task_updated.emit()
                self.close()
            except:
                QMessageBox.information(self, "Warning", "Entry has not been added.")

    def update_task(self):
        status = self.task_status_box.currentText()
        user_id = self.assigned_user_box.currentData()

        try:
            query = "UPDATE tasks set status=?, user_id=? WHERE id=?"
            self.cursor.execute(query, (status, user_id, self.task_id))
            self.connection.commit()
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
                query_entries = "DELETE FROM entries WHERE task_id=?"
                self.cursor.execute(query_entries, (self.task_id,))
                self.connection.commit()
                query_task = "DELETE FROM tasks WHERE id=?"
                self.cursor.execute(query_task, (self.task_id,))
                self.connection.commit()
                QMessageBox.information(self, "Information", "Task has been deleted")
                self.task_updated.emit()
                self.close()
            except:
                QMessageBox.information(self, "Warning", "Task has not been deleted")