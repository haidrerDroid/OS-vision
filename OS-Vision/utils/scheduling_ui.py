"""Shared Streamlit interface for the separate CPU scheduling pages."""

from __future__ import annotations

import re
from collections.abc import Callable

import pandas as pd
import plotly.express as px
import streamlit as st

from algorithms.fcfs import schedule_fcfs
from algorithms.round_robin import schedule_round_robin
from algorithms.scheduling import ScheduleResult
from algorithms.sjf import schedule_sjf
from algorithms.srtf import schedule_srtf
from visualizations.process_animation import build_process_animation_html


SAMPLE_DATA = pd.DataFrame(
    [
        {"Process ID": "P1", "Arrival Time": 0, "Burst Time": 5},
        {"Process ID": "P2", "Arrival Time": 1, "Burst Time": 3},
        {"Process ID": "P3", "Arrival Time": 2, "Burst Time": 8},
        {"Process ID": "P4", "Arrival Time": 10, "Burst Time": 2},
    ]
)

SCENARIOS = {
    "Balanced workload": SAMPLE_DATA,
    "Long job blocks short jobs": pd.DataFrame(
        [
            {"Process ID": "P1", "Arrival Time": 0, "Burst Time": 9},
            {"Process ID": "P2", "Arrival Time": 1, "Burst Time": 2},
            {"Process ID": "P3", "Arrival Time": 2, "Burst Time": 1},
        ]
    ),
    "CPU idle gaps": pd.DataFrame(
        [
            {"Process ID": "P1", "Arrival Time": 3, "Burst Time": 2},
            {"Process ID": "P2", "Arrival Time": 9, "Burst Time": 1},
            {"Process ID": "P3", "Arrival Time": 12, "Burst Time": 3},
        ]
    ),
    "Simultaneous arrivals": pd.DataFrame(
        [
            {"Process ID": "P1", "Arrival Time": 0, "Burst Time": 4},
            {"Process ID": "P2", "Arrival Time": 0, "Burst Time": 2},
            {"Process ID": "P3", "Arrival Time": 0, "Burst Time": 3},
        ]
    ),
}

ALGORITHMS: dict[str, Callable[..., ScheduleResult]] = {
    "FCFS": schedule_fcfs,
    "SJF": schedule_sjf,
    "SRTF": schedule_srtf,
    "Round Robin": schedule_round_robin,
}

DESCRIPTIONS = {
    "FCFS": (
        "First Come, First Served",
        "Processes run in arrival order. Once selected, a process keeps the CPU until it completes.",
    ),
    "SJF": (
        "Shortest Job First",
        "The non-preemptive scheduler selects the ready process with the smallest CPU burst.",
    ),
    "SRTF": (
        "Shortest Job First with Preemption",
        "The preemptive scheduler always selects the ready process with the least remaining CPU time.",
    ),
    "Round Robin": (
        "Round Robin",
        "Processes share the CPU in FIFO order. An unfinished process returns to the queue after its time slice.",
    ),
}

STYLE = """
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
.hero p { max-width:700px; margin:0; color:#a8b5c8; font-size:1rem; }
.section-title { margin:.1rem 0 .2rem; color:#f1f5f9; font-size:1.35rem; font-weight:700; }
.section-copy { margin:0 0 1rem; color:#94a3b8; }
[data-testid="stMetric"] { min-height:112px; padding:1rem 1.1rem; border:1px solid rgba(148,163,184,.14); border-radius:14px; background:linear-gradient(145deg,rgba(21,33,51,.96),rgba(15,25,40,.92)); }
[data-testid="stMetricLabel"] p { color:#9aabc0; font-size:.78rem; }
[data-testid="stMetricValue"] { color:#f1f5f9; font-weight:700; }
[data-testid="stVerticalBlockBorderWrapper"] { border-color:rgba(148,163,184,.16); border-radius:16px; background:rgba(15,25,40,.55); }
div[data-testid="stDataFrame"] { border:1px solid rgba(148,163,184,.14); border-radius:12px; overflow:hidden; }
.stButton>button,.stDownloadButton>button { min-height:2.65rem; border-radius:10px; font-weight:600; transition:transform 120ms ease,border-color 120ms ease; }
.stButton>button:hover,.stDownloadButton>button:hover { transform:translateY(-1px); }
</style>
"""


def _state_keys(algorithm: str) -> dict[str, str]:
    prefix = re.sub(r"[^a-z0-9]+", "_", algorithm.lower()).strip("_")
    return {
        "input": f"{prefix}_input",
        "editor_version": f"{prefix}_editor_version",
        "scenario": f"{prefix}_scenario",
        "result": f"{prefix}_result",
        "error": f"{prefix}_error",
    }


