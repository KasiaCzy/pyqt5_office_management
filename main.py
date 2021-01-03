import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sqlite3
from datetime import date
import bcrypt
from deleteUser import DeleteUserWindow
from addTask import AddTaskWindow, ConfirmWindow
from addEvent import AddEventWindow
from loginWindow import LoginWindow
from displayTask import DisplayTaskWindow
from updateEvent import UpdateEventWindow
import style


class MainApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)

        self.connection = sqlite3.connect("office.db")
        self.cursor = self.connection.cursor()

        self.login_window = LoginWindow(self.connection, self.cursor)
        self.login_window.show()
        self.login_window.login_successful.connect(self.create_main_window)

    def create_main_window(self):
        self.main_window = MainWindow(self.connection, self.cursor, self.login_window.logged_user_id)
        self.main_window.show()
        self.login_window.active_user_name.connect(self.main_window.logged_user_label.setText)

        self.main_window.delete_user_requested.connect(self.create_delete_user_window)

        self.main_window.add_task_requested.connect(self.create_add_task_window)

        self.main_window.display_task_requested.connect(self.create_display_task_window)

        self.main_window.add_event_requested.connect(self.create_add_event_window)

        self.main_window.update_event_requested.connect(self.create_update_event_window)

    def create_delete_user_window(self):
        self.delete_user_window = DeleteUserWindow(self.connection, self.cursor, self.main_window.logged_user_id)
        self.delete_user_window.show()

    def create_add_task_window(self):
        self.add_task_window = AddTaskWindow(self.connection, self.cursor)
        self.add_task_window.show()
        self.add_task_window.confirm_task.connect(self.create_confirm_task_window)

    def create_display_task_window(self):
        self.display_task_window = DisplayTaskWindow(self.connection, self.cursor, self.main_window.task_id,
                                                     self.main_window.logged_user_id)
        self.display_task_window.show()
        self.display_task_window.task_updated.connect(self.main_window.refresh_view)
        self.display_task_window.entries_updated.connect(self.create_display_task_window)

    def create_add_event_window(self):
        self.add_event_window = AddEventWindow(self.connection, self.cursor, self.main_window.db_date,
                                               self.main_window.logged_user_id)
        self.add_event_window.show()
        self.add_event_window.event_added.connect(self.main_window.refresh_events_calendar_view)

    def create_confirm_task_window(self):
        self.confirm_window = ConfirmWindow(self.connection, self.cursor, self.add_task_window.name,
                                            self.add_task_window.user_id, self.add_task_window.user_name,
                                            self.add_task_window.status)
        self.confirm_window.show()
        self.confirm_window.task_added.connect(self.main_window.refresh_view)

    def create_update_event_window(self):
        self.update_event_window = UpdateEventWindow(self.connection, self.cursor, self.main_window.selected_event_id)
        self.update_event_window.show()


