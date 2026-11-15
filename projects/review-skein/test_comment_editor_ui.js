"use strict";
// Event/data checks only. This small DOM substitute does not test browser layout,
// focus order, actual downloads or assistive technology.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const {startEditor} = require("./comment_editor.js");

class Element {
  constructor(tag) {
    this.tag = tag; this.children = []; this.listeners = {}; this.attributes = {};
    this.textContent = ""; this.value = ""; this.validityMessage = "";
  }
  appendChild(child) { this.children.push(child); child.parent = this; return child; }
  setAttribute(key, value) { this.attributes[key] = value; }
  addEventListener(event, handler) { this.listeners[event] = handler; }
  fire(event) { this.listeners[event]({preventDefault() {}}); }
  setCustomValidity(message) { this.validityMessage = message; }
  reportValidity() { return this.validityMessage === ""; }
  focus() { this.focused = true; }
  click() { this.clicked = true; }
  remove() { this.parent.children.splice(this.parent.children.indexOf(this), 1); }
}

function setup(envelope, anchors) {
  const elements = Object.fromEntries(["editor-data", "editor-status", "download", "comments", "comment-index", "composer"]
    .map(id => [id, new Element("div")]));
  elements["editor-data"].textContent = JSON.stringify(envelope);
  if (anchors) {
    elements["anchor-data"] = new Element("script");
    elements["anchor-data"].textContent = JSON.stringify(anchors);
  }
  const document = {body: new Element("body"), getElementById: id => elements[id], createElement: tag => new Element(tag)};
  const blobs = []; const revoked = []; const timers = []; const listeners = {};
  const environment = {
    Blob: class { constructor(parts, options) { this.text = parts.join(""); this.type = options.type; } },
    URL: {createObjectURL: blob => { blobs.push(blob); return "blob:test"; }, revokeObjectURL: url => revoked.push(url)},
    setTimeout: callback => timers.push(callback), addEventListener: (name, callback) => { listeners[name] = callback; },
  };
  startEditor(document, environment);
  const all = element => [element, ...element.children.flatMap(all)];
  return {elements, get nodes() { return Object.values(elements).flatMap(all); }, blobs, timers, revoked, listeners};
}

function exercise(envelope) {
  const page = setup(envelope);
  const bodies = page.nodes.filter(n => n.tag === "textarea");
  const selects = page.nodes.filter(n => n.tag === "select");
  assert.equal(bodies.length, envelope.document.comments.length);
  assert.equal(selects.length, bodies.length);
  for (const field of [...bodies, ...selects]) {
    assert(page.nodes.some(n => n.tag === "label" && n.htmlFor === field.id));
    assert.equal(field.attributes.tabindex, undefined, "ordinary native keyboard controls");
  }
  if (!bodies.length) {
    assert(page.nodes.some(n => n.textContent.includes("No comments yet")));
    page.elements.download.fire("click");
    assert.deepEqual(JSON.parse(page.blobs[0].text), envelope);
    return page;
  }
  const first = envelope.document.comments[0];
  assert.equal(bodies[0].value, first.body);
  assert(page.nodes.some(n => n.tag === "pre" && n.textContent.includes(first.anchor.path)));
  for (const record of envelope.document.comments.filter(c => c.state === "orphan")) {
    assert(page.nodes.some(n => n.textContent.includes(record.orphan_reason)));
    assert(page.nodes.some(n => n.textContent === "Rebased from"));
  }
  bodies[0].value = "   "; bodies[0].fire("input");
  page.elements.download.fire("click");
  assert.equal(page.blobs.length, 0);
  assert.equal(bodies[0].focused, true);
  assert(page.elements["editor-status"].textContent.includes("blocked"));
  for (const invalid of ["x".repeat(20001), "NUL\0body"]) {
    bodies[0].value = invalid; bodies[0].fire("input");
    assert.notEqual(bodies[0].validityMessage, "");
  }
  bodies[0].value = 'Edited café ☃ <script> & "quoted"'; bodies[0].fire("input");
  selects[0].value = "resolved"; selects[0].fire("change");
  selects[0].value = "open"; selects[0].fire("change");
  selects[0].value = "resolved"; selects[0].fire("change");
  assert.equal(bodies[0].validityMessage, "");
  assert(page.elements["editor-status"].textContent.includes("1 changed"));
  let prevented = false;
  page.listeners.beforeunload({preventDefault() { prevented = true; }});
  assert(prevented);
  page.elements.download.fire("click");
  assert.equal(page.blobs[0].type, "application/json");
  const saved = JSON.parse(page.blobs[0].text);
  assert.equal(saved.document.comments[0].resolution, "resolved");
  assert.equal(saved.document.comments[0].body, bodies[0].value);
  assert.deepEqual({...saved.document.comments[0], body: first.body, resolution: first.resolution}, first);
  assert.deepEqual(saved.document.comments.slice(1), envelope.document.comments.slice(1));
  assert.equal(saved.base_sha256, envelope.base_sha256);
  assert(page.elements["editor-status"].textContent.includes("Download requested"));
  assert.equal(page.revoked.length, 0);
  page.timers.forEach(timer => timer());
  assert.deepEqual(page.revoked, ["blob:test"]);
  prevented = false;
  page.listeners.beforeunload({preventDefault() { prevented = true; }});
  assert.equal(prevented, false);
  bodies[0].value += " next edit"; bodies[0].fire("input");
  page.listeners.beforeunload({preventDefault() { prevented = true; }});
  assert(prevented);
  return page;
}

