"""OSVision operating-systems algorithm simulators."""

from __future__ import annotations

import streamlit as st

from utils.ambient_audio import AMBIENT_AUDIO_HTML

st.set_page_config(
    page_title="OSVision | OS Lab",
    page_icon="⚙️",
    layout="wide",
)


page = st.navigation(
    [
        st.Page("pages/fcfs.py", title="FCFS", icon=":material/first_page:", default=True),
        st.Page("pages/sjf.py", title="SJF", icon=":material/short_text:"),
        st.Page("pages/srtf.py", title="SJF with Preemption (SRTF)", icon=":material/swap_horiz:"),
        st.Page("pages/round_robin.py", title="Round Robin", icon=":material/replay:"),
        st.Page("pages/deadlock.py", title="Deadlock Simulator", icon=":material/account_tree:"),
        st.Page("pages/bankers.py", title="Banker's Algorithm", icon=":material/account_tree:"),
        st.Page("pages/challenges.py", title="Algorithm Challenges", icon=":material/quiz:"),
        st.Page("pages/memory_management.py", title="Memory Management", icon=":material/memory:"),
    ],
    position="sidebar",
)
with st.sidebar:
    st.divider()
    st.components.v1.html(AMBIENT_AUDIO_HTML, height=145, scrolling=False)
page.run()
