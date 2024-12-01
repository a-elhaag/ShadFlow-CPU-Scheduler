# SchadFlow: Process Scheduling Visualization Tool

SchadFlow is an interactive tool for visualizing CPU scheduling algorithms. Designed for educational purposes, it simplifies understanding process scheduling through a clean GUI and detailed visualizations.

---

## **Features**

1. **Scheduling Algorithms Implemented:**
   - First Come, First Serve (FCFS)
   - Shortest Job First (SJF)
   - Round Robin
   - Shortest Remaining Time First (SRTF)
   - Priority Scheduling

2. **Visualizations:**
   - Gantt charts for process scheduling timelines.
   - Interactive and dynamic interface for real-time updates.

3. **Dark Themed UI:**
   - Modern, visually appealing dark theme with clear contrasts.

4. **Extensible Design:**
   - Easily add new scheduling algorithms or extend existing functionalities.

---

## **File Structure**

```
SchadFlow/
│
├── main.py                     # Entry point for the application
│
├── scheduler/                  # Scheduling logic
│   ├── __init__.py
│   ├── base_scheduler.py       # Abstract base class for schedulers
│   ├── fcfs.py                 # First Come, First Serve algorithm
│   ├── sjf.py                  # Shortest Job First algorithm
│   ├── round_robin.py          # Round Robin algorithm
│   ├── srtf.py                 # Shortest Remaining Time First algorithm
│   ├── priority.py             # Priority scheduling algorithm
│   └── utils.py                # Utility functions for schedulers
│
├── gui/                        # GUI components
│   ├── __init__.py
│   ├── main_window.py          # Main application window
│
├── visuals/                    # Visualization components
│   ├── __init__.py
│   └── gantt_chart.py          # Gantt chart visualization
│
├── data/                       # Data handling
│   ├── __init__.py
│   ├── task.py                 # Task or process representation
│   └── scheduler.py            # Interface for schedulers
│
├── assets/                     # Static assets (icons, fonts, stylesheets)
│   └── README.md               # Documentation for assets
│
├── requirements.txt            # Required Python libraries
└── README.md                   # Project documentation
```

---

## **Technologies Used**

- **Python**: Programming language for the entire project.
- **PySide6**: GUI framework for a polished user interface.
- **Plotly**: Visualization library for interactive Gantt charts.
- **Pandas**: Data manipulation and handling.
- **Matplotlib**: Optional for quick static visualizations.
- **PyQtGraph**: For high-performance, custom visualizations.

---

## **Setup Instructions**

### **1. Clone the Repository**
```bash
git clone https://github.com/username/SchadFlow.git
cd SchadFlow
```

### **2. Set Up Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Run the Application**
```bash
python main.py
```

---

## **Future Plans**

- Add more scheduling algorithms (e.g., Multilevel Queue, Multilevel Feedback Queue).
- Generate detailed reports for scheduling results.
- Export visualizations as images or PDFs.
- Incorporate user-friendly forms to input processes dynamically.

---

## **License**

This project is licensed under the MIT License. See `LICENSE` for more details.
```

Let me know if you need further edits or any additional sections!
