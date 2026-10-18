 <p align="center">
  <img src="assets/banner.svg" alt="OSVision Banner" width="900" />
</p>

<h1 align="center">OSVision</h1>

<p align="center">
  <strong>Interactive Operating Systems Simulator</strong>
</p>

<p align="center">
  <em>Visualize. Simulate. Understand Operating Systems.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Project-Educational%20Simulator-6366f1?style=for-the-badge" alt="Educational Simulator" />
  <img src="https://img.shields.io/badge/Frontend-React%20%7C%20TypeScript-3178C6?style=for-the-badge" alt="React and TypeScript" />
  <img src="https://img.shields.io/badge/Build%20Tool-Vite-646CFF?style=for-the-badge" alt="Vite" />
  <img src="https://img.shields.io/badge/License-TBD-lightgrey?style=for-the-badge" alt="License to be determined" />
</p>

<p align="center">
  <strong>Explore CPU Scheduling · Analyze Performance · Understand Deadlocks · Simulate Resource Allocation</strong>
</p>

---

## 📑 Table of Contents

- [🌟 Project Overview](#-project-overview)
- [❓ Problem Statement](#-problem-statement)
- [🎯 Project Objectives](#-project-objectives)
- [✨ Core Features](#-core-features)
- [👥 Target Users](#-target-users)
- [🛠️ Technology Stack](#️-technology-stack)
- [🏗️ System Architecture](#️-system-architecture)
- [📋 Functional Requirements](#-functional-requirements)
- [⚙️ Non-Functional Requirements](#️-non-functional-requirements)
- [🗺️ Implementation Roadmap](#️-implementation-roadmap)
- [🧪 Testing Strategy](#-testing-strategy)
- [📊 Expected Outcomes](#-expected-outcomes)
- [⚠️ Limitations](#️-limitations)
- [🚀 Future Scope](#-future-scope)
- [💻 Getting Started](#-getting-started)
- [🤝 Contributing](#-contributing)
- [📜 License](#-license)
- [💡 Project Philosophy](#-project-philosophy)

---

## 🌟 Project Overview

**OSVision** is an interactive, visualization-driven Operating Systems simulator designed to help students and developers understand how operating systems manage CPU scheduling, process execution, and resource allocation.

The project transforms theoretical Operating Systems concepts into practical, step-by-step simulations. Users will be able to create processes, configure their parameters, select algorithms, execute simulations, visualize system behavior, and analyze performance using Gantt charts, process tables, timelines, and statistical metrics.

By combining algorithmic correctness with interactive visualizations, OSVision aims to bridge the gap between textbook theory and practical understanding.

### 🔍 What Does OSVision Offer?

| Module | Purpose |
|---|---|
| 🖥️ CPU Scheduling | Simulate and compare scheduling algorithms |
| 📊 Gantt Charts | Visualize process execution over time |
| 📈 Performance Analytics | Calculate and compare scheduling metrics |
| 🔄 Algorithm Comparison | Evaluate algorithms using identical workloads |
| 🔒 Deadlock Simulator | Explore resource contention and deadlock conditions |
| 🏦 Banker's Algorithm | Analyze safe states and resource allocation |
| ⏯️ Step-by-Step Execution | Inspect algorithm decisions and state transitions |
| 📁 Reporting | Export simulation results for further analysis |

> **Core idea:** Instead of merely reading how an operating system works, users can experiment with its algorithms and observe their behavior.

---

## ❓ Problem Statement

Operating Systems is a fundamental subject in computer science, but many of its concepts are difficult to understand through theoretical explanations alone.

Students often struggle to visualize:

- How CPU scheduling algorithms select processes for execution.
- How arrival time, burst time, and time quantum affect execution.
- How preemption changes the execution order of processes.
- How waiting time, turnaround time, and response time are calculated.
- How processes compete for CPU time and shared resources.
- How deadlocks develop when processes wait for resources.
- How deadlock avoidance algorithms determine whether a system is in a safe state.

Traditional learning methods frequently rely on static examples and manual calculations. These methods may not clearly demonstrate how changing one parameter affects the entire system.

### 💡 Proposed Solution

**OSVision provides an interactive environment in which users can configure, execute, visualize, and compare Operating Systems algorithms.**

It makes otherwise abstract concepts observable through execution timelines, resource matrices, performance charts, event logs, and step-by-step explanations.

---

## 🎯 Project Objectives

The primary objectives of OSVision are to:

1. Implement major CPU scheduling algorithms.
2. Visualize process execution through interactive Gantt charts and timelines.
3. Calculate waiting time, turnaround time, response time, CPU utilization, and throughput where applicable.
4. Demonstrate preemptive and non-preemptive scheduling behavior.
5. Simulate deadlock scenarios involving processes and limited resources.
6. Implement the Banker's Algorithm for deadlock avoidance.
7. Explain algorithm execution through step-by-step event traces.
8. Allow users to modify process and resource parameters.
9. Compare algorithm performance using charts and statistical summaries.
10. Provide an intuitive, accessible educational interface.
11. Support reproducible experiments for assignments and laboratory exercises.
12. Establish an extensible architecture for additional Operating Systems concepts.

---

## ✨ Core Features

### 🖥️ 1. CPU Scheduling Simulator

OSVision will support four fundamental CPU scheduling algorithms.

#### 🔹 First Come, First Served (FCFS)

Processes execute in order of arrival.

**Scheduling type:** Non-preemptive.

**Learning objective:** Understand arrival-order scheduling, waiting time, and the convoy effect.

#### 🔹 Shortest Job First (SJF)

The available process with the shortest CPU burst is selected for execution.

**Scheduling type:** Non-preemptive.

**Learning objective:** Understand how burst-time selection influences average waiting time.

#### 🔹 Shortest Remaining Time First (SRTF)

The preemptive version of SJF. A newly arrived process can interrupt the currently running process if it has a shorter remaining execution time.

**Scheduling type:** Preemptive.

**Learning objective:** Understand preemption, remaining burst time, and execution-order changes.

#### 🔹 Round Robin (RR)

Each ready process receives a fixed CPU time quantum. Processes that do not finish within their allocated quantum return to the ready queue.

**Scheduling type:** Preemptive.

**Learning objective:** Understand time-sharing, fairness, and the effect of time quantum on performance.

#### ⚙️ Scheduling Controls

Users will be able to:

- ➕ Add processes.
- ✏️ Edit process parameters.
- 🗑️ Remove processes.
- 🆔 Specify process IDs.
- 🕒 Configure arrival times and burst times.
- ⏱️ Set the Round Robin time quantum.
- ▶️ Run simulations.
- ⏸️ Pause and resume execution.
- ⏭️ Advance one simulation event at a time.
- 🔄 Reset and repeat experiments.
- 🔍 Inspect the ready queue and running process.
- 📋 View completion times and detailed calculations.

---

### 📊 2. Interactive Gantt Chart

The Gantt chart will visualize how the CPU is allocated over time.

It will display:

- 🟦 Process execution intervals.
- 🕒 Start and finish times.
- ⏳ CPU idle periods.
- 🔀 Preemption and resumption events.
- 🔁 Context-switch boundaries when explicitly modeled.
- 🧭 The chronological execution sequence.

Users will be able to inspect timeline segments and determine which process occupied the CPU at a particular time.

**Example:**

```text
Time:    0       4       7       10
         |  P1   |  P2   |  P3   |
         └───────┴───────┴───────┘
```

*Illustrative example only; the actual schedule depends on the selected algorithm and process workload.*

---

### 📈 3. Performance Analysis Dashboard

After each simulation, OSVision will calculate relevant performance metrics.

| Metric | Formula | Meaning |
|---|---|---|
| Completion Time (CT) | Time when process finishes | Final completion point |
| Turnaround Time (TAT) | `CT − AT` | Total time from arrival to completion |
| Waiting Time (WT) | `TAT − BT` | Total time spent waiting for CPU service |
| Response Time (RT) | `First Start Time − AT` | Time until first CPU allocation |
| Average Waiting Time | `ΣWT / n` | Mean waiting time across processes |
| Average Turnaround Time | `ΣTAT / n` | Mean turnaround time across processes |
| Average Response Time | `ΣRT / n` | Mean response time across processes |
| CPU Utilization | `Busy Time / Total Time × 100%` | Percentage of elapsed time spent executing processes |
| Throughput | `Completed Processes / Elapsed Time` | Completion rate over the simulated interval |

**Notation:**

- `AT` = Arrival Time
- `BT` = Burst Time
- `CT` = Completion Time
- `n` = Number of processes

Additional metrics may include:

- Number of preemptions.
- Number of context switches.
- Total elapsed simulation time.
- CPU idle time.

All metrics will use documented calculation assumptions. In particular, context-switch overhead will be excluded unless explicitly modeled, and CPU utilization will be calculated over a clearly defined interval.

---

### 🔄 4. Algorithm Comparison

OSVision will allow users to execute multiple scheduling algorithms against the same process workload.

The comparison dashboard will display:

- Average waiting time.
- Average turnaround time.
- Average response time.
- CPU utilization.
- Throughput.
- Preemption count.
- Context-switch count, where supported.

Visual comparisons will help users understand how algorithm choice affects performance.

> **Important:** No scheduling algorithm is universally optimal. Performance depends on the workload, evaluation metric, and system assumptions.

---

### 🔒 5. Deadlock Simulator

The deadlock module will demonstrate how processes can become blocked while waiting for resources held by other processes.

Users will be able to:

- Define processes and resource types.
- Configure resource instances and allocations.
- Model resource requests and releases.
- Observe available resources.
- Visualize resource allocation and waiting relationships.
- Explore scenarios involving circular waits.
- Inspect the conditions that contribute to deadlock.

The initial implementation will use a controlled resource-allocation model rather than attempting to reproduce every behavior of a production operating system.

---

### 🏦 6. Banker's Algorithm Simulator

The Banker's Algorithm module will demonstrate **deadlock avoidance** by checking whether a resource allocation leaves the system in a safe state.

#### ⚙️ Configurable Parameters

Users will be able to define:

- Number of processes.
- Number of resource types.
- Available resource instances.
- Allocation matrix.
- Maximum resource requirement matrix.
- Resource requests.

#### 🧮 Need Matrix

The Need Matrix represents the remaining resources each process may require.

```text
Need = Maximum − Allocation
```

#### 🔍 Simulation Results

The simulator will display:

- Available resource vector.
- Allocation matrix.
- Maximum matrix.
- Need matrix.
- Processes that can safely complete.
- Resource updates after simulated completion.
- Final safe or unsafe state.
- A safe sequence when one exists.

**Safety note:** An unsafe state does not necessarily mean that deadlock has already occurred. It means that the current state cannot be shown to have a safe completion sequence under the model's assumptions.

Resource requests will be validated against maximum declared needs and current availability before the resulting state is evaluated.

---

### ⏯️ 7. Step-by-Step Execution

OSVision will provide an event-by-event simulation mode for educational analysis.

Users will be able to:

- ▶️ Start a simulation.
- ⏸️ Pause or resume execution.
- ⏭️ Advance one event at a time.
- 🔍 Inspect the running process.
- ⏳ Track remaining burst time.
- 📋 Observe ready-queue changes.
- 🔄 Review resource-allocation changes.
- 💬 Understand why an algorithm selected a particular process.
- 🔁 Reset and repeat the same experiment.

Each event will be recorded in a simulation log to make the algorithm's behavior easier to follow.

---

### 📉 8. Visualization and Reporting

The project will provide a unified environment for analyzing simulation results.

Planned outputs include:

- Interactive Gantt charts.
- Process execution tables.
- Performance comparison charts.
- Resource-allocation matrices.
- Deadlock and safe-state explanations.
- Step-by-step event logs.
- CSV export of supported simulation results.

Additional export formats may be introduced in future releases.

---

## 👥 Target Users

OSVision is intended for:

- 🎓 Computer science and engineering students.
- 📚 Operating Systems learners.
- 👨‍🏫 Teachers and laboratory instructors.
- 💻 Developers exploring scheduling algorithms.
- 📝 Students preparing for examinations and technical interviews.
- 🧑‍💻 Project teams developing educational software.

---

## 🛠️ Technology Stack

OSVision will prioritize free, cross-platform technologies.

| Component | Technology | Purpose |
|---|---|---|
| Frontend | React | Component-based user interface |
| Programming Language | TypeScript | Type-safe application and simulation logic |
| Build Tool | Vite | Development server and production builds |
| UI | HTML5 and CSS | Responsive layout and styling |
| Visualization | A suitable charting library | Gantt charts and performance graphs |
| Testing | Vitest | Unit and algorithm tests |
| UI Testing | React Testing Library | Component and interaction tests |
| Code Quality | TypeScript and linting tools | Type checking and maintainability |
| Version Control | Git and GitHub | Source control and collaboration |
| Package Management | npm | Dependency management |
| Editor | Visual Studio Code | Development environment |
| Deployment | GitHub Pages or equivalent static hosting | Publishing the client-side application |

### 💰 Cost and Infrastructure

The initial release is planned to:

- Use free and open-source development tools.
- Run simulation logic directly in the browser.
- Avoid mandatory paid external services.
- Work without a database or backend server.
- Support deployment to a static hosting platform.

---

## 🏗️ System Architecture

OSVision will use a modular architecture consisting of four primary layers.

```text
┌─────────────────────────────────────────┐
│            PRESENTATION LAYER            │
│     React UI · Forms · Charts · Tables   │
└────────────────────┬────────────────────┘
                     │
┌────────────────────▼────────────────────┐
│           SIMULATION ENGINE              │
│      FCFS · SJF · SRTF · Round Robin     │
│        Deadlock · Banker's Algorithm     │
└────────────────────┬────────────────────┘
                     │
┌────────────────────▼────────────────────┐
│        METRICS & ANALYSIS LAYER           │
│  Waiting · Turnaround · Response · CPU   │
│        Utilization · Comparison          │
└────────────────────┬────────────────────┘
                     │
┌────────────────────▼────────────────────┐
│        STATE & VALIDATION LAYER           │
│   Input Validation · Events · State      │
│       Reproducibility · Error Handling   │
└─────────────────────────────────────────┘
```

### 🧩 Architecture Responsibilities

**1. Presentation Layer**

Responsible for the dashboard, process forms, navigation, controls, charts, tables, and visual feedback.

**2. Simulation Engine**

Responsible for scheduling algorithms, resource-allocation models, deadlock scenarios, and Banker's Algorithm execution.

**3. Metrics and Analysis Layer**

Responsible for calculating performance metrics, preparing comparison datasets, and generating educational explanations.

**4. State and Validation Layer**

Responsible for validating inputs, maintaining simulation state, recording events, and ensuring reproducible results.

The simulation engine will remain independent of the user interface so that algorithm correctness can be tested without running the frontend.

---

## 📋 Functional Requirements

The system shall:

1. Allow users to create valid process workloads.
2. Validate arrival times, burst times, and algorithm-specific settings.
3. Execute the selected scheduling algorithm.
4. Generate an execution timeline and completion records.
5. Calculate supported performance metrics.
6. Compare scheduling algorithms using identical workloads.
7. Accept resource-allocation data for deadlock experiments.
8. Execute Banker's Algorithm on valid resource states.
9. Explain simulation results through event traces.
10. Allow users to reset and rerun simulations.
11. Handle invalid input without crashing.
12. Export simulation results when the export feature is implemented.

---

## ⚙️ Non-Functional Requirements

| Requirement | Description |
|---|---|
| ✅ Correctness | Algorithms and metrics must pass known test cases |
| 🎨 Usability | Controls and visualizations should be understandable |
| ⚡ Performance | Typical classroom-sized workloads should run smoothly |
| 🧱 Maintainability | Algorithms should have separate implementations and tests |
| 🌐 Portability | Support modern browsers on macOS, Windows, and Linux |
| ♿ Accessibility | Provide keyboard navigation, readable labels, and suitable contrast |
| 🔁 Reproducibility | Identical inputs and settings should yield identical results |
| 🛡️ Reliability | Invalid inputs and edge cases should be handled predictably |

---

## 🗺️ Implementation Roadmap

The project will be developed incrementally, beginning with the simulation foundation and progressing toward visualization, analysis, and advanced resource-management modules.

- [ ] **Phase 1 — Project Foundation**
  - [ ] Create and configure the GitHub repository.
  - [ ] Set up React, TypeScript, and Vite.
  - [ ] Establish the project folder structure.
  - [ ] Build the initial dashboard and navigation.
  - [ ] Define shared process and simulation types.

- [ ] **Phase 2 — CPU Scheduling**
  - [ ] Implement FCFS.
  - [ ] Implement non-preemptive SJF.
  - [ ] Implement preemptive SRTF.
  - [ ] Implement Round Robin.
  - [ ] Test arrival times, idle periods, ties, and process completion.

- [ ] **Phase 3 — Visualization**
  - [ ] Build the Gantt chart.
  - [ ] Create process tables and execution timelines.
  - [ ] Add play, pause, step, and reset controls.
  - [ ] Display ready-queue transitions and event logs.

- [ ] **Phase 4 — Performance Analysis**
  - [ ] Calculate waiting, turnaround, and response times.
  - [ ] Calculate CPU utilization and throughput.
  - [ ] Add performance charts.
  - [ ] Implement algorithm comparison.

- [ ] **Phase 5 — Deadlock Analysis**
  - [ ] Implement a resource-allocation model.
  - [ ] Demonstrate resource contention and deadlock scenarios.
  - [ ] Add a resource-allocation visualization.

- [ ] **Phase 6 — Banker's Algorithm**
  - [ ] Implement Need Matrix calculation.
  - [ ] Implement safe-sequence detection.
  - [ ] Add resource-request validation.
  - [ ] Display each step of the safety algorithm.

- [ ] **Phase 7 — Quality Assurance**
  - [ ] Add unit and integration tests.
  - [ ] Verify algorithms using manually calculated examples.
  - [ ] Test invalid inputs and boundary cases.
  - [ ] Improve accessibility and error handling.

- [ ] **Phase 8 — Documentation and Release**
  - [ ] Complete project documentation.
  - [ ] Add screenshots and demonstrations.
  - [ ] Publish installation and usage instructions.
  - [ ] Deploy the first stable version.
  - [ ] Document limitations and future improvements.

---

## 🧪 Testing Strategy

Testing will cover mathematical correctness, edge cases, and user interactions.

### 🖥️ CPU Scheduling Tests

- Single-process workloads.
- Multiple processes arriving simultaneously.
- Different arrival times.
- CPU idle intervals.
- Equal burst times.
- Preemption in SRTF.
- Different Round Robin time quanta.
- Processes completing exactly at scheduling boundaries.

### 📈 Metrics Tests

- Completion time.
- Turnaround time.
- Waiting time.
- Response time.
- Average values.
- CPU utilization.
- Throughput.

### 🔒 Deadlock Tests

- No-deadlock scenarios.
- Resource contention.
- Circular-wait scenarios.
- Resource availability changes.

### 🏦 Banker's Algorithm Tests

- Safe states.
- Unsafe states.
- Multiple possible safe sequences.
- Invalid resource matrices.
- Requests exceeding declared maximum needs.
- Requests exceeding currently available resources.

Expected results will be checked against independently calculated outputs.

---

## 📊 Expected Outcomes

At completion, OSVision should provide an educational environment in which users can:

- Understand CPU scheduling visually.
- Calculate and compare process performance.
- Explore preemptive and non-preemptive execution.
- Understand resource contention and deadlocks.
- Examine safe and unsafe resource-allocation states.
- Experiment with parameters and inspect their effects.
- Use reproducible simulations for coursework and demonstrations.

The intended outcome is a practical, modular learning tool that makes fundamental Operating Systems algorithms easier to explore and understand.

---

## ⚠️ Limitations

OSVision is an educational simulator, **not a replacement for a real operating system kernel**.

The initial release will use simplified models of CPU bursts, process arrivals, and resource allocation.

It will not initially model:

- Real hardware interrupts.
- Kernel-level process execution.
- I/O scheduling.
- Multicore CPU scheduling.
- Virtual memory management.
- Every synchronization mechanism used by production operating systems.

Deadlock analysis will depend on the resource model and assumptions supplied by the user. The simulator will distinguish between deadlock detection and deadlock avoidance.

These limitations will be documented, with more advanced models considered for future releases.

---

## 🚀 Future Scope

OSVision is designed to be extensible. Future versions may include the following modules.

### 🖥️ Advanced CPU Scheduling

- Priority Scheduling — preemptive and non-preemptive.
- Multilevel Queue Scheduling.
- Multilevel Feedback Queue Scheduling.
- Multicore CPU Scheduling.

### 🔄 Process Synchronization

- Semaphores.
- Mutexes and critical sections.
- Producer–Consumer Problem.
- Readers–Writers Problem.
- Dining Philosophers Problem.

### 🧠 Memory Management

- FIFO Page Replacement.
- LRU Page Replacement.
- Optimal Page Replacement.
- First Fit, Best Fit, and Worst Fit.
- Virtual memory and page-fault visualization.

### 💽 Disk Scheduling

- FCFS.
- SSTF.
- SCAN.
- C-SCAN.

### 🎓 Educational Enhancements

- Interactive tutorials.
- Guided algorithm explanations.
- Practice questions and quizzes.
- User-defined workloads.
- Downloadable experiment reports.
- Advanced simulation modes.
- Additional performance metrics.

These enhancements will be prioritized according to project scope, correctness, and development resources.

---

## 💻 Getting Started

### 📌 Prerequisites

Install the following tools before setting up the project:

- [Node.js](https://nodejs.org/) — includes npm.
- [Git](https://git-scm.com/).
- [Visual Studio Code](https://code.visualstudio.com/) or another editor.
- A modern web browser.

### 📥 Installation

Clone the repository:

```bash
git clone https://github.com/haidrerDroid/OSVision.git
```

Enter the project directory:

```bash
cd OSVision
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Open the local URL printed by Vite in your terminal.

**Note:** These commands assume that the repository uses the proposed React + TypeScript + Vite setup and that the application files and npm scripts have been created. Replace the repository URL if your GitHub repository uses a different name or URL.

### 🏗️ Production Build

```bash
npm run build
```

Preview the production build locally:

```bash
npm run preview
```

### 🧪 Run Tests

When the testing scripts have been configured:

```bash
npm run test
```

---

## 📁 Planned Project Structure

```text
OSVision/
├── public/
├── assets/
│   └── banner.svg
├── src/
│   ├── components/
│   │   ├── Dashboard/
│   │   ├── GanttChart/
│   │   ├── ProcessTable/
│   │   └── MetricsPanel/
│   ├── modules/
│   │   ├── scheduling/
│   │   │   ├── fcfs.ts
│   │   │   ├── sjf.ts
│   │   │   ├── srtf.ts
│   │   │   └── roundRobin.ts
│   │   ├── deadlock/
│   │   └── bankers/
│   ├── engine/
│   ├── metrics/
│   ├── types/
│   ├── utils/
│   ├── App.tsx
│   └── main.tsx
├── tests/
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

*This is a proposed structure. The actual directory layout may change during implementation.*

---

## 🤝 Contributing

Contributions, suggestions, bug reports, and educational feedback are welcome.

Potential contributions include:

- Improving algorithm correctness.
- Adding new scheduling or resource-management algorithms.
- Enhancing Gantt chart visualizations.
- Improving accessibility and user experience.
- Writing automated tests.
- Improving documentation and examples.

### Contribution Workflow

1. Fork the repository.
2. Create a feature branch.
3. Implement and test your changes.
4. Submit a pull request describing the changes.

Please ensure that algorithm implementations are tested against known examples before submitting changes.

---

## 📜 License

The project license has not yet been finalized.

A license should be selected and added to the repository before the project is distributed for reuse. Until then, do not assume that the source code is available for unrestricted reuse.

---

## 💡 Project Philosophy

OSVision is built around a simple principle:

> **Operating Systems should not only be studied theoretically — they should be explored experimentally.**

By combining algorithmic correctness, interactive visualization, and measurable performance analysis, OSVision aims to make fundamental Operating Systems concepts easier to understand, test, and compare.

The long-term vision is to expand the project into a comprehensive educational environment for exploring how operating systems schedule processes, manage resources, coordinate execution, and handle memory.

---

<p align="center">
  <strong>OSVision — Visualize. Simulate. Understand Operating Systems.</strong>
</p>

<p align="center">
  Built to make Operating Systems concepts visible, interactive, and understandable.
</p>
