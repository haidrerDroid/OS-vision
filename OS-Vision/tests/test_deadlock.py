import pytest

from algorithms.deadlock import (
    create_state,
    detect_deadlock,
    grant_request,
    has_resource_allocation_cycle,
    queue_request,
    release_resources,
)


def test_single_instance_resource_cycle_is_deadlock():
    state = create_state(
        [1, 1],
        [[1, 0], [0, 1], [0, 0]],
        [[0, 1], [1, 0], [0, 0]],
    )

    result = detect_deadlock(state)

    assert result.is_deadlocked
    assert has_resource_allocation_cycle(state)
    assert result.completed_processes == (2,)
    assert result.deadlocked_processes == (0, 1)
    assert result.final_work == (0, 0)


def test_cycle_is_not_a_deadlock_when_an_instance_allows_progress():
    state = create_state(
        [3, 2],
        [[1, 0], [0, 1], [1, 0]],
        [[0, 1], [1, 0], [0, 0]],
    )

    result = detect_deadlock(state)

    assert result.is_deadlocked is False
    assert has_resource_allocation_cycle(state)
    assert result.completed_processes == (0, 1, 2)
    assert result.deadlocked_processes == ()
    assert result.steps[0].work_before == (1, 1)
    assert result.steps[0].work_after == (2, 1)
    assert result.final_work == (3, 2)


def test_zero_allocation_processes_start_finished():
    state = create_state([1], [[0], [1]], [[1], [0]])

    result = detect_deadlock(state)

    assert result.is_deadlocked is False
    assert result.completed_processes == (0, 1)


def test_queue_request_does_not_allocate_until_granted():
    initial = create_state([2], [[1], [0]], [[0], [0]])
    queued = queue_request(initial, 1, 0, 2)

    assert queued.allocation == initial.allocation
    assert queued.request == ((0,), (2,))
    assert queued.available == (1,)

    with pytest.raises(ValueError, match="only 1 are available"):
        grant_request(queued, 1, 0, 2)

    partially_granted = grant_request(queued, 1, 0, 1)
    assert partially_granted.allocation == ((1,), (1,))
    assert partially_granted.request == ((0,), (1,))
    assert partially_granted.available == (0,)


def test_release_returns_instances_and_can_break_deadlock():
    deadlocked = create_state(
        [1, 1],
        [[1, 0], [0, 1]],
        [[0, 1], [1, 0]],
    )
    released = release_resources(deadlocked, 0, 0, 1)

    assert released.available == (1, 0)
    assert released.allocation[0] == (0, 0)
    assert detect_deadlock(released).is_deadlocked is False


@pytest.mark.parametrize(
    ("total", "allocation", "requests", "message"),
    [
        ([], [[0]], [[0]], "at least one resource"),
        ([1], [], [], "at least one process"),
        ([1, 2], [[0]], [[0]], "2 resource values"),
        ([1], [[0], [0]], [[0]], "same number of processes"),
        ([1], [[2]], [[0]], "exceed its total instances"),
        ([1], [[1]], [[1]], "allocation plus outstanding request"),
        ([1], [[0]], [[-1]], "non-negative"),
        ([1], [[0.5]], [[0]], "finite non-negative integer"),
    ],
)
def test_invalid_resource_states_are_rejected(total, allocation, requests, message):
    with pytest.raises(ValueError, match=message):
        create_state(total, allocation, requests)


@pytest.mark.parametrize(
    ("operation", "arguments", "message"),
    [
        (queue_request, (1, 0, 2), "exceed"),
        (grant_request, (0, 0, 1), "outstanding units"),
        (release_resources, (0, 0, 1), "holds only 0"),
        (queue_request, (2, 0, 1), "between 0 and 1"),
        (queue_request, (0, 1, 1), "between 0 and 0"),
        (queue_request, (0, 0, 0), "at least one"),
    ],
)
def test_resource_operations_validate_process_resource_and_units(
    operation, arguments, message
):
    state = create_state([1], [[0], [0]], [[0], [0]])

    with pytest.raises(ValueError, match=message):
        operation(state, *arguments)


def test_deadlock_page_demonstrates_detection_and_resource_operations():
    from pathlib import Path

    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(Path(__file__).parents[1] / "app.py").run(timeout=30)
    app = app.switch_page("pages/deadlock.py").run(timeout=30)

    assert not app.exception, app.exception
    assert any(metric.value == "DEADLOCK" for metric in app.metric)
    assert app.session_state["deadlock_result"].deadlocked_processes == (0, 1)
    assert app.session_state["deadlock_has_cycle"] is True

    next(item for item in app.selectbox if item.label == "Scenario").select(
        "Cycle with multiple instances — no deadlock"
    ).run(timeout=30)
    assert not app.exception, app.exception
    assert any(metric.value == "NO DEADLOCK" for metric in app.metric)
    assert app.session_state["deadlock_result"].is_deadlocked is False
    assert app.session_state["deadlock_has_cycle"] is True
    assert any("cycle" in item.value.lower() for item in app.info)
    assert any(
        item.label == "Step through deadlock detection" for item in app.slider
    )

    next(item for item in app.selectbox if item.label == "Scenario").select(
        "Single-instance cycle — deadlock"
    ).run(timeout=30)
    next(item for item in app.selectbox if item.label == "Process").select("P3")
    next(button for button in app.button if button.label == "Queue request").click().run(
        timeout=30
    )
    assert not app.exception, app.exception
    assert app.session_state["deadlock_state"].request[2] == (1, 0)


def test_deadlock_page_resizes_and_undoes_resource_operations():
    from pathlib import Path

    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(Path(__file__).parents[1] / "app.py").run(timeout=30)
    app = app.switch_page("pages/deadlock.py").run(timeout=30)

    next(item for item in app.number_input if item.label == "Processes").set_value(4)
    next(item for item in app.number_input if item.label == "Resource types").set_value(3)
    next(button for button in app.button if button.label == "Apply dimensions").click().run(
        timeout=30
    )
    assert not app.exception, app.exception
    assert app.session_state["deadlock_allocation"].shape == (4, 3)
    assert app.session_state["deadlock_request"].shape == (4, 3)

    next(item for item in app.number_input if item.label == "Processes").set_value(2)
    next(item for item in app.number_input if item.label == "Resource types").set_value(1)
    next(button for button in app.button if button.label == "Apply dimensions").click().run(
        timeout=30
    )
    assert not app.exception, app.exception
    assert app.session_state["deadlock_allocation"].shape == (2, 1)

    app = app.switch_page("pages/deadlock.py").run(timeout=30)
    next(button for button in app.button if button.label == "↺  Reset scenario").click().run(
        timeout=30
    )
    next(item for item in app.selectbox if item.label == "Process").select("P1")
    next(item for item in app.selectbox if item.label == "Resource").select("R1")
    next(button for button in app.button if button.label == "Release resources").click().run(
        timeout=30
    )
    assert not app.exception, app.exception
    assert app.session_state["deadlock_state"].allocation[0] == (0, 0)
    next(button for button in app.button if button.label == "↶  Undo last operation").click().run(
        timeout=30
    )
    assert not app.exception, app.exception
    assert app.session_state["deadlock_state"].allocation[0] == (1, 0)
