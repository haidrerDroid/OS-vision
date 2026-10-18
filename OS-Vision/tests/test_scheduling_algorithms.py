import pytest

from algorithms.fcfs import Process
from algorithms.round_robin import schedule_round_robin
from algorithms.sjf import schedule_sjf
from algorithms.srtf import schedule_srtf


def interval_pairs(result):
    return [(item.start, item.finish, item.process_id) for item in result.intervals]


def test_sjf_selects_shortest_ready_job_without_preemption():
    result = schedule_sjf(
        [Process("A", 0, 8), Process("B", 1, 4), Process("C", 2, 2), Process("D", 3, 1)]
    )

    assert interval_pairs(result) == [
        (0, 8, "A"),
        (8, 9, "D"),
        (9, 11, "C"),
        (11, 15, "B"),
    ]
    assert result.average_waiting_time == pytest.approx(5.5)
    assert result.average_turnaround_time == pytest.approx(9.25)
    assert result.average_response_time == pytest.approx(5.5)
    assert result.cpu_utilization == pytest.approx(1)
    assert result.throughput == pytest.approx(4 / 15)


def test_sjf_ties_use_arrival_then_original_input_order_and_tracks_idle():
    result = schedule_sjf(
        [Process("later-row", 2, 1), Process("first-row", 2, 1)]
    )

    assert interval_pairs(result) == [
        (0, 2, None),
        (2, 3, "later-row"),
        (3, 4, "first-row"),
    ]


def test_srtf_preempts_when_a_shorter_job_arrives_and_preserves_metrics():
    result = schedule_srtf(
        [Process("A", 0, 8), Process("B", 1, 4), Process("C", 2, 2), Process("D", 3, 1)]
    )

    assert interval_pairs(result) == [
        (0, 1, "A"),
        (1, 2, "B"),
        (2, 4, "C"),
        (4, 5, "D"),
        (5, 8, "B"),
        (8, 15, "A"),
    ]
    assert {
        item.process_id: (item.start_time, item.completion_time, item.waiting_time, item.response_time)
        for item in result.processes
    } == {
        "A": (0, 15, 7, 0),
        "B": (1, 8, 3, 0),
        "C": (2, 4, 0, 0),
        "D": (4, 5, 1, 1),
    }


def test_srtf_ties_and_idle_gaps_are_deterministic():
    result = schedule_srtf([Process("P1", 3, 2), Process("P2", 3, 2)])

    assert interval_pairs(result) == [(0, 3, None), (3, 5, "P1"), (5, 7, "P2")]


def test_round_robin_rotation_and_arrivals_at_quantum_boundary():
    result = schedule_round_robin(
        [Process("P1", 0, 5), Process("P2", 1, 3), Process("P3", 2, 1)], quantum=2
    )

    assert interval_pairs(result) == [
        (0, 2, "P1"),
        (2, 4, "P2"),
        (4, 5, "P3"),
        (5, 7, "P1"),
        (7, 8, "P2"),
        (8, 9, "P1"),
    ]
    assert {
        item.process_id: (item.completion_time, item.turnaround_time, item.waiting_time)
        for item in result.processes
    } == {"P1": (9, 9, 4), "P2": (8, 7, 4), "P3": (5, 3, 2)}


@pytest.mark.parametrize("quantum", [0, -1, 1.5, True])
def test_round_robin_rejects_non_positive_or_non_integer_quantum(quantum):
    with pytest.raises(ValueError):
        schedule_round_robin([Process("P1", 0, 1)], quantum)
