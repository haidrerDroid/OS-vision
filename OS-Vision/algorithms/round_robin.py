"""Round Robin CPU scheduling."""

from __future__ import annotations

from collections import deque

from algorithms.scheduling import (
    ExecutionInterval,
    ProcessInput,
    ScheduleResult,
    build_schedule_result,
    coerce_processes,
    validate_time,
)


def schedule_round_robin(processes: ProcessInput, quantum: int) -> ScheduleResult:
    """Schedule FIFO time slices; arrivals at a slice boundary join before requeue."""

    normalized = coerce_processes(processes)
    quantum = validate_time(quantum, "time quantum", 0)
    if quantum <= 0:
        raise ValueError("Time quantum must be greater than zero.")

    ordered = [
        process
        for _, process in sorted(
            enumerate(normalized), key=lambda entry: (entry[1].arrival_time, entry[0])
        )
    ]
    remaining = {process.process_id: process.burst_time for process in normalized}
    intervals: list[ExecutionInterval] = []
    ready: deque[str] = deque()
    next_process = 0
    current_time = 0

    while next_process < len(ordered) or ready:
        while next_process < len(ordered) and ordered[next_process].arrival_time <= current_time:
            ready.append(ordered[next_process].process_id)
            next_process += 1
        if not ready:
            next_arrival = ordered[next_process].arrival_time
            intervals.append(ExecutionInterval(current_time, next_arrival, None))
            current_time = next_arrival
            continue

        process_id = ready.popleft()
        run_for = min(quantum, remaining[process_id])
        finish = current_time + run_for
        intervals.append(ExecutionInterval(current_time, finish, process_id))
        remaining[process_id] -= run_for
        current_time = finish

        while next_process < len(ordered) and ordered[next_process].arrival_time <= current_time:
            ready.append(ordered[next_process].process_id)
            next_process += 1
        if remaining[process_id] > 0:
            ready.append(process_id)

    return build_schedule_result(normalized, intervals)
