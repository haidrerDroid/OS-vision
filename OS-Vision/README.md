# OSVision

OSVision is an interactive educational simulator for operating-systems algorithms.
The current increment provides four working CPU schedulers—FCFS, non-preemptive
SJF, preemptive SRTF, and Round Robin. Each algorithm has a separate page,
workload editor, simulation, and results, alongside computed performance
metrics and CSV export. Browser-side playback animates actual execution intervals with
process-card movement, a synchronized SVG Gantt chart, event log, run/pause,
next-event stepping, reset, and adjustable simulation speed.
The interface uses a dark navy and teal visual theme configured locally in
`.streamlit/config.toml`.

## Architecture

```text
app.py                              Streamlit navigation for separate algorithm pages
pages/fcfs.py                      FCFS simulator page
pages/sjf.py                       Non-preemptive SJF simulator page
pages/srtf.py                      Preemptive SJF (SRTF) simulator page
pages/round_robin.py               Round Robin simulator page
pages/deadlock.py                  Deadlock detector and resource graph page
pages/bankers.py                   Banker's algorithm simulator page
pages/challenges.py                Predict-before-reveal practice across modules
pages/memory_management.py         Paging, replacement, and address translation
utils/ambient_audio.py             Opt-in local soundtrack controls
utils/scheduling_ui.py             Shared UI components with per-algorithm state
algorithms/scheduling.py            Shared process models, validation, and metrics
algorithms/fcfs.py                  First Come, First Served
algorithms/sjf.py                   Non-preemptive Shortest Job First
algorithms/srtf.py                  Preemptive Shortest Remaining Time First
algorithms/round_robin.py           Round Robin with configurable quantum
algorithms/bankers.py               Safety algorithm and resource-request simulation
algorithms/memory_management.py     FIFO/LRU/Optimal and virtual address translation
visualizations/process_animation.py Browser-side live execution and Gantt view
visualizations/gantt_chart.py       Plotly Gantt chart helper
tests/                              Algorithm, playback, and visualization tests
requirements.txt                   Runtime and test dependencies
```

The algorithms share validated process/result models while each computes its
own actual execution timeline. The selected Python schedule is serialized into
the self-contained browser animation, which advances smoothly without Streamlit
reruns; process lanes, the event log, and SVG Gantt cursor all read one simulated
clock. The same result types and interface can support later OS labs.

## Requirements and macOS setup

Python 3.10 or newer and Streamlit 1.66 or newer are recommended. The project
uses standard Python packages and runs locally; no paid services or cloud
resources are required.

From Terminal, move to the project directory and run:

```bash
cd /Users/haiderhamid/OS-Vision
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Apple Silicon, use a native Apple Silicon Python 3 installation where
available. The listed dependencies provide macOS wheels and do not require a
paid service.

## Run and verify

With the virtual environment activated:

```bash
streamlit run app.py
```

Streamlit prints a local URL, usually `http://localhost:8501`. Use the sidebar
to open the separate **FCFS**, **SJF**, **SJF with Preemption (SRTF)**,
**Round Robin**, **Deadlock Simulator**, **Banker's Algorithm**,
**Algorithm Challenges**, or **Memory Management** page. Each
CPU scheduler has its own editable process table and run button; changing pages
preserves that page's results and workload. Round Robin's time quantum is editable. Presets
demonstrate a balanced workload, the convoy effect from a long first job, idle
CPU gaps, and simultaneous arrivals. In each CPU simulator,
**Play/Pause** starts or stops the animation, **Next event** advances to the
next arrival, dispatch, or completion, and **Reset** returns to time zero.
Adjust playback speed from 1× to 10×. The process cards move between the
incoming, numbered algorithm-aware ready queue, CPU, and completed lanes. The live
explanation describes each selection or idle interval, while the event log and
Gantt cursor follow the same clock. When the run finishes, a recap shows each
process's completion, turnaround, waiting, and response times. **Reset sample**
restores the balanced workload.
FCFS highlights the convoy effect when a long first job delays shorter jobs.
SJF and SRTF show candidate burst/remaining times in the live process view.
Round Robin includes a workload-specific quantum analysis of waiting/response
times, CPU utilization, throughput, and process switches.
The Banker's page has configurable process/resource dimensions, editable
Available, Allocation, and Maximum editors, learning presets, calculated Need,
and a step-through Work/Finish trace. It simulates resource requests against the
current state without mutating it.
The Deadlock page separately edits total instances, allocations, and outstanding
requests; supports queue, grant, and release operations; draws the resource-
allocation graph and individual instance ownership; and runs instance-aware
detection independently of cycle checking. Dimensions are configurable and
resource operations can be undone.
The Algorithm Challenges page lets learners predict a CPU scheduling decision,
the first Banker-eligible process, or a multi-instance deadlock result before it
reveals the computed answer and explanation.
The Memory Management page simulates FIFO, LRU, and Optimal replacement on one
page-reference string, compares fault/hit counts, and exposes each frame state
at a selected step. Its address translator derives page number and offset from
the entered address, then maps through the selected policy's page-table snapshot
or reports a page fault. The Belady preset verifies the classic FIFO fault-count
increase from three frames to four.
Optional background music is available in the sidebar across the app. The
user-provided `static/audio/oppenheimer_theme.mp3` soundtrack is silent by
default, starts only after Play is pressed, and includes a volume control. The
local audio file is served by Streamlit static serving; no external audio
service is used. Ensure you have rights to use and distribute the soundtrack
with this app.

