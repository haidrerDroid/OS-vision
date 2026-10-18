import pytest
from pathlib import Path

from algorithms.bankers import check_safety, create_state, simulate_request
from streamlit.testing.v1 import AppTest


@pytest.fixture
def sample_state():
    return create_state(
        [3, 3, 2],
        [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]],
        [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]],
    )


def test_need_matrix_and_sample_safe_sequence_are_derived(sample_state):
    assert sample_state.need == (
        (7, 4, 3),
        (1, 2, 2),
        (6, 0, 0),
        (0, 1, 1),
        (4, 3, 1),
    )

    result = check_safety(sample_state)

    assert result.is_safe
    assert result.safe_sequence == (1, 3, 0, 2, 4)
    assert [step.work_before for step in result.steps] == [
        (3, 3, 2),
        (5, 3, 2),
        (7, 4, 3),
        (7, 5, 3),
        (10, 5, 5),
    ]
    assert result.steps[-1].work_after == (10, 5, 7)
    assert result.unfinished_processes == ()


def test_safety_check_reports_unsafe_state_and_processes_that_cannot_finish():
    state = create_state([0, 0], [[1, 0], [0, 1]], [[1, 1], [1, 1]])

    result = check_safety(state)

    assert not result.is_safe
    assert result.safe_sequence == ()
    assert result.unfinished_processes == (0, 1)


def test_safe_resource_request_is_granted_without_mutating_original_state(sample_state):
    result = simulate_request(sample_state, 1, [1, 0, 2])

    assert result.granted
    assert result.safety is not None and result.safety.is_safe
    assert result.safety.safe_sequence == (1, 3, 0, 2, 4)
    assert result.resulting_state is not None
    assert result.resulting_state.available == (2, 3, 0)
    assert result.resulting_state.allocation[1] == (3, 0, 2)
    assert sample_state.available == (3, 3, 2)
    assert sample_state.allocation[1] == (2, 0, 0)


def test_request_that_would_make_state_unsafe_is_denied(sample_state):
    result = simulate_request(sample_state, 4, [3, 3, 0])

    assert not result.granted
    assert "unsafe" in result.reason
    assert result.safety is not None and not result.safety.is_safe
    assert result.safety.unfinished_processes == (0, 1, 2, 3, 4)


@pytest.mark.parametrize(
    ("request_values", "message"),
    [
        ([8, 0, 0], "remaining claim"),
        ([4, 0, 0], "currently available"),
    ],
)
def test_request_denials_explain_need_or_available_limit(sample_state, request_values, message):
    result = simulate_request(sample_state, 0, request_values)

    assert not result.granted
    assert message in result.reason


@pytest.mark.parametrize(
    ("process_index", "request_values", "message"),
    [
        (0, [-1, 0, 0], "non-negative"),
        (0, [1, 0], "3 resource values"),
        (5, [0, 0, 0], "between 0 and 4"),
        (0, [True, 0, 0], "non-negative integer"),
    ],
)
def test_resource_requests_reject_invalid_input(
    sample_state, process_index, request_values, message
):
    with pytest.raises(ValueError, match=message):
        simulate_request(sample_state, process_index, request_values)


@pytest.mark.parametrize(
    ("available", "allocation", "maximum", "message"),
    [
        ([], [[0]], [[1]], "at least one resource"),
        ([1], [], [], "at least one process"),
        ([1, 2], [[0]], [[1]], "2 resource values"),
        ([1], [[0], [0]], [[1]], "same number of processes"),
        ([1], [[2]], [[1]], "cannot exceed"),
        ([1], [[0]], [[2]], "total number of instances"),
        ([-1], [[0]], [[1]], "non-negative"),
        ([1], [[0.5]], [[1]], "finite non-negative integer"),
    ],
)
def test_bankers_state_rejects_invalid_matrices(available, allocation, maximum, message):
    with pytest.raises(ValueError, match=message):
        create_state(available, allocation, maximum)


