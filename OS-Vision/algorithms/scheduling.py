"""Shared types and validation for CPU scheduling algorithms."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable, Mapping


@dataclass(frozen=True)
class Process:
    """A CPU-bound process with an arrival time and positive burst time."""

    process_id: str
    arrival_time: int
    burst_time: int


@dataclass(frozen=True)
class ExecutionInterval:
    """A half-open CPU interval; a missing process ID means the CPU is idle."""

    start: int
    finish: int
    process_id: str | None


@dataclass(frozen=True)
class ProcessMetrics:
    """Calculated scheduling metrics for one completed process."""

    process_id: str
    arrival_time: int
    burst_time: int
    start_time: int
    completion_time: int
    turnaround_time: int
    waiting_time: int
    response_time: int


@dataclass(frozen=True)
class ScheduleResult:
    """Timeline, per-process metrics, and aggregate CPU performance metrics."""

    intervals: tuple[ExecutionInterval, ...]
    processes: tuple[ProcessMetrics, ...]
    average_waiting_time: float
    average_turnaround_time: float
    average_response_time: float
    cpu_utilization: float
    throughput: float
    makespan: int


ProcessInput = Iterable[Process | Mapping[str, object]]


def coerce_processes(processes: ProcessInput) -> list[Process]:
    """Validate process records and preserve their input order."""

    normalized: list[Process] = []
    seen_ids: set[str] = set()
    for index, item in enumerate(processes):
        if isinstance(item, Process):
            process_id, arrival, burst = item.process_id, item.arrival_time, item.burst_time
        elif isinstance(item, Mapping):
            try:
                process_id = item["process_id"]
                arrival = item["arrival_time"]
                burst = item["burst_time"]
            except KeyError as exc:
                raise ValueError(
                    f"Process row {index + 1} is missing {exc.args[0]!r}."
                ) from exc
        else:
            raise ValueError(f"Process row {index + 1} must be a Process or mapping.")

        if not isinstance(process_id, str) or not process_id.strip():
            raise ValueError(f"Process row {index + 1} must have a non-empty process ID.")
        process_id = process_id.strip()
        if process_id in seen_ids:
            raise ValueError(f"Duplicate process ID: {process_id!r}.")
        seen_ids.add(process_id)

        arrival_time = validate_time(arrival, "arrival time", index)
        burst_time = validate_time(burst, "burst time", index)
        if arrival_time < 0:
            raise ValueError(f"Arrival time for {process_id!r} cannot be negative.")
        if burst_time <= 0:
            raise ValueError(f"Burst time for {process_id!r} must be greater than zero.")
        normalized.append(Process(process_id, arrival_time, burst_time))

    if not normalized:
        raise ValueError("At least one process is required.")
    return normalized


def validate_time(value: object, label: str, index: int) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label.capitalize()} in process row {index + 1} must be an integer.")
    if isinstance(value, float) and (not isfinite(value) or not value.is_integer()):
        raise ValueError(
            f"{label.capitalize()} in process row {index + 1} must be a finite integer."
        )
    return int(value)


def build_schedule_result(
    processes: list[Process], intervals: list[ExecutionInterval]
) -> ScheduleResult:
    """Calculate per-process and aggregate metrics from a completed timeline."""

    first_start: dict[str, int] = {}
    completion: dict[str, int] = {}
    for interval in intervals:
        if interval.process_id is not None:
            first_start.setdefault(interval.process_id, interval.start)
            completion[interval.process_id] = interval.finish
    if len(completion) != len(processes):
        raise ValueError("The execution timeline does not complete every process.")

    metrics = []
    for process in processes:
        completion_time = completion[process.process_id]
        turnaround_time = completion_time - process.arrival_time
        start_time = first_start[process.process_id]
        metrics.append(
            ProcessMetrics(
                process_id=process.process_id,
                arrival_time=process.arrival_time,
                burst_time=process.burst_time,
                start_time=start_time,
                completion_time=completion_time,
                turnaround_time=turnaround_time,
                waiting_time=turnaround_time - process.burst_time,
                response_time=start_time - process.arrival_time,
            )
        )

    makespan = intervals[-1].finish if intervals else 0
    count = len(metrics)
    total_burst = sum(process.burst_time for process in processes)
    return ScheduleResult(
        intervals=tuple(intervals),
        processes=tuple(metrics),
        average_waiting_time=sum(item.waiting_time for item in metrics) / count,
        average_turnaround_time=sum(item.turnaround_time for item in metrics) / count,
        average_response_time=sum(item.response_time for item in metrics) / count,
        cpu_utilization=total_burst / makespan if makespan else 0.0,
        throughput=count / makespan if makespan else 0.0,
        makespan=makespan,
    )
