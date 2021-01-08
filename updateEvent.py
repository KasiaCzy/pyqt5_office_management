from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from datetime import datetime
import style
from dataEnum import EventData


class UpdateEventWindow(QWidget):
    event_updated = pyqtSignal()

    def __init__(self, connection, cursor, event_id):
        super().__init__()
        self.connection = connection
        self.cursor = cursor
        self.selected_event_id = event_id
        self.setWindowTitle("Update event")
        self.setWindowIcon(QIcon("icons/addEvent.png"))
        self.setGeometry(250, 150, 320, 400)
        self.setFixedSize(self.size())
        self.create_UI()

    def create_UI(self):
        self.create_widgets()
        self.create_layouts()

    def create_widgets(self):
        # top layout widgets
        self.text = QLabel("Update Event")
        self.text.setAlignment(Qt.AlignCenter)

        # bottom layout widgets
        event = self.get_events(self.selected_event_id)
        self.events_box = QComboBox()
        self.events_box.addItems(['holiday', 'work day'])
        index = self.events_box.findText(event[EventData.NAME], Qt.MatchFixedString)
        self.events_box.setCurrentIndex(index)

        self.event_date = QDateEdit()
        self.event_date.setFont(QFont('', 10))
        dt = datetime.strptime(event[EventData.DATE], "%d.%m.%Y")
        self.event_date.setDate(dt)
        self.event_date.setCalendarPopup(True)

        self.note_entry = QTextEdit()
        self.note_entry.setMaximumHeight(50)
        self.note_entry.setText(event[EventData.NOTE])

        # button
        self.submit_btn = QPushButton("Submit")
        self.submit_btn.clicked.connect(self.submit_update)
        self.submit_btn.setStyleSheet(style.btn_style())

    def create_layouts(self):
        self.main_layout = QVBoxLayout()
        self.top_layout = QVBoxLayout()
        self.bottom_layout = QFormLayout()
        self.top_frame = QFrame()
        self.bottom_frame = QFrame()

        # top layout
        self.top_layout.addWidget(self.text)
        self.top_frame.setLayout(self.top_layout)

        # bottom layout
        self.bottom_layout.addRow(QLabel("Event: "), self.events_box)
        self.bottom_layout.addRow(QLabel("Date: "), self.event_date)
        self.bottom_layout.addRow(QLabel("More details: "), self.note_entry)
        self.bottom_layout.addRow("", self.submit_btn)
        self.bottom_frame.setLayout(self.bottom_layout)

        self.main_layout.addWidget(self.top_frame)
        self.main_layout.addWidget(self.bottom_frame)

        self.setLayout(self.main_layout)

    def submit_update(self):
        name = self.events_box.currentText()
        date = self.event_date.text()
        note = self.note_entry.toPlainText()
        try:
            self.update_event(name, date, note)
            self.event_updated.emit()
            QMessageBox.information(self, "Success", "Event has been updated.")
            self.close()
        except:
            QMessageBox.information(self, "Warning", "Event has not been updated.")

    def get_events(self, event_id):
        return self.cursor.execute(f"SELECT * FROM events WHERE id={event_id}").fetchone()

    def update_event(self, name, date, note):
        query = "UPDATE events set name=?, date=?, note=? WHERE id=?"
        self.cursor.execute(query, (name, date, note, self.selected_event_id))
        self.connection.commit()
