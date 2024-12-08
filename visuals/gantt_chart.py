import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patches import Rectangle
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.widgets import Button


class GanttChart(FigureCanvas):
    def __init__(self):
        self.figure, self.ax = plt.subplots(figsize=(10, 4))
        super().__init__(self.figure)
        self.init_chart()
        self.processes = []  # Initialize processes list

        # Create styled hover annotation
        self.hover_annotation = self.ax.annotate(
            "",
            xy=(0, 0),
            xytext=(20, 20),
            textcoords="offset points",
            ha="center",
            va="bottom",
            bbox=dict(
                boxstyle="round,pad=0.5",
                fc="#333333",
                ec="white",
                alpha=0.9,
                linewidth=1,
            ),
            arrowprops=dict(
                arrowstyle="->",
                connectionstyle="arc3,rad=0.2",
                color="white",
                lw=1.5,
            ),
            fontsize=9,
            color="white",
        )
        self.hover_annotation.set_visible(False)

        # Connect hover event
        self.figure.canvas.mpl_connect("motion_notify_event", self.on_hover)
        self.active_bar = None  # To track the currently hovered bar

    def init_chart(self):
        self.ax.clear()
        self.ax.set_title("Interactive Gantt Chart", fontsize=14, color='white', weight="bold")

        # Set dark theme
        self.ax.set_facecolor("#2e2e2e")  # Dark background
        self.figure.patch.set_facecolor("#2e2e2e")
        self.ax.title.set_color("white")
        self.ax.tick_params(colors='white')
        self.ax.xaxis.label.set_color('white')

        # Remove spines
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        self.ax.set_yticks([])
        self.ax.set_xticks([])

    def update_chart(self, schedule, processes):
        self.init_chart()
        self.processes = processes  # Store the processes
        y_position = 0
        self.bars = []
        time_points = set()
        max_finish_time = 0

        # Create a custom colormap
        num_processes = len(set(p["Process"] for p in schedule))
        colors = cm.get_cmap('viridis', num_processes)

        process_colors = {}
        process_total_times = {}     # Total burst times per process
        process_remaining_times = {} # Remaining times per process

        # Calculate total burst times for each process
        for process in self.processes:
            proc_name = f"{process['Process']}"
            process_total_times[proc_name] = process["Burst Time"]
            process_remaining_times[proc_name] = process["Burst Time"]

        for i, process in enumerate(schedule):
            start = process["Start"]
            finish = process["Finish"]
            proc_name = f"{process['Process']}"
            max_finish_time = max(max_finish_time, finish)
            time_points.update([start, finish])

            if proc_name not in process_colors:
                process_colors[proc_name] = colors(len(process_colors))

            # Calculate executed time
            executed_time = finish - start

            # Draw bars
            bar = self.ax.barh(
                y=y_position,
                width=executed_time,
                left=start,
                color=process_colors[proc_name],
                edgecolor="white",
                height=0.5,
                alpha=0.9,
            )[0]
            self.bars.append((bar, process))

            # Update remaining time
            remaining_time = process_remaining_times[proc_name] - executed_time
            process_remaining_times[proc_name] = remaining_time

            # Add process labels with remaining time
            self.ax.text(
                x=start + executed_time / 2,
                y=y_position,
                s=f"{proc_name}\nRem: {remaining_time}",
                ha="center",
                va="center",
                fontsize=10,
                weight="bold",
                color="white",
            )

        # Add time labels
        for time in sorted(time_points):
            self.ax.text(
                x=time,
                y=y_position - 0.6,
                s=str(time),
                ha="center",
                va="center",
                fontsize=9,
                color="white",
            )

        # Adjust axis limits
        self.ax.set_xlim(0, max_finish_time + 1)
        self.ax.set_ylim(-1, 1)
        self.draw()
        self.process_remaining_times = process_remaining_times  # Store for hover use
        self.schedule = schedule  # Store schedule for hover use

    def on_hover(self, event):
        if event.inaxes == self.ax:
            for bar, process in self.bars:
                contains, _ = bar.contains(event)
                if contains:
                    self.hover_annotation.xy = (event.xdata, event.ydata)
                    proc_name = f"{process['Process']}"
                    rem_time = self.process_remaining_times.get(proc_name, 0)
                    executed_time = process['Finish'] - process['Start']
                    tooltip_text = (
                        f"Process: {proc_name}\n"
                        f"Start Time: {process['Start']}\n"
                        f"Finish Time: {process['Finish']}\n"
                        f"Executed: {executed_time}\n"
                        f"Remaining Time: {rem_time}"
                    )
                    self.hover_annotation.set_text(tooltip_text)
                    self.hover_annotation.set_visible(True)

                    # Highlight the bar
                    if self.active_bar is not bar:
                        if self.active_bar:
                            self.active_bar.set_alpha(0.9)
                            self.active_bar.set_edgecolor("white")
                            self.active_bar.set_linewidth(1)
                        bar.set_alpha(1.0)
                        bar.set_edgecolor("#FFD700")  # Gold edge
                        bar.set_linewidth(2)
                        self.active_bar = bar
                    self.draw_idle()
                    return
            # Reset hover state
            if self.active_bar:
                self.active_bar.set_alpha(0.9)
                self.active_bar.set_edgecolor("white")
                self.active_bar.set_linewidth(1)
                self.active_bar = None
            self.hover_annotation.set_visible(False)
            self.draw_idle()


# Example Usage
if __name__ == "__main__":
    schedule = [
        {"Process": 1, "Start": 0, "Finish": 3},
        {"Process": 2, "Start": 3, "Finish": 7},
        {"Process": 3, "Start": 7, "Finish": 9},
        {"Process": 4, "Start": 9, "Finish": 12},
    ]

    chart = GanttChart()
    chart.update_chart(schedule)
    plt.show()
