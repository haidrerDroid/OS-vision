from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_challenge_page_checks_predictions_and_updates_score():
    app = AppTest.from_file(Path(__file__).parents[1] / "app.py").run(timeout=30)
    app = app.switch_page("pages/challenges.py").run(timeout=30)

    assert not app.exception, app.exception
    next(item for item in app.selectbox if item.label == "Choose your answer").select("P1")
    next(button for button in app.button if button.label == "Check my answer").click().run(
        timeout=30
    )

    assert not app.exception, app.exception
    assert app.session_state["challenge_attempts"] == 1
    assert app.session_state["challenge_correct"] == 1
    assert any("Correct prediction" in item.value for item in app.success)


def test_challenge_answers_are_computed_for_the_selected_deadlock_module():
    app = AppTest.from_file(Path(__file__).parents[1] / "app.py").run(timeout=30)
    app = app.switch_page("pages/challenges.py").run(timeout=30)
    next(item for item in app.selectbox if item.label == "Choose a challenge").select(
        "Deadlock detection"
    ).run(timeout=30)
    next(item for item in app.selectbox if item.label == "Choose your answer").select(
        "No deadlock"
    )
    next(button for button in app.button if button.label == "Check my answer").click().run(
        timeout=30
    )

    assert not app.exception, app.exception
    assert app.session_state["challenge_correct"] == 1


def test_bankers_challenge_accepts_any_process_eligible_at_initial_work():
    app = AppTest.from_file(Path(__file__).parents[1] / "app.py").run(timeout=30)
    app = app.switch_page("pages/challenges.py").run(timeout=30)
    next(item for item in app.selectbox if item.label == "Choose a challenge").select(
        "Banker's safety check"
    ).run(timeout=30)
    next(item for item in app.selectbox if item.label == "Choose your answer").select("P3")
    next(button for button in app.button if button.label == "Check my answer").click().run(
        timeout=30
    )

    assert not app.exception, app.exception
    assert app.session_state["challenge_correct"] == 1
