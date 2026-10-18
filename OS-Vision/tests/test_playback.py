from algorithms.fcfs import schedule_fcfs
from algorithms.playback import next_schedule_boundary, process_states_at
from algorithms.srtf import schedule_srtf
from visualizations.gantt_chart import build_gantt_chart


def test_process_states_follow_arrival_running_and_completion_times():
    result = schedule_fcfs(
        [
            {"process_id": "P1", "arrival_time": 0, "burst_time": 2},
            {"process_id": "P2", "arrival_time": 3, "burst_time": 1},
        ]
    )

    assert [row["State"] for row in process_states_at(result, 0)] == [
        "Running",
        "Not arrived",
    ]
    assert [row["State"] for row in process_states_at(result, 2.5)] == [
        "Complete",
        "Not arrived",
    ]
    assert [row["State"] for row in process_states_at(result, 3)] == [
        "Complete",
        "Running",
    ]
    assert [row["State"] for row in process_states_at(result, 4)] == [
        "Complete",
        "Complete",
    ]


def test_next_event_advances_to_the_next_interval_boundary():
    result = schedule_fcfs(
        [
            {"process_id": "P1", "arrival_time": 0, "burst_time": 4},
            {"process_id": "P2", "arrival_time": 1, "burst_time": 1},
        ]
    )

    assert next_schedule_boundary(result, 0) == 1
    assert next_schedule_boundary(result, 1) == 4
    assert next_schedule_boundary(result, 2) == 4
    assert next_schedule_boundary(result, 2.5) == 4
    assert next_schedule_boundary(result, 6) == 5


def test_process_states_follow_preemptions_in_srtf_schedule():
    result = schedule_srtf(
        [
            {"process_id": "P1", "arrival_time": 0, "burst_time": 5},
            {"process_id": "P2", "arrival_time": 2, "burst_time": 1},
        ]
    )

    assert [row["State"] for row in process_states_at(result, 2.5)] == ["Waiting", "Running"]
    assert [row["State"] for row in process_states_at(result, 4)] == ["Running", "Complete"]


def test_live_gantt_chart_marks_current_simulation_time():
    result = schedule_fcfs(
        [{"process_id": "P1", "arrival_time": 0, "burst_time": 3}]
    )

    chart = build_gantt_chart(result, current_time=1.5)

    assert chart.layout.title.text == "LIVE CPU TIMELINE"
    assert len(chart.layout.shapes) == 1
    assert chart.layout.shapes[0].x0 == 1.5
    assert list(chart.data[1].x) == [1.5]
