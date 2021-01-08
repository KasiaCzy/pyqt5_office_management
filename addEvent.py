from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import style


class AddEventWindow(QWidget):
    event_added = pyqtSignal()

    def __init__(self, connection, cursor, date, user_id):
        super().__init__()
        self.connection = connection
        self.cursor = cursor
        self.date = date
        self.logged_user_id = user_id
        self.setWindowTitle("Add event")
        self.setWindowIcon(QIcon("icons/addEvent.png"))
        self.setGeometry(250, 150, 300, 400)
        self.setFixedSize(self.size())
        self.create_UI()

    def create_UI(self):
        self.create_widgets()
        self.create_layouts()

    def create_widgets(self):
        # top layout widgets
        self.text = QLabel("Event")
        self.text.setAlignment(Qt.AlignCenter)
        self.img = QLabel()
        self.img.setPixmap(QPixmap('icons/addEvent.png'))
        self.img.setAlignment(Qt.AlignCenter)

        # bottom layout widgets
        self.events_box = QComboBox()
        self.events_box.addItems(['--Select--', 'holiday', 'work day'])

        self.note_entry = QTextEdit()
        self.note_entry.setMaximumHeight(50)
        self.note_entry.setPlaceholderText("Enter useful information")

        self.submit_btn = QPushButton("Submit")
        self.submit_btn.setStyleSheet(style.btn_style())
        self.submit_btn.clicked.connect(self.add_event)

    def create_layouts(self):
        self.main_layout = QVBoxLayout()
        self.top_layout = QVBoxLayout()
        self.bottom_layout = QFormLayout()

        # frames
        self.top_frame = QFrame()
        self.top_frame.setStyleSheet(style.window_top_frame())
        self.bottom_frame = QFrame()
        self.bottom_frame.setStyleSheet(style.window_bottom_frame())

        # top layout
        self.top_layout.addWidget(self.text)
        self.top_layout.addWidget(self.img)
        self.top_frame.setLayout(self.top_layout)

        # bottom layout
        self.bottom_layout.addRow(QLabel("Event: "), self.events_box)
        self.bottom_layout.addRow(QLabel("More details: "), self.note_entry)
        self.bottom_layout.addRow("", self.submit_btn)
        self.bottom_frame.setLayout(self.bottom_layout)

        self.main_layout.addWidget(self.top_frame)
        self.main_layout.addWidget(self.bottom_frame)

        self.setLayout(self.main_layout)

    def add_event(self):
        name = self.events_box.currentText()
        note = self.note_entry.toPlainText()
        if self.events_box.currentIndex() != 0:
            try:
                self.insert_event(name, note)
                self.event_added.emit()
                self.close()
            except:
                QMessageBox.information(self, "Warning", "Event has not been added.")
        else:
            QMessageBox.information(self, "Warning", 'Field: "Event" can not be empty.')

    def insert_event(self, name, note):
        query = "INSERT INTO 'events' (name,date,note,user_id) VALUES (?,?,?,?)"
        self.cursor.execute(query, (name, self.date, note, self.logged_user_id))
        self.connection.commit()
