import datetime
import os
import random
import sys
from math import ceil, floor

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QDockWidget,
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
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

        # Create the output log directory if it doesn't exist
        self.output_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "output"
        )
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # Default output file
        self.output_file = os.path.join(self.output_dir, "scheduling_results.txt")

        # Set up central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)

        # Set up left dock with process input
        self.left_dock = QDockWidget("Process Input", self)
        self.left_dock.setFeatures(
            QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable
        )
        self.left_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        # Build left dock content
        dock_content = QWidget()
        dock_layout = QVBoxLayout(dock_content)
        dock_layout.setContentsMargins(10, 10, 10, 10)
        dock_layout.setSpacing(15)

        # Title label
        title_label = QLabel("ShadFlow CPU Scheduler")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
        title_label.setAlignment(Qt.AlignCenter)
        dock_layout.addWidget(title_label, alignment=Qt.AlignCenter)

        # Algorithm selector
        alg_label = QLabel("Select Algorithm:")
        alg_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #FFFFFF;")
        dock_layout.addWidget(alg_label)

        self.algorithm_selector = QComboBox()
        self.algorithm_selector.addItems(["FCFS", "SRTF", "Priority", "Round Robin"])
        self.algorithm_selector.setStyleSheet("font-size: 13px; color: #000;")
        self.algorithm_selector.currentTextChanged.connect(self.on_algorithm_changed)
        dock_layout.addWidget(self.algorithm_selector)

        # Process table
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

        # Quantum input
        self.quantum_input = QSpinBox()
        self.quantum_input.setRange(1, 100)
        self.quantum_input.setValue(2)
        self.quantum_input.setPrefix("Quantum: ")
        self.quantum_input.setStyleSheet("font-size: 13px; color: #FFFFFF;")
        self.quantum_input.setVisible(False)
        dock_layout.addWidget(self.quantum_input)

        # Statistical parameters group for random data generation
        stats_group = QGroupBox("Random Data Parameters")
        stats_group.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        stats_layout = QGridLayout()

        # Arrival Time Mean
        stats_layout.addWidget(QLabel("Arrival Time Mean (μ):"), 0, 0)
        self.arrival_mean = QDoubleSpinBox()
        self.arrival_mean.setRange(0, 100)
        self.arrival_mean.setValue(3.0)
        self.arrival_mean.setDecimals(1)
        self.arrival_mean.setStyleSheet("color: #FFFFFF;")
        stats_layout.addWidget(self.arrival_mean, 0, 1)

        # Arrival Time StdDev
        stats_layout.addWidget(QLabel("Arrival StdDev (σ):"), 0, 2)
        self.arrival_std = QDoubleSpinBox()
        self.arrival_std.setRange(0.1, 20)
        self.arrival_std.setValue(2.0)
        self.arrival_std.setDecimals(1)
        self.arrival_std.setStyleSheet("color: #FFFFFF;")
        stats_layout.addWidget(self.arrival_std, 0, 3)

        # Burst Time Mean
        stats_layout.addWidget(QLabel("Burst Time Mean (μ):"), 1, 0)
        self.burst_mean = QDoubleSpinBox()
        self.burst_mean.setRange(1, 100)
        self.burst_mean.setValue(5.0)
        self.burst_mean.setDecimals(1)
        self.burst_mean.setStyleSheet("color: #FFFFFF;")
        stats_layout.addWidget(self.burst_mean, 1, 1)

        # Burst Time StdDev
        stats_layout.addWidget(QLabel("Burst StdDev (σ):"), 1, 2)
        self.burst_std = QDoubleSpinBox()
        self.burst_std.setRange(0.1, 20)
        self.burst_std.setValue(2.0)
        self.burst_std.setDecimals(1)
        self.burst_std.setStyleSheet("color: #FFFFFF;")
        stats_layout.addWidget(self.burst_std, 1, 3)

        # Help label
        help_label = QLabel("μ = Average value | σ = Spread of values")
        help_label.setStyleSheet("color: #AAAAAA; font-style: italic; font-size: 11px;")
        help_label.setAlignment(Qt.AlignCenter)
        stats_layout.addWidget(help_label, 2, 0, 1, 4)

        stats_group.setLayout(stats_layout)
        dock_layout.addWidget(stats_group)

        # Import configuration button
        import_config_button = QPushButton("Load From File")
        import_config_button.setStyleSheet(
            """
            QPushButton {
                background-color: #3070C0; 
                color: white; 
                border: none; 
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #4080D0; }
            QPushButton:pressed { background-color: #2060B0; }
        """
        )
        import_config_button.setToolTip(
            "Load process parameters from a configuration file"
        )
        import_config_button.clicked.connect(self.load_config_from_file)
        dock_layout.addWidget(import_config_button, alignment=Qt.AlignCenter)

        # Unified button style
        button_style = """
            QPushButton {
                background-color: #4CAF50; 
                color: white; 
                border: none; 
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #45A049; }
            QPushButton:pressed { background-color: #388E3C; }
        """

        # Action buttons
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

        # Generate button
        generate_button = QPushButton("Generate Schedule")
        generate_button.setStyleSheet(
            button_style + "font-size: 14px; padding: 8px 15px;"
        )
        generate_button.clicked.connect(self.generate_schedule)
        dock_layout.addWidget(generate_button, alignment=Qt.AlignCenter)

        # Compare All Algorithms button
        compare_button = QPushButton("Compare All Algorithms")
        compare_button.setStyleSheet(
            """
            QPushButton {
                background-color: #7B68EE; 
                color: white; 
                border: none; 
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #9370DB; }
            QPushButton:pressed { background-color: #6A5ACD; }
            """
        )
        compare_button.setToolTip(
            "Run all scheduling algorithms and compare performance"
        )
        compare_button.clicked.connect(self.compare_all_algorithms)
        dock_layout.addWidget(compare_button, alignment=Qt.AlignCenter)

        # Separator line
        spacer_frame = QFrame()
        spacer_frame.setFrameShape(QFrame.HLine)
        spacer_frame.setFrameShadow(QFrame.Sunken)
        spacer_frame.setStyleSheet("color: #FFFFFF;")
        dock_layout.addWidget(spacer_frame)

        # Finalize left dock
        dock_content.setLayout(dock_layout)
        self.left_dock.setWidget(dock_content)
        self.left_dock.setMinimumWidth(400)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.left_dock)

        # Right Side (Central Widget)
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(15)

        # Output table
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

        # Metrics display
        self.metrics_label = QLabel("")
        self.metrics_label.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #FFFFFF;"
        )
        right_layout.addWidget(self.metrics_label)

        # Gantt chart
        self.chart = GanttChart()
        right_layout.addWidget(self.chart)

        # Finalize right side
        right_container = QWidget()
        right_container.setLayout(right_layout)
        main_layout.addWidget(right_container)

        # Initialize UI state
        self.on_algorithm_changed(self.algorithm_selector.currentText())

    def on_algorithm_changed(self, algorithm):
        priority_required = algorithm == "Priority"
        self.process_table.setColumnHidden(3, not priority_required)
        self.process_table.setColumnHidden(4, True)
        self.quantum_input.setVisible(algorithm == "Round Robin")

    def load_config_from_file(self):
        """Load process configuration from a text file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Process Configuration File",
            "",
            "Text Files (*.txt);;All Files (*)",
        )

        if not file_path:
            return

        try:
            with open(file_path, "r") as file:
                lines = file.readlines()

                if len(lines) < 4:
                    QMessageBox.warning(
                        self,
                        "Invalid Format",
                        "File must contain at least 4 lines with the required parameters.",
                    )
                    return

                # Parse number of processes
                try:
                    num_processes = int(lines[0].strip())
                except ValueError:
                    QMessageBox.warning(
                        self,
                        "Invalid Format",
                        "Line 1 must contain the number of processes.",
                    )
                    return

                # Parse arrival time mean and std dev
                try:
                    arrival_params = lines[1].strip().split()
                    if len(arrival_params) < 2:
                        raise ValueError("Not enough parameters")
                    arrival_mean = float(arrival_params[0])
                    arrival_std = float(arrival_params[1])
                except (ValueError, IndexError):
                    QMessageBox.warning(
                        self,
                        "Invalid Format",
                        "Line 2 must contain mean and standard deviation for arrival time.",
                    )
                    return

                # Parse burst time mean and std dev
                try:
                    burst_params = lines[2].strip().split()
                    if len(burst_params) < 2:
                        raise ValueError("Not enough parameters")
                    burst_mean = float(burst_params[0])
                    burst_std = float(burst_params[1])
                except (ValueError, IndexError):
                    QMessageBox.warning(
                        self,
                        "Invalid Format",
                        "Line 3 must contain mean and standard deviation for burst time.",
                    )
                    return

                # Parse lambda for priority
                try:
                    priority_lambda = float(lines[3].strip())
                except ValueError:
                    QMessageBox.warning(
                        self,
                        "Invalid Format",
                        "Line 4 must contain lambda for priority.",
                    )
                    return

                # Update the UI controls with loaded values
                self.arrival_mean.setValue(arrival_mean)
                self.arrival_std.setValue(arrival_std)
                self.burst_mean.setValue(burst_mean)
                self.burst_std.setValue(burst_std)

                # Generate the processes with the loaded parameters
                self.generate_from_config(num_processes, priority_lambda)

                QMessageBox.information(
                    self,
                    "Configuration Loaded",
                    f"Successfully loaded configuration for {num_processes} processes.",
                )

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load configuration: {str(e)}"
            )

    def generate_from_config(self, num_processes, priority_lambda):
        """Generate processes based on loaded configuration."""
        self.clear_table()
        algorithm = self.algorithm_selector.currentText()
        self.process_table.setRowCount(num_processes)

        # Get statistical parameters from UI controls
        arrival_mean = self.arrival_mean.value()
        arrival_std = self.arrival_std.value()
        burst_mean = self.burst_mean.value()
        burst_std = self.burst_std.value()

        for i in range(num_processes):
            process_name = f"P{i+1}"

            # Generate arrival time using normal distribution
            arrival_time = max(0, round(random.gauss(arrival_mean, arrival_std)))

            # Generate burst time using normal distribution
            burst_time = max(1, round(random.gauss(burst_mean, burst_std)))

            # Generate priority using exponential distribution
            priority = None
            if "Priority" in algorithm:
                # Lower values have higher priority (1 is highest priority)
                # We use ceil to avoid 0 priority and ensure minimum of 1
                priority = ceil(random.expovariate(priority_lambda))

            # Generate deadline for EDF/RMS algorithms
            deadline = None
            if "EDF" in algorithm or "RMS" in algorithm:
                deadline = arrival_time + burst_time + random.randint(0, 10)

            # Populate the table
            self.process_table.setItem(i, 0, QTableWidgetItem(process_name))
            self.process_table.setItem(i, 1, QTableWidgetItem(str(arrival_time)))
            self.process_table.setItem(i, 2, QTableWidgetItem(str(burst_time)))
            if priority is not None:
                self.process_table.setItem(i, 3, QTableWidgetItem(str(priority)))
            if deadline is not None:
                self.process_table.setItem(i, 4, QTableWidgetItem(str(deadline)))

    def fill_random_sample_data(self):
        """Generate random sample data using UI parameters."""
        self.clear_table()
        algorithm = self.algorithm_selector.currentText()
        num_processes = random.randint(3, 10)

        # For Priority algorithm, use lambda=0.5 by default (can be overridden from file)
        priority_lambda = 0.5 if "Priority" in algorithm else None

        self.generate_from_config(num_processes, priority_lambda)

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

        # Save results to file
        self.save_results_to_file(
            algorithm, schedule, avg_waiting_time, avg_turnaround_time
        )

    def compare_all_algorithms(self):
        """Run all scheduling algorithms on the same process set and compare results."""
        # Get processes from the table
        processes = []
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
                    if priority_item and priority_item.text():
                        p_data["Priority"] = int(priority_item.text())
                    if deadline_item and deadline_item.text():
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

        if not processes:
            QMessageBox.warning(
                self,
                "No Processes",
                "Add at least one process before comparing algorithms.",
            )
            return

        # Check if Priority data is available
        has_priority = all("Priority" in p for p in processes)
        if not has_priority:
            # Assign default priorities (1 to all)
            for p in processes:
                p["Priority"] = 1

        # Run all algorithms
        algorithms = ["FCFS", "SRTF", "Priority", "Round Robin"]
        results = []

        # Prepare the output display
        self.metrics_label.setText("Comparing algorithms...")

        # Create a dialog to display results
        comparison_dialog = QDialog(self)
        comparison_dialog.setWindowTitle("Algorithm Comparison")
        comparison_dialog.setMinimumSize(1200, 800)  # Larger size to fit all charts

        # Use scroll area to ensure all content is accessible
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)

        # Results table
        results_table = QTableWidget(len(algorithms), 3)
        results_table.setHorizontalHeaderLabels(
            ["Algorithm", "Avg. Waiting Time", "Avg. Turnaround Time"]
        )
        results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        results_table.setMaximumHeight(150)
        layout.addWidget(QLabel("<b>Performance Comparison:</b>"))
        layout.addWidget(results_table)

        # Run each algorithm and store results
        best_algorithm = None
        min_waiting_time = float("inf")

        for i, algorithm in enumerate(algorithms):
            quantum = 2 if algorithm == "Round Robin" else None
            scheduler = Scheduler(processes.copy(), algorithm, quantum)
            schedule, avg_waiting_time, avg_turnaround_time = scheduler.run()

            results.append(
                {
                    "algorithm": algorithm,
                    "schedule": schedule,
                    "avg_waiting_time": avg_waiting_time,
                    "avg_turnaround_time": avg_turnaround_time,
                }
            )

            # Update result table
            results_table.setItem(i, 0, QTableWidgetItem(algorithm))
            results_table.setItem(i, 1, QTableWidgetItem(f"{avg_waiting_time:.2f}"))
            results_table.setItem(i, 2, QTableWidgetItem(f"{avg_turnaround_time:.2f}"))

            # Track best algorithm based on waiting time
            if avg_waiting_time < min_waiting_time:
                min_waiting_time = avg_waiting_time
                best_algorithm = algorithm

        # Highlight best algorithm in the table
        for i in range(results_table.rowCount()):
            if results_table.item(i, 0).text() == best_algorithm:
                for j in range(results_table.columnCount()):
                    results_table.item(i, j).setBackground(
                        QColor(152, 251, 152)
                    )  # Light green

        # Add summary label
        summary = QLabel(
            f"<b>Best Algorithm:</b> {best_algorithm} with {min_waiting_time:.2f} avg. waiting time"
        )
        summary.setStyleSheet("color: green; font-size: 14px;")
        layout.addWidget(summary)

        # Create a section for each algorithm with detailed output and chart
        for result in results:
            alg_name = result["algorithm"]
            schedule = result["schedule"]

            # Add algorithm header with metrics
            is_best = alg_name == best_algorithm
            header_style = (
                "color: green; font-weight: bold; font-size: 16px;"
                if is_best
                else "font-weight: bold; font-size: 16px;"
            )
            best_badge = " [BEST]" if is_best else ""

            algorithm_section = QGroupBox(f"{alg_name}{best_badge}")
            algorithm_section.setStyleSheet(f"QGroupBox {{ {header_style} }}")
            alg_layout = QVBoxLayout(algorithm_section)

            # Add metrics for this algorithm
            metrics_label = QLabel(
                f"Average Waiting Time: {result['avg_waiting_time']:.2f} units | "
                f"Average Turnaround Time: {result['avg_turnaround_time']:.2f} units"
            )
            alg_layout.addWidget(metrics_label)

            # Add schedule table
            schedule_table = QTableWidget(len(schedule), 3)
            schedule_table.setHorizontalHeaderLabels(
                ["Process", "Start Time", "Finish Time"]
            )
            schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            schedule_table.setMaximumHeight(200)

            for row, entry in enumerate(schedule):
                schedule_table.setItem(row, 0, QTableWidgetItem(str(entry["Process"])))
                schedule_table.setItem(row, 1, QTableWidgetItem(str(entry["Start"])))
                schedule_table.setItem(row, 2, QTableWidgetItem(str(entry["Finish"])))

            alg_layout.addWidget(QLabel("<b>Schedule:</b>"))
            alg_layout.addWidget(schedule_table)

            # Add Gantt chart for this algorithm
            alg_layout.addWidget(QLabel("<b>Gantt Chart:</b>"))
            chart = GanttChart()
            chart.update_chart(schedule, processes)
            chart.setMinimumHeight(250)  # Set minimum height to ensure visibility
            alg_layout.addWidget(chart)

            layout.addWidget(algorithm_section)

            # If this is the best algorithm, also update the main window
            if alg_name == best_algorithm:
                self.output_table.setRowCount(len(schedule))
                for row, entry in enumerate(schedule):
                    self.output_table.setItem(
                        row, 0, QTableWidgetItem(str(entry["Process"]))
                    )
                    self.output_table.setItem(
                        row, 1, QTableWidgetItem(str(entry["Start"]))
                    )
                    self.output_table.setItem(
                        row, 2, QTableWidgetItem(str(entry["Finish"]))
                    )

                self.metrics_label.setText(
                    f"Best Algorithm: {best_algorithm} | "
                    f"Average Waiting Time: {result['avg_waiting_time']:.2f} units | "
                    f"Average Turnaround Time: {result['avg_turnaround_time']:.2f} units"
                )

                self.chart.update_chart(schedule, processes)

        # Add export button
        export_button = QPushButton("Export Results")
        export_button.clicked.connect(lambda: self.export_comparison_results(results))
        layout.addWidget(export_button, alignment=Qt.AlignCenter)

        # Save all results to the output file, replacing any previous content
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Open in 'w' mode to clear the file before writing new results
        with open(self.output_file, "w") as file:
            file.write(f"{'='*50}\n")
            file.write(f"ALGORITHM COMPARISON ({timestamp})\n")
            file.write(f"{'='*50}\n\n")

            # Sort results by average waiting time
            sorted_results = sorted(results, key=lambda x: x["avg_waiting_time"])

            for i, result in enumerate(sorted_results):
                file.write(f"{i+1}. {result['algorithm']}\n")
                file.write(
                    f"   Average Waiting Time: {result['avg_waiting_time']:.2f}\n"
                )
                file.write(
                    f"   Average Turnaround Time: {result['avg_turnaround_time']:.2f}\n"
                )
                file.write(f"   Schedule: \n")

                for entry in result["schedule"]:
                    file.write(
                        f"      {entry['Process']}: Start={entry['Start']}, Finish={entry['Finish']}\n"
                    )

                file.write("\n")

            file.write(f"Best Algorithm: {sorted_results[0]['algorithm']}\n")

        # Show a notification about the saved file
        self.metrics_label.setText(
            self.metrics_label.text()
            + f" | Results saved to {os.path.basename(self.output_file)}"
        )

        # Set up scroll area
        scroll_area.setWidget(scroll_content)
        dialog_layout = QVBoxLayout(comparison_dialog)
        dialog_layout.addWidget(scroll_area)

        # Show the dialog
        comparison_dialog.exec()

    def export_comparison_results(self, results):
        """Export comparison results to a file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Comparison Results", "", "Text Files (*.txt);;All Files (*)"
        )

        if not file_path:
            return

        try:
            with open(file_path, "w") as file:
                file.write("ALGORITHM COMPARISON RESULTS\n")
                file.write("===========================\n\n")

                # Sort results by average waiting time
                sorted_results = sorted(results, key=lambda x: x["avg_waiting_time"])

                for i, result in enumerate(sorted_results):
                    file.write(f"{i+1}. {result['algorithm']}\n")
                    file.write(
                        f"   Average Waiting Time: {result['avg_waiting_time']:.2f}\n"
                    )
                    file.write(
                        f"   Average Turnaround Time: {result['avg_turnaround_time']:.2f}\n"
                    )
                    file.write(f"   Schedule: \n")

                    for entry in result["schedule"]:
                        file.write(
                            f"      {entry['Process']}: Start={entry['Start']}, Finish={entry['Finish']}\n"
                        )

                    file.write("\n")

                file.write("\nBest Algorithm: " + sorted_results[0]["algorithm"] + "\n")

            QMessageBox.information(
                self,
                "Export Successful",
                f"Results successfully exported to {file_path}",
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Export Failed", f"Failed to export results: {str(e)}"
            )

    def save_results_to_file(
        self, algorithm, schedule, avg_waiting_time, avg_turnaround_time
    ):
        """Save scheduling results to the output file."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Open in 'w' mode to clear the file before writing new results
        with open(self.output_file, "w") as file:
            file.write(f"{'='*50}\n")
            file.write(f"SINGLE ALGORITHM RUN: {algorithm} ({timestamp})\n")
            file.write(f"{'='*50}\n\n")

            file.write(f"Average Waiting Time: {avg_waiting_time:.2f}\n")
            file.write(f"Average Turnaround Time: {avg_turnaround_time:.2f}\n")
            file.write("Schedule:\n")

            for entry in schedule:
                file.write(
                    f"   {entry['Process']}: Start={entry['Start']}, Finish={entry['Finish']}\n"
                )

        # Show a notification about the saved file
        self.metrics_label.setText(
            self.metrics_label.text()
            + f" | Results saved to {os.path.basename(self.output_file)}"
        )
