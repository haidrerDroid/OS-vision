# OSVision — Interactive Operating Systems Simulator

**Visualize. Simulate. Understand Operating Systems.**

## 1. Project Overview

OSVision is an interactive, visualization-driven Operating Systems simulator designed to help students and developers understand how an operating system manages CPU scheduling, process execution, and deadlocks.

The project transforms theoretical Operating Systems concepts into practical, step-by-step simulations. Users can create processes, configure their parameters, select algorithms, execute simulations, observe system behavior, and analyze performance through Gantt charts, process tables, timelines, and statistical metrics.

OSVision aims to bridge the gap between textbook theory and practical understanding by making the internal behavior of operating system algorithms visible, measurable, and easy to explore.

## 2. Problem Statement

Operating Systems is a fundamental subject in computer science, but many of its concepts are difficult to understand through theoretical explanations alone.

Students often struggle to visualize:
- How CPU scheduling algorithms select processes for execution.
- How arrival time, burst time, and time quantum affect process execution.
- How preemption changes the execution order of processes.
- How waiting time and turnaround time are calculated.
- How processes compete for CPU resources.
- How deadlocks occur when processes compete for limited resources.
- How deadlock avoidance algorithms determine whether a system is in a safe state.

Traditional learning methods often rely on static examples and manual calculations. These methods may not clearly demonstrate how changing one parameter affects the entire system.

**OSVision addresses this problem by providing an interactive environment in which users can configure, execute, visualize, and compare operating system algorithms in real time.**

## 3. Project Objectives

The primary objectives of OSVision are to:

1. Simulate major CPU scheduling algorithms.
2. Visualize process execution using Gantt charts and timelines.
3. Calculate waiting time, turnaround time, response time, and CPU utilization where applicable.
4. Demonstrate preemptive and non-preemptive scheduling behavior.
5. Simulate deadlock scenarios involving multiple processes and resources.
6. Implement the Banker's Algorithm for deadlock avoidance.
7. Explain algorithm execution through step-by-step traces.
8. Allow users to modify process and resource parameters.
9. Compare algorithm performance using charts and statistical summaries.
10. Provide a user-friendly educational interface.
11. Support reproducible simulations for assignments, demonstrations, and laboratory exercises.
12. Establish an extensible architecture for adding further operating system concepts.

## 4. Core Features

### A. CPU Scheduling Simulator

OSVision will support the following CPU scheduling algorithms:

**First Come, First Served (FCFS)**

Processes execute in order of arrival. The simulator demonstrates non-preemptive scheduling and its effect on waiting time.

**Shortest Job First (SJF)**

The process with the shortest available CPU burst is selected. This version is non-preemptive.

**Shortest Remaining Time First (SRTF)**

The preemptive version of SJF. A newly arrived process may interrupt the running process if it has a shorter remaining execution time.

**Round Robin (RR)**

Each ready process receives a fixed CPU time quantum. Processes that do not finish within their quantum return to the ready queue.

For each algorithm, users can:
- Add, edit, and remove processes.
- Specify process ID, arrival time, and burst time.
- Configure the time quantum for Round Robin.
- Run, pause, reset, and step through simulations.
- Inspect the ready queue and currently running process.
- View execution order and process completion times.
- Examine detailed calculations and results.

### B. Interactive Gantt Chart

The Gantt chart will visualize how the CPU is allocated over time.

It will display:
- Process execution intervals.
- Start and finish times.
- Idle CPU periods.
- Context-switch boundaries when modeled.
- Process preemption and resumption.
- Execution sequence.

Users will be able to inspect individual timeline segments and identify which process occupied the CPU at a particular time.

### C. Performance Analysis Dashboard

After each simulation, OSVision will calculate and display relevant performance metrics.

**Turnaround Time**

Turnaround time is the difference between a process's completion time and arrival time.

Turnaround Time = Completion Time − Arrival Time

**Waiting Time**

For the standard single-CPU scheduling model:

Waiting Time = Turnaround Time − Burst Time

**Response Time**

Response time measures the interval between a process's arrival and its first CPU allocation.

Response Time = First Start Time − Arrival Time

**Average Waiting Time**

Average Waiting Time = Sum of Waiting Times / Number of Processes

**Average Turnaround Time**

Average Turnaround Time = Sum of Turnaround Times / Number of Processes

Additional metrics may include:
- Average response time.
- CPU utilization.
- Throughput.
- Total elapsed simulation time.
- Number of preemptions.
- Number of context switches, when context-switch behavior is explicitly modeled.

The dashboard will present results in tables, charts, and summary cards. Metric definitions and calculation assumptions will be documented to ensure that results are interpreted correctly.

### D. Algorithm Comparison

Users will be able to execute multiple scheduling algorithms on the same process workload and compare their results.

The comparison module will show:
- Average waiting time.
- Average turnaround time.
- Average response time.
- CPU utilization.
- Throughput.
- Preemption and context-switch counts, where supported.

