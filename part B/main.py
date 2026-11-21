import sys
import sqlite3
from datetime import date

from PyQt6.QtCore import Qt, QDate, QPoint, QRectF
from PyQt6.QtGui import QColor, QBrush, QPainter, QPen, QFont
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QLineEdit,
    QTextEdit, QComboBox, QDateEdit, QCalendarWidget, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,
    QGridLayout, QScrollArea, QMessageBox, QHeaderView,
    QAbstractItemView, QStackedWidget, QProgressBar, QSizePolicy,
)

from database import (
    initialize_database, add_task, get_all_tasks, get_task_by_id,
    update_task, delete_task, set_task_completed, get_task_counts,
)


class PriorityChart(QWidget):
    """Draw a lightweight priority chart without extra packages."""

    COLORS = {"High": "#EF4444", "Medium": "#F59E0B", "Low": "#10B981"}

    def __init__(self):
        super().__init__()
        self.counts = {"High": 0, "Medium": 0, "Low": 0}
        self.setMinimumHeight(190)

    def set_counts(self, counts):
        self.counts = counts
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        font = QFont("Segoe UI", 10)
        painter.setFont(font)
        left, right = 75, 70
        width = max(50, self.width() - left - right)
        maximum = max(1, *self.counts.values())
        for index, name in enumerate(("High", "Medium", "Low")):
            y = 25 + index * 53
            painter.setPen(QColor("#475569"))
            painter.drawText(4, y + 18, name)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#E8EEF7"))
            painter.drawRoundedRect(QRectF(left, y, width, 23), 7, 7)
            amount = self.counts[name]
            if amount:
                painter.setBrush(QColor(self.COLORS[name]))
                painter.drawRoundedRect(
                    QRectF(left, y, width * amount / maximum, 23), 7, 7
                )
            painter.setPen(QColor("#334155"))
            painter.drawText(left + width + 12, y + 18, str(amount))
        painter.end()


class TaskFlowWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.editing_task_id = None
        self.all_tasks = []
        self.calendar_view_mode = "month"
        self.setWindowTitle("TaskFlow | Smart Task Manager | Pema Cheki | Roll 14")
        self.resize(1250, 820)
        self.setMinimumSize(860, 620)
        self.build_interface()
        self.apply_styles()
        self.load_tasks()

    def scroll_page(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        content.setObjectName("pageContent")
        scroll.setWidget(content)
        layout = QVBoxLayout(content)
        layout.setContentsMargins(27, 25, 27, 27)
        layout.setSpacing(18)
        return scroll, layout

    def make_button(self, text, object_name, height=42):
        button = QPushButton(text)
        button.setObjectName(object_name)
        button.setMinimumHeight(height)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        return button

    def create_card(self, title, color):
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumHeight(112)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        label = QLabel(title)
        label.setObjectName("cardTitle")
        value = QLabel("0")
        value.setObjectName("cardNumber")
        value.setStyleSheet(f"color: {color};")
        layout.addWidget(label)
        layout.addWidget(value)
        return card, value

    def build_interface(self):
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Persistent navigation sidebar.
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(17, 26, 17, 18)
        sidebar_layout.setSpacing(12)
        brand = QLabel("TaskFlow")
        brand.setObjectName("brand")
        sidebar_layout.addWidget(brand)
        tagline = QLabel("SMART TASK MANAGER")
        tagline.setObjectName("sidebarCaption")
        sidebar_layout.addWidget(tagline)
        sidebar_layout.addSpacing(26)
        self.dashboard_nav = self.make_button("  Dashboard", "navActive", 48)
        self.tasks_nav = self.make_button("  My Tasks", "navButton", 48)
        self.calendar_nav = self.make_button("  Calendar", "navButton", 48)
        self.completed_nav = self.make_button("  Completed Tasks", "navButton", 48)
        self.nav_buttons = (
            self.dashboard_nav, self.tasks_nav,
            self.calendar_nav, self.completed_nav,
        )
        for button in self.nav_buttons:
            sidebar_layout.addWidget(button)
        sidebar_layout.addStretch()
        author = QLabel("Pema Cheki  |  Roll 14")
        author.setObjectName("sidebarFoot")
        sidebar_layout.addWidget(author)
        root_layout.addWidget(sidebar)

        self.pages = QStackedWidget()
        root_layout.addWidget(self.pages, stretch=1)
        self.build_dashboard()
        self.build_tasks_page()
        self.build_calendar_page()
        self.build_completed_page()

        # Main menu.
        file_menu = self.menuBar().addMenu("File")
        refresh_action = file_menu.addAction("Refresh Tasks")
        exit_action = file_menu.addAction("Exit")
        help_menu = self.menuBar().addMenu("Help")
        about_action = help_menu.addAction("About TaskFlow")
        self.statusBar().showMessage("TaskFlow is ready.")

        # Navigation and task events.
        self.dashboard_nav.clicked.connect(lambda: self.switch_page(0))
        self.tasks_nav.clicked.connect(lambda: self.switch_page(1))
        self.calendar_nav.clicked.connect(lambda: self.switch_page(2))
        self.completed_nav.clicked.connect(lambda: self.switch_page(3))
        self.month_calendar.clicked.connect(self.show_selected_day_tasks)
        self.month_calendar.currentPageChanged.connect(self.on_calendar_month_changed)
        self.calendar_month_button.clicked.connect(self.show_month_tasks)
        self.calendar_add_button.clicked.connect(self.create_task_for_date)
        self.completed_table.itemSelectionChanged.connect(self.update_reopen_button)
        self.reopen_button.clicked.connect(self.reopen_completed_task)
        self.save_button.clicked.connect(self.save_task)
        self.cancel_button.clicked.connect(self.reset_form)
        self.edit_button.clicked.connect(self.start_editing)
        self.complete_button.clicked.connect(self.toggle_completion)
        self.delete_button.clicked.connect(self.remove_task)
        self.title_input.returnPressed.connect(self.save_task)
        self.calendar_button.clicked.connect(self.show_calendar)
        self.calendar_popup.clicked.connect(self.select_calendar_date)
        self.task_table.itemSelectionChanged.connect(self.update_action_buttons)
        self.task_table.cellDoubleClicked.connect(self.start_editing)
        self.search_input.textChanged.connect(self.apply_filters)
        self.priority_filter.currentIndexChanged.connect(self.apply_filters)
        self.status_filter.currentIndexChanged.connect(self.apply_filters)
        self.sort_filter.currentIndexChanged.connect(self.apply_filters)
        self.clear_filter_button.clicked.connect(self.clear_filters)
        refresh_action.triggered.connect(self.load_tasks)
        exit_action.triggered.connect(self.close)
        about_action.triggered.connect(self.show_about)
        self.update_action_buttons()
        self.switch_page(0)

    def build_dashboard(self):
        page, layout = self.scroll_page()
        self.pages.addWidget(page)
        heading = QLabel("Dashboard Overview")
        heading.setObjectName("pageHeading")
        layout.addWidget(heading)
        subtitle = QLabel("See your progress and keep track of upcoming tasks.")
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)

        cards = QGridLayout()
        cards.setSpacing(13)
        self.total_card, self.total_value = self.create_card("Total Tasks", "#2563EB")
        self.pending_card, self.pending_value = self.create_card("Pending", "#D97706")
        self.completed_card, self.completed_value = self.create_card("Completed", "#059669")
        self.overdue_card, self.overdue_value = self.create_card("Overdue", "#DC2626")
        for i, card in enumerate((self.total_card, self.pending_card,
                                  self.completed_card, self.overdue_card)):
            cards.addWidget(card, i // 2, i % 2)
        layout.addLayout(cards)

        progress_panel = QFrame()
        progress_panel.setObjectName("panel")
        progress_layout = QVBoxLayout(progress_panel)
        progress_layout.setContentsMargins(22, 22, 22, 22)
        progress_layout.setSpacing(12)
        progress_label = QLabel("Overall Completion Progress")
        progress_label.setObjectName("sectionHeading")
        self.progress_text = QLabel("0% completed")
        self.progress_text.setObjectName("subtitle")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(18)
        progress_layout.addWidget(progress_label)
        progress_layout.addWidget(self.progress_text)
        progress_layout.addWidget(self.progress_bar)
        layout.addWidget(progress_panel)

        chart_panel = QFrame()
        chart_panel.setObjectName("panel")
        chart_layout = QVBoxLayout(chart_panel)
        chart_layout.setContentsMargins(22, 20, 22, 20)
        title = QLabel("Tasks by Priority")
        title.setObjectName("sectionHeading")
        self.priority_chart = PriorityChart()
        chart_layout.addWidget(title)
        chart_layout.addWidget(self.priority_chart)
        layout.addWidget(chart_panel)

        upcoming_panel = QFrame()
        upcoming_panel.setObjectName("panel")
        upcoming_layout = QVBoxLayout(upcoming_panel)
        upcoming_layout.setContentsMargins(22, 20, 22, 20)
        upcoming_title = QLabel("Upcoming Tasks")
        upcoming_title.setObjectName("sectionHeading")
        self.upcoming_label = QLabel("No upcoming tasks yet.")
        self.upcoming_label.setWordWrap(True)
        self.upcoming_label.setObjectName("upcoming")
        upcoming_layout.addWidget(upcoming_title)
        upcoming_layout.addWidget(self.upcoming_label)
        layout.addWidget(upcoming_panel)

        view_tasks = self.make_button("Open My Tasks", "primaryButton", 46)
        view_tasks.clicked.connect(lambda: self.switch_page(1))
        layout.addWidget(view_tasks)
        layout.addStretch()

    def build_tasks_page(self):
        page, layout = self.scroll_page()
        self.pages.addWidget(page)
        heading = QLabel("My Tasks")
        heading.setObjectName("pageHeading")
        layout.addWidget(heading)
        subtitle = QLabel("Add, update, organize, and complete your tasks.")
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)

        form_panel = QFrame()
        form_panel.setObjectName("panel")
        form_layout = QVBoxLayout(form_panel)
        form_layout.setContentsMargins(22, 20, 22, 22)
        form_layout.setSpacing(16)
        self.form_heading = QLabel("Create a New Task")
        self.form_heading.setObjectName("sectionHeading")
        form_layout.addWidget(self.form_heading)
        grid = QGridLayout()
        grid.setHorizontalSpacing(17)
        grid.setVerticalSpacing(14)
        grid.setColumnMinimumWidth(0, 105)
        grid.setColumnStretch(1, 1)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("What do you need to get done?")
        self.title_input.setMaxLength(100)
        self.title_input.setMinimumHeight(42)
        grid.addWidget(QLabel("Task Title"), 0, 0)
        grid.addWidget(self.title_input, 0, 1)

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Add task details (optional)")
        self.description_input.setFixedHeight(85)
        grid.addWidget(QLabel("Description"), 1, 0, Qt.AlignmentFlag.AlignTop)
        grid.addWidget(self.description_input, 1, 1)

        self.priority_input = QComboBox()
        self.priority_input.addItems(["Low", "Medium", "High"])
        self.priority_input.setCurrentText("Medium")
        self.priority_input.setMinimumHeight(42)
        grid.addWidget(QLabel("Priority"), 2, 0)
        grid.addWidget(self.priority_input, 2, 1)

        self.due_date_input = QDateEdit()
        self.due_date_input.setCalendarPopup(True)
        self.due_date_input.setDisplayFormat("dd MMM yyyy")
        self.due_date_input.setDate(QDate.currentDate().addDays(1))
        self.due_date_input.setMinimumHeight(42)
        self.calendar_button = self.make_button("Choose Date", "secondaryButton", 42)
        self.calendar_popup = QCalendarWidget(self)
        self.calendar_popup.setWindowFlags(Qt.WindowType.Popup)
        self.calendar_popup.setGridVisible(True)
        self.calendar_popup.hide()
        date_row = QHBoxLayout()
        date_row.setSpacing(10)
        date_row.addWidget(self.due_date_input, stretch=1)
        date_row.addWidget(self.calendar_button)
        grid.addWidget(QLabel("Due Date"), 3, 0)
        grid.addLayout(date_row, 3, 1)
        form_layout.addLayout(grid)

        form_buttons = QHBoxLayout()
        form_buttons.addStretch()
        self.cancel_button = self.make_button("Cancel Editing", "secondaryButton", 44)
        self.cancel_button.hide()
        self.save_button = self.make_button("+ Add Task", "primaryButton", 44)
        form_buttons.addWidget(self.cancel_button)
        form_buttons.addWidget(self.save_button)
        form_layout.addLayout(form_buttons)
        layout.addWidget(form_panel)

        table_panel = QFrame()
        table_panel.setObjectName("panel")
        table_layout = QVBoxLayout(table_panel)
        table_layout.setContentsMargins(20, 20, 20, 20)
        table_layout.setSpacing(13)
        table_heading = QLabel("Your Tasks")
        table_heading.setObjectName("sectionHeading")
        table_layout.addWidget(table_heading)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by task title or description...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setMinimumHeight(42)
        table_layout.addWidget(self.search_input)
        filters = QHBoxLayout()
        filters.setSpacing(8)
        self.priority_filter = QComboBox()
        self.priority_filter.addItems(["All Priorities", "High", "Medium", "Low"])
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All Statuses", "Pending", "Completed", "Overdue"])
        self.sort_filter = QComboBox()
        self.sort_filter.addItems([
            "Due Date (Earliest)", "Due Date (Latest)",
            "Priority (Highest)", "Newest First", "Title (A-Z)"
        ])
        self.clear_filter_button = self.make_button("Clear Filters", "secondaryButton", 40)
        for control in (self.priority_filter, self.status_filter, self.sort_filter):
            control.setMinimumHeight(40)
            filters.addWidget(control, 1)
        filters.addWidget(self.clear_filter_button)
        table_layout.addLayout(filters)
        self.results_label = QLabel("Showing 0 tasks")
        self.results_label.setObjectName("subtitle")
        table_layout.addWidget(self.results_label)

        self.task_table = QTableWidget(0, 5)
        self.task_table.setHorizontalHeaderLabels([
            "ID", "Task", "Priority", "Due Date", "Status"
        ])
        self.task_table.setMinimumHeight(270)
        self.task_table.setAlternatingRowColors(True)
        self.task_table.setShowGrid(False)
        self.task_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.task_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.task_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.task_table.verticalHeader().setVisible(False)
        self.task_table.verticalHeader().setDefaultSectionSize(44)
        header = self.task_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for column in (2, 3, 4):
            header.setSectionResizeMode(column, QHeaderView.ResizeMode.Fixed)
        self.task_table.setColumnWidth(0, 55)
        self.task_table.setColumnWidth(2, 95)
        self.task_table.setColumnWidth(3, 115)
        self.task_table.setColumnWidth(4, 100)
        table_layout.addWidget(self.task_table)

        actions = QHBoxLayout()
        actions.setSpacing(10)
        self.edit_button = self.make_button("Edit Task", "secondaryButton")
        self.complete_button = self.make_button("Mark Completed", "successButton")
        self.delete_button = self.make_button("Delete Task", "dangerButton")
        actions.addWidget(self.edit_button)
        actions.addWidget(self.complete_button)
        actions.addWidget(self.delete_button)
        actions.addStretch()
        table_layout.addLayout(actions)
        layout.addWidget(table_panel)
        layout.addStretch()

    def build_calendar_page(self):
        """Show the entire selected month or one clicked day."""
        page, layout = self.scroll_page()
        self.pages.addWidget(page)
        heading = QLabel("Task Calendar")
        heading.setObjectName("pageHeading")
        layout.addWidget(heading)
        subtitle = QLabel(
            "Browse all tasks for a month, or click a date to focus on that day."
        )
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)

        calendar_panel = QFrame()
        calendar_panel.setObjectName("panel")
        panel_layout = QVBoxLayout(calendar_panel)
        panel_layout.setContentsMargins(22, 20, 22, 22)
        panel_layout.setSpacing(14)

        self.month_calendar = QCalendarWidget()
        self.month_calendar.setGridVisible(True)
        self.month_calendar.setMinimumHeight(315)
        self.month_calendar.setSelectedDate(QDate.currentDate())
        panel_layout.addWidget(self.month_calendar)
        layout.addWidget(calendar_panel)

        list_panel = QFrame()
        list_panel.setObjectName("panel")
        list_layout = QVBoxLayout(list_panel)
        list_layout.setContentsMargins(22, 20, 22, 22)
        list_layout.setSpacing(12)

        view_header = QHBoxLayout()
        self.calendar_day_heading = QLabel("Tasks This Month")
        self.calendar_day_heading.setObjectName("sectionHeading")
        view_header.addWidget(self.calendar_day_heading, stretch=1)
        self.calendar_month_button = self.make_button(
            "Show All Month Tasks", "secondaryButton"
        )
        view_header.addWidget(self.calendar_month_button)
        list_layout.addLayout(view_header)

        self.calendar_count_label = QLabel("0 tasks")
        self.calendar_count_label.setObjectName("subtitle")
        list_layout.addWidget(self.calendar_count_label)

        self.calendar_task_table = QTableWidget(0, 4)
        self.calendar_task_table.setHorizontalHeaderLabels([
            "Due Date", "Task", "Priority", "Status"
        ])
        self.calendar_task_table.setMinimumHeight(230)
        self.calendar_task_table.setAlternatingRowColors(True)
        self.calendar_task_table.setShowGrid(False)
        self.calendar_task_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.calendar_task_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.calendar_task_table.verticalHeader().setVisible(False)
        self.calendar_task_table.verticalHeader().setDefaultSectionSize(38)
        calendar_header = self.calendar_task_table.horizontalHeader()
        calendar_header.setSectionResizeMode(
            0, QHeaderView.ResizeMode.Fixed
        )
        calendar_header.setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        calendar_header.setSectionResizeMode(
            2, QHeaderView.ResizeMode.Fixed
        )
        calendar_header.setSectionResizeMode(
            3, QHeaderView.ResizeMode.Fixed
        )
        self.calendar_task_table.setColumnWidth(0, 125)
        self.calendar_task_table.setColumnWidth(2, 105)
        self.calendar_task_table.setColumnWidth(3, 115)
        list_layout.addWidget(self.calendar_task_table)

        self.calendar_add_button = self.make_button(
            "+ Create Task for Selected Date", "primaryButton"
        )
        list_layout.addWidget(self.calendar_add_button)
        layout.addWidget(list_panel)
        layout.addStretch()

    def build_completed_page(self):
        """List completed tasks and allow reopening them."""
        page, layout = self.scroll_page()
        self.pages.addWidget(page)
        heading = QLabel("Completed Tasks")
        heading.setObjectName("pageHeading")
        layout.addWidget(heading)
        subtitle = QLabel("Review finished tasks or move one back to pending.")
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)

        panel = QFrame()
        panel.setObjectName("panel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(22, 20, 22, 22)
        panel_layout.setSpacing(12)
        self.completed_count_label = QLabel("0 completed tasks")
        self.completed_count_label.setObjectName("sectionHeading")
        panel_layout.addWidget(self.completed_count_label)
        self.completed_table = QTableWidget(0, 4)
        self.completed_table.setHorizontalHeaderLabels(
            ["ID", "Task", "Priority", "Due Date"]
        )
        self.completed_table.setMinimumHeight(300)
        self.completed_table.setAlternatingRowColors(True)
        self.completed_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.completed_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.completed_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.completed_table.verticalHeader().setVisible(False)
        header = self.completed_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.completed_table.setColumnWidth(0, 55)
        self.completed_table.setColumnWidth(2, 110)
        self.completed_table.setColumnWidth(3, 135)
        panel_layout.addWidget(self.completed_table)
        self.reopen_button = self.make_button("Mark Selected Task Pending", "successButton")
        self.reopen_button.setEnabled(False)
        panel_layout.addWidget(self.reopen_button)
        layout.addWidget(panel)
        layout.addStretch()

    def switch_page(self, index):
        self.pages.setCurrentIndex(index)
        for i, button in enumerate(self.nav_buttons):
            button.setObjectName("navActive" if i == index else "navButton")
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()
        if index == 2:
            self.show_month_tasks()
        elif index == 3:
            self.update_completed_page()

    def highlight_calendar_dates(self, *args):
        """Highlight dates that have at least one saved task."""
        from PyQt6.QtGui import QTextCharFormat

        year = self.month_calendar.yearShown()
        month = self.month_calendar.monthShown()
        first = QDate(year, month, 1)
        day = first
        while day.isValid() and day.month() == month:
            self.month_calendar.setDateTextFormat(day, QTextCharFormat())
            day = day.addDays(1)

        due_dates = {
            task["due_date"] for task in self.all_tasks
            if task["due_date"].startswith(f"{year:04d}-{month:02d}-")
        }
        for due_date in due_dates:
            day = QDate.fromString(due_date, "yyyy-MM-dd")
            fmt = QTextCharFormat()
            fmt.setFontWeight(QFont.Weight.Bold)
            fmt.setForeground(QColor("#1D4ED8"))
            self.month_calendar.setDateTextFormat(day, fmt)

    def on_calendar_month_changed(self, year, month):
        """Changing the displayed month shows all of its tasks."""
        self.highlight_calendar_dates()
        self.show_month_tasks()

    def show_month_tasks(self):
        """Display every saved task due in the displayed calendar month."""
        self.calendar_view_mode = "month"
        year = self.month_calendar.yearShown()
        month = self.month_calendar.monthShown()
        prefix = f"{year:04d}-{month:02d}-"
        matching = [
            task for task in self.all_tasks
            if task["due_date"].startswith(prefix)
        ]
        month_name = QDate(year, month, 1).toString("MMMM yyyy")
        self.calendar_day_heading.setText(f"Tasks for {month_name}")
        self.calendar_month_button.setEnabled(False)
        self.populate_calendar_task_table(matching)

    def show_selected_day_tasks(self, selected_day):
        """Clicking a calendar date displays only that day's tasks."""
        self.calendar_view_mode = "day"
        iso_date = selected_day.toString("yyyy-MM-dd")
        matching = [
            task for task in self.all_tasks
            if task["due_date"] == iso_date
        ]
        self.calendar_day_heading.setText(
            "Tasks due " + selected_day.toString("dd MMMM yyyy")
        )
        self.calendar_month_button.setEnabled(True)
        self.populate_calendar_task_table(matching)

    def populate_calendar_task_table(self, tasks):
        """Populate the monthly or daily task table from saved data."""
        today = date.today().isoformat()
        ranks = {"High": 0, "Medium": 1, "Low": 2}
        ordered = sorted(
            tasks,
            key=lambda task: (
                task["due_date"],
                bool(task["completed"]),
                ranks[task["priority"]],
                task["id"],
            ),
        )
        self.calendar_task_table.setRowCount(len(ordered))
        for row, task in enumerate(ordered):
            completed = bool(task["completed"])
            overdue = not completed and task["due_date"] < today
            status = (
                "Completed" if completed
                else "Overdue" if overdue
                else "Pending"
            )
            values = (
                task["due_date"], task["title"],
                task["priority"], status,
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column != 1:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if column == 2:
                    item.setForeground(QColor({
                        "High": "#DC2626",
                        "Medium": "#B45309",
                        "Low": "#15803D",
                    }[task["priority"]]))
                if column == 3:
                    item.setForeground(QColor({
                        "Completed": "#15803D",
                        "Overdue": "#DC2626",
                        "Pending": "#B45309",
                    }[status]))
                if completed and column == 1:
                    font = item.font()
                    font.setStrikeOut(True)
                    item.setFont(font)
                if overdue:
                    item.setBackground(QBrush(QColor("#FFF1F2")))
                self.calendar_task_table.setItem(row, column, item)

        number = len(ordered)
        unit = "task" if number == 1 else "tasks"
        self.calendar_count_label.setText(f"{number} {unit} found")
        if not ordered:
            self.calendar_task_table.setRowCount(0)

    def update_calendar_tasks(self):
        """Refresh the current month/day view after a database change."""
        if self.calendar_view_mode == "day":
            self.show_selected_day_tasks(self.month_calendar.selectedDate())
        else:
            self.show_month_tasks()

    def create_task_for_date(self):
        self.reset_form()
        self.due_date_input.setDate(self.month_calendar.selectedDate())
        self.switch_page(1)
        self.title_input.setFocus()

    def update_completed_page(self):
        done = sorted(
            (t for t in self.all_tasks if t["completed"]),
            key=lambda t: (t["due_date"], t["id"]), reverse=True
        )
        self.completed_count_label.setText(f"{len(done)} completed tasks")
        self.completed_table.blockSignals(True)
        self.completed_table.setRowCount(len(done))
        self.completed_table.clearSelection()
        for row, task in enumerate(done):
            for column, value in enumerate((
                str(task["id"]), task["title"],
                task["priority"], task["due_date"]
            )):
                item = QTableWidgetItem(value)
                if column != 1:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.completed_table.setItem(row, column, item)
        self.completed_table.setCurrentCell(-1, -1)
        self.completed_table.blockSignals(False)
        self.update_reopen_button()

    def update_reopen_button(self):
        self.reopen_button.setEnabled(
            self.completed_table.selectionModel().hasSelection()
        )

    def reopen_completed_task(self):
        row = self.completed_table.currentRow()
        if row < 0 or not self.completed_table.selectionModel().hasSelection():
            return
        item = self.completed_table.item(row, 0)
        if item is None:
            return
        task_id = int(item.text())
        try:
            changed = set_task_completed(task_id, 0)
        except (sqlite3.Error, ValueError) as error:
            QMessageBox.critical(self, "Update Error", str(error))
            return
        if not changed:
            QMessageBox.warning(self, "Task Not Found", "This task no longer exists.")
        self.load_tasks()
        self.statusBar().showMessage(
            "Task moved back to pending." if changed else "Task list refreshed.", 5000
        )

    def show_calendar(self):
        self.calendar_popup.setSelectedDate(self.due_date_input.date())
        position = self.calendar_button.mapToGlobal(
            QPoint(0, self.calendar_button.height())
        )
        self.calendar_popup.move(position)
        self.calendar_popup.show()
        self.calendar_popup.raise_()

    def select_calendar_date(self, selected_date):
        self.due_date_input.setDate(selected_date)
        self.calendar_popup.hide()
        self.statusBar().showMessage(
            f"Due date selected: {selected_date.toString('dd MMM yyyy')}", 4000
        )

    def selected_task_id(self):
        row = self.task_table.currentRow()
        if row < 0 or not self.task_table.selectionModel().hasSelection():
            return None
        item = self.task_table.item(row, 0)
        return int(item.text()) if item is not None else None

    def update_action_buttons(self):
        task_id = self.selected_task_id()
        enabled = task_id is not None
        for button in (self.edit_button, self.complete_button, self.delete_button):
            button.setEnabled(enabled)
        status_item = self.task_table.item(self.task_table.currentRow(), 4) if enabled else None
        self.complete_button.setText(
            "Mark Pending" if status_item and status_item.text() == "Completed"
            else "Mark Completed"
        )

    def reset_form(self):
        self.editing_task_id = None
        self.title_input.clear()
        self.description_input.clear()
        self.priority_input.setCurrentText("Medium")
        self.due_date_input.setDate(QDate.currentDate().addDays(1))
        self.form_heading.setText("Create a New Task")
        self.save_button.setText("+ Add Task")
        self.cancel_button.hide()

    def save_task(self):
        title = self.title_input.text().strip()
        description = self.description_input.toPlainText().strip()
        priority = self.priority_input.currentText()
        due_date = self.due_date_input.date().toString("yyyy-MM-dd")
        if not title:
            QMessageBox.warning(self, "Missing Title", "Please enter a task title.")
            self.title_input.setFocus()
            return
        try:
            if self.editing_task_id is None:
                add_task(title, description, priority, due_date)
                message = "Task added successfully."
            else:
                updated = update_task(
                    self.editing_task_id, title, description, priority, due_date
                )
                if not updated:
                    QMessageBox.warning(self, "Task Not Found", "This task no longer exists.")
                    self.reset_form()
                    self.load_tasks()
                    return
                message = "Task updated successfully."
        except (ValueError, sqlite3.Error) as error:
            QMessageBox.warning(self, "Unable to Save Task", str(error))
            return
        self.reset_form()
        self.load_tasks()
        self.statusBar().showMessage(message, 5000)

    def start_editing(self, *args):
        task_id = self.selected_task_id()
        if task_id is None:
            return
        try:
            task = get_task_by_id(task_id)
        except sqlite3.Error as error:
            QMessageBox.critical(self, "Database Error", str(error))
            return
        if task is None:
            QMessageBox.warning(self, "Task Not Found", "This task no longer exists.")
            self.load_tasks()
            return
        self.editing_task_id = task_id
        self.title_input.setText(task["title"])
        self.description_input.setPlainText(task["description"] or "")
        self.priority_input.setCurrentText(task["priority"])
        task_date = QDate.fromString(task["due_date"], "yyyy-MM-dd")
        if task_date.isValid():
            self.due_date_input.setDate(task_date)
        self.form_heading.setText(f"Edit Task #{task_id}")
        self.save_button.setText("Save Changes")
        self.cancel_button.show()
        self.title_input.setFocus()
        self.statusBar().showMessage("Edit the task and save your changes.")

    def toggle_completion(self):
        task_id = self.selected_task_id()
        if task_id is None:
            return
        try:
            task = get_task_by_id(task_id)
            if task is None:
                QMessageBox.warning(self, "Task Not Found", "This task no longer exists.")
                self.load_tasks()
                return
            new_status = 0 if task["completed"] else 1
            if not set_task_completed(task_id, new_status):
                raise ValueError("Could not update this task.")
        except (sqlite3.Error, ValueError) as error:
            QMessageBox.critical(self, "Update Error", str(error))
            return
        self.load_tasks()
        self.statusBar().showMessage(
            "Task marked completed." if new_status else "Task marked pending.", 5000
        )

    def remove_task(self):
        task_id = self.selected_task_id()
        if task_id is None:
            return
        try:
            task = get_task_by_id(task_id)
        except sqlite3.Error as error:
            QMessageBox.critical(self, "Database Error", str(error))
            return
        if task is None:
            self.load_tasks()
            return
        answer = QMessageBox.question(
            self, "Confirm Deletion",
            f"Delete '{task['title']}' permanently?\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            removed = delete_task(task_id)
        except sqlite3.Error as error:
            QMessageBox.critical(self, "Database Error", str(error))
            return
        if self.editing_task_id == task_id:
            self.reset_form()
        self.load_tasks()
        self.statusBar().showMessage(
            "Task deleted." if removed else "Task already removed.", 5000
        )

    def load_tasks(self):
        try:
            self.all_tasks = get_all_tasks()
            counts = get_task_counts()
        except sqlite3.Error as error:
            QMessageBox.critical(self, "Database Error", str(error))
            return
        today = date.today().isoformat()
        overdue = sum(
            1 for task in self.all_tasks
            if not task["completed"] and task["due_date"] < today
        )
        self.total_value.setText(str(counts["total"]))
        self.pending_value.setText(str(counts["pending"]))
        self.completed_value.setText(str(counts["completed"]))
        self.overdue_value.setText(str(overdue))
        completion = round(100 * counts["completed"] / counts["total"]) if counts["total"] else 0
        self.progress_bar.setValue(completion)
        self.progress_text.setText(f"{completion}% completed ({counts['completed']} of {counts['total']} tasks)")
        priority_counts = {
            name: sum(1 for t in self.all_tasks if t["priority"] == name)
            for name in ("High", "Medium", "Low")
        }
        self.priority_chart.set_counts(priority_counts)
        upcoming = sorted(
            (t for t in self.all_tasks if not t["completed"] and t["due_date"] >= today),
            key=lambda t: (t["due_date"], t["id"]),
        )[:5]
        if upcoming:
            self.upcoming_label.setText("\n".join(
                f"• {t['title']}  —  {t['due_date']}  ({t['priority']})"
                for t in upcoming
            ))
        else:
            self.upcoming_label.setText("No upcoming tasks yet.")
        self.apply_filters()
        self.highlight_calendar_dates()
        self.update_calendar_tasks()
        self.update_completed_page()

    def apply_filters(self, *args):
        query = self.search_input.text().strip().casefold()
        priority = self.priority_filter.currentText()
        status = self.status_filter.currentText()
        order = self.sort_filter.currentText()
        today = date.today().isoformat()
        filtered = []
        for task in self.all_tasks:
            combined = (task["title"] + " " + (task["description"] or "")).casefold()
            if query not in combined:
                continue
            if priority != "All Priorities" and task["priority"] != priority:
                continue
            finished = bool(task["completed"])
            late = not finished and task["due_date"] < today
            if status == "Completed" and not finished:
                continue
            if status == "Pending" and finished:
                continue
            if status == "Overdue" and not late:
                continue
            filtered.append(task)
        ranks = {"High": 0, "Medium": 1, "Low": 2}
        if order == "Due Date (Earliest)":
            filtered.sort(key=lambda t: (t["due_date"], t["id"]))
        elif order == "Due Date (Latest)":
            filtered.sort(key=lambda t: (t["due_date"], t["id"]), reverse=True)
        elif order == "Priority (Highest)":
            filtered.sort(key=lambda t: (ranks[t["priority"]], t["due_date"], t["id"]))
        elif order == "Newest First":
            filtered.sort(key=lambda t: t["id"], reverse=True)
        elif order == "Title (A-Z)":
            filtered.sort(key=lambda t: (t["title"].casefold(), t["id"]))
        self.populate_table(filtered)
        self.results_label.setText(f"Showing {len(filtered)} of {len(self.all_tasks)} tasks")

    def populate_table(self, tasks):
        today = date.today().isoformat()
        self.task_table.blockSignals(True)
        self.task_table.setRowCount(len(tasks))
        self.task_table.clearSelection()
        for row, task in enumerate(tasks):
            finished = bool(task["completed"])
            late = not finished and task["due_date"] < today
            status = "Completed" if finished else "Overdue" if late else "Pending"
            values = [str(task["id"]), task["title"], task["priority"], task["due_date"], status]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                if col != 1:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if col == 2:
                    item.setForeground(QColor({
                        "High": "#DC2626", "Medium": "#B45309", "Low": "#15803D"
                    }[task["priority"]]))
                if col == 4:
                    item.setForeground(QColor({
                        "Completed": "#15803D", "Pending": "#B45309", "Overdue": "#DC2626"
                    }[status]))
                if col == 1 and finished:
                    font = item.font()
                    font.setStrikeOut(True)
                    item.setFont(font)
                if late:
                    item.setBackground(QBrush(QColor("#FFF1F2")))
                self.task_table.setItem(row, col, item)
        self.task_table.setCurrentCell(-1, -1)
        self.task_table.blockSignals(False)
        self.update_action_buttons()

    def clear_filters(self):
        self.search_input.clear()
        self.priority_filter.setCurrentIndex(0)
        self.status_filter.setCurrentIndex(0)
        self.sort_filter.setCurrentIndex(0)
        self.apply_filters()
        self.statusBar().showMessage("Filters cleared.", 4000)

    def show_about(self):
        QMessageBox.information(
            self, "About TaskFlow",
            "TaskFlow – Smart Task Manager\n\n"
            "Developed by: Pema Cheki | Roll 14\n"
            "Unit V – Exploring GUI Frameworks\n\n"
            "Built with Python, PyQt6 and SQLite.\n"
            "Features: dashboard, task calendar, completed-task history, "
            "progress chart, task management, search and deadline tracking."
        )

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow, QWidget#root, QWidget#pageContent, QScrollArea {
                background: #F4F7FC;
            }
            QScrollArea { border: none; }
            QLabel { font-family: 'Segoe UI'; font-size: 13px; color: #27344B; }
            QFrame#sidebar { background: #13213B; }
            QLabel#brand { color: white; font-size: 27px; font-weight: bold; }
            QLabel#sidebarCaption { color: #AFC0E1; font-size: 10px; font-weight: bold; }
            QLabel#sidebarFoot { color: #B5C2DC; font-size: 11px; }
            QPushButton#navButton, QPushButton#navActive {
                text-align: left; border: none; border-radius: 8px;
                font-size: 14px; font-weight: bold; padding: 12px;
            }
            QPushButton#navButton { color: #D0DAED; background: transparent; }
            QPushButton#navButton:hover { background: #243A62; }
            QPushButton#navActive { color: white; background: #2563EB; }
            QLabel#pageHeading { color: #172554; font-size: 28px; font-weight: bold; }
            QLabel#subtitle { color: #64748B; font-size: 13px; }
            QLabel#sectionHeading { color: #172554; font-size: 18px; font-weight: bold; }
            QLabel#upcoming { line-height: 1.5; color: #334155; }
            QFrame#panel, QFrame#card {
                background: #FFFFFF; border: 1px solid #E0E7F1; border-radius: 12px;
            }
            QLabel#cardTitle { color: #64748B; font-size: 13px; }
            QLabel#cardNumber { font-size: 28px; font-weight: bold; }
            QLineEdit, QTextEdit, QComboBox, QDateEdit {
                background: white; color: #243047; border: 1px solid #CBD5E1;
                border-radius: 7px; padding: 6px 10px; font-size: 13px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {
                border: 2px solid #2563EB;
            }
            QComboBox::drop-down, QDateEdit::drop-down { width: 26px; border: none; }
            QPushButton#primaryButton, QPushButton#secondaryButton,
            QPushButton#successButton, QPushButton#dangerButton {
                border-radius: 7px; padding: 9px 14px; font-size: 13px; font-weight: bold;
            }
            QPushButton#primaryButton { color: white; background: #2563EB; border: none; }
            QPushButton#primaryButton:hover { background: #1D4ED8; }
            QPushButton#secondaryButton { color: #1D4ED8; background: #E8EFFD; border: 1px solid #BFDBFE; }
            QPushButton#secondaryButton:hover { background: #DBEAFE; }
            QPushButton#successButton { color: #166534; background: #DCFCE7; border: none; }
            QPushButton#dangerButton { color: #B91C1C; background: #FEE2E2; border: none; }
            QPushButton:disabled { color: #94A3B8; background: #F1F5F9; border: 1px solid #E2E8F0; }
            QProgressBar { background: #E8EEF7; border: none; border-radius: 9px; }
            QProgressBar::chunk { background: #2563EB; border-radius: 9px; }
            QCalendarWidget { background: white; color: #243047; }
            QCalendarWidget QToolButton { color: #1E3A8A; background: #E8EFFD; }
            QCalendarWidget QAbstractItemView {
                background: white; color: #243047;
                selection-background-color: #2563EB;
            }
            QTableWidget {
                background: white; alternate-background-color: #F8FAFC;
                color: #243047; border: 1px solid #E2E8F0;
                border-radius: 8px; selection-background-color: #DBEAFE;
                selection-color: #1E3A8A;
            }
            QHeaderView::section {
                background: #E8EFFD; color: #1E3A8A;
                font-weight: bold; padding: 10px; border: none;
            }
            QMenuBar, QStatusBar { background: #FFFFFF; color: #243047; }
            QMenuBar::item:selected { background: #DBEAFE; }
        """)


def main():
    app = QApplication(sys.argv)
    try:
        initialize_database()
    except sqlite3.Error as error:
        QMessageBox.critical(None, "Startup Error", f"Unable to initialize database:\n{error}")
        return 1
    window = TaskFlowWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
