from algorithms.fcfs import schedule_fcfs
from algorithms.round_robin import schedule_round_robin
from algorithms.srtf import schedule_srtf
from visualizations.process_animation import build_process_animation_html


def test_animation_embeds_the_real_schedule_and_live_controls():
    result = schedule_fcfs(
        [
            {"process_id": "P1", "arrival_time": 0, "burst_time": 3},
            {"process_id": "P2", "arrival_time": 1, "burst_time": 2},
        ]
    )

    document = build_process_animation_html(result)

    assert '"makespan":5' in document
    assert '"id":"P1","arrival":0,"burst":3,"start":0,"finish":3' in document
    assert '"start":3,"finish":5,"process":"P2"' in document
    assert '"turnaround":4,"waiting":2,"response":2' in document
    assert '"averages":{"turnaround":3.5,"waiting":1.0,"response":1.0}' in document
    assert "requestAnimationFrame(frame)" in document
    assert "Next event" in document
    assert "EVENT LOG" in document
    assert "gantt-cursor" in document
    assert "tooltip.textContent" in document
    assert 'card.classList.add("event-flash")' in document
    assert 'interval.start<=t&&t<interval.finish' in document
    assert "FCFS runs the earliest-arrived ready process" in document
    assert "ready queue" in document
    assert "__MAX_LANE_HEIGHT__" not in document
    assert "Ready · burst" in document
    assert "non-preemptive choice runs to completion" in document


def test_animation_safely_serializes_user_supplied_process_ids():
    result = schedule_fcfs(
        [{"process_id": "</script><img src=x>", "arrival_time": 0, "burst_time": 1}]
    )

    document = build_process_animation_html(result)

    assert '"id":"\\u003c/script\\u003e\\u003cimg src=x\\u003e"' in document
    assert "</script><img" not in document


def test_preemptive_animation_uses_actual_srtf_segments_and_preemption_events():
    result = schedule_srtf(
        [
            {"process_id": "P1", "arrival_time": 0, "burst_time": 6},
            {"process_id": "P2", "arrival_time": 2, "burst_time": 1},
        ]
    )

    document = build_process_animation_html(result, "SRTF")

    assert '"algorithm":"SRTF"' in document
    assert '"start":0,"finish":2,"process":"P1"' in document
    assert '"start":2,"finish":3,"process":"P2"' in document
    assert 'kind==="PREEMPTED"' in document
    assert "shortest remaining time" in document
    assert "Ready remaining times" in document


def test_round_robin_animation_includes_quantum_and_queue_rotation():
    result = schedule_round_robin(
        [
            {"process_id": "P1", "arrival_time": 0, "burst_time": 3},
            {"process_id": "P2", "arrival_time": 1, "burst_time": 2},
        ],
        quantum=1,
    )

    document = build_process_animation_html(result, "Round Robin", time_quantum=1)

    assert '"algorithm":"Round Robin","quantum":1' in document
    assert '"QUANTUM EXPIRED"' in document
    assert "roundRobinReadyQueue" in document
