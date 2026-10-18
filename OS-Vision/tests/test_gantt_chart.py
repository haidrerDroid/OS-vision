from algorithms.fcfs import schedule_fcfs
from visualizations.gantt_chart import build_gantt_chart


def test_gantt_chart_uses_process_and_idle_intervals_from_schedule():
    result = schedule_fcfs(
        [
            {"process_id": "P1", "arrival_time": 2, "burst_time": 3},
            {"process_id": "P2", "arrival_time": 8, "burst_time": 1},
        ]
    )

    chart = build_gantt_chart(result)

    assert list(chart.data[0].base) == [0, 2, 5, 8]
    assert list(chart.data[0].x) == [2, 3, 3, 1]
    assert [item[0] for item in chart.data[0].customdata] == [
        "CPU Idle",
        "P1",
        "CPU Idle",
        "P2",
    ]
