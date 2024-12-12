import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patches import Rectangle
from matplotlib import cm
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMenu

class GanttChart(FigureCanvas):
    def __init__(self):
        self.figure, self.ax = plt.subplots(figsize=(10, 4))
        super().__init__(self.figure)
        self.init_chart()
        self.processes = []
        self.bars = []
        self.schedule = []
        self.process_remaining_times = {}
        self.active_bar = None
        self.selected_bar = None

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

        # Vertical line and time annotation
        self.vertical_line = self.ax.axvline(x=0, color="#FFD700", linewidth=1, alpha=0.8, linestyle="--", visible=False)
        self.time_annotation = self.ax.annotate(
            "",
            xy=(0, -0.6),
            xytext=(0, -20),
            textcoords="offset points",
            ha="center",
            va="top",
            bbox=dict(
                boxstyle="round,pad=0.3",
                fc="#333333",
                ec="white",
                alpha=0.9,
                linewidth=1,
            ),
            fontsize=9,
            color="white",
        )
        self.time_annotation.set_visible(False)

        self.cid_hover = self.figure.canvas.mpl_connect("motion_notify_event", self.on_hover)
        self.cid_leave = self.figure.canvas.mpl_connect("axes_leave_event", self.on_leave)
        self.cid_click = self.figure.canvas.mpl_connect("button_press_event", self.on_click)
        self.cid_scroll = self.figure.canvas.mpl_connect("scroll_event", self.on_scroll)
        self.cid_dblclick = self.figure.canvas.mpl_connect("button_release_event", self.on_double_click_release)

        self.last_click_time = None
        self.double_click_threshold = 0.3  # seconds for double click

        # Enable pan/zoom with mouse drag
        self.panning = False
        self.last_mouse_x = None
        self.cid_press = self.figure.canvas.mpl_connect('button_press_event', self.on_button_press)
        self.cid_release = self.figure.canvas.mpl_connect('button_release_event', self.on_button_release)
        self.cid_motion = self.figure.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)

    def init_chart(self):
        self.ax.clear()
        self.ax.set_title("Interactive Gantt Chart", fontsize=14, color='white', weight="bold")
        self.ax.set_facecolor("#2e2e2e")
        self.figure.patch.set_facecolor("#2e2e2e")
        self.ax.title.set_color("white")
        self.ax.tick_params(colors='white')
        self.ax.xaxis.label.set_color('white')
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
        colors = cm.get_cmap('viridis', num_processes)
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
                edgecolor="white",
                height=0.5,
                alpha=0.9,
            )[0]
            self.bars.append((bar, process))
            remaining_time = self.process_remaining_times[proc_name] - executed_time
            self.process_remaining_times[proc_name] = remaining_time
            self.ax.text(
                x=start + executed_time / 2,
                y=0,
                s=f"{proc_name}\nRem: {remaining_time}",
                ha="center",
                va="center",
                fontsize=10,
                weight="bold",
                color="white",
            )

        for time in sorted(time_points):
            self.ax.text(
                x=time,
                y=-0.6,
                s=str(time),
                ha="center",
                va="center",
                fontsize=9,
                color="white",
            )

        self.ax.set_xlim(0, max_finish_time + 1)
        self.ax.set_ylim(-1, 1)
        self.draw()

    def on_hover(self, event):
        if event.inaxes == self.ax:
            if event.xdata is not None:
                self.vertical_line.set_xdata(event.xdata)
                self.vertical_line.set_visible(True)
                self.time_annotation.xy = (event.xdata, -0.6)
                self.time_annotation.set_text(f"Time: {int(event.xdata)}")
                self.time_annotation.set_visible(True)

            hovered_bar = None
            for bar, process in self.bars:
                contains, _ = bar.contains(event)
                if contains:
                    hovered_bar = (bar, process)
                    break

            if hovered_bar:
                bar, process = hovered_bar
                proc_name = process["Process"]
                rem_time = self.process_remaining_times.get(proc_name, 0)
                executed_time = process['Finish'] - process['Start']
                tooltip_text = (
                    f"Process: {proc_name}\n"
                    f"Start Time: {process['Start']}\n"
                    f"Finish Time: {process['Finish']}\n"
                    f"Executed: {executed_time}\n"
                    f"Remaining Time: {rem_time}"
                )
                self.hover_annotation.xy = (event.xdata, event.ydata)
                self.hover_annotation.set_text(tooltip_text)
                self.hover_annotation.set_visible(True)

                if self.active_bar is not bar:
                    if self.active_bar:
                        self.reset_bar_style(self.active_bar)
                    self.highlight_bar(bar)
                    self.active_bar = bar
                self.draw_idle()
            else:
                if self.active_bar and self.active_bar != self.selected_bar:
                    self.reset_bar_style(self.active_bar)
                    self.active_bar = None
                self.hover_annotation.set_visible(False)
                self.draw_idle()
        else:
            self.vertical_line.set_visible(False)
            self.time_annotation.set_visible(False)
            self.hover_annotation.set_visible(False)
            if self.active_bar and self.active_bar != self.selected_bar:
                self.reset_bar_style(self.active_bar)
                self.active_bar = None
            self.draw_idle()

    def on_leave(self, event):
        self.vertical_line.set_visible(False)
        self.time_annotation.set_visible(False)
        self.hover_annotation.set_visible(False)
        if self.active_bar and self.active_bar != self.selected_bar:
            self.reset_bar_style(self.active_bar)
        self.active_bar = None
        self.draw_idle()

    def on_click(self, event):
        if event.button == 3 and event.inaxes == self.ax:  # Right click
            # Check if clicked on a bar
            clicked_bar = None
            for bar, process in self.bars:
                contains, _ = bar.contains(event)
                if contains:
                    clicked_bar = (bar, process)
                    break
            if clicked_bar:
                self.show_context_menu(clicked_bar, event)
        
        # For double click, we track release event to measure time difference
        # Store the time of click
        import time
        self.last_click_time = time.time()

    def on_double_click_release(self, event):
        # Check if it's a double-click
        # if last_click_time is set and elapsed time < threshold
        if event.button == 1 and event.inaxes == self.ax:
            import time
            if self.last_click_time is not None and (time.time() - self.last_click_time) < self.double_click_threshold:
                # Double click detected
                # Check if clicked on a bar
                clicked_bar = None
                for bar, process in self.bars:
                    contains, _ = bar.contains(event)
                    if contains:
                        clicked_bar = (bar, process)
                        break
                if clicked_bar:
                    self.select_bar(clicked_bar[0])
                    self.draw_idle()

    def on_scroll(self, event):
        # Zoom in/out based on scroll
        base_scale = 1.1
        cur_xlim = self.ax.get_xlim()
        xdata = event.xdata
        if xdata is None:
            xdata = (cur_xlim[0] + cur_xlim[1]) / 2

        if event.step > 0:
            scale_factor = 1 / base_scale
        else:
            scale_factor = base_scale

        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
        self.ax.set_xlim([xdata - (1 - relx) * new_width, xdata + relx * new_width])
        self.draw_idle()

    def on_button_press(self, event):
        if event.button == 2 and event.inaxes == self.ax:  # Middle button drag to pan
            self.panning = True
            self.last_mouse_x = event.xdata

    def on_button_release(self, event):
        if event.button == 2:
            self.panning = False
            self.last_mouse_x = None

    def on_mouse_move(self, event):
        if self.panning and event.inaxes == self.ax and self.last_mouse_x is not None and event.xdata is not None:
            dx = event.xdata - self.last_mouse_x
            cur_xlim = self.ax.get_xlim()
            self.ax.set_xlim(cur_xlim[0] - dx, cur_xlim[1] - dx)
            self.last_mouse_x = event.xdata
            self.draw_idle()

    def show_context_menu(self, bar_process, event):
        # Show a context menu with additional options
        menu = QMenu()
        process = bar_process[1]
        proc_name = process["Process"]
        
        info_action = menu.addAction(f"Show info for {proc_name}")
        selected_action = menu.exec_(self.figure.canvas.mapToGlobal(self.figure.canvas.get_tk_widget().mapFromGlobal(self.figure.canvas.cursor().pos())))
        if selected_action == info_action:
            # Just show a simple message in the tooltip or print
            self.hover_annotation.set_text(f"{proc_name}:\nArrival: {process['Start']}\nFinish: {process['Finish']}")
            self.hover_annotation.set_visible(True)
            self.draw_idle()

    def highlight_bar(self, bar):
        bar.set_alpha(1.0)
        bar.set_edgecolor("#FFD700")
        bar.set_linewidth(2)

    def reset_bar_style(self, bar):
        bar.set_alpha(0.9)
        bar.set_edgecolor("white")
        bar.set_linewidth(1)

    def select_bar(self, bar):
        # If there's currently a selected bar, reset it
        if self.selected_bar and self.selected_bar != bar:
            self.reset_bar_style(self.selected_bar)
        self.selected_bar = bar
        # Highlight the selected bar differently
        bar.set_alpha(1.0)
        bar.set_edgecolor("#00FF00")
        bar.set_linewidth(3)
