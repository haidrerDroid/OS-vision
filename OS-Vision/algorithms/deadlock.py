"""Resource-instance-aware deadlock detection and operations."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence


@dataclass(frozen=True)
class ResourceState:
    """Total instances, allocated instances, and outstanding requests."""

    total: tuple[int, ...]
    allocation: tuple[tuple[int, ...], ...]
    request: tuple[tuple[int, ...], ...]

    @property
    def resource_count(self) -> int:
        return len(self.total)

    @property
    def process_count(self) -> int:
        return len(self.allocation)

    @property
    def available(self) -> tuple[int, ...]:
        return tuple(
            total - sum(row[resource] for row in self.allocation)
            for resource, total in enumerate(self.total)
        )


@dataclass(frozen=True)
class DetectionStep:
    process_index: int
    work_before: tuple[int, ...]
    released_allocation: tuple[int, ...]
    work_after: tuple[int, ...]


@dataclass(frozen=True)
class DeadlockResult:
    is_deadlocked: bool
    completed_processes: tuple[int, ...]
    deadlocked_processes: tuple[int, ...]
    steps: tuple[DetectionStep, ...]
    final_work: tuple[int, ...]


def _integer(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a non-negative integer.")
    if isinstance(value, float) and (not isfinite(value) or not value.is_integer()):
        raise ValueError(f"{label} must be a finite non-negative integer.")
    integer = int(value)
    if integer < 0:
        raise ValueError(f"{label} must be a non-negative integer.")
    return integer


def _vector(values: Sequence[object], label: str) -> tuple[int, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence) or not values:
        raise ValueError(f"{label} must contain at least one resource.")
    return tuple(_integer(value, f"{label}[{index}]") for index, value in enumerate(values))


def _matrix(
    values: Sequence[Sequence[object]], label: str, resource_count: int
) -> tuple[tuple[int, ...], ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence) or not values:
        raise ValueError(f"{label} must contain at least one process.")
    matrix = tuple(
        _vector(row, f"{label} process {process}")
        for process, row in enumerate(values)
    )
    if any(len(row) != resource_count for row in matrix):
        raise ValueError(f"Every {label} row must have {resource_count} resource values.")
    return matrix


def create_state(
    total: Sequence[object],
    allocation: Sequence[Sequence[object]],
    request: Sequence[Sequence[object]],
) -> ResourceState:
    """Validate resource instances, allocations, and current outstanding requests."""

    normalized_total = _vector(total, "Total")
    normalized_allocation = _matrix(allocation, "Allocation", len(normalized_total))
    normalized_request = _matrix(request, "Request", len(normalized_total))
    if len(normalized_allocation) != len(normalized_request):
        raise ValueError("Allocation and Request must have the same number of processes.")
    for resource, total_instances in enumerate(normalized_total):
        allocated = sum(row[resource] for row in normalized_allocation)
        if allocated > total_instances:
            raise ValueError(
                f"Allocated instances for resource {resource} ({allocated}) exceed "
                f"its total instances ({total_instances})."
            )
        for process, (allocation_row, request_row) in enumerate(
            zip(normalized_allocation, normalized_request)
        ):
            if allocation_row[resource] + request_row[resource] > total_instances:
                raise ValueError(
                    f"P{process}'s allocation plus outstanding request for resource "
                    f"{resource} exceeds the total instances ({total_instances})."
                )
    return ResourceState(normalized_total, normalized_allocation, normalized_request)


def detect_deadlock(state: ResourceState) -> DeadlockResult:
    """Apply the multi-instance deadlock-detection Work/Finish algorithm."""

    work = list(state.available)
    finished = [
        not any(allocation_row)
        for allocation_row in state.allocation
    ]
    steps: list[DetectionStep] = []
    completed: list[int] = [
        index for index, is_finished in enumerate(finished) if is_finished
    ]
    while True:
        process = next(
            (
                index
                for index, is_finished in enumerate(finished)
                if not is_finished
                and all(
                    outstanding <= available
                    for outstanding, available in zip(state.request[index], work)
                )
            ),
            None,
        )
        if process is None:
            break
        before = tuple(work)
        released = state.allocation[process]
        work = [available + allocated for available, allocated in zip(work, released)]
        finished[process] = True
        completed.append(process)
        steps.append(
            DetectionStep(
                process_index=process,
                work_before=before,
                released_allocation=released,
                work_after=tuple(work),
            )
        )

    deadlocked = tuple(index for index, is_finished in enumerate(finished) if not is_finished)
    return DeadlockResult(
        is_deadlocked=bool(deadlocked),
        completed_processes=tuple(completed),
        deadlocked_processes=deadlocked,
        steps=tuple(steps),
        final_work=tuple(work),
    )


def has_resource_allocation_cycle(state: ResourceState) -> bool:
    """Report whether the resource-type RAG contains a directed cycle."""

    graph: dict[str, list[str]] = {
        **{f"P{index}": [] for index in range(state.process_count)},
        **{f"R{index}": [] for index in range(state.resource_count)},
    }
    for process, (allocation_row, request_row) in enumerate(
        zip(state.allocation, state.request)
    ):
        for resource, allocated in enumerate(allocation_row):
            if allocated:
                graph[f"R{resource}"].append(f"P{process}")
        for resource, requested in enumerate(request_row):
            if requested:
                graph[f"P{process}"].append(f"R{resource}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        for neighbor in graph[node]:
            if visit(neighbor):
                return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in graph)


def queue_request(
    state: ResourceState, process_index: int, resource_index: int, units: int
) -> ResourceState:
    """Record a valid outstanding request without allocating unavailable units."""

    process_index, resource_index, units = _validate_operation(
        state, process_index, resource_index, units
    )
    request = [list(row) for row in state.request]
    requested = request[process_index][resource_index] + units
    maximum_outstanding = (
        state.total[resource_index] - state.allocation[process_index][resource_index]
    )
    if requested > maximum_outstanding:
        raise ValueError(
            f"P{process_index}'s allocation plus outstanding request would exceed "
            f"the {state.total[resource_index]} instances of resource {resource_index}."
        )
    request[process_index][resource_index] = requested
    return create_state(state.total, state.allocation, request)


def grant_request(
    state: ResourceState, process_index: int, resource_index: int, units: int
) -> ResourceState:
    """Grant units from an existing request only when those units are available."""

    process_index, resource_index, units = _validate_operation(
        state, process_index, resource_index, units
    )
    pending = state.request[process_index][resource_index]
    if units > pending:
        raise ValueError(
            f"P{process_index} has only {pending} outstanding units requested "
            f"for resource {resource_index}."
        )
    available = state.available[resource_index]
    if units > available:
        raise ValueError(
            f"Cannot grant {units} units of resource {resource_index}; only "
            f"{available} are available."
        )
    allocation = [list(row) for row in state.allocation]
    request = [list(row) for row in state.request]
    allocation[process_index][resource_index] += units
    request[process_index][resource_index] -= units
    return create_state(state.total, allocation, request)


def release_resources(
    state: ResourceState, process_index: int, resource_index: int, units: int
) -> ResourceState:
    """Release allocated instances back to the available pool."""

    process_index, resource_index, units = _validate_operation(
        state, process_index, resource_index, units
    )
    allocated = state.allocation[process_index][resource_index]
    if units > allocated:
        raise ValueError(
            f"P{process_index} holds only {allocated} units of resource {resource_index}."
        )
    allocation = [list(row) for row in state.allocation]
    allocation[process_index][resource_index] -= units
    return create_state(state.total, allocation, state.request)


def _validate_operation(
    state: ResourceState, process_index: int, resource_index: int, units: int
) -> tuple[int, int, int]:
    process_index = _integer(process_index, "Process index")
    resource_index = _integer(resource_index, "Resource index")
    units = _integer(units, "Units")
    if process_index >= state.process_count:
        raise ValueError(f"Process index must be between 0 and {state.process_count - 1}.")
    if resource_index >= state.resource_count:
        raise ValueError(f"Resource index must be between 0 and {state.resource_count - 1}.")
    if units == 0:
        raise ValueError("An operation must affect at least one resource unit.")
    return process_index, resource_index, units
