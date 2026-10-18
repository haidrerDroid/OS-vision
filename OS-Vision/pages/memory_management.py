"""Interactive paging and page-replacement learning lab."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from algorithms.memory_management import (
    ReplacementPolicy,
    ReplacementResult,
    parse_reference_string,
    simulate_page_replacement,
    translate_virtual_address,
)


st.set_page_config(page_title="OSVision | Memory Management", page_icon="⚙️", layout="wide")
st.markdown(
    """
    <style>
    .stApp { background: radial-gradient(ellipse at 80% 0%, rgba(13,148,136,.13), transparent 38%), #0b1120; }
    .stApp, [data-testid="stMarkdownContainer"] { font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
    [data-testid="stHeader"] { background: rgba(11,17,32,.82); }
    [data-testid="stSidebar"] { background: linear-gradient(180deg,#101a2b 0%,#0c1422 100%); border-right: 1px solid rgba(148,163,184,.12); }
    .block-container { padding-top: 2.5rem; padding-bottom: 3rem; max-width: 1400px; }
    .hero { padding:2rem 2.2rem; margin-bottom:1.6rem; border:1px solid rgba(94,234,212,.18); border-radius:20px; background:linear-gradient(115deg,rgba(18,35,52,.98),rgba(13,27,42,.86)); }
    .eyebrow,.section-kicker { color:#5eead4; font: .72rem ui-monospace,SFMono-Regular,Menlo,monospace; letter-spacing:.12em; text-transform:uppercase; }
    .hero h1 { color:#f1f5f9; font-size:clamp(2rem,4vw,3rem); font-weight:800; letter-spacing:-.055em; margin:.55rem 0 .35rem; }
    .hero p,.section-copy { color:#94a3b8; }
    [data-testid="stMetric"] { min-height:100px; padding:1rem 1.1rem; border:1px solid rgba(148,163,184,.14); border-radius:14px; background:linear-gradient(145deg,rgba(21,33,51,.96),rgba(15,25,40,.92)); }
    [data-testid="stMetricLabel"] p { color:#9aabc0; font-size:.78rem; }
    [data-testid="stMetricValue"] { color:#f1f5f9; font-weight:700; }
    [data-testid="stVerticalBlockBorderWrapper"] { border-color:rgba(148,163,184,.16); border-radius:16px; background:rgba(15,25,40,.55); }
    .stButton>button { min-height:2.65rem; border-radius:10px; font-weight:600; }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown(
        """
        <div style="padding:.6rem 0 1.2rem">
          <div style="color:#5eead4;font-family:ui-monospace,monospace;font-size:.72rem;letter-spacing:.13em">◈ OSVISION</div>
          <div style="color:#f1f5f9;font-size:1.3rem;font-weight:800;margin-top:.3rem">Control room</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown('<div class="section-kicker">Active module</div>', unsafe_allow_html=True)
    st.markdown("### Memory management")
    st.caption("Page replacement and virtual address translation")

SCENARIOS = {
    "Locality and reuse": {
        "references": "1, 2, 3, 2, 4, 1, 5, 2, 1, 2, 3, 4",
        "frames": 3,
        "virtual_pages": 8,
        "page_size": 1024,
    },
    "Belady's anomaly (FIFO)": {
        "references": "1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5",
        "frames": 3,
        "virtual_pages": 8,
        "page_size": 1024,
    },
    "Sequential scan": {
        "references": "0, 1, 2, 3, 4, 0, 1, 2, 3, 4",
        "frames": 3,
        "virtual_pages": 8,
        "page_size": 1024,
    },
}
POLICIES: tuple[ReplacementPolicy, ...] = ("FIFO", "LRU", "Optimal")


def _load_scenario() -> None:
    scenario = SCENARIOS[st.session_state.memory_scenario]
    st.session_state.memory_reference_text = scenario["references"]
    st.session_state.memory_frame_count = scenario["frames"]
    st.session_state.memory_virtual_page_count = scenario["virtual_pages"]
    st.session_state.memory_page_size = scenario["page_size"]
    st.session_state.pop("memory_results", None)
    st.session_state.pop("memory_result_signature", None)
    st.session_state.pop("memory_error", None)


if "memory_scenario" not in st.session_state:
    st.session_state.memory_scenario = "Locality and reuse"
    _load_scenario()

st.markdown(
    """
    <section class="hero">
      <div class="eyebrow">OS lab · virtual memory</div>
      <h1>Memory management</h1>
      <p>Compare real FIFO, LRU, and Optimal page replacement, inspect frame contents after each reference, and translate virtual addresses through the resulting page table.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-kicker">01 / configure the memory workload</div>', unsafe_allow_html=True)
st.selectbox(
    "Learning scenario",
    list(SCENARIOS),
    key="memory_scenario",
    on_change=_load_scenario,
    help="The Belady scenario uses the same reference string to demonstrate how FIFO faults can increase with more frames.",
)
with st.container(border=True):
    reference_text = st.text_input(
        "Page reference string",
        key="memory_reference_text",
        help="Enter non-negative page numbers separated by commas or spaces.",
    )
    config_cols = st.columns(3)
    config_cols[0].number_input(
        "Physical frames",
        min_value=1,
        max_value=8,
        step=1,
        key="memory_frame_count",
    )
    config_cols[1].number_input(
        "Virtual pages",
        min_value=1,
        max_value=64,
        step=1,
        key="memory_virtual_page_count",
        help="References and translated addresses must fit in this virtual address space.",
    )
    config_cols[2].selectbox(
        "Page size (bytes)",
        [256, 512, 1024, 2048, 4096],
        key="memory_page_size",
    )
    run_clicked = st.button("Run page-replacement simulation", type="primary")

page_size = int(st.session_state.memory_page_size)
virtual_page_count = int(st.session_state.memory_virtual_page_count)
frame_count = int(st.session_state.memory_frame_count)
if run_clicked:
    try:
        references = parse_reference_string(reference_text)
        if any(page >= virtual_page_count for page in references):
            raise ValueError(
                f"Every page reference must be less than the virtual page count "
                f"({virtual_page_count})."
            )
        st.session_state.memory_results = {
            policy: simulate_page_replacement(references, frame_count, policy)
            for policy in POLICIES
        }
        st.session_state.memory_result_signature = (
            references,
            frame_count,
            virtual_page_count,
            page_size,
        )
        st.session_state.pop("memory_error", None)
    except ValueError as exc:
        st.session_state.pop("memory_results", None)
        st.session_state.pop("memory_result_signature", None)
        st.session_state.memory_error = str(exc)

if st.session_state.get("memory_error"):
    st.error(st.session_state.memory_error)

current_signature = (
    parse_reference_string(reference_text)
    if reference_text.strip() and all(part.isdecimal() for part in reference_text.replace(",", " ").split())
    else None,
    frame_count,
    virtual_page_count,
    page_size,
)
results: dict[str, ReplacementResult] | None = st.session_state.get("memory_results")
if results and st.session_state.get("memory_result_signature") == current_signature:
    st.markdown('<div class="section-kicker" style="margin-top:1.8rem">02 / compare replacement policies</div>', unsafe_allow_html=True)
    st.markdown("### Each policy runs on the same references and frame count")
    summary = pd.DataFrame(
        [
            {
                "Policy": policy,
                "Page faults": results[policy].page_faults,
                "Hits": results[policy].hits,
                "Fault rate": results[policy].fault_rate,
                "Hit rate": results[policy].hit_rate,
            }
            for policy in POLICIES
        ]
    )
    metric_cols = st.columns(len(POLICIES))
    for column, policy in zip(metric_cols, POLICIES):
        column.metric(
            f"{policy} page faults",
            results[policy].page_faults,
            f"{results[policy].hits} hits",
        )
    chart = px.bar(
        summary,
        x="Policy",
        y="Page faults",
        color="Policy",
        text="Page faults",
        color_discrete_map={"FIFO": "#38bdf8", "LRU": "#2dd4bf", "Optimal": "#a78bfa"},
        template="plotly_dark",
        title="Page faults for the same workload",
    )
    chart.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(chart, width="stretch")
    st.dataframe(
        summary.style.format({"Fault rate": "{:.1%}", "Hit rate": "{:.1%}"}),
        hide_index=True,
        width="stretch",
    )

    policy = st.selectbox(
        "Trace to inspect",
        POLICIES,
        key="memory_trace_policy",
    )
    result = results[policy]
    step_count = st.slider(
        "Step through references",
        min_value=0,
        max_value=len(result.steps),
        value=0,
        key=f"memory_trace_step_{policy}",
        help="At step 0 all frames are empty; each subsequent step applies one page reference.",
    )
    frame_snapshot: tuple[int | None, ...] = (
        tuple([None] * frame_count)
        if step_count == 0
        else result.steps[step_count - 1].frames
    )
    page_table: list[int | None] = [None] * virtual_page_count
    for frame_number, resident_page in enumerate(frame_snapshot):
        if resident_page is not None:
            page_table[resident_page] = frame_number

    if step_count:
        step = result.steps[step_count - 1]
        if step.is_page_fault:
            evicted = (
                f" Page {step.replaced_page} was evicted from frame {step.frame_index}."
                if step.replaced_page is not None
                else f" Page loaded into frame {step.frame_index}."
            )
            st.warning(f"Reference {step.reference_index + 1}: page {step.page} fault.{evicted}")
        else:
            st.success(
                f"Reference {step.reference_index + 1}: page {step.page} is already resident (hit)."
            )
    else:
        st.info("No reference has been processed; all physical frames are empty.")

    frame_cols = st.columns(frame_count)
    for frame_number, column in enumerate(frame_cols):
        resident = frame_snapshot[frame_number]
        column.metric(
            f"Frame {frame_number}",
            "Empty" if resident is None else f"Page {resident}",
        )

    st.markdown("#### Current page table")
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Virtual page": page,
                    "Physical frame": "Not resident" if frame is None else frame,
                    "Valid": frame is not None,
                }
                for page, frame in enumerate(page_table)
            ]
        ),
        hide_index=True,
        width="stretch",
    )

    trace = pd.DataFrame(
        [
            {
                "Reference #": item.reference_index + 1,
                "Page": item.page,
                **{
                    f"Frame {frame_index}": (
                        "—" if resident is None else resident
                    )
                    for frame_index, resident in enumerate(item.frames)
                },
                "Outcome": "Fault" if item.is_page_fault else "Hit",
                "Replaced page": (
                    "—" if item.replaced_page is None else item.replaced_page
                ),
            }
            for item in result.steps
        ]
    )
    st.markdown("#### Reference-by-reference frame table")
    st.dataframe(trace, hide_index=True, width="stretch")
    st.caption(
        "Optimal is an offline benchmark: it replaces the page whose next use is farthest in the known future, so a real OS cannot generally implement it without future knowledge."
    )

    st.markdown('<div class="section-kicker" style="margin-top:1.8rem">03 / virtual address translation</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">Translation uses the page table created by the selected policy at the chosen trace step. A page not resident in that snapshot causes a page fault.</div>',
        unsafe_allow_html=True,
    )
    max_address = virtual_page_count * page_size - 1
    address = int(
        st.number_input(
            "Virtual address (bytes)",
            min_value=0,
            max_value=max_address,
            value=0,
            step=1,
            key=f"memory_address_{page_size}_{virtual_page_count}",
        )
    )
    translation = translate_virtual_address(address, page_size, page_table)
    if translation.is_page_fault:
        st.warning(
            f"Page fault: virtual page {translation.page_number} is not in a physical frame "
            f"after reference step {step_count}."
        )
    else:
        physical_cols = st.columns(4)
        physical_cols[0].metric("Virtual page", translation.page_number)
        physical_cols[1].metric("Offset", translation.offset)
        physical_cols[2].metric("Physical frame", translation.frame_number)
        physical_cols[3].metric("Physical address", translation.physical_address)
        st.success(
            f"{address} = page {translation.page_number} × {page_size} + offset "
            f"{translation.offset} → frame {translation.frame_number} × {page_size} + "
            f"{translation.offset} = physical address {translation.physical_address}."
        )

if (
    st.session_state.memory_scenario == "Belady's anomaly (FIFO)"
    and reference_text.strip()
    == SCENARIOS["Belady's anomaly (FIFO)"]["references"]
):
    fifo_three = simulate_page_replacement(
        parse_reference_string(SCENARIOS["Belady's anomaly (FIFO)"]["references"]),
        3,
        "FIFO",
    )
    fifo_four = simulate_page_replacement(
        fifo_three.references,
        4,
        "FIFO",
    )
    st.info(
        f"Belady's anomaly check for this classic reference string: FIFO has "
        f"{fifo_three.page_faults} faults with 3 frames and {fifo_four.page_faults} "
        "with 4 frames. Adding a frame can increase FIFO faults for this workload."
    )
