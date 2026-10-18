import pytest

from algorithms.fcfs import Process, schedule_fcfs


def test_fcfs_metrics_and_simultaneous_arrival_tie_breaking():
    result = schedule_fcfs(
        [
            Process("P1", 0, 5),
            Process("P2", 1, 3),
            Process("P3", 1, 2),
        ]
    )

    assert [(item.process_id, item.start_time, item.completion_time) for item in result.processes] == [
        ("P1", 0, 5),
        ("P2", 5, 8),
        ("P3", 8, 10),
    ]
    assert [(item.waiting_time, item.turnaround_time, item.response_time) for item in result.processes] == [
        (0, 5, 0),
        (4, 7, 4),
        (7, 9, 7),
    ]
    assert result.average_waiting_time == pytest.approx(11 / 3)
    assert result.average_turnaround_time == pytest.approx(7)
    assert result.average_response_time == pytest.approx(11 / 3)
    assert result.cpu_utilization == pytest.approx(1.0)
    assert result.throughput == pytest.approx(0.3)


def test_fcfs_includes_idle_intervals_before_and_between_processes():
    result = schedule_fcfs(
        [
            {"process_id": "late", "arrival_time": 4, "burst_time": 2},
            {"process_id": "later", "arrival_time": 9, "burst_time": 1},
        ]
    )

    assert [(item.start, item.finish, item.process_id) for item in result.intervals] == [
        (0, 4, None),
        (4, 6, "late"),
        (6, 9, None),
        (9, 10, "later"),
    ]
    assert [item.waiting_time for item in result.processes] == [0, 0]
    assert result.cpu_utilization == pytest.approx(0.3)
    assert result.throughput == pytest.approx(0.2)


@pytest.mark.parametrize(
    ("processes", "message"),
    [
        ([], "At least one process"),
        ([{"process_id": "P1", "arrival_time": -1, "burst_time": 2}], "cannot be negative"),
        ([{"process_id": "P1", "arrival_time": 0, "burst_time": 0}], "greater than zero"),
        (
            [
                {"process_id": "P1", "arrival_time": 0, "burst_time": 2},
                {"process_id": "P1", "arrival_time": 1, "burst_time": 3},
            ],
            "Duplicate process ID",
        ),
        ([{"process_id": " ", "arrival_time": 0, "burst_time": 1}], "non-empty"),
        ([{"process_id": "P1", "arrival_time": 1.5, "burst_time": 1}], "finite integer"),
    ],
)
def test_fcfs_rejects_invalid_input(processes, message):
    with pytest.raises(ValueError, match=message):
        schedule_fcfs(processes)
