import random
from collections import deque

class Scheduler:
    def __init__(self, processes, algorithm, quantum=None):
        self.processes = processes
        self.algorithm = algorithm
        self.quantum = quantum

    def run(self):
        algorithms = {
            "FCFS": self.fcfs,
            "SRTF": self.srtf,
            "Priority": self.priority,
            "Round Robin": self.round_robin,
        }
        schedule, _ = algorithms[self.algorithm]()
        waiting_times, turnaround_times, avg_waiting_time, avg_turnaround_time = (
            self.calculate_metrics(schedule)
        )
        return schedule, avg_waiting_time, avg_turnaround_time

    def calculate_metrics(self, schedule):
        arrival_times = {p["Process"]: p["Arrival Time"] for p in self.processes}
        burst_times = {p["Process"]: p["Burst Time"] for p in self.processes}
        finish_times = {}
        for entry in schedule:
            finish_times[entry["Process"]] = entry["Finish"]
        turnaround_times = {p: finish_times[p] - arrival_times[p] for p in finish_times}
        waiting_times = {
            p: turnaround_times[p] - burst_times[p] for p in turnaround_times
        }
        avg_waiting_time = (
            sum(waiting_times.values()) / len(waiting_times) if waiting_times else 0
        )
        avg_turnaround_time = (
            sum(turnaround_times.values()) / len(turnaround_times)
            if turnaround_times
            else 0
        )
        return waiting_times, turnaround_times, avg_waiting_time, avg_turnaround_time

    def fcfs(self):
        schedule = []
        start_time = 0
        for process in sorted(self.processes, key=lambda x: x["Arrival Time"]):
            start_time = max(start_time, process["Arrival Time"])
            finish_time = start_time + process["Burst Time"]
            schedule.append(
                {
                    "Process": process["Process"],
                    "Start": start_time,
                    "Finish": finish_time,
                }
            )
            start_time = finish_time
        return schedule, None

    def srtf(self):
        schedule = []
        current_time = 0
        processes = [dict(p, remaining=p["Burst Time"]) for p in self.processes]
        processes = sorted(processes, key=lambda x: x["Arrival Time"])
        executed_process = None
        start_time = None

        while processes:
            available = [p for p in processes if p["Arrival Time"] <= current_time]
            if not available:
                current_time += 1
                continue
            current_process = min(available, key=lambda x: x["remaining"])
            if executed_process != current_process:
                if executed_process and executed_process["remaining"] > 0:
                    schedule.append(
                        {
                            "Process": executed_process["Process"],
                            "Start": start_time,
                            "Finish": current_time,
                        }
                    )
                executed_process = current_process
                start_time = current_time
            current_process["remaining"] -= 1
            current_time += 1
            if current_process["remaining"] == 0:
                schedule.append(
                    {
                        "Process": current_process["Process"],
                        "Start": start_time,
                        "Finish": current_time,
                    }
                )
                processes.remove(current_process)
                executed_process = None
        return schedule, None

    def round_robin(self):
        schedule = []
        current_time = 0
        processes = [dict(p, remaining=p["Burst Time"]) for p in self.processes]
        processes = sorted(processes, key=lambda x: x["Arrival Time"])
        queue = deque()
        while processes or queue:
            while processes and processes[0]["Arrival Time"] <= current_time:
                queue.append(processes.pop(0))
            if not queue:
                if processes:
                    current_time = processes[0]["Arrival Time"]
                else:
                    break
                continue
            current_process = queue.popleft()
            start_time = current_time
            execution_time = min(self.quantum, current_process["remaining"])
            current_time += execution_time
            current_process["remaining"] -= execution_time
            schedule.append(
                {
                    "Process": current_process["Process"],
                    "Start": start_time,
                    "Finish": current_time,
                }
            )
            while processes and processes[0]["Arrival Time"] <= current_time:
                queue.append(processes.pop(0))
            if current_process["remaining"] > 0:
                queue.append(current_process)
        return schedule, None

    def priority(self):
        schedule = []
        current_time = 0
        processes = [dict(p) for p in self.processes]
        processes = sorted(processes, key=lambda x: x["Arrival Time"])
        while processes:
            available = [p for p in processes if p["Arrival Time"] <= current_time]
            if not available:
                current_time += 1
                continue
            current_process = min(available, key=lambda x: x["Priority"])
            start = (
                current_time
                if current_time >= current_process["Arrival Time"]
                else current_process["Arrival Time"]
            )
            finish = start + current_process["Burst Time"]
            schedule.append(
                {
                    "Process": current_process["Process"],
                    "Start": start,
                    "Finish": finish,
                }
            )
            current_time = finish
            processes.remove(current_process)
        return schedule, None
