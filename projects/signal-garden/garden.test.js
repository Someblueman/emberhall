"use strict";
// Handler/state checks with a tiny DOM double. No browser/layout/keyboard claim.
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");

function page() {
  class Element {
    constructor() { this.children = []; this.events = {}; this.attributes = {}; this.value = ""; this.hidden = false; this.textContent = ""; }
    append(...children) { this.children.push(...children); }
    replaceChildren(...children) { this.children = children; }
    setAttribute(name, value) { this.attributes[name] = value; }
    addEventListener(name, handler) { this.events[name] = handler; }
    focus() { focused = this; }
    fire(name) { if (!this.disabled) this.events[name](); }
  }
  const html = fs.readFileSync(path.join(__dirname, "index.html"), "utf8");
  const elements = Object.fromEntries([...html.matchAll(/id="([^"]+)"/g)].map(match => [match[1], new Element()]));
  let focused;
  elements["burst-start"].value = "1";
  elements["burst-length"].value = "4";
  elements.begin.disabled = true;
  elements.walkthrough.hidden = true;
  const context = vm.createContext({ document: {
    getElementById: id => elements[id], createElement: () => new Element()
  } });
  for (const file of ["model.js", "garden.js"]) {
    vm.runInContext(fs.readFileSync(path.join(__dirname, file), "utf8"), context, { filename: file });
  }
  const predict = (value = "interleaved") => {
    elements.prediction.value = value;
    elements.prediction.fire("change");
    elements.begin.fire("click");
  };
  return { elements, predict, focused: () => focused };
}

test("prediction gates the reveal, steps withhold the verdict until decoding, and back clears it", () => {
  const { elements: e, predict, focused } = page();
  assert.equal(e.picture.children.length, 16);
  assert.equal(e.begin.disabled, true);
  e.begin.fire("click"); assert.equal(e.walkthrough.hidden, true);
  predict();
  assert.equal(e.walkthrough.hidden, false);
  assert.equal(focused(), e["stage-title"]);
  assert.match(e["stage-title"].textContent, /Encode/);
  assert.equal(e.verdict.hidden, true);
  assert.doesNotMatch(e.trace.textContent, /changed pixel|recovered/);
  for (let step = 1; step <= 3; step++) {
    e.next.fire("click");
    assert.equal(e.comparison.children.length, 2);
    assert.equal(e.verdict.hidden, step !== 3);
    if (step < 3) assert.doesNotMatch(e.trace.textContent, /changed pixel|recovered/);
  }
  assert.match(e.verdict.textContent, /Your prediction matches.*Only interleaved/);
  assert.match(e.trace.textContent, /simulator knowledge/);
  e.previous.fire("click");
  assert.equal(e.verdict.hidden, true);
  assert.equal(e.verdict.textContent, "");
  assert.doesNotMatch(e.trace.textContent, /changed pixel|recovered/);
});

test("input edits reset prediction/results and tile state; end bursts are clamped", () => {
  const { elements: e, predict } = page();
  predict();
  const tile = e.picture.children[0];
  tile.fire("click");
  assert.equal(tile.textContent, "1");
  assert.equal(tile.attributes["aria-pressed"], "true");
  assert.equal(e.walkthrough.hidden, true);
  assert.equal(e.begin.disabled, true);
  assert.equal(e.trace.textContent, "");
  e["reset-picture"].fire("click");
  assert.equal(tile.textContent, "0");
  e["burst-start"].value = "25";
  e["burst-length"].value = "8";
  e["burst-length"].fire("change");
  assert.equal(e["burst-start"].max, "21");
  assert.equal(e["burst-start"].value, "21");
  assert.equal(e["start-value"].textContent, "21");
  predict("neither");
  e.next.fire("click"); e.next.fire("click"); e.next.fire("click");
  assert.match(e.trace.textContent, /21\.\.28/);
  e["try-again"].fire("click");
  assert.equal(e.walkthrough.hidden, true);
  assert.equal(e.prediction.value, "");
});

test("changing a prediction clears old results and preserves the newly chosen answer", () => {
  const { elements: e, predict } = page();
  predict();
  e.prediction.value = "both"; e.prediction.fire("change");
  assert.equal(e.prediction.value, "both");
  assert.equal(e.begin.disabled, false);
  assert.equal(e.walkthrough.hidden, true);
  e.begin.fire("click");
  e.next.fire("click"); e.next.fire("click"); e.next.fire("click");
  assert.match(e.verdict.textContent, /A surprise to investigate/);
  e.next.fire("click");
  assert.match(e["stage-title"].textContent, /Encode/);
  assert.equal(e.verdict.hidden, true);
});
