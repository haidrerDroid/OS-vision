"""Interactive Banker's algorithm and resource-request simulator."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from algorithms.bankers import BankerState, SafetyResult, check_safety, create_state, simulate_request


st.set_page_config(page_title="OSVision | Banker's Algorithm", page_icon="⚙️", layout="wide")

PROCESS_IDS = [f"P{index}" for index in range(5)]
RESOURCE_IDS = ["A", "B", "C"]
SAMPLE_AVAILABLE = [3, 3, 2]
SAMPLE_ALLOCATION = [
    [0, 1, 0],
    [2, 0, 0],
    [3, 0, 2],
    [2, 1, 1],
    [0, 0, 2],
]
SAMPLE_MAXIMUM = [
    [7, 5, 3],
    [3, 2, 2],
    [9, 0, 2],
    [2, 2, 2],
    [4, 3, 3],
]
PRESETS = {
    "Classic safe state": {
        "available": SAMPLE_AVAILABLE,
        "allocation": SAMPLE_ALLOCATION,
        "maximum": SAMPLE_MAXIMUM,
        "request_process": "P1",
        "request": [1, 0, 2],
    },
    "Unsafe state": {
        "available": [1, 1],
        "allocation": [[1, 0], [0, 1]],
        "maximum": [[1, 2], [2, 1]],
        "request_process": "P0",
        "request": [0, 1],
    },
    "Request exceeds Need": {
        "available": SAMPLE_AVAILABLE,
        "allocation": SAMPLE_ALLOCATION,
        "maximum": SAMPLE_MAXIMUM,
        "request_process": "P0",
        "request": [8, 0, 0],
    },
    "Request exceeds Available": {
        "available": SAMPLE_AVAILABLE,
        "allocation": SAMPLE_ALLOCATION,
        "maximum": SAMPLE_MAXIMUM,
        "request_process": "P0",
        "request": [4, 0, 0],
    },
}

st.markdown(
    """
    <style>
    .stApp { background: radial-gradient(ellipse at 80% 0%, rgba(13,148,136,.13), transparent 38%), #0b1120; }
    .stApp, [data-testid="stMarkdownContainer"] { font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
    [data-testid="stHeader"] { background: rgba(11,17,32,.82); }
    [data-testid="stSidebar"] { background: linear-gradient(180deg,#101a2b 0%,#0c1422 100%); border-right: 1px solid rgba(148,163,184,.12); }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #a8b5c8; }
    .block-container { padding-top: 2.5rem; padding-bottom: 3rem; max-width: 1400px; }
    .hero { position:relative; overflow:hidden; padding:2rem 2.2rem; margin-bottom:1.6rem; border:1px solid rgba(94,234,212,.18); border-radius:20px; background:linear-gradient(115deg,rgba(18,35,52,.98),rgba(13,27,42,.86)); box-shadow:0 18px 60px rgba(0,0,0,.2); }
    .hero:after { content:''; position:absolute; width:240px; height:240px; right:5%; top:-145px; border-radius:50%; background:rgba(45,212,191,.13); filter:blur(2px); }
    .eyebrow,.section-kicker { color:#5eead4; font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:.72rem; font-weight:500; letter-spacing:.12em; text-transform:uppercase; }
    .hero h1 { margin:.55rem 0 .35rem; color:#f1f5f9; font-size:clamp(2rem,4vw,3rem); font-weight:800; letter-spacing:-.055em; }
    .hero p { max-width:760px; margin:0; color:#a8b5c8; font-size:1rem; }
    .section-title { margin:.1rem 0 .2rem; color:#f1f5f9; font-size:1.35rem; font-weight:700; }
    .section-copy { margin:0 0 1rem; color:#94a3b8; }
    [data-testid="stMetric"] { min-height:100px; padding:1rem 1.1rem; border:1px solid rgba(148,163,184,.14); border-radius:14px; background:linear-gradient(145deg,rgba(21,33,51,.96),rgba(15,25,40,.92)); }
    [data-testid="stMetricLabel"] p { color:#9aabc0; font-size:.78rem; }
    [data-testid="stMetricValue"] { color:#f1f5f9; font-weight:700; }
    [data-testid="stVerticalBlockBorderWrapper"] { border-color:rgba(148,163,184,.16); border-radius:16px; background:rgba(15,25,40,.55); }
    div[data-testid="stDataFrame"] { border:1px solid rgba(148,163,184,.14); border-radius:12px; overflow:hidden; }
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
    st.markdown("### Banker's algorithm")
    st.markdown(
        """
        <div style="margin-top:1.2rem;padding:1rem;border-radius:12px;border:1px solid rgba(148,163,184,.14);background:rgba(255,255,255,.025)">
          <div style="color:#5eead4;font-weight:700;font-size:.84rem">SAFETY FIRST</div>
          <p style="font-size:.84rem;line-height:1.55;margin:.5rem 0 0">
            A safe state has at least one order in which every process can finish
            using the available resources and resources released by completed processes.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <section class="hero">
      <div class="eyebrow">OS lab · deadlock avoidance</div>
      <h1>Banker's algorithm</h1>
      <p>Edit the resource state, inspect the calculated Need matrix, find a safe sequence,
      and test a resource request without mutating the original state.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

def _resource_ids(count: int) -> list[str]:
    return [chr(ord("A") + index) for index in range(count)]


def _process_ids(count: int) -> list[str]:
    return [f"P{index}" for index in range(count)]


if "banker_available" not in st.session_state:
    st.session_state.banker_available = pd.DataFrame([SAMPLE_AVAILABLE], columns=RESOURCE_IDS)
if "banker_allocation" not in st.session_state:
    st.session_state.banker_allocation = pd.DataFrame(
        SAMPLE_ALLOCATION, index=PROCESS_IDS, columns=RESOURCE_IDS
    ).rename_axis("Process")
if "banker_maximum" not in st.session_state:
    st.session_state.banker_maximum = pd.DataFrame(
        SAMPLE_MAXIMUM, index=PROCESS_IDS, columns=RESOURCE_IDS
    ).rename_axis("Process")
if "banker_editor_version" not in st.session_state:
    st.session_state.banker_editor_version = 0
if "banker_process_count" not in st.session_state:
    st.session_state.banker_process_count = len(st.session_state.banker_allocation)
if "banker_resource_count" not in st.session_state:
    st.session_state.banker_resource_count = len(st.session_state.banker_available.columns)
if "banker_active_process_count" not in st.session_state:
    st.session_state.banker_active_process_count = len(st.session_state.banker_allocation)
if "banker_active_resource_count" not in st.session_state:
    st.session_state.banker_active_resource_count = len(st.session_state.banker_available.columns)
if "banker_preset" not in st.session_state:
    st.session_state.banker_preset = "Classic safe state"


def _matrix(rows: list[list[int]], processes: list[str], resources: list[str]) -> pd.DataFrame:
    return pd.DataFrame(rows, index=processes, columns=resources).rename_axis("Process")


def _apply_dimensions() -> None:
    process_ids = _process_ids(int(st.session_state.banker_process_count))
    resource_ids = _resource_ids(int(st.session_state.banker_resource_count))
    st.session_state.banker_active_process_count = len(process_ids)
    st.session_state.banker_active_resource_count = len(resource_ids)
    st.session_state.banker_available = (
        st.session_state.banker_available.reindex(columns=resource_ids, fill_value=0)
    )
    st.session_state.banker_allocation = (
        st.session_state.banker_allocation.reindex(
            index=process_ids, columns=resource_ids, fill_value=0
        )
        .fillna(0)
        .rename_axis("Process")
    )
    st.session_state.banker_maximum = (
        st.session_state.banker_maximum.reindex(
            index=process_ids, columns=resource_ids, fill_value=0
        )
        .fillna(0)
        .rename_axis("Process")
    )
    st.session_state.banker_editor_version += 1
    st.session_state.pop("banker_request_result", None)
    st.session_state.pop("banker_request_signature", None)
    st.session_state.pop("banker_request_error", None)


def _load_preset() -> None:
    preset = PRESETS[st.session_state.banker_preset]
    processes = [f"P{index}" for index in range(len(preset["allocation"]))]
    resources = _resource_ids(len(preset["available"]))
    st.session_state.banker_process_count = len(processes)
    st.session_state.banker_resource_count = len(resources)
    st.session_state.banker_active_process_count = len(processes)
    st.session_state.banker_active_resource_count = len(resources)
    st.session_state.banker_available = pd.DataFrame(
        [preset["available"]], columns=resources
    )
    st.session_state.banker_allocation = _matrix(
        preset["allocation"], processes, resources
    )
    st.session_state.banker_maximum = _matrix(
        preset["maximum"], processes, resources
    )
    st.session_state.banker_request_process = preset["request_process"]
    for resource, value in zip(resources, preset["request"]):
        st.session_state[f"banker_request_{resource}"] = value
    st.session_state.banker_editor_version += 1
    st.session_state.pop("banker_request_result", None)
    st.session_state.pop("banker_request_signature", None)
    st.session_state.pop("banker_request_error", None)
    st.session_state.pop("banker_input_error", None)


def reset_banker_sample() -> None:
    st.session_state.banker_process_count = len(PROCESS_IDS)
    st.session_state.banker_resource_count = len(RESOURCE_IDS)
    st.session_state.banker_active_process_count = len(PROCESS_IDS)
    st.session_state.banker_active_resource_count = len(RESOURCE_IDS)
    st.session_state.banker_preset = "Classic safe state"
    st.session_state.banker_available = pd.DataFrame([SAMPLE_AVAILABLE], columns=RESOURCE_IDS)
    st.session_state.banker_allocation = pd.DataFrame(
        SAMPLE_ALLOCATION, index=PROCESS_IDS, columns=RESOURCE_IDS
    ).rename_axis("Process")
    st.session_state.banker_maximum = pd.DataFrame(
        SAMPLE_MAXIMUM, index=PROCESS_IDS, columns=RESOURCE_IDS
    ).rename_axis("Process")
    st.session_state.banker_editor_version += 1
    st.session_state.pop("banker_request_result", None)
    st.session_state.pop("banker_request_signature", None)
    st.session_state.pop("banker_request_error", None)
    st.session_state.pop("banker_input_error", None)


st.selectbox(
    "Learning preset",
    list(PRESETS),
    key="banker_preset",
    on_change=_load_preset,
    help="Load a safe, unsafe, or deliberately invalid request scenario.",
)
dimension_cols = st.columns([1, 1, 1, 2])
dimension_cols[0].number_input(
    "Processes", min_value=1, max_value=10, step=1, key="banker_process_count"
)
dimension_cols[1].number_input(
    "Resource types", min_value=1, max_value=6, step=1, key="banker_resource_count"
)
if dimension_cols[2].button("Apply dimensions", key="banker_apply_dimensions"):
    _apply_dimensions()
    st.rerun()

PROCESS_IDS = _process_ids(int(st.session_state.banker_active_process_count))
RESOURCE_IDS = _resource_ids(int(st.session_state.banker_active_resource_count))

st.markdown('<div class="section-kicker">01 / current resource state</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Edit the matrices</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="section-copy">Edit allocation and maximum claims directly. Change the process and resource counts above; shared matrix values are preserved.</div>',
    unsafe_allow_html=True,
)
editor_version = st.session_state.banker_editor_version
matrix_cols = st.columns([1, 1.6, 1.6])
with matrix_cols[0]:
    st.markdown("#### Available")
    available_frame = st.data_editor(
        st.session_state.banker_available,
        hide_index=True,
        width="stretch",
        column_config={
            resource: st.column_config.NumberColumn(resource, min_value=0, step=1, required=True)
            for resource in RESOURCE_IDS
        },
        key=f"banker_available_editor_{editor_version}",
    )
with matrix_cols[1]:
    st.markdown("#### Allocation")
    allocation_frame = st.data_editor(
        st.session_state.banker_allocation,
        hide_index=False,
        width="stretch",
        column_config={
            "Process": st.column_config.TextColumn("Process", disabled=True),
            **{
                resource: st.column_config.NumberColumn(
                    resource, min_value=0, step=1, required=True
                )
                for resource in RESOURCE_IDS
            },
        },
        key=f"banker_allocation_editor_{editor_version}",
    )
with matrix_cols[2]:
    st.markdown("#### Maximum")
    maximum_frame = st.data_editor(
        st.session_state.banker_maximum,
        hide_index=False,
        width="stretch",
        column_config={
            "Process": st.column_config.TextColumn("Process", disabled=True),
            **{
                resource: st.column_config.NumberColumn(
                    resource, min_value=0, step=1, required=True
                )
                for resource in RESOURCE_IDS
            },
        },
        key=f"banker_maximum_editor_{editor_version}",
    )

st.session_state.banker_available = available_frame
st.session_state.banker_allocation = allocation_frame
st.session_state.banker_maximum = maximum_frame
reset_col, _, _ = st.columns([1.3, 1, 2.7])
reset_col.button("↺  Reset sample matrices", on_click=reset_banker_sample)

try:
    process_ids = allocation_frame.index.astype(str).tolist()
    if process_ids != maximum_frame.index.astype(str).tolist():
        raise ValueError("Allocation and Maximum process rows must match.")
    state = create_state(
        available_frame.iloc[0][RESOURCE_IDS].tolist(),
        allocation_frame[RESOURCE_IDS].values.tolist(),
        maximum_frame[RESOURCE_IDS].values.tolist(),
    )
    baseline_safety = check_safety(state)
    st.session_state.pop("banker_input_error", None)
except (KeyError, IndexError, TypeError, ValueError) as exc:
    state = None
    baseline_safety = None
    st.session_state.banker_input_error = str(exc)

if st.session_state.get("banker_input_error"):
    st.error(st.session_state.banker_input_error)
    st.session_state.pop("banker_request_result", None)
    st.stop()

assert state is not None
assert baseline_safety is not None
state_signature = (state.available, state.allocation, state.maximum)
need_frame = pd.DataFrame(state.need, index=process_ids, columns=RESOURCE_IDS).rename_axis(
    "Process"
)

st.markdown('<div class="section-kicker" style="margin-top:1.8rem">02 / calculated need</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Need = Maximum − Allocation</div>', unsafe_allow_html=True)
st.dataframe(need_frame, width="stretch")

st.markdown('<div class="section-kicker" style="margin-top:1.8rem">03 / safety check</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Can every process finish?</div>', unsafe_allow_html=True)
safety_cols = st.columns([1, 3])
safety_cols[0].metric("Current state", "SAFE" if baseline_safety.is_safe else "UNSAFE")
if baseline_safety.is_safe:
    safe_sequence = " → ".join(process_ids[index] for index in baseline_safety.safe_sequence)
    safety_cols[1].success(f"Safe sequence found: {safe_sequence}")
else:
    blocked = ", ".join(process_ids[index] for index in baseline_safety.unfinished_processes)
    safety_cols[1].warning(
        f"No safe sequence exists. {blocked} cannot complete with the remaining Work vector. "
        "An unsafe state means safety is not guaranteed; it does not by itself prove a deadlock."
    )

trace_rows = [
    {
        "Step": step_number,
        "Process that can finish": process_ids[step.process_index],
        "Work before": str(list(step.work_before)),
        "Finish before": str(
            [index in baseline_safety.safe_sequence[: step_number - 1] for index in range(state.process_count)]
        ),
        "Need ≤ Work": "Yes",
        "Allocation released": str(list(step.released_allocation)),
        "Work after": str(list(step.work_after)),
        "Finish after": str(
            [index in baseline_safety.safe_sequence[:step_number] for index in range(state.process_count)]
        ),
    }
    for step_number, step in enumerate(baseline_safety.steps, start=1)
]
if trace_rows:
    st.markdown("#### Safety algorithm trace")
    st.caption("At each step, choose an unfinished process whose entire Need vector is no greater than Work; then add its Allocation back to Work.")
    walkthrough_step = st.slider(
        "Step through the safety check",
        min_value=0,
        max_value=len(baseline_safety.steps),
        value=0,
        key="banker_safety_walkthrough",
        help="Move one step at a time to see the Work vector grow and Finish flags change.",
    )
    completed_before = baseline_safety.safe_sequence[:walkthrough_step]
    work_now = (
        state.available
        if walkthrough_step == 0
        else baseline_safety.steps[walkthrough_step - 1].work_after
    )
    finish_now = [
        process_index in completed_before for process_index in range(state.process_count)
    ]
    work_cols = st.columns([1, 2])
    work_cols[0].metric("Walkthrough", f"{walkthrough_step} / {len(baseline_safety.steps)}")
    work_cols[1].info(
        f"Work = {list(work_now)} · Finish = {finish_now}"
        + (
            f" · Next candidate: {process_ids[baseline_safety.steps[walkthrough_step].process_index]}"
            if walkthrough_step < len(baseline_safety.steps)
            else " · Every process can finish."
        )
    )
    if walkthrough_step:
        st.dataframe(
            pd.DataFrame(trace_rows).head(walkthrough_step),
            hide_index=True,
            width="stretch",
        )
    else:
        st.caption("No process has completed yet; Work still equals Available.")
elif not baseline_safety.is_safe:
    st.info("No process can satisfy Need ≤ Available, so the safety check cannot make progress.")

st.markdown('<div class="section-kicker" style="margin-top:1.8rem">04 / resource-request simulation</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">What if a process requests resources?</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-copy">Requests are tested against this state as a tentative allocation. The edited base matrices are never changed by a request simulation.</div>',
    unsafe_allow_html=True,
)
request_cols = st.columns([1.3, 3])
request_process = request_cols[0].selectbox(
    "Requesting process", process_ids, key="banker_request_process"
)
request_values: list[int] = []
for column, resource in zip(request_cols[1].columns(len(RESOURCE_IDS)), RESOURCE_IDS):
    request_values.append(
        int(
            column.number_input(
                f"Request · {resource}",
                min_value=0,
                value=0,
                step=1,
                key=f"banker_request_{resource}",
            )
        )
    )
request_clicked = st.button("Simulate request", type="primary")
if request_clicked:
    try:
        st.session_state.banker_request_result = simulate_request(
            state, process_ids.index(request_process), request_values
        )
        st.session_state.banker_request_signature = state_signature
        st.session_state.pop("banker_request_error", None)
    except ValueError as exc:
        st.session_state.banker_request_error = str(exc)
        st.session_state.pop("banker_request_result", None)

if st.session_state.get("banker_request_error"):
    st.error(st.session_state.banker_request_error)
if (
    "banker_request_result" in st.session_state
    and st.session_state.get("banker_request_signature") == state_signature
):
    request_result = st.session_state.banker_request_result
    if request_result.granted:
        requested_sequence = " → ".join(
            process_ids[index] for index in request_result.safety.safe_sequence
        )
        st.success(f"{request_result.reason} Safe sequence: {requested_sequence}")
        st.caption("This is a simulation only; the editable base matrices remain unchanged.")
    else:
        st.warning(request_result.reason)
        if request_result.safety and request_result.safety.steps:
            st.caption("The partial safety trace shows which processes could complete before the tentative state became stuck.")
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "Step": step_number,
                            "Process that can finish": process_ids[step.process_index],
                            "Work before": str(list(step.work_before)),
                            "Work after release": str(list(step.work_after)),
                        }
                        for step_number, step in enumerate(
                            request_result.safety.steps, start=1
                        )
                    ]
                ),
                hide_index=True,
                width="stretch",
            )

st.markdown('<div class="section-kicker" style="margin-top:1.8rem">05 / resource visualization</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Allocation and remaining claims</div>', unsafe_allow_html=True)
figure = make_subplots(
    rows=1,
    cols=2,
    subplot_titles=("Current allocation", "Remaining need"),
    horizontal_spacing=0.16,
)
for column_index, (title, matrix) in enumerate(
    (("Allocation", state.allocation), ("Need", state.need)), start=1
):
    figure.add_trace(
        go.Heatmap(
            z=matrix,
            x=RESOURCE_IDS,
            y=process_ids,
            text=matrix,
            texttemplate="%{text}",
            colorscale=[[0, "#132238"], [0.5, "#126e68"], [1, "#5eead4"]],
            showscale=column_index == 2,
            colorbar={"title": "Units"} if column_index == 2 else None,
            hovertemplate="Process %{y}<br>Resource %{x}<br>Units: %{z}<extra></extra>",
        ),
        row=1,
        col=column_index,
    )
figure.update_layout(
    height=340,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font={"color": "#dbe7f4"},
    margin={"l": 30, "r": 30, "t": 55, "b": 25},
)
figure.update_yaxes(autorange="reversed", title_text=None)
figure.update_xaxes(title_text="Resource type")
st.plotly_chart(figure, width="stretch")

resource_cols = st.columns(len(RESOURCE_IDS))
for index, (column, resource) in enumerate(zip(resource_cols, RESOURCE_IDS)):
    allocated_total = sum(row[index] for row in state.allocation)
    column.metric(
        f"Resource {resource}",
        f"{state.available[index]} available",
        f"{allocated_total} allocated",
    )
