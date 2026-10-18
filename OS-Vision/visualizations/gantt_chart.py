"""Plotly Gantt chart for CPU scheduling results."""

from __future__ import annotations

import math

import plotly.graph_objects as go

from algorithms.fcfs import ScheduleResult


def build_gantt_chart(
    result: ScheduleResult, current_time: float | None = None
) -> go.Figure:
    """Build a CPU timeline directly from the scheduler's execution intervals."""

    palette = ["#2dd4bf", "#60a5fa", "#fbbf24", "#c084fc", "#fb7185", "#a3e635"]
    process_ids = list(dict.fromkeys(
        interval.process_id for interval in result.intervals if interval.process_id is not None
    ))
    colors = {
        process_id: palette[index % len(palette)]
        for index, process_id in enumerate(process_ids)
    }

    starts = [interval.start for interval in result.intervals]
    durations = [interval.finish - interval.start for interval in result.intervals]
    labels = [
        interval.process_id if interval.process_id is not None else "CPU Idle"
        for interval in result.intervals
    ]
    finishes = [interval.finish for interval in result.intervals]
    bar_colors = []
    for interval in result.intervals:
        process_color = (
            colors[interval.process_id] if interval.process_id is not None else "#475569"
        )
        if current_time is None or interval.finish <= current_time:
            bar_colors.append(process_color)
        elif interval.start <= current_time and interval.process_id is not None:
            bar_colors.append("#243449")
        else:
            bar_colors.append("#1b293b")

    figure = go.Figure(
        go.Bar(
            x=durations,
            y=["CPU"] * len(result.intervals),
            base=starts,
            orientation="h",
            marker={"color": bar_colors, "line": {"color": "#0b1120", "width": 2}},
            text=labels,
            textposition="inside",
            insidetextanchor="middle",
            textfont={"color": "#dbeafe", "size": 12},
            customdata=list(zip(labels, starts, finishes)),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Start: %{customdata[1]}<br>"
                "Finish: %{customdata[2]}<br>"
                "Duration: %{x}<extra></extra>"
            ),
            showlegend=False,
        )
    )
    if current_time is not None:
        for interval in result.intervals:
            if (
                interval.process_id is not None
                and interval.start <= current_time < interval.finish
            ):
                progress = current_time - interval.start
                if progress > 0:
                    figure.add_trace(
                        go.Bar(
                            x=[progress],
                            y=["CPU"],
                            base=[interval.start],
                            orientation="h",
                            marker={
                                "color": colors[interval.process_id],
                                "line": {"color": "#0b1120", "width": 1},
                            },
                            hoverinfo="skip",
                            showlegend=False,
                        )
                    )
                break
        figure.add_vline(
            x=max(0, min(current_time, result.makespan)),
            line_color="#fbbf24",
            line_width=2,
            line_dash="dot",
        )
    tick_step = max(1, math.ceil(result.makespan / 12))
    figure.update_layout(
        title={
            "text": "LIVE CPU TIMELINE" if current_time is not None else "FCFS CPU TIMELINE",
            "font": {"color": "#e2e8f0", "size": 13},
            "x": 0.02,
            "xanchor": "left",
        },
        xaxis={
            "title": {"text": "TIME", "font": {"color": "#94a3b8", "size": 11}},
            "range": [0, result.makespan],
            "tickmode": "linear",
            "dtick": tick_step,
            "showgrid": True,
            "gridcolor": "rgba(148, 163, 184, 0.12)",
            "zeroline": True,
            "zerolinecolor": "rgba(148, 163, 184, 0.35)",
            "tickfont": {"color": "#94a3b8"},
        },
        yaxis={"visible": False, "range": [-0.7, 0.7]},
        height=190,
        margin={"l": 12, "r": 12, "t": 20, "b": 45},
        bargap=0.28,
        hoverlabel={"namelength": 0},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, ui-sans-serif, sans-serif", "color": "#e2e8f0"},
    )
    return figure