Run the automated tests from the project directory:

```bash
python -m pytest -q
```

## Scheduling assumptions and metric definitions

- FCFS is non-preemptive: earliest arrival first; input row order breaks
  simultaneous-arrival ties.
- SJF is non-preemptive and chooses the shortest burst among ready processes.
  Ties are resolved by arrival time, then input row order.
- SRTF re-evaluates the running process whenever a new process arrives. It
  selects the shortest remaining time; ties use arrival time, then input row
  order. If a new arrival ties the running process, the earlier arrival retains
  the CPU.
- Round Robin uses a FIFO ready queue. An unfinished process joins the back
  after its quantum expires; processes arriving at that exact time join the
  queue before the expired process is re-queued.
- Time values are non-negative integer units, and burst times must be positive.
- Round Robin's time quantum must be a positive integer.
- Banker's inputs are non-negative integer resource counts. Allocation cannot
  exceed Maximum, and a maximum claim cannot exceed the resource instances in
  the system. A request must not exceed the process's remaining Need or the
  currently Available vector, and is granted only if the tentative allocation
  leaves a safe state.
- The timeline begins at time zero, so pre-arrival idle time is included in
  utilization.
- `TAT = CT - AT`, `WT = TAT - BT`, and `RT = first start - AT`.
- `CPU utilization = total burst time / makespan`.
- `Throughput = process count / makespan`.
- The Gantt chart includes idle intervals and is generated from the scheduler's
  actual execution intervals.

## Sample scenario and expected results

The initial UI data is:

| Process | Arrival | Burst |
|---|---:|---:|
| P1 | 0 | 5 |
| P2 | 1 | 3 |
| P3 | 2 | 8 |
| P4 | 10 | 2 |

Expected FCFS order and intervals: `P1 (0-5)`, `P2 (5-8)`, `P3 (8-16)`,
`P4 (16-18)`. The final completion time is 18; average waiting time is 4,
average turnaround time is 8.5, average response time is 4, CPU utilization is
100%, and throughput is `4/18` processes per time unit.

The Banker's page loads the standard five-process, three-resource example.
It derives the safe sequence `P1 → P3 → P0 → P2 → P4`. A request of `[1, 0, 2]`
from `P1` is safe; `[3, 3, 0]` from `P4` is denied because its tentative state
has no safe sequence. The request simulation does not change the editable base
matrices.

## Implemented

- FCFS, SJF, SRTF, and Round Robin scheduling with per-process completion,
  turnaround, waiting, and response times.
- Aggregate waiting, turnaround, and response time, CPU utilization, and
  throughput on each separate algorithm page.
- Editable input, validation messages, sample reset, actual-result Gantt chart,
  configurable Round Robin quantum, and CSV download.
- Separate Banker's Algorithm page with editable resource matrices, derived
  Need, configurable dimensions, safe/unsafe/request-limit presets,
  step-through Work/Finish trace, resource-request validation/simulation, and
  allocation and remaining-need heatmaps.
- Separate deadlock simulator with editable resource instances, request/
  allocation/release operations, RAG visualization, multi-instance detection,
  configurable dimensions, undo/reset, instance ownership, and
  cycle-versus-deadlock scenarios.
- Browser-side live animation with smoothly moving process cards, CPU burst
  progress, simulation clock, synchronized Gantt cursor, and recent-event log.
- Play/pause, next arrival/dispatch/completion stepping, reset, and playback
  speeds from 1× to 10×.
- Ready-queue position labels, algorithm-aware dispatch explanations, explicit
  idle-CPU explanations, FCFS convoy insights, and four learning scenario
  presets.
- Round Robin quantum tradeoff charts and predict-before-reveal challenges
  backed by computed algorithm outcomes.
- Memory-management lab with FIFO, LRU, and Optimal traces, policy comparison,
  page-table snapshots, virtual-to-physical translation, and a Belady anomaly
  demonstration.
- End-of-run per-process metrics recap and responsive compact-screen controls.
- Tests for metrics, equal-arrival tie-breaking, idle gaps, and invalid input.

## Roadmap and current limitations

The next increments can add disk scheduling, synchronization, TLB modeling,
and persistent scenario import/export. The current build does not yet include
priority scheduling or simulated context-switch overhead.
