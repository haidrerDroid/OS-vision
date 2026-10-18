from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_FILE = Path(__file__).parents[1] / "app.py"


def test_each_cpu_scheduler_has_a_separate_page_and_independent_result():
    app = AppTest.from_file(APP_FILE).run(timeout=30)
    assert not app.exception, app.exception
    assert {
        page["page_name"] for page in app._registered_pages.values()
    } == {
        "FCFS",
        "SJF",
        "SJF with Preemption (SRTF)",
        "Round Robin",
        "Deadlock Simulator",
        "Banker's Algorithm",
        "Algorithm Challenges",
        "Memory Management",
    }
    assert [button.label for button in app.button] == ["Run FCFS", "↺  Reset sample"]

    app.button[0].click().run(timeout=30)
    assert not app.exception, app.exception
    assert app.session_state["fcfs_result"].average_waiting_time == 4

    sjf = app.switch_page("pages/sjf.py").run(timeout=30)
    assert not sjf.exception, sjf.exception
    assert [button.label for button in sjf.button] == ["Run SJF", "↺  Reset sample"]
    next(item for item in sjf.selectbox if item.label == "Load a learning scenario").select(
        "Long job blocks short jobs"
    ).run(timeout=30)
    assert sjf.session_state["sjf_input"]["Burst Time"].tolist() == [9, 2, 1]
    assert app.session_state["fcfs_input"]["Burst Time"].tolist() == [5, 3, 8, 2]
    next(item for item in sjf.selectbox if item.label == "Load a learning scenario").select(
        "Balanced workload"
    ).run(timeout=30)
    sjf.button[0].click().run(timeout=30)
    assert sjf.session_state["sjf_result"].average_waiting_time == 4

    srtf = sjf.switch_page("pages/srtf.py").run(timeout=30)
    assert not srtf.exception, srtf.exception
    assert [button.label for button in srtf.button] == ["Run SRTF", "↺  Reset sample"]
    srtf.button[0].click().run(timeout=30)
    assert srtf.session_state["srtf_result"].average_waiting_time == 2.75

    round_robin = srtf.switch_page("pages/round_robin.py").run(timeout=30)
    assert not round_robin.exception, round_robin.exception
    assert [button.label for button in round_robin.button] == [
        "Run Round Robin",
        "↺  Reset sample",
    ]
    assert next(item for item in round_robin.number_input if item.label == "Time quantum").value == 2
    round_robin.button[0].click().run(timeout=30)
    assert round_robin.session_state["round_robin_result"].average_waiting_time == 5.5
    assert not round_robin.exception, round_robin.exception
    assert any(
        "time slice change performance" in item.value.lower()
        for item in round_robin.markdown
    )

    fcfs = round_robin.switch_page("pages/fcfs.py").run(timeout=30)
    assert fcfs.session_state["fcfs_result"].average_waiting_time == 4
    assert fcfs.session_state["sjf_result"].average_waiting_time == 4
    assert fcfs.session_state["srtf_result"].average_waiting_time == 2.75
    assert fcfs.session_state["round_robin_result"].average_waiting_time == 5.5


def test_round_robin_page_uses_its_own_selected_quantum():
    app = AppTest.from_file(APP_FILE).run(timeout=30)
    app = app.switch_page("pages/round_robin.py").run(timeout=30)
    next(item for item in app.number_input if item.label == "Time quantum").set_value(1)
    next(button for button in app.button if button.label == "Run Round Robin").click().run(timeout=30)

    assert not app.exception, app.exception
    result = app.session_state["round_robin_result"]
    assert result.intervals[0].finish == 1


def test_fcfs_page_explains_convoy_effect_for_long_first_job():
    app = AppTest.from_file(APP_FILE).run(timeout=30)
    app = app.switch_page("pages/fcfs.py").run(timeout=30)
    next(item for item in app.selectbox if item.label == "Load a learning scenario").select(
        "Long job blocks short jobs"
    ).run(timeout=30)
    next(button for button in app.button if button.label == "Run FCFS").click().run(
        timeout=30
    )

    assert not app.exception, app.exception
    assert any("Convoy effect" in item.value for item in app.info)
