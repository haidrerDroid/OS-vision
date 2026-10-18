"""Self-contained browser animation for a completed CPU schedule."""

from __future__ import annotations

import json

from algorithms.scheduling import ScheduleResult


def build_process_animation_html(
    result: ScheduleResult, algorithm_name: str = "FCFS", time_quantum: int | None = None
) -> str:
    """Create an animated process-flow view driven by the actual CPU schedule."""

    schedule = {
        "makespan": result.makespan,
        "algorithm": algorithm_name,
        "quantum": time_quantum,
        "processes": [
            {
                "id": process.process_id,
                "arrival": process.arrival_time,
                "burst": process.burst_time,
                "start": process.start_time,
                "finish": process.completion_time,
                "turnaround": process.turnaround_time,
                "waiting": process.waiting_time,
                "response": process.response_time,
            }
            for process in result.processes
        ],
        "averages": {
            "turnaround": result.average_turnaround_time,
            "waiting": result.average_waiting_time,
            "response": result.average_response_time,
        },
        "intervals": [
            {
                "start": interval.start,
                "finish": interval.finish,
                "process": interval.process_id,
            }
            for interval in result.intervals
        ],
    }
    schedule_json = json.dumps(schedule, ensure_ascii=True, separators=(",", ":"))
    schedule_json = (
        schedule_json.replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )

    return (
        _ANIMATION_HTML.replace("__SCHEDULE_DATA__", schedule_json)
        .replace("__MAX_LANE_HEIGHT__", str(max(260, len(result.processes) * 88 + 58)))
    )


