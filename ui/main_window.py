from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
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
        self.setGeometry(100, 100, 1200, 700)

        # Main Container
        container = QWidget()
        self.setCentralWidget(container)
        layout = QHBoxLayout(container)

        # Left Panel: Input and Controls
        self.left_panel = QVBoxLayout()
        self.left_panel.setContentsMargins(20, 20, 20, 20)

        # Algorithm Selection Label
        alg_label = QLabel("Select Algorithm:")
        self.left_panel.addWidget(alg_label)

        # Algorithm Selector
        self.algorithm_selector = QComboBox()
        self.algorithm_selector.addItems(
            [
                "FCFS",
                "SJF",
                "SRTF",
                "Priority",
                "Round Robin",
            ]
        )
        self.left_panel.addWidget(self.algorithm_selector)

        # Input Table
        table_label = QLabel("Process Details:")
        self.left_panel.addWidget(table_label)
        self.process_table = QTableWidget(0, 5)  # Changed to 5 columns
        self.process_table.setHorizontalHeaderLabels(
            ["Process", "Arrival Time", "Burst Time", "Priority", "Deadline"]
        )
        self.left_panel.addWidget(self.process_table)

        # Parameters Panel
        self.params_panel = QWidget()
        params_layout = QVBoxLayout(self.params_panel)

        # Quantum input for Round Robin
        self.quantum_input = QSpinBox()
        self.quantum_input.setRange(1, 100)
        self.quantum_input.setValue(2)
        self.quantum_input.setPrefix("Quantum: ")
        params_layout.addWidget(self.quantum_input)

        self.left_panel.addWidget(self.params_panel)

        # Update process table
        self.process_table.setColumnCount(5)
        self.process_table.setHorizontalHeaderLabels(
            ["Process", "Arrival Time", "Burst Time", "Priority", "Deadline"]
        )

        # Connect algorithm selection change
        self.algorithm_selector.currentTextChanged.connect(self.on_algorithm_changed)

        # Buttons
        add_process_button = QPushButton("Add Process")
        add_process_button.clicked.connect(self.add_process)
        self.left_panel.addWidget(add_process_button)

        fill_sample_button = QPushButton("Fill Sample Data")
        fill_sample_button.clicked.connect(self.fill_sample_data)
        self.left_panel.addWidget(fill_sample_button)

        generate_button = QPushButton("Generate Schedule")
        generate_button.clicked.connect(self.generate_schedule)
        self.left_panel.addWidget(generate_button)

        layout.addLayout(self.left_panel)

        # Right Panel: Output and Chart
        self.right_panel = QVBoxLayout()
        self.right_panel.setContentsMargins(20, 20, 20, 20)

        # Output Table
        self.output_table = QTableWidget(0, 3)
        self.output_table.setHorizontalHeaderLabels(
            ["Process", "Start Time", "Finish Time"]
        )
        self.right_panel.addWidget(self.output_table)

        # Add waiting time label after output table
        self.waiting_time_label = QLabel()
        self.right_panel.addWidget(self.waiting_time_label)

        # Gantt Chart Canvas
        self.chart = GanttChart()
        self.right_panel.addWidget(self.chart)

        layout.addLayout(self.right_panel)

    def add_process(self):
        # Add an empty row to the process table
        self.process_table.insertRow(self.process_table.rowCount())

    def on_algorithm_changed(self, algorithm):
        # Adjust visibility of inputs based on selected algorithm
        self.quantum_input.setVisible(algorithm == "Round Robin")
        # Update table columns visibility
        self.process_table.setColumnHidden(
            3, algorithm != "Priority"
        )  # Priority column
        self.process_table.setColumnHidden(4, True)  # Hide Deadline column

    def generate_schedule(self):
        # Extract processes from table
        processes = []
        algorithm = self.algorithm_selector.currentText()
        for row in range(self.process_table.rowCount()):
            process_item = self.process_table.item(row, 0)
            arrival_time_item = self.process_table.item(row, 1)
            burst_time_item = self.process_table.item(row, 2)
            priority_item = self.process_table.item(row, 3)
            deadline_item = self.process_table.item(row, 4)

            if process_item and arrival_time_item and burst_time_item:
                process_data = {
                    "Process": process_item.text(),
                    "Arrival Time": int(arrival_time_item.text()),
                    "Burst Time": int(burst_time_item.text()),
                }

                # Add priority and deadline if needed
                if algorithm in ["Priority", "Multilevel Queue"] and priority_item:
                    process_data["Priority"] = int(priority_item.text())
                if algorithm in ["EDF", "RMS"] and deadline_item:
                    process_data["Deadline"] = int(deadline_item.text())

                processes.append(process_data)

        # Get algorithm parameters
        quantum = self.quantum_input.value() if algorithm == "Round Robin" else None

        # Update the scheduler initialization
        scheduler = Scheduler(processes, algorithm, quantum)

        schedule, avg_waiting_time = scheduler.run()

        # Update output table
        self.output_table.setRowCount(len(schedule))
        for row, process in enumerate(schedule):
            self.output_table.setItem(row, 0, QTableWidgetItem(process["Process"]))
            self.output_table.setItem(row, 1, QTableWidgetItem(str(process["Start"])))
            self.output_table.setItem(row, 2, QTableWidgetItem(str(process["Finish"])))

        # Update waiting time label
        self.waiting_time_label.setText(
            f"Average Waiting Time: {avg_waiting_time:.2f} units"
        )

        # Update Gantt chart with schedule and processes
        self.chart.update_chart(schedule, processes)

    def fill_sample_data(self):
        sample_data = [
            {"Process": "P1", "Arrival Time": 0, "Burst Time": 5},
            {"Process": "P2", "Arrival Time": 1, "Burst Time": 3},
            {"Process": "P3", "Arrival Time": 2, "Burst Time": 8},
            {"Process": "P4", "Arrival Time": 3, "Burst Time": 6},
        ]
        self.process_table.setRowCount(len(sample_data))
        for row, data in enumerate(sample_data):
            self.process_table.setItem(row, 0, QTableWidgetItem(data["Process"]))
            self.process_table.setItem(
                row, 1, QTableWidgetItem(str(data["Arrival Time"]))
            )
            self.process_table.setItem(
                row, 2, QTableWidgetItem(str(data["Burst Time"]))
            )
