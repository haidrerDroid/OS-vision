"""Playback helpers for inspecting a completed CPU schedule over time."""

from __future__ import annotations

from algorithms.fcfs import ScheduleResult


def process_states_at(result: ScheduleResult, current_time: float) -> list[dict[str, object]]:
    """Return each process's state at a point on the CPU timeline."""

    states: list[dict[str, object]] = []
    for process in result.processes:
        if current_time >= process.completion_time:
            state = "Complete"
        elif any(
            interval.process_id == process.process_id
            and interval.start <= current_time < interval.finish
            for interval in result.intervals
        ):
            state = "Running"
        elif current_time >= process.arrival_time:
            state = "Waiting"
        else:
            state = "Not arrived"
        states.append({"Process": process.process_id, "State": state})
    return states


def next_schedule_boundary(result: ScheduleResult, current_time: float) -> float:
    """Return the next process/CPU transition time, or the schedule's finish."""

    boundaries = {process.arrival_time for process in result.processes}
    boundaries.update(
        boundary
        for interval in result.intervals
        for boundary in (interval.start, interval.finish)
    )
    next_boundary = min(
        (boundary for boundary in boundaries if boundary > current_time + 1e-9),
        default=result.makespan,
    )
    return float(next_boundary)
