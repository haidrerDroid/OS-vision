"""Non-preemptive shortest-job-first CPU scheduling."""

from __future__ import annotations

from algorithms.scheduling import (
    ExecutionInterval,
    ProcessInput,
    ScheduleResult,
    build_schedule_result,
    coerce_processes,
)


def schedule_sjf(processes: ProcessInput) -> ScheduleResult:
    """Choose the shortest available burst; ties use arrival then input order."""

    normalized = coerce_processes(processes)
    input_order = {process.process_id: index for index, process in enumerate(normalized)}
    pending = set(input_order)
    by_id = {process.process_id: process for process in normalized}
    intervals: list[ExecutionInterval] = []
    current_time = 0

    while pending:
        available = [
            by_id[process_id]
            for process_id in pending
            if by_id[process_id].arrival_time <= current_time
        ]
        if not available:
            next_arrival = min(by_id[process_id].arrival_time for process_id in pending)
            intervals.append(ExecutionInterval(current_time, next_arrival, None))
            current_time = next_arrival
            available = [
                by_id[process_id]
                for process_id in pending
                if by_id[process_id].arrival_time <= current_time
            ]
        selected = min(
            available,
            key=lambda process: (
                process.burst_time,
                process.arrival_time,
                input_order[process.process_id],
            ),
        )
        completion = current_time + selected.burst_time
        intervals.append(ExecutionInterval(current_time, completion, selected.process_id))
        current_time = completion
        pending.remove(selected.process_id)

    return build_schedule_result(normalized, intervals)
