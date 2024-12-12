import random
import sys

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QAction, QColor, QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QDockWidget,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from logic.scheduler import Scheduler
from visuals.gantt_chart import GanttChart


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ShadFlow - CPU Scheduler Visualizer")
        self.setGeometry(100, 100, 1400, 800)
        self.setWindowIcon(QIcon("os project icon.ico"))
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)

        self.left_dock = QDockWidget("Process Input", self)
        self.left_dock.setFeatures(
            QDockWidget.DockWidgetMovable
            | QDockWidget.DockWidgetFloatable
            | QDockWidget.DockWidgetClosable
        )
        self.left_dock.setAllowedAreas(
            Qt.LeftDockWidgetArea
            | Qt.RightDockWidgetArea
            | Qt.TopDockWidgetArea
            | Qt.BottomDockWidgetArea
        )
        self.left_dock.visibilityChanged.connect(self.update_view_menu)

        dock_content = QWidget()
        dock_layout = QVBoxLayout(dock_content)
        dock_layout.setContentsMargins(10, 10, 10, 10)
        dock_layout.setSpacing(15)

        title_label = QLabel("ShadFlow CPU Scheduler")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
        title_label.setAlignment(Qt.AlignCenter)
        dock_layout.addWidget(title_label, alignment=Qt.AlignCenter)

        github_label = QLabel(
            '<a href="https://github.com/a-elhaag/ShadFlow-CPU-Scheduler">View on GitHub</a>'
        )
        github_label.setOpenExternalLinks(True)
        github_label.setStyleSheet("font-size: 12px; color: #1E90FF;")
        github_label.setAlignment(Qt.AlignCenter)
        dock_layout.addWidget(github_label, alignment=Qt.AlignCenter)

        alg_label = QLabel("Select Algorithm:")
        alg_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #FFFFFF;")
        dock_layout.addWidget(alg_label)

        self.algorithm_selector = QComboBox()
        self.algorithm_selector.addItems(
            ["FCFS", "SJF", "SRTF", "Priority", "Priority (Preemptive)", "Round Robin"]
        )
        self.algorithm_selector.setStyleSheet("font-size: 13px;")
        self.algorithm_selector.currentTextChanged.connect(self.on_algorithm_changed)
        dock_layout.addWidget(self.algorithm_selector)

        table_label = QLabel("Process Details:")
        table_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #FFFFFF;")
        dock_layout.addWidget(table_label)

        self.process_table = QTableWidget(0, 5)
        self.process_table.setHorizontalHeaderLabels(
            ["Process", "Arrival Time", "Burst Time", "Priority", "Deadline"]
        )
        self.process_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.process_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.process_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.process_table.setEditTriggers(
            QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked
        )
        dock_layout.addWidget(self.process_table)

        self.quantum_input = QSpinBox()
        self.quantum_input.setRange(1, 100)
        self.quantum_input.setValue(2)
        self.quantum_input.setPrefix("Quantum: ")
        self.quantum_input.setStyleSheet("font-size: 13px; color: #FFFFFF;")
        self.quantum_input.setVisible(False)
        dock_layout.addWidget(self.quantum_input)

        button_style = """
            QPushButton {
                background-color: #4CAF50; 
                color: white; 
                border: none; 
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """

        buttons_layout = QHBoxLayout()
        add_process_button = QPushButton("Add Process")
        add_process_button.setStyleSheet(button_style)
        add_process_button.clicked.connect(self.add_process)
        buttons_layout.addWidget(add_process_button)

        delete_process_button = QPushButton("Delete Selected")
        delete_process_button.setStyleSheet(button_style)
        delete_process_button.clicked.connect(self.delete_selected_process)
        buttons_layout.addWidget(delete_process_button)
        dock_layout.addLayout(buttons_layout)

        extra_actions_layout = QHBoxLayout()
        fill_sample_button = QPushButton("Random Sample Data")
        fill_sample_button.setStyleSheet(button_style)
        fill_sample_button.clicked.connect(self.fill_random_sample_data)
        extra_actions_layout.addWidget(fill_sample_button)

        clear_button = QPushButton("Clear")
        clear_button.setStyleSheet(button_style)
        clear_button.clicked.connect(self.clear_table)
        extra_actions_layout.addWidget(clear_button)
        dock_layout.addLayout(extra_actions_layout)

        generate_button = QPushButton("Generate Schedule")
        generate_button.setStyleSheet(
            button_style + "font-size: 14px; padding: 8px 15px;"
        )
        generate_button.clicked.connect(self.generate_schedule)
        dock_layout.addWidget(generate_button, alignment=Qt.AlignCenter)

        spacer_frame = QFrame()
        spacer_frame.setFrameShape(QFrame.HLine)
        spacer_frame.setFrameShadow(QFrame.Sunken)
        spacer_frame.setStyleSheet("color: #FFFFFF;")
        dock_layout.addWidget(spacer_frame)

        dock_content.setLayout(dock_layout)
        self.left_dock.setWidget(dock_content)
        self.left_dock.setMinimumWidth(400)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.left_dock)

        # Right Side (Central Widget)
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(15)

        output_label = QLabel("Scheduled Output:")
        output_label.setStyleSheet(
            "font-weight: bold; font-size: 14px; color: #FFFFFF;"
        )
        right_layout.addWidget(output_label)

        self.output_table = QTableWidget(0, 3)
        self.output_table.setHorizontalHeaderLabels(
            ["Process", "Start Time", "Finish Time"]
        )
        self.output_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        right_layout.addWidget(self.output_table)

        self.metrics_label = QLabel("")
        self.metrics_label.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #FFFFFF;"
        )
        right_layout.addWidget(self.metrics_label)

        self.chart = GanttChart()
        right_layout.addWidget(self.chart)

        right_container = QWidget()
        right_container.setLayout(right_layout)
        main_layout.addWidget(right_container)

        # Create a unified toolbar with menus and actions
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setAllowedAreas(Qt.TopToolBarArea)
        toolbar.setStyleSheet(
            """
            QToolBar {
                background-color: #4CAF50;
                border: none;
            }
            QToolButton {
                color: #FFFFFF;
                font-weight: bold;
                padding: 6px;
            }
            QToolButton:hover {
                background-color: #45A049;
            }
            """
        )

        # Create the "Help" menu as a QMenu
        help_menu = QMenu("Help", self)
        description_action = QAction("Algorithm Descriptions", self)
        description_action.triggered.connect(self.show_descriptions)
        help_menu.addAction(description_action)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # Create a toolbutton for Help menu
        help_button = QToolButton()
        help_button.setText("Help")
        help_button.setPopupMode(QToolButton.InstantPopup)
        help_button.setMenu(help_menu)
        toolbar.addWidget(help_button)

        # Create the "View" menu
        view_menu = QMenu("View", self)
        self.toggle_input_action = QAction(
            "Show/Hide Input", self, checkable=True, checked=True
        )
        self.toggle_input_action.triggered.connect(self.toggle_input_dock)
        view_menu.addAction(self.toggle_input_action)

        # Create a toolbutton for View menu
        view_button = QToolButton()
        view_button.setText("View")
        view_button.setPopupMode(QToolButton.InstantPopup)
        view_button.setMenu(view_menu)
        toolbar.addWidget(view_button)

        # Add the other actions that were originally in the toolbar
        refresh_action = QAction("Refresh Data", self)
        refresh_action.setToolTip("Generate Random Sample Data")
        refresh_action.triggered.connect(self.fill_random_sample_data)
        toolbar.addAction(refresh_action)

        generate_action = QAction("Generate", self)
        generate_action.setToolTip("Generate Schedule")
        generate_action.triggered.connect(self.generate_schedule)
        toolbar.addAction(generate_action)

        clear_action = QAction("Clear Table", self)
        clear_action.setToolTip("Clear all process data")
        clear_action.triggered.connect(self.clear_table)
        toolbar.addAction(clear_action)

        self.addToolBar(Qt.TopToolBarArea, toolbar)

        self.on_algorithm_changed(self.algorithm_selector.currentText())

    def on_algorithm_changed(self, algorithm):
        priority_required = (
            algorithm == "Priority" or algorithm == "Priority (Preemptive)"
        )
        self.process_table.setColumnHidden(3, not priority_required)
        self.process_table.setColumnHidden(4, True)
        self.quantum_input.setVisible(algorithm == "Round Robin")

    def add_process(self):
        row_count = self.process_table.rowCount()
        self.process_table.insertRow(row_count)
        self.process_table.setItem(row_count, 0, QTableWidgetItem(f"P{row_count+1}"))

    def delete_selected_process(self):
        selected_rows = self.process_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(
                self, "No selection", "Please select a process row to delete."
            )
            return
        for index in sorted(selected_rows, reverse=True):
            self.process_table.removeRow(index.row())

    def fill_random_sample_data(self):
        self.clear_table()
        algorithm = self.algorithm_selector.currentText()
        num_processes = random.randint(3, 6)
        self.process_table.setRowCount(num_processes)

        for i in range(num_processes):
            process_name = f"P{i+1}"
            arrival_time = random.randint(0, 5)
            burst_time = random.randint(1, 10)
            priority = random.randint(1, 5) if "Priority" in algorithm else None
            deadline = (
                random.randint(6, 20)
                if "EDF" in algorithm or "RMS" in algorithm
                else None
            )

            self.process_table.setItem(i, 0, QTableWidgetItem(process_name))
            self.process_table.setItem(i, 1, QTableWidgetItem(str(arrival_time)))
            self.process_table.setItem(i, 2, QTableWidgetItem(str(burst_time)))
            if priority is not None:
                self.process_table.setItem(i, 3, QTableWidgetItem(str(priority)))
            if deadline is not None:
                self.process_table.setItem(i, 4, QTableWidgetItem(str(deadline)))

    def clear_table(self):
        self.process_table.setRowCount(0)
        self.output_table.setRowCount(0)
        self.metrics_label.setText("")
        self.chart.init_chart()

    def generate_schedule(self):
        processes = []
        algorithm = self.algorithm_selector.currentText()
        for row in range(self.process_table.rowCount()):
            process_item = self.process_table.item(row, 0)
            arrival_time_item = self.process_table.item(row, 1)
            burst_time_item = self.process_table.item(row, 2)
            priority_item = self.process_table.item(row, 3)
            deadline_item = self.process_table.item(row, 4)

            if process_item and arrival_time_item and burst_time_item:
                try:
                    arrival_time = int(arrival_time_item.text())
                    burst_time = int(burst_time_item.text())
                    p_data = {
                        "Process": process_item.text(),
                        "Arrival Time": arrival_time,
                        "Burst Time": burst_time,
                    }
                    if (
                        "Priority" in algorithm
                        and priority_item
                        and priority_item.text()
                    ):
                        p_data["Priority"] = int(priority_item.text())
                    if (
                        ("EDF" in algorithm or "RMS" in algorithm)
                        and deadline_item
                        and deadline_item.text()
                    ):
                        p_data["Deadline"] = int(deadline_item.text())
                    processes.append(p_data)
                except ValueError:
                    QMessageBox.warning(
                        self,
                        "Invalid Input",
                        "Please ensure all fields are valid integers.",
                    )
                    return
            else:
                QMessageBox.warning(
                    self,
                    "Missing Data",
                    "Ensure every process has a name, arrival time, and burst time.",
                )
                return

        quantum = self.quantum_input.value() if algorithm == "Round Robin" else None
        if algorithm == "Round Robin" and not quantum:
            QMessageBox.warning(
                self,
                "Invalid Quantum",
                "Set a valid quantum time for Round Robin scheduling.",
            )
            return

        if not processes:
            QMessageBox.warning(
                self,
                "No Processes",
                "Add at least one process before generating the schedule.",
            )
            return

        scheduler = Scheduler(processes, algorithm, quantum)
        schedule, avg_waiting_time, avg_turnaround_time = scheduler.run()

        self.output_table.setRowCount(len(schedule))
        for row, entry in enumerate(schedule):
            self.output_table.setItem(row, 0, QTableWidgetItem(str(entry["Process"])))
            self.output_table.setItem(row, 1, QTableWidgetItem(str(entry["Start"])))
            self.output_table.setItem(row, 2, QTableWidgetItem(str(entry["Finish"])))

        self.metrics_label.setText(
            f"Average Waiting Time: {avg_waiting_time:.2f} units  |  Average Turnaround Time: {avg_turnaround_time:.2f} units"
        )

        self.chart.update_chart(schedule, processes)

    def show_about(self):
        QMessageBox.information(
            self,
            "About",
            "ShadFlow CPU Scheduler Visualizer\n\n"
            "A powerful tool to visualize CPU scheduling algorithms.\n"
            "Contribute or view source code at our GitHub repository.",
        )

    def show_descriptions(self):
        descriptions = (
            "<b>FCFS (First-Come, First-Served):</b><br>"
            "Processes are scheduled in the order they arrive. No preemption.<br><br>"
            "<b>SJF (Shortest Job First):</b><br>"
            "Selects the process with the smallest burst time. Non-preemptive, can lead to low waiting time for short processes.<br><br>"
            "<b>SRTF (Shortest Remaining Time First):</b><br>"
            "Preemptive version of SJF. Always choose the process with the shortest remaining burst time.<br><br>"
            "<b>Priority Scheduling:</b><br>"
            "Processes are scheduled based on priority. The lower the priority number, the higher the priority. Non-preemptive.<br><br>"
            "<b>Priority (Preemptive):</b><br>"
            "Higher priority processes can interrupt the current running process.<br><br>"
            "<b>Round Robin:</b><br>"
            "Each process gets a small time slice (quantum) and cycles through them fairly.<br><br>"
        )

        QMessageBox.information(self, "Algorithm Descriptions", descriptions)

    def toggle_input_dock(self):
        if self.toggle_input_action.isChecked():
            self.left_dock.show()
        else:
            self.left_dock.hide()

    def update_view_menu(self, visible):
        self.toggle_input_action.setChecked(visible)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Example dark mode palette
    dark_palette = app.palette()
    dark_palette.setColor(dark_palette.Window, QColor(45, 45, 45))
    dark_palette.setColor(dark_palette.WindowText, QColor(255, 255, 255))
    dark_palette.setColor(dark_palette.Base, QColor(35, 35, 35))
    dark_palette.setColor(dark_palette.AlternateBase, QColor(45, 45, 45))
    dark_palette.setColor(dark_palette.ToolTipBase, QColor(255, 255, 255))
    dark_palette.setColor(dark_palette.ToolTipText, QColor(255, 255, 255))
    dark_palette.setColor(dark_palette.Text, QColor(255, 255, 255))
    dark_palette.setColor(dark_palette.Button, QColor(53, 53, 53))
    dark_palette.setColor(dark_palette.ButtonText, QColor(255, 255, 255))
    dark_palette.setColor(dark_palette.Highlight, QColor(142, 68, 173))
    dark_palette.setColor(dark_palette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(dark_palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
