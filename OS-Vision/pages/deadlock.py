"""Interactive resource-allocation graph and deadlock-detection simulator."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from algorithms.deadlock import (
    DeadlockResult,
    ResourceState,
    create_state,
    detect_deadlock,
    grant_request,
    has_resource_allocation_cycle,
    queue_request,
    release_resources,
)


st.set_page_config(page_title="OSVision | Deadlock Simulator", page_icon="⚙️", layout="wide")

PROCESS_IDS = ["P1", "P2", "P3"]
RESOURCE_IDS = ["R1", "R2"]

SCENARIOS = {
    "Single-instance cycle — deadlock": {
        "total": [1, 1],
        "allocation": [[1, 0], [0, 1], [0, 0]],
        "request": [[0, 1], [1, 0], [0, 0]],
    },
    "Cycle with multiple instances — no deadlock": {
        "total": [3, 2],
        "allocation": [[1, 0], [0, 1], [1, 0]],
        "request": [[0, 1], [1, 0], [0, 0]],
    },
    "Queued request — no cycle": {
        "total": [3, 2],
        "allocation": [[1, 0], [0, 2], [1, 0]],
        "request": [[0, 0], [1, 0], [0, 0]],
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
    .hero p { max-width:780px; margin:0; color:#a8b5c8; font-size:1rem; }
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
    st.markdown("### Deadlock simulator")
    st.markdown(
        """
        <div style="margin-top:1.2rem;padding:1rem;border-radius:12px;border:1px solid rgba(148,163,184,.14);background:rgba(255,255,255,.025)">
          <div style="color:#5eead4;font-weight:700;font-size:.84rem">INSTANCES MATTER</div>
          <p style="font-size:.84rem;line-height:1.55;margin:.5rem 0 0">
            A resource-allocation graph cycle alone is not enough to prove deadlock
            when resource types have multiple instances.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <section class="hero">
      <div class="eyebrow">OS lab · resource allocation</div>
      <h1>Deadlock simulator</h1>
      <p>Allocate and release real resource instances, queue outstanding requests,
      inspect the resource-allocation graph, and run the multi-instance deadlock detector.</p>
    </section>
    """,
    unsafe_allow_html=True,
)


def _process_ids(count: int) -> list[str]:
    return [f"P{index + 1}" for index in range(count)]


def _resource_ids(count: int) -> list[str]:
    return [f"R{index + 1}" for index in range(count)]


def _matrix_frame(
    rows: list[list[int]], columns: list[str], processes: list[str] | None = None
) -> pd.DataFrame:
    return pd.DataFrame(
        rows, index=processes or PROCESS_IDS, columns=columns
    ).rename_axis("Process")


def _load_scenario() -> None:
    scenario = SCENARIOS[st.session_state.deadlock_scenario]
    process_ids = _process_ids(len(scenario["allocation"]))
    resource_ids = _resource_ids(len(scenario["total"]))
    st.session_state.deadlock_process_count = len(process_ids)
    st.session_state.deadlock_resource_count = len(resource_ids)
    st.session_state.deadlock_total = pd.DataFrame(
        [scenario["total"]], columns=resource_ids
    )
    st.session_state.deadlock_allocation = _matrix_frame(
        scenario["allocation"], resource_ids, process_ids
    )
    st.session_state.deadlock_request = _matrix_frame(
        scenario["request"], resource_ids, process_ids
    )
    st.session_state.deadlock_editor_version += 1
    st.session_state.deadlock_operation_log = []
    st.session_state.deadlock_undo_stack = []
    st.session_state.pop("deadlock_operation_error", None)


if "deadlock_scenario" not in st.session_state:
    st.session_state.deadlock_editor_version = 0
    st.session_state.deadlock_scenario = "Single-instance cycle — deadlock"
    _load_scenario()
if "deadlock_undo_stack" not in st.session_state:
    st.session_state.deadlock_undo_stack = []

st.markdown('<div class="section-kicker">01 / choose a scenario</div>', unsafe_allow_html=True)
st.selectbox(
    "Scenario",
    list(SCENARIOS),
    key="deadlock_scenario",
    on_change=_load_scenario,
    help="Compare a genuine deadlock with a resource-allocation cycle that is not deadlocked.",
)
dimension_cols = st.columns([1, 1, 1, 2])
dimension_cols[0].number_input(
    "Processes", min_value=1, max_value=10, step=1, key="deadlock_process_count"
)
dimension_cols[1].number_input(
    "Resource types", min_value=1, max_value=6, step=1, key="deadlock_resource_count"
)


def _apply_dimensions() -> None:
    global PROCESS_IDS, RESOURCE_IDS
    PROCESS_IDS = _process_ids(int(st.session_state.deadlock_process_count))
    RESOURCE_IDS = _resource_ids(int(st.session_state.deadlock_resource_count))
    st.session_state.deadlock_total = st.session_state.deadlock_total.reindex(
        columns=RESOURCE_IDS, fill_value=0
    )
    st.session_state.deadlock_allocation = (
        st.session_state.deadlock_allocation.reindex(
            index=PROCESS_IDS, columns=RESOURCE_IDS, fill_value=0
        )
        .fillna(0)
        .rename_axis("Process")
    )
    st.session_state.deadlock_request = (
        st.session_state.deadlock_request.reindex(
            index=PROCESS_IDS, columns=RESOURCE_IDS, fill_value=0
        )
        .fillna(0)
        .rename_axis("Process")
    )
    st.session_state.deadlock_editor_version += 1
    st.session_state.deadlock_undo_stack = []
    st.session_state.deadlock_operation_log = []


if dimension_cols[2].button("Apply dimensions", key="deadlock_apply_dimensions"):
    _apply_dimensions()
    st.rerun()
PROCESS_IDS = _process_ids(len(st.session_state.deadlock_allocation))
RESOURCE_IDS = list(st.session_state.deadlock_total.columns)
st.markdown('<div class="section-kicker" style="margin-top:1rem">02 / current resource state</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Resource instances, allocations, and outstanding requests</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-copy">Available instances are derived as Total − allocated. A queued request does not own resources until it is granted.</div>',
    unsafe_allow_html=True,
)

resource_cols = st.columns([1, 1.5, 1.5])
editor_version = st.session_state.deadlock_editor_version
with resource_cols[0]:
    st.markdown("#### Total instances")
    total_frame = st.data_editor(
        st.session_state.deadlock_total,
        hide_index=True,
        width="stretch",
        column_config={
            resource: st.column_config.NumberColumn(
                resource, min_value=0, step=1, required=True
            )
            for resource in RESOURCE_IDS
        },
        key=f"deadlock_total_{editor_version}",
    )
with resource_cols[1]:
    st.markdown("#### Allocation")
    allocation_frame = st.data_editor(
        st.session_state.deadlock_allocation,
        hide_index=False,
        width="stretch",
        column_config={
            resource: st.column_config.NumberColumn(
                resource, min_value=0, step=1, required=True
            )
            for resource in RESOURCE_IDS
        },
        key=f"deadlock_allocation_{editor_version}",
    )
with resource_cols[2]:
    st.markdown("#### Outstanding request")
    request_frame = st.data_editor(
        st.session_state.deadlock_request,
        hide_index=False,
        width="stretch",
        column_config={
            resource: st.column_config.NumberColumn(
                resource, min_value=0, step=1, required=True
            )
            for resource in RESOURCE_IDS
        },
        key=f"deadlock_request_{editor_version}",
    )

st.session_state.deadlock_total = total_frame
st.session_state.deadlock_allocation = allocation_frame
st.session_state.deadlock_request = request_frame

try:
    process_ids = allocation_frame.index.astype(str).tolist()
    if process_ids != request_frame.index.astype(str).tolist():
        raise ValueError("Allocation and Request process rows must match.")
    state = create_state(
        total_frame.iloc[0][RESOURCE_IDS].tolist(),
        allocation_frame[RESOURCE_IDS].values.tolist(),
        request_frame[RESOURCE_IDS].values.tolist(),
    )
    detection = detect_deadlock(state)
    graph_has_cycle = has_resource_allocation_cycle(state)
    st.session_state.deadlock_state = state
    st.session_state.deadlock_result = detection
    st.session_state.deadlock_has_cycle = graph_has_cycle
    st.session_state.pop("deadlock_input_error", None)
except (KeyError, IndexError, TypeError, ValueError) as exc:
    state = None
    detection = None
    graph_has_cycle = False
    st.session_state.deadlock_input_error = str(exc)

if st.session_state.get("deadlock_input_error"):
    st.error(st.session_state.deadlock_input_error)
    st.stop()

assert state is not None
assert detection is not None

st.markdown('<div class="section-kicker" style="margin-top:1.8rem">03 / detection result</div>', unsafe_allow_html=True)
status_cols = st.columns([1, 3])
status_cols[0].metric(
    "Current state", "DEADLOCK" if detection.is_deadlocked else "NO DEADLOCK"
)
if detection.is_deadlocked:
    blocked = ", ".join(process_ids[index] for index in detection.deadlocked_processes)
    status_cols[1].error(
        f"Deadlock detected. {blocked} cannot satisfy their outstanding requests "
        f"with the available Work vector {list(detection.final_work)}."
    )
else:
    completion_order = " → ".join(
        process_ids[index] for index in detection.completed_processes
    )
    status_cols[1].success(f"No deadlock detected. Completion order: {completion_order}")
    if graph_has_cycle:
        st.info(
            "The resource-type graph contains a cycle, but this is not a deadlock: "
            "multiple instances let the detector make progress and find a completion order."
        )

initially_finished = {
    index for index, row in enumerate(state.allocation) if not any(row)
}
finished = set(initially_finished)
trace_rows = []
for step_number, step in enumerate(detection.steps, start=1):
    finish_before = [index in finished for index in range(state.process_count)]
    finished.add(step.process_index)
    trace_rows.append(
        {
            "Step": step_number,
            "Process that can finish": process_ids[step.process_index],
            "Request ≤ Work": "Yes",
            "Work before": str(list(step.work_before)),
            "Finish before": str(finish_before),
            "Released allocation": str(list(step.released_allocation)),
            "Work after": str(list(step.work_after)),
            "Finish after": str(
                [index in finished for index in range(state.process_count)]
            ),
        }
    )
if trace_rows:
    st.markdown("#### Detection trace")
    st.caption("The detector starts with Work = Available. It finishes any process whose outstanding Request is no greater than Work, then adds that process's Allocation back.")
    walkthrough_step = st.slider(
        "Step through deadlock detection",
        min_value=0,
        max_value=len(detection.steps),
        value=0,
        key="deadlock_detection_walkthrough",
    )
    completed_by_step = {
        *initially_finished,
        *(step.process_index for step in detection.steps[:walkthrough_step]),
    }
    work_now = (
        state.available
        if walkthrough_step == 0
        else detection.steps[walkthrough_step - 1].work_after
    )
    work_cols = st.columns([1, 2])
    work_cols[0].metric(
        "Walkthrough", f"{walkthrough_step} / {len(detection.steps)}"
    )
    next_process = (
        process_ids[detection.steps[walkthrough_step].process_index]
        if walkthrough_step < len(detection.steps)
        else None
    )
    work_cols[1].info(
        f"Work = {list(work_now)} · Finish = "
        f"{[index in completed_by_step for index in range(state.process_count)]}"
        + (f" · Next candidate: {next_process}" if next_process else "")
    )
    if walkthrough_step:
        st.dataframe(
            pd.DataFrame(trace_rows).head(walkthrough_step),
            hide_index=True,
            width="stretch",
        )
    else:
        st.caption("No process has been released yet; Work still equals Available.")
if detection.deadlocked_processes:
    st.warning(
        "Unfinished processes: "
        + ", ".join(process_ids[index] for index in detection.deadlocked_processes)
    )


st.markdown('<div class="section-kicker" style="margin-top:1.8rem">04 / resource operations</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Change the running resource state</div>', unsafe_allow_html=True)
operation_cols = st.columns([1.2, 1.2, 1.2, 1])
operation_process = operation_cols[0].selectbox(
    "Process", process_ids, key="deadlock_operation_process"
)
operation_resource = operation_cols[1].selectbox(
    "Resource", RESOURCE_IDS, key="deadlock_operation_resource"
)
operation_units = int(
    operation_cols[2].number_input(
        "Units", min_value=1, value=1, step=1, key="deadlock_operation_units"
    )
)
operation_index = process_ids.index(operation_process)
resource_index = RESOURCE_IDS.index(operation_resource)
queue_clicked = operation_cols[3].button("Queue request", use_container_width=True)
grant_clicked, release_clicked, _ = st.columns([1.2, 1.2, 2.2])
grant_clicked = grant_clicked.button("Grant queued request", use_container_width=True)
release_clicked = release_clicked.button("Release resources", use_container_width=True)

if queue_clicked or grant_clicked or release_clicked:
    try:
        if queue_clicked:
            new_state = queue_request(
                state, operation_index, resource_index, operation_units
            )
            message = (
                f"{operation_process} queued a request for {operation_units} "
                f"instance(s) of {operation_resource}; allocation is unchanged."
            )
        elif grant_clicked:
            new_state = grant_request(
                state, operation_index, resource_index, operation_units
            )
            message = (
                f"Granted {operation_units} instance(s) of {operation_resource} "
                f"to {operation_process}."
            )
        else:
            new_state = release_resources(
                state, operation_index, resource_index, operation_units
            )
            message = (
                f"{operation_process} released {operation_units} instance(s) "
                f"of {operation_resource}."
            )
        st.session_state.deadlock_undo_stack = [
            *st.session_state.get("deadlock_undo_stack", []),
            state,
        ][-20:]
        st.session_state.deadlock_total = pd.DataFrame(
            [new_state.total], columns=RESOURCE_IDS
        )
        st.session_state.deadlock_allocation = _matrix_frame(
            [list(row) for row in new_state.allocation], RESOURCE_IDS
        )
        st.session_state.deadlock_request = _matrix_frame(
            [list(row) for row in new_state.request], RESOURCE_IDS
        )
        st.session_state.deadlock_editor_version += 1
        st.session_state.deadlock_operation_log = [
            *st.session_state.get("deadlock_operation_log", []),
            message,
        ]
        st.session_state.pop("deadlock_operation_error", None)
        st.rerun()
    except ValueError as exc:
        st.session_state.deadlock_operation_error = str(exc)

if st.session_state.get("deadlock_operation_error"):
    st.error(st.session_state.deadlock_operation_error)
undo_col, _ = st.columns([1, 3])
if undo_col.button(
    "↶  Undo last operation",
    key="deadlock_undo",
    disabled=not st.session_state.get("deadlock_undo_stack"),
):
    previous = st.session_state.deadlock_undo_stack.pop()
    st.session_state.deadlock_total = pd.DataFrame(
        [previous.total], columns=RESOURCE_IDS
    )
    st.session_state.deadlock_allocation = _matrix_frame(
        [list(row) for row in previous.allocation], RESOURCE_IDS, PROCESS_IDS
    )
    st.session_state.deadlock_request = _matrix_frame(
        [list(row) for row in previous.request], RESOURCE_IDS, PROCESS_IDS
    )
    if st.session_state.deadlock_operation_log:
        st.session_state.deadlock_operation_log.pop()
    st.session_state.deadlock_editor_version += 1
    st.rerun()
if st.session_state.get("deadlock_operation_log"):
    st.markdown("#### Operation history")
    for operation in reversed(st.session_state.deadlock_operation_log[-8:]):
        st.write(f"· {operation}")

st.button("↺  Reset scenario", key="deadlock_reset", on_click=_load_scenario)

st.markdown('<div class="section-kicker" style="margin-top:1.8rem">05 / resource-allocation graph</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Who holds resources, and who is waiting?</div>', unsafe_allow_html=True)
available = state.available
figure = go.Figure()
process_y = {process: 2 - index for index, process in enumerate(process_ids)}
resource_y = {
    resource: 2 - index * 2 / max(1, len(RESOURCE_IDS) - 1)
    for index, resource in enumerate(RESOURCE_IDS)
}

for process_index, process in enumerate(process_ids):
    for resource_index, resource in enumerate(RESOURCE_IDS):
        allocated = state.allocation[process_index][resource_index]
        requested = state.request[process_index][resource_index]
        if allocated:
            figure.add_annotation(
                x=0.2,
                y=process_y[process] + 0.08,
                ax=1.8,
                ay=resource_y[resource] + 0.08,
                xref="x",
                yref="y",
                axref="x",
                ayref="y",
                text="",
                showarrow=True,
                arrowhead=2,
                arrowwidth=2,
                arrowcolor="#38bdf8",
            )
            figure.add_annotation(
                x=1.03,
                y=(process_y[process] + resource_y[resource]) / 2 + 0.14,
                text=f"holds {allocated}",
                showarrow=False,
                font={"color": "#7dd3fc", "size": 10},
                bgcolor="rgba(11,17,32,.85)",
            )
        if requested:
            figure.add_annotation(
                x=1.8,
                y=resource_y[resource] - 0.08,
                ax=0.2,
                ay=process_y[process] - 0.08,
                xref="x",
                yref="y",
                axref="x",
                ayref="y",
                text="",
                showarrow=True,
                arrowhead=2,
                arrowwidth=2,
                arrowcolor="#fb7185",
            )
            figure.add_annotation(
                x=1.03,
                y=(process_y[process] + resource_y[resource]) / 2 - 0.14,
                text=f"requests {requested}",
                showarrow=False,
                font={"color": "#fda4af", "size": 10},
                bgcolor="rgba(11,17,32,.85)",
            )

figure.add_trace(
    go.Scatter(
        x=[0.2] * len(process_ids),
        y=[process_y[process] for process in process_ids],
        mode="markers+text",
        text=process_ids,
        textposition="middle center",
        marker={"size": 58, "color": "#173652", "line": {"color": "#60a5fa", "width": 2}},
        textfont={"color": "#eff6ff", "size": 13},
        hovertemplate="%{text}<extra>Process</extra>",
        name="Processes",
    )
)
resource_labels = [
    f"{resource}<br>{state.total[index]} instances<br>{available[index]} available"
    for index, resource in enumerate(RESOURCE_IDS)
]
figure.add_trace(
    go.Scatter(
        x=[1.8] * len(RESOURCE_IDS),
        y=[resource_y[resource] for resource in RESOURCE_IDS],
        mode="markers+text",
        text=resource_labels,
        textposition="middle center",
        marker={"size": 85, "symbol": "square", "color": "#17443f", "line": {"color": "#2dd4bf", "width": 2}},
        textfont={"color": "#effffb", "size": 11},
        hovertemplate="%{text}<extra>Resource type</extra>",
        name="Resource types",
    )
)
figure.update_layout(
    height=440,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font={"color": "#dbe7f4"},
    margin={"l": 20, "r": 20, "t": 15, "b": 20},
    xaxis={"range": [-0.4, 2.4], "visible": False, "fixedrange": True},
    yaxis={"range": [-0.7, 2.7], "visible": False, "fixedrange": True},
    showlegend=False,
)
st.plotly_chart(figure, width="stretch")
st.markdown(
    '<span style="color:#7dd3fc">━━▶ Resource → process: allocated instances</span>'
    '&nbsp;&nbsp;&nbsp;'
    '<span style="color:#fda4af">━━▶ Process → resource: outstanding request</span>',
    unsafe_allow_html=True,
)
st.caption(
    f"Resource-type graph cycle: {'yes' if graph_has_cycle else 'no'} · "
    f"Deadlock by multi-instance detection: {'yes' if detection.is_deadlocked else 'no'}"
)

instance_rows = []
for resource_index, resource in enumerate(RESOURCE_IDS):
    owners = [
        process
        for process_index, process in enumerate(process_ids)
        for _ in range(state.allocation[process_index][resource_index])
    ]
    owners.extend(["Available"] * available[resource_index])
    for instance_number, owner in enumerate(owners, start=1):
        instance_rows.append(
            {"Instance": f"{resource}#{instance_number}", "Resource": resource, "State": owner}
        )
st.markdown("#### Individual resource instances")
st.caption("Instances of the same resource type are equivalent; this view makes the aggregate allocation counts concrete.")
st.dataframe(pd.DataFrame(instance_rows), hide_index=True, width="stretch")

resource_metrics = st.columns(len(RESOURCE_IDS))
for index, (column, resource) in enumerate(zip(resource_metrics, RESOURCE_IDS)):
    allocated_total = sum(row[index] for row in state.allocation)
    column.metric(
        f"{resource} instances",
        f"{available[index]} available",
        f"{allocated_total} allocated of {state.total[index]}",
    )
