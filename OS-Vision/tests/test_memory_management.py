from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from algorithms.memory_management import (
    parse_reference_string,
    simulate_page_replacement,
    translate_virtual_address,
)


def test_reference_string_parser_accepts_comma_and_space_separators():
    assert parse_reference_string("1, 2  3,4") == (1, 2, 3, 4)


@pytest.mark.parametrize(
    ("reference_text", "message"),
    [
        ("", "at least one"),
        ("1, -2", "non-negative integer"),
        ("1, x", "non-negative integer"),
    ],
)
def test_reference_string_parser_rejects_invalid_input(reference_text, message):
    with pytest.raises(ValueError, match=message):
        parse_reference_string(reference_text)


def test_fifo_lru_and_optimal_have_distinct_derived_fault_counts():
    references = parse_reference_string("7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2")

    fifo = simulate_page_replacement(references, 3, "FIFO")
    lru = simulate_page_replacement(references, 3, "LRU")
    optimal = simulate_page_replacement(references, 3, "Optimal")

    assert (fifo.page_faults, lru.page_faults, optimal.page_faults) == (10, 9, 7)
    assert fifo.hits + fifo.page_faults == len(references)
    assert optimal.steps[0].frames == (7, None, None)
    assert optimal.steps[0].is_page_fault
    assert not optimal.steps[4].is_page_fault


def test_fifo_classic_string_demonstrates_beladys_anomaly():
    references = parse_reference_string("1,2,3,4,1,2,5,1,2,3,4,5")

    three_frames = simulate_page_replacement(references, 3, "FIFO")
    four_frames = simulate_page_replacement(references, 4, "FIFO")

    assert three_frames.page_faults == 9
    assert four_frames.page_faults == 10


@pytest.mark.parametrize(
    ("references", "frame_count", "policy", "message"),
    [
        ([], 2, "FIFO", "At least one page reference"),
        ([0, 1], 0, "FIFO", "positive integer"),
        ([0], True, "FIFO", "positive integer"),
        ([0], 1, "Random", "Unsupported"),
        ([0, -1], 1, "LRU", "non-negative integer"),
        ([0, 1.5], 1, "Optimal", "non-negative integer"),
    ],
)
def test_page_replacement_rejects_invalid_input(
    references, frame_count, policy, message
):
    with pytest.raises(ValueError, match=message):
        simulate_page_replacement(references, frame_count, policy)


def test_virtual_address_translation_calculates_frame_and_offset():
    translated = translate_virtual_address(2500, 1024, [3, None, 1])

    assert translated.page_number == 2
    assert translated.offset == 452
    assert translated.frame_number == 1
    assert translated.physical_address == 1476
    assert not translated.is_page_fault


def test_virtual_address_translation_reports_page_fault_and_bounds():
    fault = translate_virtual_address(1025, 1024, [2, None])

    assert fault.page_number == 1
    assert fault.offset == 1
    assert fault.is_page_fault
    assert fault.physical_address is None
    with pytest.raises(ValueError, match="outside the configured address space"):
        translate_virtual_address(2048, 1024, [2, None])


def test_memory_page_computes_policy_results_and_translation():
    app = AppTest.from_file(Path(__file__).parents[1] / "app.py").run(timeout=30)
    app = app.switch_page("pages/memory_management.py").run(timeout=30)

    assert not app.exception, app.exception
    next(button for button in app.button if button.label == "Run page-replacement simulation").click().run(
        timeout=30
    )

    assert not app.exception, app.exception
    results = app.session_state["memory_results"]
    assert set(results) == {"FIFO", "LRU", "Optimal"}
    assert results["Optimal"].page_faults <= results["LRU"].page_faults
    assert any(item.label == "Step through references" for item in app.slider)
    next(item for item in app.slider if item.label == "Step through references").set_value(
        1
    ).run(timeout=30)
    next(item for item in app.number_input if item.label == "Virtual address (bytes)").set_value(
        1024
    ).run(timeout=30)
    assert not app.exception, app.exception
    assert any(
        "physical address 0" in item.value.lower() for item in app.success
    )


def test_memory_page_rejects_references_outside_virtual_space():
    app = AppTest.from_file(Path(__file__).parents[1] / "app.py").run(timeout=30)
    app = app.switch_page("pages/memory_management.py").run(timeout=30)
    next(item for item in app.text_input if item.label == "Page reference string").set_value(
        "8, 1"
    )
    next(button for button in app.button if button.label == "Run page-replacement simulation").click().run(
        timeout=30
    )

    assert not app.exception, app.exception
    assert "less than the virtual page count" in app.session_state["memory_error"]
    assert "memory_results" not in app.session_state


def test_memory_page_belady_preset_shows_computed_anomaly_counts():
    app = AppTest.from_file(Path(__file__).parents[1] / "app.py").run(timeout=30)
    app = app.switch_page("pages/memory_management.py").run(timeout=30)
    next(item for item in app.selectbox if item.label == "Learning scenario").select(
        "Belady's anomaly (FIFO)"
    ).run(timeout=30)

    assert not app.exception, app.exception
    assert any(
        "9 faults with 3 frames and 10 with 4" in item.value for item in app.info
    )