def test_bankers_page_shows_safe_sequence_and_simulates_safe_request():
    app = AppTest.from_file(Path(__file__).parents[1] / "app.py").run(timeout=30)
    app = app.switch_page("pages/bankers.py").run(timeout=30)

    assert not app.exception, app.exception
    assert "banker_input_error" not in app.session_state
    assert ("Current state", "SAFE") in [(metric.label, metric.value) for metric in app.metric]
    assert any(
        "P1 → P3 → P0 → P2 → P4" in item.value for item in app.success
    )
    assert any(
        item.label == "Step through the safety check" for item in app.slider
    )

    next(item for item in app.selectbox if item.label == "Requesting process").select("P1")
    next(item for item in app.number_input if item.label == "Request · A").set_value(1)
    next(item for item in app.number_input if item.label == "Request · C").set_value(2)
    next(button for button in app.button if button.label == "Simulate request").click().run(
        timeout=30
    )

    assert not app.exception, app.exception
    assert app.session_state["banker_request_result"].granted
    assert app.session_state["banker_available"].iloc[0].tolist() == [3, 3, 2]


def test_bankers_page_denies_unsafe_request_without_changing_base_matrices():
    app = AppTest.from_file(Path(__file__).parents[1] / "app.py").run(timeout=30)
    app = app.switch_page("pages/bankers.py").run(timeout=30)
    next(item for item in app.selectbox if item.label == "Requesting process").select("P4")
    next(item for item in app.number_input if item.label == "Request · A").set_value(3)
    next(item for item in app.number_input if item.label == "Request · B").set_value(3)
    next(button for button in app.button if button.label == "Simulate request").click().run(
        timeout=30
    )

    assert not app.exception, app.exception
    assert not app.session_state["banker_request_result"].granted
    assert "unsafe" in app.session_state["banker_request_result"].reason
    assert app.session_state["banker_available"].iloc[0].tolist() == [3, 3, 2]
    assert app.session_state["banker_allocation"].loc["P4"].tolist() == [0, 0, 2]


def test_bankers_page_loads_presets_and_resizes_matrices():
    app = AppTest.from_file(Path(__file__).parents[1] / "app.py").run(timeout=30)
    app = app.switch_page("pages/bankers.py").run(timeout=30)
    next(item for item in app.selectbox if item.label == "Learning preset").select(
        "Unsafe state"
    ).run(timeout=30)

    assert not app.exception, app.exception
    assert app.session_state["banker_allocation"].shape == (2, 2)
    assert any("No safe sequence exists" in item.value for item in app.warning)

    next(item for item in app.number_input if item.label == "Processes").set_value(3)
    next(item for item in app.number_input if item.label == "Resource types").set_value(3)
    next(button for button in app.button if button.label == "Apply dimensions").click().run(
        timeout=30
    )

    assert not app.exception, app.exception
    assert app.session_state["banker_allocation"].shape == (3, 3)
    assert app.session_state["banker_maximum"].shape == (3, 3)
    assert list(app.session_state["banker_available"].columns) == ["A", "B", "C"]

    next(item for item in app.number_input if item.label == "Processes").set_value(1)
    next(item for item in app.number_input if item.label == "Resource types").set_value(1)
    next(button for button in app.button if button.label == "Apply dimensions").click().run(
        timeout=30
    )
    assert not app.exception, app.exception
    assert app.session_state["banker_allocation"].shape == (1, 1)


def test_banker_request_presets_cover_need_and_available_rejections():
    app = AppTest.from_file(Path(__file__).parents[1] / "app.py").run(timeout=30)
    app = app.switch_page("pages/bankers.py").run(timeout=30)

    for preset_name, expected_reason in (
        ("Request exceeds Need", "remaining claim"),
        ("Request exceeds Available", "currently available"),
    ):
        next(item for item in app.selectbox if item.label == "Learning preset").select(
            preset_name
        ).run(timeout=30)
        next(button for button in app.button if button.label == "Simulate request").click().run(
            timeout=30
        )
        assert not app.exception, app.exception
        assert expected_reason in app.session_state["banker_request_result"].reason