function exerciseComposer(envelope, anchors) {
  const page = setup(envelope, anchors);
  if (!anchors.length) {
    assert(page.nodes.some(n => n.textContent.includes("no rendered lines")));
    page.elements.download.fire("click");
    return page;
  }
  const find = id => page.nodes.find(n => n.id === id);
  const identifier = find("new-id");
  const body = find("new-body");
  const line = find("new-anchor");
  const form = page.nodes.find(n => n.tag === "form");
  for (const field of [identifier, body, line]) {
    assert(page.nodes.some(n => n.tag === "label" && n.htmlFor === field.id));
  }
  identifier.value = "bad id"; identifier.fire("input");
  body.value = "Question"; body.fire("input");
  page.elements.download.fire("click");
  assert.equal(page.blobs.length, 0, "unfinished draft must not silently disappear from a download");
  form.fire("submit");
  assert(identifier.validityMessage);
  identifier.value = "offline-new-1"; identifier.fire("input");
  body.value = " "; body.fire("input"); form.fire("submit");
  assert(body.validityMessage);
  line.value = String(anchors.length - 1); line.fire("change");
  assert(find("new-anchor-preview").textContent.includes(anchors.at(-1).commit));
  body.value = "New offline café question"; body.fire("input"); form.fire("submit");
  assert.equal(identifier.value, ""); assert.equal(body.value, "");
  assert.equal(page.nodes.filter(n => n.tag === "article").length, envelope.document.comments.length + 1);
  identifier.value = "offline-new-1"; identifier.fire("input");
  body.value = "Collision"; body.fire("input"); form.fire("submit");
  assert(identifier.validityMessage);
  identifier.value = "offline-new-2"; identifier.fire("input");
  body.value = "Old or new side question"; body.fire("input");
  line.value = "0"; form.fire("submit");
  // Newly appended records use the same edit and resolution controls as originals.
  const stagedBodies = page.nodes.filter(n => n.tag === "textarea" && n.id.startsWith("comment-"));
  stagedBodies.at(-1).value += " edited"; stagedBodies.at(-1).fire("input");
  const stagedResolution = page.nodes.filter(n => n.tag === "select" && n.id.startsWith("comment-"));
  stagedResolution.at(-1).value = "resolved"; stagedResolution.at(-1).fire("change");
  let prevented = false;
  page.listeners.beforeunload({preventDefault() { prevented = true; }});
  assert(prevented);
  page.elements.download.fire("click");
  const saved = JSON.parse(page.blobs[0].text);
  assert.equal(saved.version, 2);
  assert.equal(saved.document.comments.length, envelope.document.comments.length + 2);
  assert.deepEqual(saved.document.comments.slice(0, envelope.document.comments.length), envelope.document.comments);
  assert.deepEqual(saved.document.comments.at(-2).anchor, anchors.at(-1));
  assert.deepEqual(saved.document.comments.at(-1).anchor, anchors[0]);
  assert.equal(saved.document.comments.at(-1).resolution, "resolved");
  assert.equal(saved.packet_sha256, envelope.packet_sha256);
  assert.equal(saved.anchors_sha256, envelope.anchors_sha256);
  return page;
}

if (process.argv.length > 2) {
  const envelope = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
  const page = process.argv[4] ? exerciseComposer(envelope, JSON.parse(fs.readFileSync(process.argv[4], "utf8"))) : exercise(envelope);
  fs.writeFileSync(process.argv[3], page.blobs[0].text);
} else {
  const anchor = {commit: "a".repeat(40), path: "café.py", side: "new", line: 2, text: "<code>"};
  const record = {id: "reader-1", anchor, body: "Original", resolution: "open", state: "anchored", rebased_from: null, orphan_reason: null};
  const envelope = {format: "skein-comment-edits", version: 1, base_sha256: "b".repeat(64), document: {format: "skein-comments", version: 2, comments: [record,
    {...record, id: "reader-2", state: "orphan", orphan_reason: "line gone", rebased_from: anchor}]}};
  exercise(envelope);
  exercise({...envelope, document: {...envelope.document, comments: []}});
  const compose = {...envelope, version: 2, packet_sha256: "c".repeat(64), anchors_sha256: "d".repeat(64)};
  exerciseComposer(compose, [anchor]);
  exerciseComposer({...compose, document: {...compose.document, comments: []}}, [anchor]);
  exerciseComposer({...compose, document: {...compose.document, comments: []}}, []);
}
console.log("editor event/data checks passed (no browser witness)");
