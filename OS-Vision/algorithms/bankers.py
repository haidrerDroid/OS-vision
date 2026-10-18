"""Banker's algorithm safety checks and resource-request simulation."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence


@dataclass(frozen=True)
class BankerState:
    """Current resource state for a fixed set of processes and resource types."""

    available: tuple[int, ...]
    allocation: tuple[tuple[int, ...], ...]
    maximum: tuple[tuple[int, ...], ...]

    @property
    def need(self) -> tuple[tuple[int, ...], ...]:
        return tuple(
            tuple(maximum - allocated for maximum, allocated in zip(max_row, allocation_row))
            for allocation_row, max_row in zip(self.allocation, self.maximum)
        )

    @property
    def process_count(self) -> int:
        return len(self.allocation)

    @property
    def resource_count(self) -> int:
        return len(self.available)


@dataclass(frozen=True)
class SafetyStep:
    """One successful process completion considered during a safety check."""

    process_index: int
    work_before: tuple[int, ...]
    released_allocation: tuple[int, ...]
    work_after: tuple[int, ...]


@dataclass(frozen=True)
class SafetyResult:
    """Safe-state result and the work-vector trace used to derive it."""

    is_safe: bool
    safe_sequence: tuple[int, ...]
    steps: tuple[SafetyStep, ...]
    unfinished_processes: tuple[int, ...]


@dataclass(frozen=True)
class ResourceRequestResult:
    """Outcome of hypothetically granting a process's resource request."""

    granted: bool
    reason: str
    resulting_state: BankerState | None
    safety: SafetyResult | None


def _integer(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a non-negative integer.")
    if isinstance(value, float) and (not isfinite(value) or not value.is_integer()):
        raise ValueError(f"{label} must be a finite non-negative integer.")
    converted = int(value)
    if converted < 0:
        raise ValueError(f"{label} must be a non-negative integer.")
    return converted


def _vector(values: Sequence[object], label: str) -> tuple[int, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence) or not values:
        raise ValueError(f"{label} must contain at least one resource value.")
    return tuple(_integer(value, f"{label}[{index}]") for index, value in enumerate(values))


def _matrix(
    values: Sequence[Sequence[object]], label: str, resource_count: int
) -> tuple[tuple[int, ...], ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence) or not values:
        raise ValueError(f"{label} must contain at least one process row.")
    matrix = tuple(
        _vector(row, f"{label} process {index}") for index, row in enumerate(values)
    )
    if any(len(row) != resource_count for row in matrix):
        raise ValueError(f"Every {label} row must have {resource_count} resource values.")
    return matrix


def create_state(
    available: Sequence[object],
    allocation: Sequence[Sequence[object]],
    maximum: Sequence[Sequence[object]],
) -> BankerState:
    """Validate Banker's algorithm input and derive the resource claim state."""

    normalized_available = _vector(available, "Available")
    normalized_allocation = _matrix(
        allocation, "Allocation", len(normalized_available)
    )
    normalized_maximum = _matrix(maximum, "Maximum", len(normalized_available))
    if len(normalized_allocation) != len(normalized_maximum):
        raise ValueError("Allocation and Maximum must contain the same number of processes.")
    total_resources = tuple(
        available + sum(row[resource_index] for row in normalized_allocation)
        for resource_index, available in enumerate(normalized_available)
    )
    for process_index, (allocation_row, maximum_row) in enumerate(
        zip(normalized_allocation, normalized_maximum)
    ):
        for resource_index, (allocated, claimed) in enumerate(
            zip(allocation_row, maximum_row)
        ):
            if allocated > claimed:
                raise ValueError(
                    f"Allocation for process {process_index}, resource {resource_index} "
                    "cannot exceed its maximum claim."
                )
            if claimed > total_resources[resource_index]:
                raise ValueError(
                    f"Maximum claim for process {process_index}, resource "
                    f"{resource_index} cannot exceed the total number of instances "
                    f"({total_resources[resource_index]})."
                )
    return BankerState(normalized_available, normalized_allocation, normalized_maximum)


def check_safety(state: BankerState) -> SafetyResult:
    """Run the safety algorithm and return its safe-sequence work trace."""

    work = list(state.available)
    finished = [False] * state.process_count
    steps: list[SafetyStep] = []
    sequence: list[int] = []

    while True:
        process_index = next(
            (
                index
                for index in range(state.process_count)
                if not finished[index]
                and all(
                    need <= available
                    for need, available in zip(state.need[index], work)
                )
            ),
            None,
        )
        if process_index is None:
            break

        work_before = tuple(work)
        released = state.allocation[process_index]
        work = [available + allocated for available, allocated in zip(work, released)]
        finished[process_index] = True
        sequence.append(process_index)
        steps.append(
            SafetyStep(
                process_index=process_index,
                work_before=work_before,
                released_allocation=released,
                work_after=tuple(work),
            )
        )

    unfinished = tuple(index for index, done in enumerate(finished) if not done)
    return SafetyResult(
        is_safe=not unfinished,
        safe_sequence=tuple(sequence),
        steps=tuple(steps),
        unfinished_processes=unfinished,
    )


def simulate_request(
    state: BankerState, process_index: int, request: Sequence[object]
) -> ResourceRequestResult:
    """Check a request against Need/Available and tentatively test the new state."""

    if isinstance(process_index, bool) or not isinstance(process_index, int):
        raise ValueError("Process index must be an integer.")
    if not 0 <= process_index < state.process_count:
        raise ValueError(f"Process index must be between 0 and {state.process_count - 1}.")
    normalized_request = _vector(request, "Request")
    if len(normalized_request) != state.resource_count:
        raise ValueError(f"Request must contain {state.resource_count} resource values.")

    for resource_index, (requested, needed) in enumerate(
        zip(normalized_request, state.need[process_index])
    ):
        if requested > needed:
            return ResourceRequestResult(
                granted=False,
                reason=(
                    f"Request exceeds P{process_index}'s remaining claim for resource "
                    f"{resource_index} ({requested} requested, {needed} needed)."
                ),
                resulting_state=None,
                safety=None,
            )
    for resource_index, (requested, available) in enumerate(
        zip(normalized_request, state.available)
    ):
        if requested > available:
            return ResourceRequestResult(
                granted=False,
                reason=(
                    f"Request exceeds currently available units for resource "
                    f"{resource_index} ({requested} requested, {available} available)."
                ),
                resulting_state=None,
                safety=None,
            )

    available_after = tuple(
        available - requested
        for available, requested in zip(state.available, normalized_request)
    )
    allocation_after = tuple(
        tuple(
            allocated + requested
            for allocated, requested in zip(row, normalized_request)
        )
        if index == process_index
        else row
        for index, row in enumerate(state.allocation)
    )
    tentative = BankerState(available_after, allocation_after, state.maximum)
    safety = check_safety(tentative)
    if not safety.is_safe:
        blocked = ", ".join(f"P{index}" for index in safety.unfinished_processes)
        return ResourceRequestResult(
            granted=False,
            reason=(
                f"Grant denied: it would leave the system unsafe. "
                f"These processes cannot finish from the remaining Work vector: {blocked}."
            ),
            resulting_state=tentative,
            safety=safety,
        )
    return ResourceRequestResult(
        granted=True,
        reason="Grant allowed: the tentative state is safe.",
        resulting_state=tentative,
        safety=safety,
    )