Comparison charts will help users understand that algorithm performance depends on the workload and the selected evaluation metric. No single algorithm will be presented as universally optimal.

### E. Deadlock Simulator

The deadlock module will demonstrate how processes can become blocked while waiting for resources held by other processes.

Users will be able to:
- Define processes and resource types.
- Specify resource instances and allocations.
- Model resource requests.
- Observe resource availability.
- Visualize resource allocation and waiting relationships.
- Explore scenarios in which processes cannot proceed.
- Inspect the conditions contributing to deadlock.

The initial version will use a controlled resource-allocation model rather than attempting to reproduce every behavior of a production operating system.

### F. Banker's Algorithm Simulator

The Banker's Algorithm module will demonstrate deadlock avoidance by checking whether a resource allocation leaves the system in a safe state.

Users can configure:
- Number of processes.
- Number of resource types.
- Available resource instances.
- Allocation matrix.
- Maximum resource requirement matrix.
- Resource requests.

The simulator will calculate:

**Need Matrix**

Need = Maximum − Allocation

It will then evaluate whether a safe execution sequence exists under the configured resource model.

The results will show:
- Available resources.
- Allocation matrix.
- Maximum matrix.
- Need matrix.
- Processes that can safely finish.
- Resource updates after each simulated completion.
- Final safe or unsafe state.
- A safe sequence when one is found.

An unsafe state does not necessarily mean that a deadlock has already occurred; it means the simulator cannot establish a safe sequence for the current state.

### G. Step-by-Step Execution

OSVision will provide a step-through mode for educational analysis.

Users will be able to:
- Advance the simulation one event at a time.
- Inspect the current process and remaining burst time.
- Observe ready-queue changes.
- Review resource allocation changes.
- Understand why an algorithm selects a particular process.
- Reset the simulation and repeat the same experiment.

### H. Visualization and Reporting

The project will provide:
- Interactive Gantt charts.
- Process execution tables.
- Performance comparison charts.
- Resource allocation matrices.
- Deadlock and safe-state explanations.
- Simulation event logs.
- Exportable results in formats such as CSV, with additional formats considered for future releases.

## 5. Target Users

OSVision is intended for:
- Computer science and engineering students.
- Operating Systems learners.
- Teachers and laboratory instructors.
- Developers exploring scheduling algorithms.
- Students preparing for examinations and technical interviews.
- Project teams developing educational software.

## 6. Technology Stack

The initial implementation will prioritize free, cross-platform tools.

**Frontend**
- React
- TypeScript
- Vite
- HTML5 and CSS
- A charting library for Gantt charts and performance visualization

**Simulation Engine**
- TypeScript-based modular algorithm implementations.
- Deterministic event processing.
- Separate modules for scheduling, metrics, resource allocation, and deadlock analysis.

**Testing**
- Vitest for unit and algorithm tests.
- React Testing Library for interface tests.
- TypeScript type checking and linting.

**Development Tools**
- Git and GitHub for version control.
- Visual Studio Code for development.
- npm for dependency management.

**Deployment**
- Static web hosting, such as GitHub Pages, for a client-side implementation.
- Optional backend integration in a future version if persistent accounts, collaborative sessions, or server-side execution become necessary.

The initial release will not require a database or paid external services.

## 7. System Architecture

OSVision will use a modular architecture with four major layers.

### Presentation Layer

Responsible for the user interface, process forms, controls, tables, charts, and visual feedback.

### Simulation Engine

Responsible for implementing FCFS, SJF, SRTF, Round Robin, deadlock scenarios, and the Banker's Algorithm.

### Metrics and Analysis Layer

Responsible for calculating performance metrics, preparing comparison datasets, and generating explanations.

### State and Validation Layer

Responsible for validating user input, maintaining simulation state, recording events, and ensuring reproducible results.

The simulation engine will remain independent of the user interface so that algorithm correctness can be tested without running the frontend.

## 8. Functional Requirements

The system shall:
1. Allow users to create valid process workloads.
2. Validate arrival times, burst times, and algorithm-specific settings.
3. Execute the selected scheduling algorithm.
4. Produce an execution timeline and completion records.
5. Calculate supported performance metrics.
6. Allow users to compare scheduling algorithms.
7. Accept resource-allocation data for deadlock experiments.
8. Execute Banker's Algorithm on valid resource states.
9. Explain simulation results using event traces.
10. Allow users to reset and rerun simulations.
11. Handle invalid input without crashing.
12. Support exporting simulation results when the export feature is implemented.

## 9. Non-Functional Requirements

**Correctness:** Algorithms and metrics must be validated against known test cases.

**Usability:** Controls and visualizations should be understandable to learners.

**Performance:** Typical classroom-sized workloads should run smoothly in the browser.

**Maintainability:** Each algorithm should have a separate implementation and test suite.

**Portability:** The application should work in modern browsers on macOS, Windows, and Linux.

**Accessibility:** The interface should support keyboard navigation, readable labels, and appropriate contrast.

