import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class GanttChart(FigureCanvas):
    def __init__(self):
        self.figure, self.ax = plt.subplots(figsize=(10, 4))
        super().__init__(self.figure)
        self.init_chart()
        self.processes = []
        self.bars = []
        self.schedule = []
        self.process_remaining_times = {}

        # Disable all interactive elements
        plt.rcParams["interactive"] = False
        plt.rcParams["toolbar"] = "None"

    def init_chart(self):
        self.ax.clear()
        self.ax.set_title(
            "CPU Scheduling Gantt Chart", fontsize=16, color="#3070C0", weight="bold"
        )
        self.ax.set_facecolor("#1E1E1E")  # Darker background for better contrast
        self.figure.patch.set_facecolor("#1E1E1E")
        self.ax.title.set_color("#3070C0")  # Blue title for a modern look
        self.ax.tick_params(colors="#E0E0E0")  # Light grey ticks for better visibility
        self.ax.xaxis.label.set_color("#E0E0E0")
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        self.ax.set_yticks([])
        self.ax.set_xticks([])

    def update_chart(self, schedule, processes):
        self.init_chart()
        self.processes = processes
        self.schedule = schedule
        self.bars = []
        time_points = set()
        max_finish_time = 0

        num_processes = len(set(p["Process"] for p in schedule))
        colors = cm.get_cmap("cool", num_processes)  # Blue-focused colormap
        process_colors = {}
        self.process_remaining_times = {}

        for p in self.processes:
            self.process_remaining_times[p["Process"]] = p["Burst Time"]

        for process in schedule:
            start = process["Start"]
            finish = process["Finish"]
            proc_name = process["Process"]
            max_finish_time = max(max_finish_time, finish)
            time_points.update([start, finish])
            if proc_name not in process_colors:
                process_colors[proc_name] = colors(len(process_colors))

            executed_time = finish - start
            bar = self.ax.barh(
                y=0,
                width=executed_time,
                left=start,
                color=process_colors[proc_name],
                edgecolor="#FFFFFF",
                height=0.5,
                alpha=0.95,
            )[0]
            self.bars.append((bar, process))
            remaining_time = self.process_remaining_times[proc_name] - executed_time
            self.process_remaining_times[proc_name] = remaining_time
            self.ax.text(
                x=start + executed_time / 2,
                y=0,
                s=f"{proc_name}\nTime: {executed_time}",
                ha="center",
                va="center",
                fontsize=10,
                weight="bold",
                color="#FFFFFF",
            )

        # Add time labels at each point
        for time in sorted(time_points):
            self.ax.text(
                x=time,
                y=-0.6,
                s=str(time),
                ha="center",
                va="center",
                fontsize=9,
                color="#E0E0E0",
            )
            # Add vertical grid lines at time points
            self.ax.axvline(x=time, color="#3070C0", alpha=0.2, linestyle=":")

        # Add a summary label showing total execution time
        self.ax.text(
            x=max_finish_time / 2,
            y=-0.8,
            s=f"Total Execution Time: {max_finish_time}",
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
            color="#3070C0",
            bbox=dict(
                facecolor="#252530",
                edgecolor="#3070C0",
                boxstyle="round,pad=0.5",
                alpha=0.8,
            ),
        )

        # Set fixed axis limits
        self.ax.set_xlim(0, max_finish_time + 1)
        self.ax.set_ylim(-1, 1)

        # Add proper x-axis ticks
        self.ax.set_xticks(list(range(0, max_finish_time + 1)))

        self.draw()
