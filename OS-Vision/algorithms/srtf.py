"""Preemptive shortest-remaining-time-first CPU scheduling."""

from __future__ import annotations

from algorithms.scheduling import (
    ExecutionInterval,
    ProcessInput,
    ScheduleResult,
    build_schedule_result,
    coerce_processes,
)


def schedule_srtf(processes: ProcessInput) -> ScheduleResult:
    """Preempt on arrivals; ties use remaining time, arrival, then input order."""

    normalized = coerce_processes(processes)
    input_order = {process.process_id: index for index, process in enumerate(normalized)}
    remaining = {process.process_id: process.burst_time for process in normalized}
    completed: set[str] = set()
    intervals: list[ExecutionInterval] = []
    current_time = 0

    while len(completed) < len(normalized):
        available = [
            process
            for process in normalized
            if process.process_id not in completed
            and remaining[process.process_id] > 0
            and process.arrival_time <= current_time
        ]
        if not available:
            next_arrival = min(
                process.arrival_time
                for process in normalized
                if process.process_id not in completed
            )
            intervals.append(ExecutionInterval(current_time, next_arrival, None))
            current_time = next_arrival
            continue

        selected = min(
            available,
            key=lambda process: (
                remaining[process.process_id],
                process.arrival_time,
                input_order[process.process_id],
            ),
        )
        next_arrival = min(
            (
                process.arrival_time
                for process in normalized
                if process.process_id not in completed
                and process.arrival_time > current_time
            ),
            default=None,
        )
        run_for = remaining[selected.process_id]
        if next_arrival is not None:
            run_for = min(run_for, next_arrival - current_time)
        finish = current_time + run_for
        if intervals and intervals[-1].process_id == selected.process_id:
            previous = intervals[-1]
            intervals[-1] = ExecutionInterval(previous.start, finish, selected.process_id)
        else:
            intervals.append(ExecutionInterval(current_time, finish, selected.process_id))
        remaining[selected.process_id] -= run_for
        current_time = finish
        if remaining[selected.process_id] == 0:
            completed.add(selected.process_id)

    return build_schedule_result(normalized, intervals)
