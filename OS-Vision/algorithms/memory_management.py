"""Page-replacement simulation and virtual-address translation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from math import isfinite
from typing import Literal, Sequence


ReplacementPolicy = Literal["FIFO", "LRU", "Optimal"]


@dataclass(frozen=True)
class ReplacementStep:
    """Frame contents and outcome after one page reference."""

    reference_index: int
    page: int
    frames: tuple[int | None, ...]
    is_page_fault: bool
    replaced_page: int | None
    frame_index: int | None


@dataclass(frozen=True)
class ReplacementResult:
    """Complete page-reference trace and aggregate replacement metrics."""

    policy: ReplacementPolicy
    frame_count: int
    references: tuple[int, ...]
    steps: tuple[ReplacementStep, ...]
    page_faults: int
    hits: int

    @property
    def fault_rate(self) -> float:
        return self.page_faults / len(self.references)

    @property
    def hit_rate(self) -> float:
        return self.hits / len(self.references)


@dataclass(frozen=True)
class AddressTranslation:
    """Virtual-to-physical address mapping at a specific page-table snapshot."""

    virtual_address: int
    page_number: int
    offset: int
    frame_number: int | None
    physical_address: int | None

    @property
    def is_page_fault(self) -> bool:
        return self.frame_number is None


def parse_reference_string(value: str) -> tuple[int, ...]:
    """Parse comma- or whitespace-separated non-negative page numbers."""

    if not isinstance(value, str):
        raise ValueError("Page references must be entered as text.")
    tokens = [token for token in re.split(r"[\s,]+", value.strip()) if token]
    if not tokens:
        raise ValueError("Enter at least one page reference.")
    references: list[int] = []
    for index, token in enumerate(tokens, start=1):
        if not token.isdecimal():
            raise ValueError(f"Page reference {index} must be a non-negative integer.")
        references.append(int(token))
    return tuple(references)


def _non_negative_integer(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a non-negative integer.")
    if isinstance(value, float) and (not isfinite(value) or not value.is_integer()):
        raise ValueError(f"{label} must be a finite non-negative integer.")
    integer = int(value)
    if integer < 0:
        raise ValueError(f"{label} must be a non-negative integer.")
    return integer


def simulate_page_replacement(
    references: Sequence[object],
    frame_count: int,
    policy: ReplacementPolicy,
) -> ReplacementResult:
    """Run FIFO, LRU, or Optimal over an actual page-reference sequence."""

    if isinstance(frame_count, bool) or not isinstance(frame_count, int) or frame_count <= 0:
        raise ValueError("Frame count must be a positive integer.")
    if policy not in ("FIFO", "LRU", "Optimal"):
        raise ValueError(f"Unsupported page-replacement policy: {policy!r}.")
    if isinstance(references, (str, bytes)) or not isinstance(references, Sequence):
        raise ValueError("Page references must be a sequence of non-negative integers.")
    if not references:
        raise ValueError("At least one page reference is required.")

    pages = tuple(
        _non_negative_integer(page, f"Page reference {index}")
        for index, page in enumerate(references, start=1)
    )
    frames: list[int | None] = [None] * frame_count
    fifo_order: list[int] = []
    last_used: dict[int, int] = {}
    steps: list[ReplacementStep] = []
    faults = 0

    for reference_index, page in enumerate(pages):
        if page in frames:
            last_used[page] = reference_index
            steps.append(
                ReplacementStep(
                    reference_index, page, tuple(frames), False, None, None
                )
            )
            continue

        faults += 1
        empty_frame = next(
            (index for index, resident in enumerate(frames) if resident is None),
            None,
        )
        replaced_page = None
        if empty_frame is not None:
            frame_index = empty_frame
        elif policy == "FIFO":
            frame_index = fifo_order.pop(0)
            replaced_page = frames[frame_index]
        elif policy == "LRU":
            def last_use_for_frame(index: int) -> int:
                resident = frames[index]
                assert resident is not None
                return last_used[resident]

            frame_index = min(
                range(frame_count),
                key=last_use_for_frame,
            )
            replaced_page = frames[frame_index]
        else:
            def next_use(frame_index: int) -> int:
                resident = frames[frame_index]
                try:
                    return pages.index(resident, reference_index + 1)
                except ValueError:
                    return len(pages)

            frame_index = max(
                range(frame_count),
                key=lambda index: (next_use(index), -index),
            )
            replaced_page = frames[frame_index]

        frames[frame_index] = page
        last_used[page] = reference_index
        if policy == "FIFO":
            fifo_order.append(frame_index)
        steps.append(
            ReplacementStep(
                reference_index, page, tuple(frames), True, replaced_page, frame_index
            )
        )

    return ReplacementResult(
        policy=policy,
        frame_count=frame_count,
        references=pages,
        steps=tuple(steps),
        page_faults=faults,
        hits=len(pages) - faults,
    )


def translate_virtual_address(
    virtual_address: object,
    page_size: object,
    page_table: Sequence[int | None],
) -> AddressTranslation:
    """Translate an address through a page table or report a page fault."""

    address = _non_negative_integer(virtual_address, "Virtual address")
    size = _non_negative_integer(page_size, "Page size")
    if size <= 0:
        raise ValueError("Page size must be a positive integer.")
    if not page_table:
        raise ValueError("Page table must contain at least one virtual page.")

    page_number, offset = divmod(address, size)
    if page_number >= len(page_table):
        raise ValueError(
            f"Virtual address {address} is outside the configured address space "
            f"of {len(page_table) * size} bytes."
        )
    frame_number = page_table[page_number]
    if frame_number is not None:
        frame_number = _non_negative_integer(frame_number, "Frame number")
    physical_address = (
        None if frame_number is None else frame_number * size + offset
    )
    return AddressTranslation(
        virtual_address=address,
        page_number=page_number,
        offset=offset,
        frame_number=frame_number,
        physical_address=physical_address,
    )
