"""First Come, First Served CPU scheduling."""

from __future__ import annotations

from algorithms.scheduling import (
    ExecutionInterval,
    Process,
    ProcessInput,
    ProcessMetrics,
    ScheduleResult,
    build_schedule_result,
    coerce_processes,
)


def schedule_fcfs(processes: ProcessInput) -> ScheduleResult:
    """Schedule by arrival time, preserving input order for simultaneous arrivals."""

    ordered = sorted(
        enumerate(coerce_processes(processes)),
        key=lambda entry: (entry[1].arrival_time, entry[0]),
    )
    intervals: list[ExecutionInterval] = []
    current_time = 0
    for _, process in ordered:
        if current_time < process.arrival_time:
            intervals.append(ExecutionInterval(current_time, process.arrival_time, None))
            current_time = process.arrival_time
        completion = current_time + process.burst_time
        intervals.append(ExecutionInterval(current_time, completion, process.process_id))
        current_time = completion
    return build_schedule_result([process for _, process in ordered], intervals)
