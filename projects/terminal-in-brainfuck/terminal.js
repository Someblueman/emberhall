"use strict";
// Transport and display only: no text placement, wrap, erase or scroll rules.
const ROWS = 24, COLS = 40, FRAME_SIZE = 964;
const $ = id => document.getElementById(id);
let machine, frameBytes = [], lastFrame = null, framesSeen = 0;
let running = false, timer = null, targetFrame = null, error = "";
let followHead = true;

function receive(byte) {
  frameBytes.push(byte);
  if (frameBytes.length === 1 && byte !== 255) throw new Error("Missing frame start marker");
  if (frameBytes.length !== FRAME_SIZE) return;
  const row = frameBytes[961], col = frameBytes[962];
  if (byte !== 254 || row >= ROWS || col >= COLS ||
      frameBytes.slice(1, 961).some(n => n < 32 || n > 126)) {
    throw new Error("Malformed screen frame");
  }
  lastFrame = {cells: frameBytes.slice(1, 961), row, col};
  frameBytes = [];
  framesSeen++;
}

function stop() {
  running = false;
  targetFrame = null;
  if (timer !== null) cancelAnimationFrame(timer);
  timer = null;
  $("run").textContent = "Run";
}

function attempt(action) {
  try { error = ""; action(); }
  catch (e) { error = e.message; stop(); }
  render();
}

function reset(bytes) {
  stop();
  frameBytes = []; lastFrame = null; framesSeen = 0;
  machine = new BrainfuckMachine(BF_PROGRAM, receive);
  machine.feed(bytes);
  // Initialisation is bounded and stops exactly on its complete empty frame.
  // No input byte is consumed until the visitor presses Run or Next frame.
  let batches = 0;
  while (!framesSeen && batches++ < 500) machine.run(20000, () => framesSeen > 0);
  if (!framesSeen) throw new Error("The program did not produce its initial frame");
}

function tick() {
  timer = null;
  attempt(() => {
    const before = framesSeen, until = performance.now() + 10;
    do {
      const boundary = framesSeen + 1;
      machine.run(10000, () => framesSeen >= boundary);
      if (targetFrame !== null && framesSeen >= targetFrame) break;
    } while (!machine.waiting && !machine.halted &&
      framesSeen - before < 4 && performance.now() < until);
    if (machine.halted || machine.waiting || (targetFrame !== null && framesSeen >= targetFrame)) stop();
    if (running) timer = requestAnimationFrame(tick);
  });
}

function play(oneFrame = false) {
  stop();
  if (machine.halted) return;
  targetFrame = oneFrame ? framesSeen + 1 : null;
  running = true;
  $("run").textContent = "Pause";
  timer = requestAnimationFrame(tick);
}

function render() {
  if (!machine) return;
  if (lastFrame) {
    const fragment = document.createDocumentFragment();
    for (let r = 0; r < ROWS; r++) {
      const row = String.fromCharCode(...lastFrame.cells.slice(r * COLS, (r + 1) * COLS));
      if (r === lastFrame.row) {
        const cursor = document.createElement("span");
        cursor.className = "cursor";
        cursor.textContent = row[lastFrame.col];
        fragment.append(row.slice(0, lastFrame.col), cursor, row.slice(lastFrame.col + 1));
      } else fragment.append(row);
      if (r < ROWS - 1) fragment.append("\n");
    }
    $("screen").replaceChildren(fragment);
    $("position").textContent = `Emitted cursor: row ${lastFrame.row + 1}, column ${lastFrame.col + 1}`;
  }
  const state = error ? `Stopped: ${error}` : machine.halted ? "Halted. Reset to begin again." :
    machine.waiting ? "Waiting for input (not ended)." : running ? "Running." : "Paused.";
  $("status").textContent = `${state} ${machine.consumed} bytes read · ${machine.queued} queued · ${framesSeen} frames.`;
  $("machine-position").textContent = `Next: ${machine.instruction} at command ${machine.pc ?? "end"} · head ${machine.ptr} · ${machine.instructions.toLocaleString()} instructions executed`;
  $("partial").textContent = frameBytes.length ? `A new frame is being emitted: ${frameBytes.length} / ${FRAME_SIZE} bytes. The screen above is the last complete frame.` : "The screen above is the last complete emitted frame.";
  let lo = followHead ? Math.floor(machine.ptr / 32) * 32 : Number($("tape-start").value);
  lo = Math.max(0, Math.min(machine.tape.length - 32, Math.trunc(lo) || 0));
  $("tape-start").value = lo;
  const fragment = document.createDocumentFragment();
  for (let i = lo; i < lo + 32; i++) {
    const cell = document.createElement("span");
    cell.className = i === machine.ptr ? "cell head" : "cell";
    const ch = machine.tape[i] >= 32 && machine.tape[i] <= 126 ? String.fromCharCode(machine.tape[i]) : "·";
    cell.textContent = `${i}\n${machine.tape[i]} ${ch}`;
    cell.title = `Cell ${i}, value ${machine.tape[i]}${i === machine.ptr ? ", tape head" : ""}`;
    fragment.append(cell);
  }
  $("tape").replaceChildren(fragment);
  $("follow").setAttribute("aria-pressed", String(followHead));
  $("step").disabled = machine.halted || running;
  $("instruction").disabled = machine.halted || running;
  $("end").disabled = machine.halted || machine.ended;
}

$("load").addEventListener("click", () => attempt(() => reset(encodeStream($("stream").value))));
$("clear").addEventListener("click", () => attempt(() => { reset([]); $("typebox").focus(); }));
$("step").addEventListener("click", () => attempt(() => play(true)));
$("instruction").addEventListener("click", () => attempt(() => { stop(); machine.step(); }));
$("run").addEventListener("click", () => attempt(() => { if (running) stop(); else play(); }));
$("end").addEventListener("click", () => attempt(() => { machine.end(); play(); }));
$("follow").addEventListener("click", () => { followHead = !followHead; render(); });
$("tape-start").addEventListener("change", () => { followHead = false; render(); });

function typeBytes(text) {
  if ([...text].some(c => c.codePointAt(0) > 127)) throw new Error("The live keyboard accepts ASCII only. Use \\xHH in the stream editor for other bytes.");
  machine.feed(Array.from(text, c => c.charCodeAt(0)));
  play();
}
$("typebox").addEventListener("input", e => {
  if (e.isComposing) return;
  const text = e.target.value;
  e.target.value = "";
  if (text) attempt(() => typeBytes(text));
});
$("typebox").addEventListener("keydown", e => {
  if (e.isComposing || e.altKey || e.ctrlKey || e.metaKey) return;
  if (e.key !== "Enter" && e.key !== "Backspace") return;
  e.preventDefault();
  attempt(() => typeBytes(e.key === "Enter" ? "\n" : "\b"));
});

const PRESETS = {
  "bell-dive": BELL_DIVE.full,
  "bell-catch": BELL_DIVE.catchAtBottom,
  overwrite: "HELLO, WORLD\\rbye",
  cursor: "ABCDE\\x1b[2DX\\x1b[0D!",
  erase: "TOP ROW\\r\\nABCDE\\x1b[2;3H\\x1b[K",
  wrap: "The quick brown fox jumps over the lazy dog",
  scroll: Array.from({length: 27}, (_, i) => "line " + String(i).padStart(2, "0") + "\\r").join("\n") + "\n",
};
for (const [id, text] of Object.entries(PRESETS)) {
  $("preset-" + id).addEventListener("click", () => attempt(() => {
    $("stream").value = text;
    reset(encodeStream(text));
  }));
}
attempt(() => reset(encodeStream($("stream").value)));
