"""Predict-before-reveal practice for the OS algorithm labs."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from algorithms.bankers import check_safety, create_state as create_banker_state
from algorithms.deadlock import create_state as create_deadlock_state, detect_deadlock
from algorithms.fcfs import schedule_fcfs
from algorithms.round_robin import schedule_round_robin
from algorithms.scheduling import ScheduleResult
from algorithms.sjf import schedule_sjf
from algorithms.srtf import schedule_srtf


st.set_page_config(page_title="OSVision | Challenges", page_icon="⚙️", layout="wide")
st.markdown(
    """
    <style>
    .stApp { background: radial-gradient(ellipse at 80% 0%, rgba(13,148,136,.13), transparent 38%), #0b1120; }
    .block-container { max-width: 1200px; padding-top: 2.5rem; }
    .hero { padding:2rem 2.2rem; margin-bottom:1.6rem; border:1px solid rgba(94,234,212,.18); border-radius:20px; background:linear-gradient(115deg,rgba(18,35,52,.98),rgba(13,27,42,.86)); }
    .eyebrow,.section-kicker { color:#5eead4; font: .72rem ui-monospace,SFMono-Regular,Menlo,monospace; letter-spacing:.12em; text-transform:uppercase; }
    .hero h1 { color:#f1f5f9; font-size:clamp(2rem,4vw,3rem); font-weight:800; letter-spacing:-.055em; margin:.55rem 0 .35rem; }
    .hero p,.section-copy { color:#94a3b8; }
    </style>
    """,
    unsafe_allow_html=True,
)

if "challenge_attempts" not in st.session_state:
    st.session_state.challenge_attempts = 0
if "challenge_correct" not in st.session_state:
    st.session_state.challenge_correct = 0

st.markdown(
    """
    <section class="hero">
      <div class="eyebrow">OS lab · predict before reveal</div>
      <h1>Algorithm challenges</h1>
      <p>Make a prediction first. Then compare it with the answer computed by the same scheduling, safety, and deadlock logic used in the simulators.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

score_cols = st.columns(2)
score_cols[0].metric("Challenges attempted", st.session_state.challenge_attempts)
score_cols[1].metric("Correct predictions", st.session_state.challenge_correct)

module = st.selectbox(
    "Choose a challenge",
    ["CPU scheduling", "Banker's safety check", "Deadlock detection"],
    key="challenge_module",
)
if module == "CPU scheduling":
    algorithm = st.selectbox(
        "Scheduler",
        ["FCFS", "SJF", "SRTF", "Round Robin"],
        key="challenge_scheduler",
    )
    workload = [
        {"process_id": "P1", "arrival_time": 0, "burst_time": 7},
        {"process_id": "P2", "arrival_time": 2, "burst_time": 4},
        {"process_id": "P3", "arrival_time": 2, "burst_time": 1},
    ]
    scheduler = {
        "FCFS": schedule_fcfs,
        "SJF": schedule_sjf,
        "SRTF": schedule_srtf,
        "Round Robin": lambda processes: schedule_round_robin(processes, 2),
    }[algorithm]
    result: ScheduleResult = scheduler(workload)
    challenge_time = 2
    running = next(
        (
            interval.process_id
            for interval in result.intervals
            if interval.start <= challenge_time < interval.finish
        ),
        None,
    )
    answer_options = [item["process_id"] for item in workload]
    expected_answer = running or "CPU idle"
    prompt = (
        f"At time t={challenge_time}, which process is on the CPU under {algorithm}?"
        + (" (Round Robin uses a quantum of 2.)" if algorithm == "Round Robin" else "")
    )
    explanation = (
        f"The computed timeline is "
        + " → ".join(
            f"{interval.process_id or 'IDLE'} [{interval.start}, {interval.finish})"
            for interval in result.intervals
        )
        + f". At t={challenge_time}, {expected_answer} owns the CPU."
    )
    signature = f"cpu:{algorithm}"
elif module == "Banker's safety check":
    banker_state = create_banker_state(
        [3, 3, 2],
        [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]],
        [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]],
    )
    eligible = [
        f"P{index}"
        for index, need in enumerate(banker_state.need)
        if all(value <= available for value, available in zip(need, banker_state.available))
    ]
    answer_options = [f"P{index}" for index in range(banker_state.process_count)]
    if not eligible:
        answer_options.append("None can finish")
    expected_answer = ", ".join(eligible) if eligible else "None can finish"
    prompt = "Using the initial Work vector, which process or processes can finish first?"
    explanation = (
        f"Initial Work is {list(banker_state.available)}. Need is "
        f"{pd.DataFrame(banker_state.need, index=answer_options[:banker_state.process_count], columns=['A', 'B', 'C']).to_dict(orient='index')}. "
        f"Eligible first processes are {expected_answer}. "
        f"The full computed state is {'safe' if check_safety(banker_state).is_safe else 'unsafe'}."
    )
    signature = "banker:first-safe-process"
else:
    deadlock_state = create_deadlock_state(
        [3, 2],
        [[1, 0], [0, 1], [1, 0]],
        [[0, 1], [1, 0], [0, 0]],
    )
    result = detect_deadlock(deadlock_state)
    expected_answer = "Deadlock" if result.is_deadlocked else "No deadlock"
    answer_options = ["Deadlock", "No deadlock"]
    prompt = "The resource-type graph has a cycle, but each type has multiple instances. Is the system deadlocked?"
    explanation = (
        f"The instance-aware detector concludes {expected_answer.lower()}. "
        f"It can complete "
        f"{', '.join(f'P{index + 1}' for index in result.completed_processes) or 'no processes'} "
        f"with Work ending at {list(result.final_work)}. A resource-type cycle alone does not prove deadlock with multiple instances."
    )
    signature = "deadlock:multi-instance-cycle"

st.markdown('<div class="section-kicker">Your prediction</div>', unsafe_allow_html=True)
st.markdown(f"### {prompt}")
with st.form("challenge_answer_form"):
    if module == "Banker's safety check":
        choices = answer_options + ["None can finish"]
    elif module == "Deadlock detection":
        choices = answer_options
    else:
        choices = answer_options
    selected_answer = st.selectbox(
        "Choose your answer",
        choices,
        key=f"challenge_answer_{module}",
    )
    submitted = st.form_submit_button("Check my answer", type="primary")

if submitted:
    correct = (
        selected_answer in expected_answer.split(", ")
        if module == "Banker's safety check"
        else selected_answer == expected_answer
    )
    st.session_state.challenge_attempts += 1
    st.session_state.challenge_correct += int(correct)
    st.session_state.challenge_feedback = {
        "signature": signature,
        "correct": correct,
        "explanation": explanation,
    }

feedback = st.session_state.get("challenge_feedback")
if feedback and feedback["signature"] == signature:
    if feedback["correct"]:
        st.success("Correct prediction.")
    else:
        st.warning("Not quite. Compare your prediction with the computed state below.")
    st.info(feedback["explanation"])
    if module == "Banker's safety check":
        safety = check_safety(banker_state)
        st.caption(
            f"Safe state: {safety.is_safe} · Safe sequence: "
            + (" → ".join(f"P{index}" for index in safety.safe_sequence) or "none")
        )
    elif module == "Deadlock detection":
        st.caption(
            "Detector trace: "
            + " → ".join(f"P{index + 1}" for index in result.completed_processes)
        )