class MainWindow(QMainWindow):
    delete_user_requested = pyqtSignal(bool)
    add_task_requested = pyqtSignal(bool)
    add_event_requested = pyqtSignal()
    display_task_requested = pyqtSignal()
    update_event_requested = pyqtSignal()

    def __init__(self, connection, cursor, logged_user_id):
        super().__init__()
        self.connection = connection
        self.cursor = cursor
        self.task_id = None
        self.logged_user_id = logged_user_id
        self.setWindowTitle("Office")
        self.setWindowIcon(QIcon("icons/mainIcon.png"))
        self.setGeometry(250, 150, 1350, 800)
        self.setFixedSize(self.size())
        self.create_UI()

    def create_UI(self):
        self.create_tool_bar()
        self.create_tab_widget()
        self.create_widgets()
        self.create_layouts()
        self.display_tasks()
        self.display_user_tasks()

    def create_tool_bar(self):
        self.tb = self.addToolBar("Tool Bar")
        self.tb.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        # Buttons
        # delete user
        self.delete_user = QAction(QIcon("icons/deleteUser.png"), "Delete user", self)
        self.tb.addAction(self.delete_user)
        self.delete_user.triggered.connect(self.delete_user_requested)
        self.tb.addSeparator()
        # add topic
        self.add_topic = QAction(QIcon("icons/addTask.png"), "Add task", self)
        self.tb.addAction(self.add_topic)
        self.add_topic.triggered.connect(self.add_task_requested)
        self.tb.addSeparator()
        # refresh button
        self.refresh = QAction(QIcon("icons/refresh.png"), "Refresh a view", self)
        self.tb.addAction(self.refresh)
        self.refresh.triggered.connect(self.refresh_view)
        self.tb.addSeparator()
        # user label
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.tb.addWidget(spacer)
        self.tb_user_label = QLabel("User: ")
        self.tb_user_label.setFont(QFont("Arial", 14))
        self.tb.addWidget(self.tb_user_label)
        self.logged_user_label = QLabel("")
        self.logged_user_label.setFont(QFont("Arial", 14))
        self.tb.addWidget(self.logged_user_label)

    def create_tab_widget(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tab_check_list = QWidget()
        self.tab_calendar = QWidget()
        self.tab_users = QWidget()
        self.tabs.addTab(self.tab_check_list, QIcon("icons/tasks.png"), "Check List")
        self.tabs.addTab(self.tab_calendar, QIcon("icons/calendar.png"), "Calendar")
        self.tabs.addTab(self.tab_users, QIcon("icons/users.png"), "About User")

    def create_widgets(self):
        self.create_tab_check_list_widgets()
        self.create_tab_calendar_widgets()
        self.create_tab_user_widgets()

    def create_tab_check_list_widgets(self):
        # check_list table widget
        self.check_list_table = QStandardItemModel(0, 5)
        self.check_list_table.setHorizontalHeaderItem(0, QStandardItem("Id"))
        self.check_list_table.setHorizontalHeaderItem(1, QStandardItem("Task"))
        self.check_list_table.setHorizontalHeaderItem(2, QStandardItem("Last entry"))
        self.check_list_table.setHorizontalHeaderItem(3, QStandardItem("Assigned to"))
        self.check_list_table.setHorizontalHeaderItem(4, QStandardItem("Status"))
        self.filter_proxy_model = QSortFilterProxyModel()
        self.filter_proxy_model.setSourceModel(self.check_list_table)
        self.filter_proxy_model.setFilterKeyColumn(1)
        self.check_list_table_view = QTableView()
        self.check_list_table_view.setModel(self.filter_proxy_model)
        self.check_list_table_view.setColumnHidden(0, True)
        self.check_list_table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.check_list_table_view.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.check_list_table_view.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.check_list_table_view.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.check_list_table_view.doubleClicked.connect(self.display_selected_task)
        self.check_list_table_view.clicked.connect(self.display_single_click_check_list_table)

        # right top layout widget
        self.tasks_search_text = QLabel("Search")
        self.tasks_search_entry = QLineEdit()
        self.tasks_search_entry.setPlaceholderText("Search for task")
        self.tasks_search_entry.textChanged.connect(self.filter_proxy_model.setFilterRegExp)

        # right middle layout widget
        self.all_tasks = QRadioButton("All tasks")
        self.all_tasks.setChecked(True)
        self.all_tasks.toggled.connect(self.filter_by_status)
        self.to_do_status = QRadioButton("To do")
        self.to_do_status.toggled.connect(self.filter_by_status)
        self.in_progress_status = QRadioButton("In progress")
        self.in_progress_status.toggled.connect(self.filter_by_status)
        self.done_status = QRadioButton("Done")
        self.done_status.toggled.connect(self.filter_by_status)
        self.closed_status = QRadioButton("Closed")
        self.closed_status.toggled.connect(self.filter_by_status)

        # right bottom layout widget
        self.user_box = QComboBox()
        self.user_box.addItem("--User--")

        query_user = "SELECT id,name FROM users"
        users = self.cursor.execute(query_user).fetchall()
        for user in users:
            self.user_box.addItem(user[1], user[0])
        self.user_box.model().sort(0)
        self.user_box.currentTextChanged.connect(self.filter_by_user)

    def create_tab_calendar_widgets(self):
        self.calendar = QCalendarWidget(self)
        self.calendar.clicked.connect(self.display_selected_day)

        self.day_events_list = QListWidget()
        self.day_events_list.setVerticalScrollBar(QScrollBar())

        self.calendar_users_box = QComboBox()
        self.calendar_users_box.addItem('--Select--')
        query_user = "SELECT id,name FROM users"
        users = self.cursor.execute(query_user).fetchall()
        for user in users:
            self.calendar_users_box.addItem(user[1], user[0])
        self.calendar_users_box.currentTextChanged.connect(self.filter_calendar_events)
        self.calendar_events_box = QComboBox()
        self.calendar_events_box.addItems(['--Select--', 'holiday', 'work day'])
        self.calendar_events_box.currentTextChanged.connect(self.filter_calendar_events)
        self.calendar_events_list = QListWidget()

    def create_tab_user_widgets(self):
        # left layout widget
        self.new_user_name = QLineEdit()
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)

        self.submit_user_name_btn = QPushButton('Update')
        self.submit_user_name_btn.setStyleSheet(style.btn_style())
        self.submit_user_name_btn.clicked.connect(self.update_username)
        self.submit_password_btn = QPushButton('Update')
        self.submit_password_btn.setStyleSheet(style.btn_style())
        self.submit_password_btn.clicked.connect(self.update_password)

        # middle layout widget
        self.select_event_box = QComboBox()
        self.select_event_box.addItems(['--Select--', 'holiday', 'work day'])
        self.select_event_box.currentTextChanged.connect(self.display_selected_event_for_user)
        self.selected_event_list = QListWidget()
        self.selected_event_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.selected_event_list.setVerticalScrollBar(QScrollBar())
        self.selected_event_update_btn = QPushButton('Update')
        self.selected_event_update_btn.setStyleSheet(style.btn_style())
        self.selected_event_update_btn.clicked.connect(self.update_selected_event)
        self.selected_event_delete_btn = QPushButton('Delete')
        self.selected_event_delete_btn.setStyleSheet(style.delete_btn_style())
        self.selected_event_delete_btn.clicked.connect(self.delete_selected_event)
        self.total_holiday_label = QLabel('')
        total_holiday = self.cursor.execute(f"SELECT count (id) FROM events WHERE user_id={self.logged_user_id} "
                                            f"and name='holiday'").fetchall()[0][0]
        self.total_holiday_label.setText(str(total_holiday))
        self.total_workday_label = QLabel('')
        total_workday = self.cursor.execute(f"SELECT count (id) FROM events WHERE user_id={self.logged_user_id} "
                                            f"and name='work day'").fetchall()[0][0]
        self.total_workday_label.setText(str(total_workday))

        # right layout widget
        self.logged_user_tasks_list = QListWidget()

    def create_layouts(self):
        self.create_tab_check_list_layout()
        self.create_tab_calendar_layout()
        self.create_tab_user_layout()

    def create_tab_check_list_layout(self):
        self.check_list_main_layout = QHBoxLayout()
        self.check_list_main_left_layout = QVBoxLayout()
        self.check_list_main_right_layout = QVBoxLayout()
        self.check_list_right_first_layout = QHBoxLayout()
        self.check_list_right_second_layout = QHBoxLayout()
        self.check_list_right_third_layout = QHBoxLayout()
        self.check_list_right_fourth_layout = QVBoxLayout()
        self.check_list_first_group_box = QGroupBox("Search")
        self.check_list_first_group_box.setStyleSheet(style.search_box_style())
        self.check_list_second_group_box = QGroupBox("Filter by status")
        self.check_list_second_group_box.setStyleSheet(style.status_box_style())
        self.check_list_third_group_box = QGroupBox("Filter by user")
        self.check_list_third_group_box.setStyleSheet(style.users_box_style())
        self.check_list_fourth_group_box = QFrame()
        self.check_list_fourth_group_box.setStyleSheet(style.check_list_entries_frame())

        # add widgets
        self.check_list_main_left_layout.addWidget(self.check_list_table_view)

        self.check_list_right_first_layout.addWidget(self.tasks_search_text)
        self.check_list_right_first_layout.addWidget(self.tasks_search_entry)
        self.check_list_first_group_box.setLayout(self.check_list_right_first_layout)

        self.check_list_right_second_layout.addWidget(self.all_tasks)
        self.check_list_right_second_layout.addWidget(self.to_do_status)
        self.check_list_right_second_layout.addWidget(self.in_progress_status)
        self.check_list_right_second_layout.addWidget(self.done_status)
        self.check_list_right_second_layout.addWidget(self.closed_status)
        self.check_list_second_group_box.setLayout(self.check_list_right_second_layout)

        self.check_list_right_third_layout.addWidget(self.user_box)
        self.check_list_third_group_box.setLayout(self.check_list_right_third_layout)

        self.check_list_fourth_group_box.setLayout(self.check_list_right_fourth_layout)

        # add layouts
        self.check_list_main_layout.addLayout(self.check_list_main_left_layout, 60)
        self.check_list_main_layout.addLayout(self.check_list_main_right_layout, 40)
        self.check_list_main_right_layout.addWidget(self.check_list_first_group_box, 15)
        self.check_list_main_right_layout.addWidget(self.check_list_second_group_box, 15)
        self.check_list_main_right_layout.addWidget(self.check_list_third_group_box, 15)
        self.check_list_main_right_layout.addWidget(self.check_list_fourth_group_box, 55)
        self.tab_check_list.setLayout(self.check_list_main_layout)

    def create_tab_calendar_layout(self):
        self.calendar_main_layout = QHBoxLayout()
        self.calendar_main_left_layout = QVBoxLayout()
        self.calendar_main_right_layout = QVBoxLayout()
        self.calendar_top_right_layout = QVBoxLayout()
        self.calendar_top_right_form_layout = QFormLayout()
        self.calendar_top_right_list_layout = QVBoxLayout()
        self.calendar_bottom_right_layout = QVBoxLayout()
        self.calendar_bottom_right_form_layout = QFormLayout()
        self.calendar_bottom_right_list_layout = QVBoxLayout()
        self.calendar_top_right_frame = QFrame()
        self.calendar_top_right_frame.setStyleSheet(style.calendar_top_frame())
        self.calendar_bottom_right_frame = QFrame()
        self.calendar_bottom_right_frame.setStyleSheet(style.calendar_bottom_frame())

        # add widgets
        self.calendar_main_left_layout.addWidget(self.calendar)

        self.calendar_bottom_right_form_layout.addRow(QLabel('Select User:'), self.calendar_users_box)
        self.calendar_bottom_right_form_layout.addRow(QLabel('Select Event:'), self.calendar_events_box)
        self.calendar_bottom_right_list_layout.addWidget(self.calendar_events_list)

        self.calendar_top_right_layout.addLayout(self.calendar_top_right_form_layout)
        self.calendar_top_right_layout.addLayout(self.calendar_top_right_list_layout)
        self.calendar_top_right_frame.setLayout(self.calendar_top_right_layout)

        self.calendar_bottom_right_layout.addLayout(self.calendar_bottom_right_form_layout)
        self.calendar_bottom_right_layout.addLayout(self.calendar_bottom_right_list_layout)
        self.calendar_bottom_right_frame.setLayout(self.calendar_bottom_right_layout)

        # add layouts
        self.calendar_main_right_layout.addWidget(self.calendar_top_right_frame, 40)
        self.calendar_main_right_layout.addWidget(self.calendar_bottom_right_frame, 60)
        self.calendar_main_layout.addLayout(self.calendar_main_left_layout, 65)
        self.calendar_main_layout.addLayout(self.calendar_main_right_layout, 35)
        self.tab_calendar.setLayout(self.calendar_main_layout)

    def create_tab_user_layout(self):
        self.user_main_layout = QHBoxLayout()
        self.user_left_layout = QFormLayout()
        self.user_middle_layout = QVBoxLayout()
        self.user_top_middle_layout = QFormLayout()
        self.user_center_middle_layout = QVBoxLayout()
        self.user_bottom_middle_layout = QFormLayout()
        self.user_right_layout = QVBoxLayout()
        self.user_left_frame = QFrame()
        self.user_left_frame.setStyleSheet(style.user_left_frame())
        self.user_middle_frame = QFrame()
        self.user_middle_frame.setStyleSheet(style.user_middle_frame())
        self.user_right_frame = QFrame()
        self.user_right_frame.setStyleSheet(style.user_right_frame())

        self.user_left_layout.addRow(QLabel('Enter new username:'), self.new_user_name)
        self.user_left_layout.addRow("", self.submit_user_name_btn)
        self.user_left_layout.addRow(QLabel('Enter new password:'), self.new_password)
        self.user_left_layout.addRow(QLabel('Confirm new password:'), self.confirm_password)
        self.user_left_layout.addRow("", self.submit_password_btn)
        self.user_left_frame.setLayout(self.user_left_layout)

        self.user_top_middle_layout.addRow(QLabel('Total holidays: '), self.total_holiday_label)
        self.user_top_middle_layout.addRow(QLabel('Total work days: '), self.total_workday_label)
        self.user_center_middle_layout.addWidget(QLabel('Select Event:'))
        self.user_center_middle_layout.addWidget(self.select_event_box)
        self.user_center_middle_layout.addWidget(self.selected_event_list)
        self.user_bottom_middle_layout.addRow(QLabel('Update selected event: '), self.selected_event_update_btn)
        self.user_bottom_middle_layout.addRow(QLabel('Delete selected events: '), self.selected_event_delete_btn)
        self.user_middle_layout.addLayout(self.user_top_middle_layout, 10)
        self.user_middle_layout.addLayout(self.user_center_middle_layout, 80)
        self.user_middle_layout.addLayout(self.user_bottom_middle_layout, 10)
        self.user_middle_frame.setLayout(self.user_middle_layout)

        self.user_right_layout.addWidget(QLabel('Tasks assigned to you:'))
        self.user_right_layout.addWidget(self.logged_user_tasks_list)
        self.user_right_frame.setLayout(self.user_right_layout)

        self.user_main_layout.addWidget(self.user_left_frame, 25)
        self.user_main_layout.addWidget(self.user_middle_frame, 35)
        self.user_main_layout.addWidget(self.user_right_frame, 40)

        self.tab_users.setLayout(self.user_main_layout)

    def display_tasks(self):
        self.check_list_table_view.setFont(QFont("Arial", 12))
        for i in reversed(range(self.check_list_table.rowCount())):
            self.check_list_table.removeRow(i)
        user_query = self.cursor.execute("SELECT id,name FROM users").fetchall()
        entry_query = self.cursor.execute("SELECT id,note,task_id FROM entries").fetchall()
        task_query = self.cursor.execute("SELECT id,name,status,user_id FROM tasks")
        self.fill_check_list_table(task_query, user_query, entry_query)

    def display_selected_task(self):
        index = self.check_list_table_view.currentIndex()
        new_index = self.check_list_table_view.model().index(index.row(), 0)
        self.task_id = self.check_list_table_view.model().data(new_index)
        self.display_task_requested.emit()

    def display_single_click_check_list_table(self):
        index = self.check_list_table_view.currentIndex()
        new_index = self.check_list_table_view.model().index(index.row(), 0)
        self.selected_task_id = self.check_list_table_view.model().data(new_index)
        # plants_right_bottom_layout
        for i in reversed(range(self.check_list_right_fourth_layout.count())):
            widget = self.check_list_right_fourth_layout.takeAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        query_user = "SELECT id,name FROM users"
        users = self.cursor.execute(query_user).fetchall()
        query_entries = "SELECT * FROM entries WHERE task_id=?"
        entries = self.cursor.execute(query_entries, (self.selected_task_id,)).fetchall()

        self.new_entry_text = QTextEdit()
        self.new_entry_text.setMaximumHeight(50)
        self.new_entry_text.setPlaceholderText("New entry...")

        user_name = ''
        self.entries_list = QListWidget()
        for entry in reversed(entries):
            for user in users:
                if entry[4] == user[0]:
                    user_name = user[1]
                    break
            self.entries_list.addItem(QListWidgetItem(f"{entry[1]}:\n{entry[2]}\nAdded by: {user_name}\n"))
        self.entries_list.setVerticalScrollBar(QScrollBar())

        add_entry_btn = QPushButton("Add")
        add_entry_btn.clicked.connect(self.add_entry)
        add_entry_btn.setStyleSheet(style.btn_style())

        self.check_list_right_fourth_layout.addWidget(self.new_entry_text)
        self.check_list_right_fourth_layout.addWidget(add_entry_btn)
        self.check_list_right_fourth_layout.addWidget(self.entries_list)

    def add_entry(self):
        mbox = QMessageBox.question(self, "Confirmation", "Are you sure to add this entry?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

        if mbox == QMessageBox.Yes:
            dt = date.today().strftime("%d.%m.%Y")
            note = self.new_entry_text.toPlainText()

            try:
                query = "INSERT INTO entries (date,note,task_id,user_id) VALUES(?,?,?,?)"
                self.cursor.execute(query, (dt, note, self.selected_task_id, self.logged_user_id))
                self.connection.commit()
                QMessageBox.information(self, "Success", "Entry has been added.")
                self.display_single_click_check_list_table()
            except:
                QMessageBox.information(self, "Warning", "Entry has not been added.")

    def filter_by_status(self):
        radio_btn = self.sender()
        if radio_btn.isChecked():
            if radio_btn == self.all_tasks:
                if self.user_box.currentText() == "--User--":
                    self.display_tasks()
                else:
                    user_id = self.user_box.currentData()
                    for i in reversed(range(self.check_list_table.rowCount())):
                        self.check_list_table.removeRow(i)
                    user_query = self.cursor.execute("SELECT id,name FROM users").fetchall()
                    entry_query = self.cursor.execute("SELECT id,note,task_id FROM entries").fetchall()
                    task_query = self.cursor.execute(
                        f"SELECT id,name,status,user_id FROM tasks WHERE user_id={user_id}") \
                        .fetchall()
                    self.fill_check_list_table(task_query, user_query, entry_query)
            else:
                if self.user_box.currentText() == "--User--":
                    status = radio_btn.text().lower()
                    for i in reversed(range(self.check_list_table.rowCount())):
                        self.check_list_table.removeRow(i)
                    user_query = self.cursor.execute("SELECT id,name FROM users").fetchall()
                    entry_query = self.cursor.execute("SELECT id,note,task_id FROM entries").fetchall()
                    task_query = self.cursor.execute(
                        f"SELECT id,name,status,user_id FROM tasks WHERE status='{status}'").fetchall()
                    self.fill_check_list_table(task_query, user_query, entry_query)
                else:
                    user_id = self.user_box.currentData()
                    status = radio_btn.text().lower()
                    for i in reversed(range(self.check_list_table.rowCount())):
                        self.check_list_table.removeRow(i)
                    user_query = self.cursor.execute("SELECT id,name FROM users").fetchall()
                    entry_query = self.cursor.execute("SELECT id,note,task_id FROM entries").fetchall()
                    task_query = self.cursor.execute(
                        f"SELECT id,name,status,user_id FROM tasks WHERE status='{status}' and user_id={user_id}").fetchall()
                    self.fill_check_list_table(task_query, user_query, entry_query)

    def filter_by_user(self):
        radio_buttons = (
            self.all_tasks, self.to_do_status, self.in_progress_status, self.done_status, self.closed_status)
        if self.user_box.currentText() == "--User--":
            for radio_btn in radio_buttons:
                if radio_btn.isChecked():
                    if radio_btn == self.all_tasks:
                        self.display_tasks()
                    else:
                        status = radio_btn.text().lower()
                        for i in reversed(range(self.check_list_table.rowCount())):
                            self.check_list_table.removeRow(i)
                        user_query = self.cursor.execute("SELECT id,name FROM users").fetchall()
                        entry_query = self.cursor.execute("SELECT id,note,task_id FROM entries").fetchall()
                        task_query = self.cursor.execute(
                            f"SELECT id,name,status,user_id FROM tasks WHERE status='{status}'").fetchall()
                        self.fill_check_list_table(task_query, user_query, entry_query)
        else:
            for radio_btn in radio_buttons:
                if radio_btn.isChecked():
                    if radio_btn == self.all_tasks:
                        user_id = self.user_box.currentData()
                        for i in reversed(range(self.check_list_table.rowCount())):
                            self.check_list_table.removeRow(i)
                        user_query = self.cursor.execute("SELECT id,name FROM users").fetchall()
                        entry_query = self.cursor.execute("SELECT id,note,task_id FROM entries").fetchall()
                        task_query = self.cursor.execute(f"SELECT id,name,status,user_id FROM tasks WHERE user_id={user_id}")\
                            .fetchall()
                        self.fill_check_list_table(task_query, user_query, entry_query)
                    else:
                        status = radio_btn.text().lower()
                        user_id = self.user_box.currentData()
                        for i in reversed(range(self.check_list_table.rowCount())):
                            self.check_list_table.removeRow(i)
                        user_query = self.cursor.execute("SELECT id,name FROM users").fetchall()
                        entry_query = self.cursor.execute("SELECT id,note,task_id FROM entries").fetchall()
                        task_query = self.cursor.execute(
                            f"SELECT id,name,status,user_id FROM tasks WHERE user_id={user_id} and status='{status}'") \
                            .fetchall()
                        self.fill_check_list_table(task_query, user_query, entry_query)

    def fill_check_list_table(self, tasks, users, entries):
        for row_data in tasks:
            user_name = ''
            for user in users:
                if user[0] == row_data[3]:
                    user_name = user[1]
                    break
            entries_list = []
            last_entry = ''
            for entry in entries:
                if entry[2] == row_data[0]:
                    entries_list.append(entry[1])
            if len(entries_list) > 0:
                last_entry = entries_list[-1]
            row_number = self.check_list_table.rowCount()
            self.check_list_table.insertRow(row_number)
            for column_number, data in enumerate(
                    (row_data[0], row_data[1], last_entry, user_name, row_data[2])
            ):
                self.check_list_table.setItem(row_number, column_number, QStandardItem(str(data)))
        self.check_list_table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def display_selected_day(self):
        for i in reversed(range(self.calendar_top_right_form_layout.count())):
            widget = self.calendar_top_right_form_layout.takeAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        self.day_events_list.clear()

        self.db_date = self.calendar.selectedDate().toString("dd.MM.yyyy")
        self.date_label = QLabel()
        today = self.calendar.selectedDate().toString()
        self.date_label.setText(today)
        self.add_event_btn = QPushButton("Add event")
        self.add_event_btn.setStyleSheet(style.btn_style())
        self.add_event_btn.clicked.connect(self.add_event_requested)

        query_user = "SELECT id,name FROM users"
        users = self.cursor.execute(query_user).fetchall()
        query_events = "SELECT * FROM events WHERE date=?"
        events = self.cursor.execute(query_events, (self.db_date,)).fetchall()
        user_name = ''
        for event in events:
            for user in users:
                if event[4] == user[0]:
                    user_name = user[1]
                    break
            self.day_events_list.addItem(QListWidgetItem(
                f"Event: {event[1]} --- User: {user_name} --- More details: {event[3]}\n"))

        # add widgets
        self.calendar_top_right_form_layout.addRow(QLabel("Date:"), self.date_label)
        self.calendar_top_right_form_layout.addRow("", self.add_event_btn)
        self.calendar_top_right_list_layout.addWidget(self.day_events_list)

    def filter_calendar_events(self):
        self.calendar_events_list.clear()
        if self.calendar_users_box.currentText() == '--Select--':
            event_text = self.calendar_events_box.currentText()
            if event_text != '--Select--':
                query_user = "SELECT id,name FROM users"
                users = self.cursor.execute(query_user).fetchall()
                query_events = "SELECT * FROM events WHERE name=?"
                events = self.cursor.execute(query_events, (event_text,)).fetchall()
                self.fill_calendar_events_list(users, events)
        else:
            user_id = self.calendar_users_box.currentData()
            if self.calendar_events_box.currentText() == '--Select--':
                query_user = "SELECT id,name FROM users"
                users = self.cursor.execute(query_user).fetchall()
                query_events = "SELECT * FROM events WHERE user_id=?"
                events = self.cursor.execute(query_events, (user_id,)).fetchall()
                self.fill_calendar_events_list(users, events)
            else:
                event_text = self.calendar_events_box.currentText()
                query_user = "SELECT id,name FROM users"
                users = self.cursor.execute(query_user).fetchall()
                query_events = "SELECT * FROM events WHERE user_id=? and name=?"
                events = self.cursor.execute(query_events, (user_id, event_text)).fetchall()
                self.fill_calendar_events_list(users, events)

    def fill_calendar_events_list(self, users, events):
        user_name = ''
        for event in events:
            for user in users:
                if event[4] == user[0]:
                    user_name = user[1]
                    break
            self.calendar_events_list.addItem(QListWidgetItem(f"Event: {event[1]} --- Date: {event[2]} "
                                                              f"--- User: {user_name}\nMore details: {event[3]}\n"))

    def display_selected_event_for_user(self):
        query_entries = "SELECT * FROM events WHERE user_id=?"
        self.user_entries = self.cursor.execute(query_entries, (self.logged_user_id,)).fetchall()
        self.selected_event_list.clear()
        if self.select_event_box.currentText() == 'holiday':
            for entry in self.user_entries:
                if entry[1] == 'holiday':
                    item = QListWidgetItem(f"Date: {entry[2]}\nNote: {entry[3]}")
                    item.value = entry[0]
                    self.selected_event_list.addItem(item)
        elif self.select_event_box.currentText() == 'work day':
            for entry in self.user_entries:
                if entry[1] == 'work day':
                    item = QListWidgetItem(f"Date: {entry[2]}\nNote: {entry[3]}")
                    item.value = entry[0]
                    self.selected_event_list.addItem(item)

    def update_selected_event(self):
        selected_event = self.selected_event_list.selectedItems()
        if len(selected_event) == 1:
            for event in selected_event:
                self.selected_event_id = event.value
                self.update_event_requested.emit()

    def delete_selected_event(self):
        mbox = QMessageBox.question(self, "Warning", "Are you sure to delete?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if mbox == QMessageBox.Yes:
            try:
                selected_events = self.selected_event_list.selectedItems()
                for event in selected_events:
                    query_event = "DELETE FROM events WHERE id=?"
                    self.cursor.execute(query_event, (event.value,))
                    self.connection.commit()
                    self.refresh_user_tab_view()
                    QMessageBox.information(self, "Information", "Event/Events has/have been deleted")
            except:
                QMessageBox.information(self, "Warning", "Event/Events has/have has not been deleted")

    def display_user_tasks(self):
        self.logged_user_tasks_list.clear()
        tasks_list = self.cursor.execute(f"SELECT * FROM tasks WHERE user_id={self.logged_user_id}").fetchall()
        for task in tasks_list:
            item = QListWidgetItem(f"{task[1]} -- Status: {task[2]}")
            item.value = task[0]
            self.logged_user_tasks_list.addItem(item)
        self.logged_user_tasks_list.setVerticalScrollBar(QScrollBar())
        self.logged_user_tasks_list.itemDoubleClicked.connect(self.display_clicked_task)

    def display_clicked_task(self):
        clicked_task = self.logged_user_tasks_list.selectedItems()
        for task in clicked_task:
            self.task_id = task.value
            self.display_task_requested.emit()

    def update_username(self):
        query_user = "SELECT name FROM users"
        users = self.cursor.execute(query_user).fetchall()
        new_user_name = self.new_user_name.text()

        if new_user_name in users:
            QMessageBox.information(self, "Warning", 'User name has to be unique.')
        else:
            if new_user_name:
                try:
                    query = "UPDATE users set name=? WHERE id=?"
                    self.cursor.execute(query, (new_user_name, self.logged_user_id))
                    self.connection.commit()
                    QMessageBox.information(self, "Success", "Username has been updated.")
                    self.logged_user_label.setText(new_user_name)
                except:
                    QMessageBox.information(self, "Warning", "Username has not been updated.")

    def update_password(self):
        password = self.new_password.text()
        cpassword = self.confirm_password.text()
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        if password == cpassword:
            try:
                query = "UPDATE users set password=? WHERE id=?"
                self.cursor.execute(query, (hashed, self.logged_user_id))
                self.connection.commit()
                QMessageBox.information(self, "Success", "Password has been updated.")
            except:
                QMessageBox.information(self, "Warning", "Password has not been updated.")

    def refresh_user_tab_view(self):
        total_holiday = self.cursor.execute(f"SELECT count (id) FROM events WHERE user_id={self.logged_user_id} "
                                            f"and name='holiday'").fetchall()[0][0]
        self.total_holiday_label.setText(str(total_holiday))
        total_workday = self.cursor.execute(f"SELECT count (id) FROM events WHERE user_id={self.logged_user_id} "
                                            f"and name='work day'").fetchall()[0][0]
        self.total_workday_label.setText(str(total_workday))
        self.selected_event_list.clear()
        self.select_event_box.setCurrentText('--Select--')

    def refresh_events_calendar_view(self):
        self.display_selected_day()
        self.refresh_user_tab_view()

    def refresh_view(self):
        self.display_tasks()
        self.display_user_tasks()
        self.all_tasks.setChecked(True)
        self.user_box.setCurrentText("--User--")
        self.refresh_user_tab_view()

        for i in reversed(range(self.check_list_right_fourth_layout.count())):
            widget = self.check_list_right_fourth_layout.takeAt(i).widget()
            if widget is not None:
                widget.deleteLater()


def main():
    app = MainApp(sys.argv)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