_ANIMATION_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root {
  color-scheme: dark;
  font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: #0b1120;
  color: #e2e8f0;
}
* { box-sizing: border-box; }
body { margin: 0; padding: 8px 2px 14px; background: #0b1120; }
button, select { font: inherit; }
.shell { max-width: 1280px; margin: 0 auto; }
.toolbar {
  display: flex; align-items: center; gap: 9px; flex-wrap: wrap;
  padding: 0 0 13px;
}
.button {
  min-height: 38px; padding: 0 14px; border: 1px solid #2a3a4e; border-radius: 10px;
  background: #142033; color: #dce8f5; font-size: 13px; font-weight: 650; cursor: pointer;
  transition: transform 120ms ease, border-color 120ms ease, background 120ms ease;
}
.button:hover { transform: translateY(-1px); border-color: #52728c; }
.button.primary { border-color: #1b9c91; background: linear-gradient(135deg,#0d766f,#11564f); color: #edfffb; }
.button:focus-visible, select:focus-visible, input:focus-visible { outline: 2px solid #5eead4; outline-offset: 2px; }
.speed-control { display: flex; align-items: center; gap: 8px; margin-left: auto; color: #91a2b9; font-size: 12px; }
.speed-control select {
  height: 36px; padding: 0 30px 0 10px; border: 1px solid #293b50; border-radius: 9px;
  background: #111c2d; color: #dce8f5;
}
.clock-strip {
  display: grid; grid-template-columns: minmax(150px,1fr) auto auto; align-items: center; gap: 18px;
  margin-bottom: 10px; padding: 13px 16px; border: 1px solid #22344a; border-radius: 13px;
  background: linear-gradient(110deg,#111e31,#101a29);
}
.clock-label { color: #7f92aa; font: 10px ui-monospace, SFMono-Regular, Menlo, monospace; letter-spacing: .13em; }
.clock-value { margin-top: 3px; color: #eff6ff; font: 700 24px ui-monospace, SFMono-Regular, Menlo, monospace; }
.cpu-state { color: #a9bacd; font-size: 12px; white-space: nowrap; }
.cpu-state strong { color: #5eead4; }
.completion-count { color: #92a4ba; font: 11px ui-monospace, SFMono-Regular, Menlo, monospace; white-space: nowrap; }
.sim-progress { height: 3px; margin: -10px 0 16px; overflow: hidden; border-radius: 5px; background: #1e2b3e; }
.sim-progress > div { width: 0; height: 100%; background: linear-gradient(90deg,#2dd4bf,#a3e635); }
.section-head {
  display: flex; align-items: baseline; justify-content: space-between; gap: 12px;
  margin: 13px 0 9px;
}
.section-head h2 { margin: 0; color: #eaf1fa; font-size: 14px; font-weight: 700; }
.section-head span { color: #70839a; font: 10px ui-monospace, SFMono-Regular, Menlo, monospace; letter-spacing: .08em; }
.stage {
  position: relative; overflow: hidden; padding: 10px; border: 1px solid #23344a;
  border-radius: 14px; background: radial-gradient(ellipse at 52% 0%,rgba(20,53,70,.22),transparent 68%),#0d1726;
}
.lane-grid {
  position: relative; display: grid; grid-template-columns: repeat(4,minmax(0,1fr)); gap: 10px;
  min-height: __MAX_LANE_HEIGHT__px;
}
.lane {
  min-width: 0; border: 1px solid rgba(119,145,174,.14); border-radius: 11px;
  background: rgba(17,29,45,.74); transition: border-color 180ms ease, background 180ms ease;
}
.lane[data-lane="cpu"].active {
  border-color: rgba(45,212,191,.46);
  background: linear-gradient(180deg,rgba(18,69,68,.23),rgba(17,29,45,.82));
}
.lane[data-lane="cpu"].idle {
  border-color: rgba(251,191,36,.36);
  background: linear-gradient(180deg,rgba(78,60,23,.2),rgba(17,29,45,.82));
}
.lane-head {
  display: flex; align-items: center; justify-content: space-between; gap: 5px;
  height: 38px; padding: 0 10px; border-bottom: 1px solid rgba(119,145,174,.13);
  color: #9bacc0; font: 10px ui-monospace, SFMono-Regular, Menlo, monospace; letter-spacing: .06em;
  text-transform: uppercase;
}
.lane-count {
  display: inline-grid; width: 20px; height: 20px; place-items: center; border-radius: 50%;
  background: rgba(138,158,183,.11); color: #becbdd; font-size: 10px; letter-spacing: 0;
}
.queue-marker { color:#fbbf24; font:9px ui-monospace,monospace; letter-spacing:.04em; }
.lane-body { position: relative; min-height: calc(__MAX_LANE_HEIGHT__px - 40px); }
.lane-hint { padding: 13px 10px; color: #607087; font-size: 11px; line-height: 1.5; }
.token {
  position: absolute; z-index: 3; width: 0; min-width: 0; height: 70px; padding: 9px;
  overflow: hidden; border: 1px solid rgba(96,165,250,.36); border-radius: 10px;
  background: linear-gradient(135deg,#1c3550,#14263a); opacity: 0; pointer-events: none;
  transform: translate(-1000px,-1000px);
  transition: transform 680ms cubic-bezier(.2,.75,.22,1), border-color 180ms ease,
    background 180ms ease, box-shadow 180ms ease, opacity 180ms ease;
  will-change: transform;
}
.lane-grid.snap .token { transition: none !important; }
.token.visible { opacity: 1; }
.token.running {
  height: 86px; border-color: rgba(45,212,191,.66);
  background: linear-gradient(135deg,#104845,#173846);
  box-shadow: 0 0 25px rgba(45,212,191,.12);
}
.token.completed { border-color: rgba(45,212,191,.2); background: #142b31; color: #b3c9c7; }
.token.event-flash { animation: event-flash 720ms ease-out; }
@keyframes event-flash {
  0% { filter: brightness(1.7); box-shadow: 0 0 0 5px rgba(94,234,212,.24), 0 0 28px rgba(45,212,191,.22); }
  100% { filter: brightness(1); }
}
.token-top { display: flex; justify-content: space-between; align-items: center; gap: 6px; }
.token-id { overflow: hidden; color: #f0f6ff; font-size: 13px; font-weight: 750; text-overflow: ellipsis; white-space: nowrap; }
.token-badge { color: #8fa2b8; font: 9px ui-monospace, SFMono-Regular, Menlo, monospace; letter-spacing: .04em; }
.token.running .token-badge { color: #5eead4; }
.token-detail { overflow: hidden; margin-top: 5px; color: #94a7bd; font-size: 10px; text-overflow: ellipsis; white-space: nowrap; }
.token-progress { height: 4px; margin-top: 6px; overflow: hidden; border-radius: 6px; background: #29404c; }
.token-progress > div { width: 0; height: 100%; border-radius: inherit; background: linear-gradient(90deg,#2dd4bf,#a3e635); }
.event-panel {
  display: grid; grid-template-columns: 145px 1fr; gap: 12px; align-items: start;
  margin-top: 10px; padding: 12px 14px; border: 1px solid #22344a; border-radius: 12px;
  background: #101a29;
}
.event-title { padding-top: 2px; color: #8295ac; font: 10px ui-monospace, SFMono-Regular, Menlo, monospace; letter-spacing: .1em; }
.event-list { display: grid; gap: 5px; }
.event-item { display: grid; grid-template-columns: 42px 76px 1fr; gap: 8px; color: #b4c1d1; font-size: 10px; }
.event-time { color: #7f92aa; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
.event-kind { color: #5eead4; font: 9px ui-monospace, SFMono-Regular, Menlo, monospace; letter-spacing: .04em; }
.event-item.complete .event-kind { color: #a3e635; }
.event-empty { color: #607087; font-size: 10px; }
.decision-panel {
  display:grid; grid-template-columns:108px 1fr; gap:12px; align-items:start;
  margin:10px 0; padding:12px 14px; border:1px solid rgba(45,212,191,.2);
  border-radius:12px; background:linear-gradient(105deg,rgba(15,57,58,.32),rgba(16,26,41,.96));
}
.decision-label { padding-top:2px; color:#5eead4; font:10px ui-monospace,monospace; letter-spacing:.09em; }
.decision-text { color:#c3d0df; font-size:11px; line-height:1.55; }
.decision-text strong { color:#f0f6ff; }
.recap { display:none; margin-top:10px; padding:14px; border:1px solid rgba(163,230,53,.25); border-radius:12px; background:linear-gradient(120deg,rgba(34,60,38,.26),rgba(16,26,41,.95)); }
.recap.visible { display:block; animation:recap-in 380ms ease-out both; }
.recap-heading { display:flex; justify-content:space-between; gap:10px; align-items:baseline; margin-bottom:10px; }
.recap-heading strong { color:#e8f5d7; font-size:13px; }
.recap-heading span { color:#8da47c; font:9px ui-monospace,monospace; letter-spacing:.08em; }
.recap-table { width:100%; border-collapse:collapse; font-size:10px; }
.recap-table th { padding:7px 6px; border-bottom:1px solid rgba(148,163,184,.16); color:#8496ac; text-align:right; font:9px ui-monospace,monospace; }
.recap-table th:first-child,.recap-table td:first-child { text-align:left; }
.recap-table td { padding:7px 6px; border-bottom:1px solid rgba(148,163,184,.09); color:#cad5e2; text-align:right; }
.recap-table tfoot td { border-bottom:0; color:#a3e635; font-weight:700; }
@keyframes recap-in { from {opacity:0;transform:translateY(6px)} to {opacity:1;transform:translateY(0)} }
.gantt-wrap {
  padding: 7px 12px 2px; border: 1px solid #22344a; border-radius: 12px;
  background: linear-gradient(145deg,#101b2b,#0e1826);
}
.gantt { display: block; width: 100%; height: 112px; overflow: visible; }
.gantt text { fill: #8fa2b8; font: 10px ui-monospace, SFMono-Regular, Menlo, monospace; }
.gantt .block-label { fill: #f2f7fd; font-weight: 700; font-size: 10px; }
.gantt .idle-label { fill: #9ba9ba; font-weight: 600; font-size: 9px; }
.gantt .tick { stroke: rgba(148,163,184,.17); stroke-width: 1; }
.gantt .cursor { stroke: #fbbf24; stroke-width: 2; }
.gantt-legend { display:flex; align-items:center; gap:14px; padding:0 1px 8px; color:#8395aa; font-size:10px; }
.legend-dot { display:inline-block; width:7px; height:7px; margin-right:5px; border-radius:50%; background:#5eead4; }
.legend-dot.idle { background:#475569; }
.legend-dot.cursor { background:#fbbf24; }
@media(max-width:700px) {
  body { padding-left:0;padding-right:0; }
  .toolbar { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:6px; }
  .button { min-height:42px; padding:0 6px; font-size:11px; white-space:nowrap; }
  .speed-control { grid-column:1 / -1; justify-content:space-between; margin:2px 0 0; }
  .speed-control select { flex:1; max-width:180px; }
  .clock-strip { grid-template-columns:1fr auto; gap:8px; padding:11px; }
  .clock-value { font-size:20px; }
  .completion-count { grid-column:1 / -1; }
  .lane-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
  .lane-head { padding:0 6px; font-size:9px; letter-spacing:0; }
  .lane-count { flex:0 0 20px; }
  .decision-panel { grid-template-columns:1fr; gap:5px; }
  .event-item { grid-template-columns:38px 68px 1fr; gap:5px; font-size:9px; }
  .stage { overflow:visible; }
  .event-panel { grid-template-columns:1fr; gap:8px; }
  .gantt-legend { gap:8px; flex-wrap:wrap; }
  .section-head h2 { font-size:12px; }
}
@media(prefers-reduced-motion:reduce) {
  *, *::before, *::after { scroll-behavior:auto!important; transition-duration:.01ms!important; animation-duration:.01ms!important; }
}
</style>
</head>
<body>
<main class="shell">
  <nav class="toolbar" aria-label="Simulation controls">
    <button id="play" class="button primary" type="button">▶ Play</button>
    <button id="step" class="button" type="button">⏭ Next event</button>
    <button id="reset" class="button" type="button">↺ Reset</button>
    <label class="speed-control" for="speed">
      Playback speed
      <select id="speed" aria-label="Playback speed">
        <option value="1">1× · slow</option>
        <option value="0.5" selected>2× · normal</option>
        <option value="0.25">4× · fast</option>
        <option value="0.1">10× · demo</option>
      </select>
    </label>
  </nav>
  <section class="clock-strip" aria-live="polite">
    <div><div class="clock-label">SIMULATION CLOCK</div><div id="clock" class="clock-value">0.0 / 0</div></div>
    <div id="cpu-state" class="cpu-state">CPU: <strong>IDLE</strong></div>
    <div id="completion-count" class="completion-count">0 / 0 COMPLETE</div>
  </section>
  <div class="sim-progress" aria-hidden="true"><div id="sim-progress-fill"></div></div>
  <div class="section-head"><h2>Process flow</h2><span>LIVE SYSTEM STATE</span></div>
  <section class="stage" aria-label="Animated process flow">
    <div id="lane-grid" class="lane-grid">
      <section class="lane" data-lane="incoming"><div class="lane-head"><span>Incoming</span><span class="lane-count">0</span></div><div class="lane-body"></div></section>
      <section class="lane" data-lane="ready"><div class="lane-head"><span id="queue-label">Ready queue</span><span class="lane-count">0</span></div><div class="lane-body"></div></section>
      <section class="lane" data-lane="cpu"><div class="lane-head"><span>CPU</span><span class="lane-count">0</span></div><div class="lane-body"><div class="lane-hint">Waiting for a process…</div></div></section>
      <section class="lane" data-lane="completed"><div class="lane-head"><span>Completed</span><span class="lane-count">0</span></div><div class="lane-body"></div></section>
    </div>
  </section>
  <section class="event-panel" aria-label="Recent scheduler events">
    <div class="event-title">EVENT LOG<br><span style="color:#566a82">MOST RECENT FIRST</span></div>
    <div id="event-list" class="event-list"><div class="event-empty">Press Play to start the simulation.</div></div>
  </section>
  <section class="decision-panel" aria-live="polite">
    <div id="decision-label" class="decision-label">SCHEDULER LOGIC</div>
    <div id="decision-text" class="decision-text">Press Play to inspect the scheduler.</div>
  </section>
  <div class="section-head"><h2>CPU execution timeline</h2><span>GOLD MARKER = CURRENT TIME</span></div>
  <section class="gantt-wrap" aria-label="Live Gantt chart">
    <svg id="gantt" class="gantt" role="img" aria-label="Live CPU scheduling Gantt chart"></svg>
    <div class="gantt-legend"><span><i class="legend-dot"></i>Process running</span><span><i class="legend-dot idle"></i>CPU idle</span><span><i class="legend-dot cursor"></i>Simulation clock</span></div>
  </section>
  <section id="recap" class="recap" aria-live="polite">
    <div class="recap-heading"><strong>Run complete · performance recap</strong><span>CALCULATED FROM THIS RUN</span></div>
    <table class="recap-table">
      <thead><tr><th>Process</th><th>CT</th><th>TAT</th><th>WT</th><th>RT</th></tr></thead>
      <tbody id="recap-body"></tbody>
      <tfoot id="recap-foot"></tfoot>
    </table>
  </section>
</main>
<script>
const DATA = __SCHEDULE_DATA__;
const COLORS = ["#2dd4bf","#60a5fa","#fbbf24","#c084fc","#fb7185","#a3e635","#38bdf8","#f97316"];
const COLOR_BY_ID = new Map(DATA.processes.map((p,i)=>[p.id,COLORS[i%COLORS.length]]));
const LANES = ["incoming","ready","cpu","completed"];
const grid = document.getElementById("lane-grid");
const lanes = new Map(LANES.map(name=>[name,document.querySelector(`[data-lane="${name}"]`)]));
const tokens = new Map();
const clockEl = document.getElementById("clock");
const cpuEl = document.getElementById("cpu-state");
const completeEl = document.getElementById("completion-count");
const progressEl = document.getElementById("sim-progress-fill");
const eventEl = document.getElementById("event-list");
const decisionEl = document.getElementById("decision-text");
const decisionLabel = document.getElementById("decision-label");
const recapEl = document.getElementById("recap");
const svg = document.getElementById("gantt");
const maxTime = DATA.makespan;
const events = [];
let now = 0, playing = false, lastFrame = 0, frameHandle = 0;
const priorStates = new Map(DATA.processes.map(process=>[process.id,null]));

function stateFor(p,t) {
  if (t >= p.finish) return "completed";
  if (DATA.intervals.some(interval=>interval.process===p.id&&interval.start<=t&&t<interval.finish)) return "cpu";
  if (t >= p.arrival) return "ready";
  return "incoming";
}
function intervalAt(t) {
  return DATA.intervals.find(interval=>interval.start<=t&&t<interval.finish);
}
function usedTime(p,t) {
  return DATA.intervals.reduce((total,interval)=>{
    if(interval.process!==p.id) return total;
    return total+Math.max(0,Math.min(t,interval.finish)-interval.start);
  },0);
}
function compareReady(a,b,t) {
  const inputOrder=DATA.processes.indexOf(a)-DATA.processes.indexOf(b);
  if(DATA.algorithm==="SJF") return a.burst-b.burst||a.arrival-b.arrival||inputOrder;
  if(DATA.algorithm==="SRTF") return (a.burst-usedTime(a,t))-(b.burst-usedTime(b,t))
    ||a.arrival-b.arrival||inputOrder;
  return a.arrival-b.arrival||inputOrder;
}
function roundRobinReadyQueue(t) {
  const queue=[];
  const arrivals=[...DATA.processes].sort((a,b)=>a.arrival-b.arrival||
    DATA.processes.indexOf(a)-DATA.processes.indexOf(b));
  const enqueued=new Set();
  let nextArrival=0;
  const enqueueThrough=limit=>{
    while(nextArrival<arrivals.length&&arrivals[nextArrival].arrival<=limit) {
      const id=arrivals[nextArrival++].id;
      if(!enqueued.has(id)) { queue.push(id); enqueued.add(id); }
    }
  };
  for(const interval of DATA.intervals) {
    if(interval.start>t) break;
    enqueueThrough(interval.start);
    if(interval.process===null) {
      if(interval.finish>t) break;
      continue;
    }
    const selected=queue.indexOf(interval.process);
    if(selected>=0) queue.splice(selected,1);
    if(interval.finish>t) break;
    enqueueThrough(interval.finish);
    const process=DATA.processes.find(item=>item.id===interval.process);
    if(interval.finish<process.finish) queue.push(interval.process);
  }
  enqueueThrough(t);
  return queue;
}
function describeEvent(event) {
  if(event.kind==="ARRIVED") return `${event.id} enters the ready queue`;
  if(event.kind==="DISPATCHED") return `${event.id} gets the CPU`;
  if(event.kind==="COMPLETED") return `${event.id} finished its burst`;
  if(event.kind==="PREEMPTED") return `${event.id} is preempted with ${event.remaining} time units left`;
  return `${event.id} uses a ${DATA.quantum}-unit time slice`;
}
function text(parent, tag, className, value) {
  const node=document.createElement(tag);
  if(className) node.className=className;
  node.textContent=value;
  parent.appendChild(node);
  return node;
}
function buildTokens() {
  DATA.processes.forEach((p,index)=>{
    const card=document.createElement("article");
    card.className="token";
    card.dataset.process=p.id;
    card.setAttribute("aria-label",`Process ${p.id}`);
    const top=text(card,"div","token-top","");
    text(top,"span","token-id",p.id);
    const badge=text(top,"span","token-badge","NEW");
    const detail=text(card,"div","token-detail","");
    const bar=document.createElement("div");
    bar.className="token-progress";
    const fill=document.createElement("div");
    fill.style.background=`linear-gradient(90deg,${COLOR_BY_ID.get(p.id)},#a3e635)`;
    bar.appendChild(fill);
    card.appendChild(bar);
    grid.appendChild(card);
    tokens.set(p.id,{card,badge,detail,fill,process:p});
  });
}
function makeEvents() {
  DATA.processes.forEach(p=>{
    events.push({time:p.arrival,kind:"ARRIVED",id:p.id});
    events.push({time:p.finish,kind:"COMPLETED",id:p.id});
  });
  DATA.intervals.forEach(interval=>{
    if(interval.process===null) return;
    events.push({time:interval.start,kind:"DISPATCHED",id:interval.process});
    const process=DATA.processes.find(item=>item.id===interval.process);
    if(interval.finish<process.finish) {
      events.push({
        time:interval.finish,
        kind:DATA.algorithm==="SRTF"?"PREEMPTED":"QUANTUM EXPIRED",
        id:interval.process,
        remaining:process.burst-usedTime(process,interval.finish)
      });
    }
  });
  events.sort((a,b)=>a.time-b.time ||
    ({ARRIVED:0,PREEMPTED:1,"QUANTUM EXPIRED":1,COMPLETED:2,DISPATCHED:3}[a.kind]-
     {ARRIVED:0,PREEMPTED:1,"QUANTUM EXPIRED":1,COMPLETED:2,DISPATCHED:3}[b.kind]));
}
function setDecision(label,message) {
  decisionLabel.textContent=label;
  decisionEl.replaceChildren();
  if(Array.isArray(message)) {
    message.forEach(part=>{
      if(typeof part==="string") decisionEl.appendChild(document.createTextNode(part));
      else text(decisionEl,"strong","",part.strong);
    });
  } else decisionEl.textContent=message;
}
function renderRecap(complete) {
  recapEl.classList.toggle("visible",complete);
  if(!complete) return;
  const body=document.getElementById("recap-body");
  const foot=document.getElementById("recap-foot");
  body.replaceChildren();
  foot.replaceChildren();
  DATA.processes.forEach(process=>{
    const row=document.createElement("tr");
    [process.id,process.finish,process.turnaround,process.waiting,process.response].forEach((value,index)=>{
      text(row,index===0?"th":"td","",String(value));
    });
    body.appendChild(row);
  });
  const averageRow=document.createElement("tr");
  text(averageRow,"td","","Average");
  text(averageRow,"td","","—");
  [DATA.averages.turnaround,DATA.averages.waiting,DATA.averages.response]
    .forEach(value=>text(averageRow,"td","",Number(value).toFixed(2)));
  foot.appendChild(averageRow);
}
function renderEvents() {
  const current=events.filter(e=>e.time<=now+1e-9).slice(-5).reverse();
  eventEl.replaceChildren();
  if(!current.length) { text(eventEl,"div","event-empty","Press Play to start the simulation."); return; }
  current.forEach(event=>{
    const row=document.createElement("div");
    row.className=`event-item ${event.kind==="COMPLETED"?"complete":""}`;
    text(row,"span","event-time",`T+${event.time}`);
    text(row,"span","event-kind",event.kind);
    text(row,"span","",describeEvent(event));
    eventEl.appendChild(row);
  });
}
function buildGantt() {
  const width=1000, left=18, right=982, bandY=30, bandH=35;
  svg.setAttribute("viewBox",`0 0 ${width} 112`);
  svg.replaceChildren();
  const ns="http://www.w3.org/2000/svg";
  const add=(tag,attrs,parent=svg)=>{
    const node=document.createElementNS(ns,tag);
    Object.entries(attrs).forEach(([key,value])=>node.setAttribute(key,String(value)));
    parent.appendChild(node);
    return node;
  };
  const scale=t=>left+(maxTime?t/maxTime:0)*(right-left);
  add("rect",{x:left,y:bandY,width:right-left,height:bandH,rx:7,fill:"#121f30"});
  DATA.intervals.forEach(interval=>{
    const x=scale(interval.start), w=Math.max(1,scale(interval.finish)-x);
    const color=interval.process===null?"#475569":COLOR_BY_ID.get(interval.process);
    const block=add("rect",{x,y:bandY,width:w,height:bandH,rx:Math.min(6,w/4),fill:color,opacity:interval.process===null?".64":".9"});
    const tooltip=document.createElementNS(ns,"title");
    tooltip.textContent=`${interval.process===null?"CPU idle":interval.process} · ${interval.start}–${interval.finish} · ${interval.finish-interval.start} time units`;
    block.appendChild(tooltip);
    if(w>35) {
      const label=add("text",{x:x+w/2,y:bandY+22,"text-anchor":"middle",class:interval.process===null?"idle-label":"block-label"});
      label.textContent=interval.process===null?"IDLE":interval.process;
    }
  });
  const tickCount=Math.min(10,Math.max(2,maxTime));
  for(let i=0;i<=tickCount;i++) {
    const value=maxTime*i/tickCount, x=scale(value);
    add("line",{x1:x,y1:bandY+bandH+3,x2:x,y2:bandY+bandH+9,class:"tick"});
    const label=add("text",{x,y:bandY+bandH+24,"text-anchor":"middle"});
    label.textContent=Number.isInteger(value)?String(value):value.toFixed(1);
  }
  const cursor=add("line",{x1:left,y1:bandY-7,x2:left,y2:bandY+bandH+3,class:"cursor"});
  cursor.id="gantt-cursor";
  const marker=add("path",{d:`M ${left-5} ${bandY-8} L ${left+5} ${bandY-8} L ${left} ${bandY-1} Z`,fill:"#fbbf24"});
  marker.id="gantt-marker";
}
function layoutTokens(states) {
  const stageRect=grid.getBoundingClientRect();
  const byLane=new Map(LANES.map(lane=>[lane,[]]));
  states.forEach(({process,lane})=>byLane.get(lane).push(process));
  LANES.forEach(lane=>{
    const laneEl=lanes.get(lane);
    const body=laneEl.querySelector(".lane-body");
    const count=byLane.get(lane).length;
    laneEl.querySelector(".lane-count").textContent=String(count);
    const hint=body.querySelector(".lane-hint");
    if(lane==="cpu") {
      laneEl.classList.toggle("active",count===1);
      const interval=intervalAt(now);
      const isIdle=count===0&&interval?.process===null;
      laneEl.classList.toggle("idle",isIdle);
      if(hint) hint.hidden=count===1;
      if(!hint && count===0) { const h=text(body,"div","lane-hint","Waiting for a process…"); h.setAttribute("aria-hidden","true"); }
      if(hint && count===0) {
        hint.hidden=false;
        const next=DATA.processes.find(process=>process.arrival>now);
        hint.textContent=isIdle&&next
          ?`CPU idle until t=${next.arrival} · waiting for ${next.id}`
          :isIdle?"CPU idle · no process is ready":"Waiting for a process…";
      }
    }
  });
  states.forEach(({process,lane,index})=>{
    const token=tokens.get(process.id);
    const {card,badge,detail,fill}=token;
    const previousLane=priorStates.get(process.id);
    if(previousLane!==null&&previousLane!==lane) {
      card.classList.remove("event-flash");
      void card.offsetWidth;
      card.classList.add("event-flash");
      window.setTimeout(()=>card.classList.remove("event-flash"),720);
    }
    const body=lanes.get(lane).querySelector(".lane-body");
    const bodyRect=body.getBoundingClientRect();
    const cardWidth=Math.max(70,bodyRect.width-14);
    const top=bodyRect.top-stageRect.top+8+index*78;
    const left=bodyRect.left-stageRect.left+7;
    card.style.width=`${cardWidth}px`;
    card.style.transform=`translate(${left}px,${top}px)`;
    card.classList.add("visible");
    card.classList.toggle("running",lane==="cpu");
    card.classList.toggle("completed",lane==="completed");
    const p=token.process;
    if(lane==="cpu") {
      const used=usedTime(p,now);
      badge.textContent="● RUNNING";
      detail.textContent=`CPU time · ${used.toFixed(1)} / ${p.burst} units`;
      fill.style.width=`${Math.min(100,used/p.burst*100)}%`;
      card.querySelector(".token-progress").hidden=false;
    } else {
      badge.textContent=lane==="ready"
        ?`${String(index+1).padStart(2,"0")} · ${index===0?"FRONT":"WAITING"}`
        :lane==="completed"?"DONE":"NEW";
      const readyDetail=DATA.algorithm==="SJF"?`Ready · burst ${p.burst} units`:
        DATA.algorithm==="SRTF"?`Ready · ${Math.max(0,p.burst-usedTime(p,now))} units remaining`:
          DATA.algorithm==="Round Robin"?`Ready · ${Math.max(0,p.burst-usedTime(p,now))} units remaining`:
            `Waiting · ${p.burst} CPU units`;
      detail.textContent=lane==="ready"
        ?readyDetail
        :lane==="completed"?`Finished · at time ${p.finish}`:`Arrives at time ${p.arrival}`;
      card.querySelector(".token-progress").hidden=true;
    }
  });
}
function render() {
  clockEl.textContent=`${now.toFixed(1)} / ${maxTime}`;
  progressEl.style.width=`${maxTime?now/maxTime*100:100}%`;
  const states=DATA.processes.map(process=>({process,lane:stateFor(process,now)}));
  const running=states.find(item=>item.lane==="cpu");
  const cpuInterval=intervalAt(now);
  const activeProcess=running&&DATA.processes.find(process=>process.id===running.process.id);
  const cpuLabel=running?running.process.id:cpuInterval?"IDLE":"DONE";
  cpuEl.replaceChildren();
  text(cpuEl,"span","", "CPU: ");
  text(cpuEl,"strong","",cpuLabel);
  const complete=states.filter(item=>item.lane==="completed").length;
  completeEl.textContent=`${complete} / ${DATA.processes.length} COMPLETE`;
  document.getElementById("queue-label").textContent=`Ready queue · ${DATA.algorithm}`;
  const queue=states.filter(item=>item.lane==="ready")
    .sort((a,b)=>compareReady(a.process,b.process,now));
  if(DATA.algorithm==="Round Robin") {
    const readyById=new Map(queue.map(item=>[item.process.id,item]));
    queue.splice(0,queue.length,...roundRobinReadyQueue(now)
      .map(id=>readyById.get(id)).filter(item=>item!==undefined));
  }
  if(running) {
    const start=cpuInterval.start;
    const candidates=DATA.processes.filter(process=>
      process.id!==running.process.id&&process.arrival<=start&&process.finish>start
    ).sort((a,b)=>compareReady(a,b,start));
    const ties=DATA.algorithm!=="Round Robin"&&candidates.length>0&&
      compareReady(activeProcess,candidates[0],start)===0;
    let reason;
    if(DATA.algorithm==="SJF") reason=`shortest available burst (${running.process.burst}); this non-preemptive choice runs to completion`;
    else if(DATA.algorithm==="SRTF") reason=`shortest remaining time (${Math.max(0,activeProcess.burst-usedTime(activeProcess,start))})`;
    else if(DATA.algorithm==="Round Robin") reason=`the process at the front of the FIFO queue${DATA.quantum?` receives up to ${DATA.quantum} time units`:""}`;
    else reason="earliest arrival among ready processes";
    setDecision("WHY THIS PROCESS",[
      {strong:running.process.id},
      ` selected at t=${start} because of ${reason}.`,
      ties?" Input order resolves the remaining tie.":"",
      DATA.algorithm==="SJF"&&candidates.length
        ?` Ready bursts: ${[running.process,...candidates].sort((a,b)=>compareReady(a,b,start)).map(process=>`${process.id}=${process.burst}`).join(", ")}. A shorter process arriving later cannot interrupt this run.`
        :DATA.algorithm==="SRTF"&&candidates.length
          ?` Ready remaining times: ${[running.process,...candidates].sort((a,b)=>compareReady(a,b,start)).map(process=>`${process.id}=${Math.max(0,process.burst-usedTime(process,start))}`).join(", ")}.`
          :"",
      queue.length?` ${queue.length} process${queue.length===1?" remains":"es remain"} in the ready queue.`:" The ready queue is empty."
    ]);
  } else if(cpuInterval?.process===null) {
    const next=DATA.processes.find(process=>process.arrival>now);
    setDecision("WHY CPU IS IDLE",next
      ?`No process has arrived yet. The CPU stays idle until ${next.id} arrives at t=${next.arrival}.`
      :"No process is ready to run.");
  } else if(now>=maxTime) {
    setDecision("RUN COMPLETE","Every process has finished. Review the waiting and turnaround times in the recap.");
  } else {
    const explanations={
      FCFS:"FCFS runs the earliest-arrived ready process to completion.",
      SJF:"SJF selects the shortest burst among ready processes and runs it to completion.",
      SRTF:"SRTF selects the shortest remaining burst and re-evaluates when a process arrives.",
      "Round Robin":`Round Robin gives the queue-front process up to ${DATA.quantum} time units, then rotates it to the back if unfinished.`
    };
    setDecision("SCHEDULER LOGIC",explanations[DATA.algorithm]);
  }
  const ordered=[
    ...states.filter(item=>item.lane==="incoming").map(item=>({...item,index:DATA.processes.indexOf(item.process)})),
    ...queue.map((item,index)=>({...item,index})),
    ...states.filter(item=>item.lane==="cpu").map(item=>({...item,index:0})),
    ...states.filter(item=>item.lane==="completed").sort((a,b)=>a.process.finish-b.process.finish)
      .map((item,index)=>({...item,index}))
  ];
  layoutTokens(ordered);
  states.forEach(item=>priorStates.set(item.process.id,item.lane));
  const x=18+(maxTime?now/maxTime:0)*964;
  document.getElementById("gantt-cursor").setAttribute("x1",String(x));
  document.getElementById("gantt-cursor").setAttribute("x2",String(x));
  document.getElementById("gantt-marker").setAttribute("d",`M ${x-5} 22 L ${x+5} 22 L ${x} 29 Z`);
  renderEvents();
  renderRecap(now>=maxTime);
}
function finish() {
  now=maxTime;
  playing=false;
  document.getElementById("play").textContent="↻ Replay";
  render();
}
function frame(timestamp) {
  if(!playing) return;
  if(lastFrame) now=Math.min(maxTime,now+(timestamp-lastFrame)/1000/Number(document.getElementById("speed").value));
  lastFrame=timestamp;
  render();
  if(now>=maxTime) { finish(); return; }
  frameHandle=requestAnimationFrame(frame);
}
function play() {
  if(now>=maxTime) {
    now=0;
    grid.classList.add("snap");
  }
  if(maxTime===0) { finish(); return; }
  playing=true;
  lastFrame=0;
  document.getElementById("play").textContent="⏸ Pause";
  frameHandle=requestAnimationFrame(frame);
  if(grid.classList.contains("snap")) {
    requestAnimationFrame(()=>requestAnimationFrame(()=>grid.classList.remove("snap")));
  }
}
document.getElementById("play").addEventListener("click",()=>{
  if(playing) {
    playing=false;
    cancelAnimationFrame(frameHandle);
    document.getElementById("play").textContent="▶ Play";
    render();
  } else play();
});
document.getElementById("reset").addEventListener("click",()=>{
  playing=false;
  cancelAnimationFrame(frameHandle);
  now=0;
  lastFrame=0;
  document.getElementById("play").textContent="▶ Play";
  grid.classList.add("snap");
  render();
  requestAnimationFrame(()=>requestAnimationFrame(()=>grid.classList.remove("snap")));
});
document.getElementById("step").addEventListener("click",()=>{
  playing=false;
  cancelAnimationFrame(frameHandle);
  const boundaries=new Set(events.map(event=>event.time));
  boundaries.add(maxTime);
  now=Math.min(...[...boundaries].filter(value=>value>now+1e-8),maxTime);
  document.getElementById("play").textContent=now>=maxTime?"↻ Replay":"▶ Play";
  render();
});
document.getElementById("speed").addEventListener("change",()=>{});
window.addEventListener("resize",()=>render());
buildTokens();
makeEvents();
buildGantt();
grid.classList.add("snap");
render();
requestAnimationFrame(()=>requestAnimationFrame(()=>grid.classList.remove("snap")));
</script>
</body>
</html>
"""