**Reproducibility:** Identical inputs and settings should produce identical simulation results.

**Reliability:** Invalid inputs and edge cases should be handled predictably.

## 10. Implementation Roadmap

### Phase 1 — Project Foundation
- Create the GitHub repository.
- Set up React, TypeScript, and Vite.
- Establish the project folder structure.
- Build the initial dashboard and navigation.
- Define common process and simulation data types.

### Phase 2 — CPU Scheduling
- Implement FCFS.
- Implement non-preemptive SJF.
- Implement preemptive SRTF.
- Implement Round Robin.
- Test arrival times, idle periods, ties, and process completion.

### Phase 3 — Visualization
- Build the Gantt chart.
- Create process tables and execution timelines.
- Add play, pause, step, and reset controls.
- Show ready-queue transitions and event logs.

### Phase 4 — Performance Analysis
- Calculate waiting, turnaround, and response times.
- Calculate CPU utilization and throughput under documented assumptions.
- Add charts and algorithm comparison.

### Phase 5 — Deadlock Analysis
- Implement a resource-allocation model.
- Demonstrate resource contention and deadlock scenarios.
- Add a visual resource-allocation representation.

### Phase 6 — Banker's Algorithm
- Implement Need Matrix calculation.
- Implement safe-sequence detection.
- Add resource-request validation and state transitions.
- Display each step of the safety algorithm.

### Phase 7 — Quality Assurance
- Add unit and integration tests.
- Verify algorithms using manually calculated examples.
- Test invalid inputs and boundary cases.
- Improve accessibility and error handling.

### Phase 8 — Documentation and Release
- Complete the README.
- Add screenshots and demonstrations.
- Publish installation and usage instructions.
- Deploy the first stable version.
- Document limitations and future improvements.

## 11. Testing Strategy

Testing will cover both mathematical correctness and user interaction.

**CPU scheduling tests**
- A single process.
- Multiple processes arriving simultaneously.
- Different arrival times.
- Idle CPU intervals.
- Equal burst times.
- Preemption in SRTF.
- Different Round Robin time quanta.
- Processes completing exactly at a scheduling boundary.

**Metric tests**
- Completion time.
- Turnaround time.
- Waiting time.
- Response time.
- Average values.
- CPU utilization and throughput under the documented model.

**Deadlock tests**
- No deadlock.
- Resource contention.
- Circular waiting scenarios.
- Resource availability changes.

**Banker's Algorithm tests**
- Safe state.
- Unsafe state.
- Multiple possible safe sequences.
- Invalid resource matrices.
- Requests exceeding declared maximum needs.
- Requests exceeding currently available resources.

Results will be checked against independently calculated expected outputs.

## 12. Expected Outcomes

At completion, OSVision should provide a practical learning environment in which users can:
- Understand CPU scheduling visually.
- Calculate and compare process performance.
- Explore preemptive and non-preemptive execution.
- Understand resource contention and deadlock.
- Examine safe and unsafe resource-allocation states.
- Experiment with parameters and immediately inspect their effects.
- Use repeatable simulations for coursework and demonstrations.

## 13. Limitations

OSVision is an educational simulator, not a replacement for a real operating system kernel.

Its initial scheduling models will use simplified assumptions about CPU bursts, process arrivals, and context switching. It will not initially model real hardware interrupts, I/O scheduling, multicore scheduling, virtual memory management, or actual kernel-level process execution.

Deadlock results will depend on the resource model and assumptions supplied by the user. The simulator will distinguish between deadlock detection and deadlock avoidance.

These limitations will be documented, and advanced models can be added in later releases.

## 14. Future Scope

Potential future enhancements include:
- Priority scheduling, with preemptive and non-preemptive variants.
- Multilevel queue scheduling.
- Multilevel feedback queue scheduling.
- Synchronization and semaphore simulations.
- Producer-consumer and readers-writers problems.
- Page replacement algorithms such as FIFO, LRU, and Optimal.
- Memory allocation strategies such as First Fit, Best Fit, and Worst Fit.
- Disk scheduling algorithms such as FCFS, SSTF, SCAN, and C-SCAN.
- Multicore CPU scheduling.
- Interactive tutorials and guided exercises.
- User-defined workloads and downloadable experiment reports.
- A teaching mode with algorithm explanations and quizzes.
- Advanced simulations of virtual memory and process synchronization.

## 15. Project Philosophy

OSVision is built around the idea that operating systems should not only be studied theoretically but also explored experimentally.

By combining algorithmic correctness, interactive visualization, and measurable performance analysis, the project aims to make fundamental operating system concepts easier to understand, test, and compare.

## 16. Conclusion

OSVision is a modular, extensible Operating Systems simulator that brings CPU scheduling, process execution, deadlock analysis, and resource-allocation algorithms into a unified educational environment.

Its goal is to transform abstract concepts into observable system behavior and provide a foundation for more advanced operating system simulations in the future.

**OSVision — Visualize. Simulate. Understand Operating Systems.**
