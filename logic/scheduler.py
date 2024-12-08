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
            "SJF": self.sjf,
            "SRTF": self.srtf,
            "Priority": self.priority,
            "Round Robin": self.round_robin,
        }
        schedule, _ = algorithms[self.algorithm]()
        avg_waiting_time = self.calculate_waiting_time(schedule)
        return schedule, avg_waiting_time

    def calculate_waiting_time(self, schedule):
        waiting_times = {}
        last_finish_times = {}
        process_arrival_times = {p["Process"]: p["Arrival Time"] for p in self.processes}

        for process in self.processes:
            waiting_times[process["Process"]] = 0
            last_finish_times[process["Process"]] = process_arrival_times[process["Process"]]

        for entry in schedule:
            proc = entry["Process"]
            arrival = process_arrival_times[proc]
            start = entry["Start"]
            finish = entry["Finish"]

            # Waiting time is increased by the time between last finish and next start
            waiting_times[proc] += max(0, start - last_finish_times[proc])

            # Update last finish time for the process
            last_finish_times[proc] = finish

        total_waiting_time = sum(waiting_times.values())
        avg_waiting_time = total_waiting_time / len(waiting_times) if waiting_times else 0
        return avg_waiting_time

    def fcfs(self):
        start_time = 0
        schedule = []
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

    def sjf(self):
        schedule = []
        current_time = 0
        remaining_processes = sorted(
            self.processes, key=lambda x: (x["Burst Time"], x["Arrival Time"])
        )

        while remaining_processes:
            available = [
                p for p in remaining_processes if p["Arrival Time"] <= current_time
            ]
            if not available:
                current_time += 1
                continue

            process = min(available, key=lambda x: x["Burst Time"])
            remaining_processes.remove(process)
            schedule.append(
                {
                    "Process": process["Process"],
                    "Start": current_time,
                    "Finish": current_time + process["Burst Time"],
                }
            )
            current_time += process["Burst Time"]

        return schedule, None

    def srtf(self):
        schedule = []
        current_time = 0
        processes = [dict(p, remaining=p["Burst Time"]) for p in self.processes]
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
                    schedule.append({
                        "Process": executed_process["Process"],
                        "Start": start_time,
                        "Finish": current_time,
                    })
                executed_process = current_process
                start_time = current_time

            current_process["remaining"] -= 1
            current_time += 1

            if current_process["remaining"] == 0:
                schedule.append({
                    "Process": current_process["Process"],
                    "Start": start_time,
                    "Finish": current_time,
                })
                processes.remove(current_process)
                executed_process = None

        return schedule, None

    def round_robin(self):
        schedule = []
        current_time = 0
        queue = deque()
        processes = sorted(
            [dict(p, remaining=p["Burst Time"]) for p in self.processes],
            key=lambda x: x["Arrival Time"]
        )

        while processes or queue:
            # Add newly arrived processes to queue
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

            schedule.append({
                "Process": current_process["Process"],
                "Start": start_time,
                "Finish": current_time,
            })

            # Add any new arrivals during execution
            while processes and processes[0]["Arrival Time"] <= current_time:
                queue.append(processes.pop(0))

            if current_process["remaining"] > 0:
                queue.append(current_process)

        return schedule, None

    def priority(self):
        schedule = []
        current_time = 0
        processes = [dict(p) for p in self.processes]

        while processes:
            available = [p for p in processes if p["Arrival Time"] <= current_time]
            if not available:
                current_time += 1
                continue

            # Lower priority number means higher priority
            current_process = min(available, key=lambda x: x["Priority"])

            start_time = current_time
            finish_time = current_time + current_process["Burst Time"]
            schedule.append({
                "Process": current_process["Process"],
                "Start": start_time,
                "Finish": finish_time,
            })
            current_time = finish_time
            processes.remove(current_process)

        return schedule, None
