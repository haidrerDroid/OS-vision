"""User-controlled local soundtrack player for the Streamlit app shell."""

from __future__ import annotations

AMBIENT_AUDIO_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
* { box-sizing: border-box; }
body {
  margin: 0;
  color: #cbd5e1;
  background: transparent;
  font: 12px Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.audio-card {
  padding: 10px;
  border: 1px solid rgba(148,163,184,.16);
  border-radius: 12px;
  background: rgba(255,255,255,.025);
}
.audio-heading { display:flex; align-items:center; gap:7px; color:#e2e8f0; font-weight:700; }
.audio-dot { width:7px; height:7px; border-radius:50%; background:#64748b; }
.audio-card.playing .audio-dot { background:#5eead4; box-shadow:0 0 10px #2dd4bf; }
.audio-description { margin:5px 0 9px; color:#94a3b8; font-size:11px; line-height:1.4; }
.audio-controls { display:flex; align-items:center; gap:8px; }
.audio-status { min-height:14px; margin:7px 0 0; color:#94a3b8; font-size:10px; }
.audio-status.error { color:#fda4af; }
.sr-only { position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0; }
button {
  min-height:32px; padding:0 10px; border:1px solid #334155; border-radius:8px;
  background:#142033; color:#e2e8f0; font:600 11px inherit; cursor:pointer;
}
button:hover { border-color:#5eead4; }
button:focus-visible,input:focus-visible { outline:2px solid #5eead4; outline-offset:2px; }
input { width:100%; accent-color:#2dd4bf; cursor:pointer; }
output { min-width:28px; color:#9aabc0; text-align:right; font-variant-numeric:tabular-nums; }
</style>
</head>
<body>
<section class="audio-card" id="audio-card" aria-label="Background music controls">
  <div class="audio-heading"><span class="audio-dot" aria-hidden="true"></span>Background music</div>
  <p class="audio-description">Can You Hear The Music · Off until you press play.</p>
  <div class="audio-controls">
    <button id="toggle" type="button" aria-pressed="false">▶ Play</button>
    <label for="volume" class="sr-only">Volume</label>
    <input id="volume" type="range" min="0" max="30" value="12" aria-label="Ambient audio volume">
    <output id="volume-value" for="volume">12%</output>
  </div>
  <p class="audio-status" id="audio-status" role="status" aria-live="polite"></p>
</section>
<audio id="track" src="/app/static/audio/oppenheimer_theme.mp3" preload="none" loop></audio>
<script>
(() => {
  const card = document.getElementById("audio-card");
  const button = document.getElementById("toggle");
  const slider = document.getElementById("volume");
  const output = document.getElementById("volume-value");
  const status = document.getElementById("audio-status");
  const track = document.getElementById("track");
  let playing = false;

  try {
    const savedVolume = Number(localStorage.getItem("osvision-ambient-volume"));
    if (Number.isFinite(savedVolume)) slider.value = String(Math.max(0, Math.min(30, savedVolume)));
  } catch (error) {
    console.info("Ambient volume preference could not be restored.", error);
  }

  function setVolume() {
    const percent = Number(slider.value);
    output.value = `${percent}%`;
    output.textContent = `${percent}%`;
    try { localStorage.setItem("osvision-ambient-volume", String(percent)); }
    catch (error) { console.info("Ambient volume preference could not be saved.", error); }
    track.volume = percent / 100;
  }

  async function start() {
    status.textContent = "";
    status.classList.remove("error");
    try {
      await track.play();
      playing = true;
      setVolume();
      button.textContent = "Ⅱ Mute";
      button.setAttribute("aria-pressed", "true");
      card.classList.add("playing");
    } catch (error) {
      status.textContent = `Couldn't play the track: ${error.message}`;
      status.classList.add("error");
      console.error("OSVision soundtrack playback failed.", error);
    }
  }

  async function stop() {
    playing = false;
    button.textContent = "▶ Play";
    button.setAttribute("aria-pressed", "false");
    card.classList.remove("playing");
    track.pause();
  }

  button.addEventListener("click", () => {
    if (playing) {
      stop();
    } else {
      start();
    }
  });
  slider.addEventListener("input", setVolume);
  track.addEventListener("error", () => {
    status.textContent = "The provided audio file could not be loaded. Check the local static audio file.";
    status.classList.add("error");
  });
  setVolume();
})();
</script>
</body>
</html>
"""
