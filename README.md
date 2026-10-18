<p align="center">
  <img src="assets/banner.svg" alt="OSVision Banner" width="900" />
</p>

<h1 align="center">OSVision</h1>
<p align="center"><strong>Interactive Operating Systems Simulator</strong><br/><em>Visualize. Simulate. Understand Operating Systems.</em></p>

<p align="center">
  <img src="https://img.shields.io/badge/Project-Educational%20Simulator-6366f1?style=for-the-badge" alt="Educational Simulator" />
  <img src="https://img.shields.io/badge/Frontend-React%20%7C%20TypeScript-3178C6?style=for-the-badge" alt="React and TypeScript" />
  <img src="https://img.shields.io/badge/Build%20Tool-Vite-646CFF?style=for-the-badge" alt="Vite" />
</p>

**Explore CPU scheduling · Analyze performance · Understand deadlocks · Simulate resource allocation**

## 📑 Contents
- [Overview](#-overview)
- [Problem and Solution](#-problem-and-solution)
- [Features](#-features)
- [Getting Started](#-getting-started)
- [Testing and Roadmap](#-testing-and-roadmap)
- [Contributing](#-contributing)
- [Team](#-team)
- [License](#-license)

## 🌟 Overview
**OSVision** is a browser-based educational simulator designed to make Operating Systems concepts easier to explore through interactive visualizations. Learners can configure processes, run algorithms, inspect execution timelines, and compare results instead of relying only on textbook explanations and manual calculations.

The project is intended for computer science students, instructors, and developers. It is an educational simulator, not a real operating system kernel.

## ❓ Problem and Solution
Operating Systems concepts can be difficult to understand from static examples. Students may struggle to follow process execution, understand preemption, calculate scheduling metrics, or see how resource contention can lead to deadlock.

OSVision aims to address this through Gantt charts, performance summaries, resource matrices, and step-by-step event logs that connect theory with practical learning.

## ✨ Features

### 1. CPU Scheduling
The planned simulator supports four fundamental algorithms:

| Algorithm | Type | Purpose |
|---|---|---|
| First Come, First Served (FCFS) | Non-preemptive | Executes processes in arrival order |
| Shortest Job First (SJF) | Non-preemptive | Selects the shortest available CPU burst |
| Shortest Remaining Time First (SRTF) | Preemptive | Reconsiders the running process when a shorter job arrives |
| Round Robin (RR) | Preemptive | Shares CPU time using a configurable quantum |

Users will be able to enter process IDs, arrival times, and burst times; configure the Round Robin quantum; run or reset simulations; and inspect scheduling decisions.

### 2. Gantt Chart and Step-by-Step Execution
An interactive timeline will show execution intervals, start and finish times, idle periods, and preemption boundaries. Planned controls include play, pause, step, and reset. An event log will explain changes to the running process and ready queue.

### 3. Performance Analysis
The simulator will calculate relevant metrics:

| Metric | Formula |
|---|---|
| Turnaround Time (TAT) | Completion Time − Arrival Time |
| Waiting Time (WT) | Turnaround Time − Burst Time |
| Response Time (RT) | First Start Time − Arrival Time |
| CPU Utilization | Busy Time ÷ Total Time × 100% |
| Throughput | Completed Processes ÷ Elapsed Time |

Average waiting, turnaround, and response times will support comparisons. Preemption counts, context switches, and idle time may also be shown where modeled. Calculation assumptions will be documented.

### 4. Algorithm Comparison
Users will be able to compare algorithms using the same process workload. Charts and summaries will show how scheduling choices affect performance. No algorithm is best for every workload; results depend on the processes and the metric being considered.

### 5. Deadlock Simulator
The planned module will model processes competing for limited resources. Users can configure resources, allocations, requests, and releases, then inspect availability and waiting relationships. Controlled examples will demonstrate resource contention and circular waits.

### 6. Banker's Algorithm
This module will demonstrate deadlock avoidance by checking whether a resource state is safe.

**Need Matrix = Maximum − Allocation**

Planned results include the Available vector, Allocation, Maximum and Need matrices, a safe sequence (if one exists), and the resulting safe or unsafe state. Requests will be checked against declared needs and available resources. An unsafe state does not necessarily mean a deadlock has already occurred.

### 7. Reports and Visualizations
Planned outputs include process tables, Gantt charts, performance graphs, resource-allocation matrices, event logs, and CSV export for supported results.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| React | User interface |
| TypeScript | Application and simulation logic |
| Vite | Development server and build tool |
| HTML and CSS | Responsive layout and styling |
| Vitest | Unit testing |
| React Testing Library | UI and interaction testing |
| Git and GitHub | Version control and collaboration |
| npm | Package management |

The intended first release uses browser-based simulation logic and free development tools, without requiring a database or backend server. A suitable charting library may be selected for visualizations.

## 🏗️ Architecture
OSVision is planned around four layers:

```text
Presentation Layer
React UI · Forms · Charts · Tables
              |
Simulation Engine
FCFS · SJF · SRTF · Round Robin
Deadlock · Banker's Algorithm
              |
Metrics and Analysis
Waiting · Turnaround · Response
Utilization · Throughput · Comparison
              |
State and Validation
Input checks · Events · Simulation state
Error handling · Reproducibility
```

The simulation engine will be separate from the interface so algorithms can be tested independently. Input validation and consistent state handling will help ensure predictable results.

## 💻 Getting Started

### Prerequisites
- [Node.js](https://nodejs.org/) (includes npm)
- [Git](https://git-scm.com/)
- [Visual Studio Code](https://code.visualstudio.com/) or another editor
- A modern web browser

### Installation

```bash
git clone https://github.com/haidrerDroid/OSVision.git
cd OSVision
npm install
npm run dev
```

Open the local URL printed by Vite.

### Build and Test

```bash
npm run build
npm run test
```

These commands require the corresponding files and npm scripts to be configured. Adjust them if the current repository structure differs.

## 🧪 Testing and Roadmap
Testing will cover algorithm correctness, edge cases, and user interactions.

- **Scheduling:** single or multiple processes, simultaneous arrivals, idle periods, equal burst times, preemption, and different Round Robin quanta.
- **Metrics:** completion, turnaround, waiting, response, utilization, and throughput calculations.
- **Deadlocks:** resource contention, circular waits, and resource availability changes.
- **Banker's Algorithm:** safe and unsafe states, multiple safe sequences, invalid matrices, and invalid requests.
- **Interface:** invalid input, reset behavior, and repeatable simulations.

### Development Phases
- [ ] Set up React, TypeScript, Vite, shared types, and dashboard.
- [ ] Implement and test FCFS, SJF, SRTF, and Round Robin.
- [ ] Add Gantt charts, process tables, playback, and event logs.
- [ ] Add performance metrics and algorithm comparisons.
- [ ] Implement deadlock scenarios and resource visualization.
- [ ] Implement Banker's Algorithm and safe-sequence detection.
- [ ] Complete testing, documentation, and deployment.

## ⚠️ Limitations and Future Scope
OSVision uses simplified educational models and is **not a real operating system**. The initial scope excludes kernel-level execution, hardware interrupts, I/O scheduling, multicore scheduling, virtual memory, and every production synchronization mechanism. Results depend on the assumptions used in each simulation.

Possible future modules:
- Priority, Multilevel Queue, and Multilevel Feedback Queue scheduling
- Semaphores, mutexes, Producer–Consumer, Readers–Writers, and Dining Philosophers
- FIFO, LRU, and Optimal page replacement
- First Fit, Best Fit, and Worst Fit memory allocation
- FCFS, SSTF, SCAN, and C-SCAN disk scheduling
- Guided tutorials, quizzes, and downloadable experiment reports

## 🤝 Contributing
Suggestions, bug reports, tests, documentation improvements, and new educational modules are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Make and test your changes.
4. Open a pull request describing the changes.

Please verify algorithm implementations against known examples before submitting changes.
## 👥 Team

| Team Member | Role |
|---|---|
| [**Haider Hamid**](https://github.com/haidrerDroid) | Project Lead · Product & UX |
| [**Suhaib Nazir**](https://github.com/lonesuhaibbb) | Frontend · Visualizations |
| [**Sayed Shakir**](https://github.com/shakirsyed819) | Scheduling Engine |
| **Sahil** | Testing · QA |
| **Zayeem Zahoor** | Deadlock · Banker's Algorithm |
| **Haroon Hamid** | Documentation · Demos |

*Visualize. Simulate. Understand.*

## 📜 License
The project license has not yet been finalized. Add a license file before distributing the project for reuse; until then, do not assume the source is available for unrestricted reuse.

---

<p align="center"><strong>OSVision — Visualize. Simulate. Understand Operating Systems.</strong><br/>Built to make Operating Systems concepts visible, interactive, and understandable.</p>