def render_scheduling_page(algorithm: str) -> None:
    """Render one self-contained scheduler page with its own editable workload."""

    if algorithm not in ALGORITHMS:
        raise ValueError(f"Unknown CPU scheduling algorithm: {algorithm}")

    full_name, explanation = DESCRIPTIONS[algorithm]
    keys = _state_keys(algorithm)
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown(
        f"""
        <section class="hero">
          <div class="eyebrow">OS lab · CPU scheduling</div>
          <h1>{full_name}</h1>
          <p>{explanation} Edit the workload, run this scheduler, and follow each process through the live timeline.</p>
        </section>
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
        st.markdown('<div class="section-kicker">Active simulator</div>', unsafe_allow_html=True)
        st.markdown(f"### {full_name}")
        st.markdown(
            f"""
            <div style="margin-top:1.2rem;padding:1rem;border-radius:12px;border:1px solid rgba(148,163,184,.14);background:rgba(255,255,255,.025)">
              <div style="color:#5eead4;font-weight:700;font-size:.84rem">SCHEDULER RULE</div>
              <p style="font-size:.84rem;line-height:1.55;margin:.5rem 0 0">{explanation}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-kicker">01 / configure workload</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Your processes</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">This simulator has its own process table and results. Other algorithm pages keep their own workloads.</div>',
        unsafe_allow_html=True,
    )

    if keys["input"] not in st.session_state:
        st.session_state[keys["input"]] = SAMPLE_DATA.copy()
    if keys["editor_version"] not in st.session_state:
        st.session_state[keys["editor_version"]] = 0
    if keys["scenario"] not in st.session_state:
        st.session_state[keys["scenario"]] = "Balanced workload"

    def clear_run() -> None:
        st.session_state.pop(keys["result"], None)
        st.session_state.pop(keys["error"], None)

    def load_scenario() -> None:
        st.session_state[keys["input"]] = SCENARIOS[st.session_state[keys["scenario"]]].copy()
        st.session_state[keys["editor_version"]] += 1
        clear_run()

    def reset_sample() -> None:
        st.session_state[keys["scenario"]] = "Balanced workload"
        st.session_state[keys["input"]] = SAMPLE_DATA.copy()
        st.session_state[keys["editor_version"]] += 1
        clear_run()

    st.selectbox(
        "Load a learning scenario",
        options=list(SCENARIOS),
        key=keys["scenario"],
        on_change=load_scenario,
        help=f"Load a workload to explore {full_name}.",
    )
    with st.container(border=True):
        st.markdown(
            '<span class="section-kicker">WORKLOAD INPUT</span><span style="color:#64748b;font-size:.8rem">&nbsp; · &nbsp; Add rows directly in the table</span>',
            unsafe_allow_html=True,
        )
        edited_data = st.data_editor(
            st.session_state[keys["input"]],
            num_rows="dynamic",
            width="stretch",
            hide_index=True,
            column_config={
                "Process ID": st.column_config.TextColumn("Process ID", required=True),
                "Arrival Time": st.column_config.NumberColumn(
                    "Arrival Time", min_value=0, step=1, required=True
                ),
                "Burst Time": st.column_config.NumberColumn(
                    "Burst Time", min_value=1, step=1, required=True
                ),
            },
            key=f"{keys['input']}_editor_{st.session_state[keys['editor_version']]}",
        )
    st.session_state[keys["input"]] = edited_data

    if algorithm == "Round Robin":
        quantum_col, run_col, reset_col = st.columns([1, 1.2, 1.2])
        quantum = int(
            quantum_col.number_input(
                "Time quantum", min_value=1, value=2, step=1, key="round_robin_quantum"
            )
        )
    else:
        run_col, reset_col = st.columns([1.2, 1.2])
        quantum = None
    run_clicked = run_col.button(f"Run {algorithm}", type="primary", use_container_width=True)
    reset_col.button("↺  Reset sample", on_click=reset_sample, use_container_width=True)

    if run_clicked:
        try:
            records = edited_data.rename(
                columns={
                    "Process ID": "process_id",
                    "Arrival Time": "arrival_time",
                    "Burst Time": "burst_time",
                }
            ).to_dict("records")
            if algorithm == "Round Robin":
                result = schedule_round_robin(records, quantum)
            else:
                result = ALGORITHMS[algorithm](records)
            st.session_state[keys["result"]] = result
            st.session_state.pop(keys["error"], None)
        except (TypeError, ValueError) as exc:
            st.session_state.pop(keys["result"], None)
            st.session_state[keys["error"]] = str(exc)

    if st.session_state.get(keys["error"]):
        st.error(st.session_state[keys["error"]])

    result: ScheduleResult | None = st.session_state.get(keys["result"])
    if result is None:
        return

    metric_cols = st.columns(5)
    metric_cols[0].metric("Avg. waiting time", f"{result.average_waiting_time:.2f}")
    metric_cols[1].metric("Avg. turnaround time", f"{result.average_turnaround_time:.2f}")
    metric_cols[2].metric("Avg. response time", f"{result.average_response_time:.2f}")
    metric_cols[3].metric("CPU utilization", f"{result.cpu_utilization:.1%}")
    metric_cols[4].metric("Throughput", f"{result.throughput:.3f} processes/unit")

    if algorithm == "FCFS" and len(result.processes) > 1:
        first = result.processes[0]
        delayed_short_jobs = [
            process
            for process in result.processes[1:]
            if process.burst_time < first.burst_time and process.waiting_time > 0
        ]
        if delayed_short_jobs:
            delayed = ", ".join(process.process_id for process in delayed_short_jobs)
            st.info(
                f"Convoy effect: long-running {first.process_id} (burst {first.burst_time}) "
                f"runs first and makes shorter job(s) {delayed} wait."
            )

    st.markdown(
        '<div class="section-kicker" style="margin-top:1.7rem">02 / execution trace</div>'
        f'<div class="section-title">Live {full_name} simulation</div>'
        '<div class="section-copy">The process flow, scheduler event log, and Gantt cursor follow the same simulation clock.</div>',
        unsafe_allow_html=True,
    )
    st.iframe(
        build_process_animation_html(result, algorithm, quantum),
        height="content",
        alt=f"Animated {full_name} process flow, event log, and synchronized Gantt chart",
    )

    st.markdown(
        '<div class="section-kicker" style="margin-top:1.7rem">03 / results</div>'
        '<div class="section-title">Process performance</div>',
        unsafe_allow_html=True,
    )
    metrics_table = pd.DataFrame(
        [
            {
                "Process ID": item.process_id,
                "Arrival Time (AT)": item.arrival_time,
                "Burst Time (BT)": item.burst_time,
                "Start Time": item.start_time,
                "Completion Time (CT)": item.completion_time,
                "Turnaround Time (TAT)": item.turnaround_time,
                "Waiting Time (WT)": item.waiting_time,
                "Response Time (RT)": item.response_time,
            }
            for item in result.processes
        ]
    )
    with st.container(border=True):
        st.dataframe(metrics_table, hide_index=True, width="stretch")
        st.caption(
            f"Final completion time: {result.makespan} · "
            f"Average waiting time: {result.average_waiting_time:.2f} · "
            f"Average turnaround time: {result.average_turnaround_time:.2f}"
        )
        suffix = f"_q{quantum}" if quantum is not None else ""
        st.download_button(
            "↓  Download results as CSV",
            metrics_table.to_csv(index=False).encode("utf-8"),
            file_name=f"osvision_{algorithm.lower().replace(' ', '_')}{suffix}_metrics.csv",
            mime="text/csv",
        )

    if algorithm == "Round Robin":
        st.markdown(
            '<div class="section-kicker" style="margin-top:1.7rem">04 / quantum impact</div>'
            '<div class="section-title">How does the time slice change performance?</div>'
            '<div class="section-copy">Each row reruns Round Robin on this exact workload. Context switches count changes between consecutive executed process IDs; repeated slices for the same process are not counted as switches.</div>',
            unsafe_allow_html=True,
        )
        quantum_limit = st.slider(
            "Compare quantum values from 1 through",
            min_value=1,
            max_value=10,
            value=6,
            key="round_robin_analysis_limit",
        )
        actual_workload = [
            {
                "process_id": item.process_id,
                "arrival_time": item.arrival_time,
                "burst_time": item.burst_time,
            }
            for item in result.processes
        ]
        quantum_rows = []
        for candidate_quantum in range(1, quantum_limit + 1):
            candidate = schedule_round_robin(actual_workload, candidate_quantum)
            process_runs = [
                interval.process_id
                for interval in candidate.intervals
                if interval.process_id is not None
            ]
            context_switches = sum(
                previous != current
                for previous, current in zip(process_runs, process_runs[1:])
            )
            quantum_rows.append(
                {
                    "Quantum": candidate_quantum,
                    "Average waiting time": candidate.average_waiting_time,
                    "Average response time": candidate.average_response_time,
                    "Process switches": context_switches,
                    "CPU utilization": candidate.cpu_utilization,
                    "Throughput": candidate.throughput,
                }
            )
        quantum_frame = pd.DataFrame(quantum_rows)
        st.plotly_chart(
            px.line(
                quantum_frame,
                x="Quantum",
                y=["Average waiting time", "Average response time"],
                markers=True,
                title="Waiting and response time by quantum",
                template="plotly_dark",
            ),
            width="stretch",
        )
        st.dataframe(
            quantum_frame.style.format(
                {
                    "Average waiting time": "{:.2f}",
                    "Average response time": "{:.2f}",
                    "CPU utilization": "{:.1%}",
                    "Throughput": "{:.3f}",
                }
            ),
            hide_index=True,
            width="stretch",
        )
