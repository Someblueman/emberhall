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
    this.hidden = false; this.disabled = false;
  }
  appendChild(child) { this.children.push(child); child.parent = this; return child; }
  replaceChildren(...items) {
    this.children = [];
    // A native select loses its selection when its options are removed.
    if (this.tag === "select") this.value = "";
    for (const item of items) this.appendChild(item);
  }
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

function assertControlsLabeled(page) {
  for (const field of page.nodes.filter(n => n.tag === "textarea" || n.tag === "select" || n.tag === "input")) {
    assert(page.nodes.some(n => n.tag === "label" && n.htmlFor === field.id), `missing label for ${field.id}`);
    assert.equal(field.attributes.tabindex, undefined, "ordinary native keyboard controls");
  }
}

function exercise(envelope) {
  const page = setup(envelope);
  const bodies = page.nodes.filter(n => n.tag === "textarea" && n.id.startsWith("comment-"));
  const selects = page.nodes.filter(n => n.tag === "select" && n.id.startsWith("comment-") && n.id.endsWith("-resolution"));
  assert.equal(bodies.length, envelope.document.comments.length);
  assert.equal(selects.length, bodies.length);
  assertControlsLabeled(page);
  if (!bodies.length) {
    assert(page.nodes.some(n => n.textContent.includes("No comments yet")));
    page.elements.download.fire("click");
    assert.deepEqual(JSON.parse(page.blobs[0].text), envelope);
    return page;
  }
  const find = id => page.nodes.find(n => n.id === id);
  const filterRes = find("filter-resolution");
  const filterState = find("filter-state");
  const filterQuery = find("filter-comment-query");
  const filterStatus = find("comment-filter-status");
  assert(filterRes && filterState && filterQuery && filterStatus, "comment filter controls must exist");
  if (envelope.document.comments.length >= 2) {
    filterState.value = "orphan"; filterState.fire("change");
    const articles = page.nodes.filter(n => n.tag === "article");
    const indexItems = page.elements["comment-index"].children;
    assert.equal(articles[0].hidden, true);
    assert.equal(indexItems[0].hidden, true);
    assert.equal(articles[1].hidden, false);
    assert(filterStatus.textContent.includes("Showing 1 of 2"));
    // Hidden invalid field must be revealed and focused when download validates.
    bodies[0].value = "   "; bodies[0].fire("input");
    page.elements.download.fire("click");
    assert.equal(page.blobs.length, 0);
    assert.equal(articles[0].hidden, false);
    assert.equal(filterState.value, "all");
    assert.equal(bodies[0].focused, true);
    assert(page.elements["editor-status"].textContent.includes("blocked"));
  }
  const first = envelope.document.comments[0];
  bodies[0].value = first.body; bodies[0].fire("input");
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
  assertControlsLabeled(page);
  if (!anchors.length) {
    assert(page.nodes.some(n => n.textContent.includes("no rendered lines")));
    page.elements.download.fire("click");
    return page;
  }
  const find = id => page.nodes.find(n => n.id === id);
  const identifier = find("new-id");
  const body = find("new-body");
  const line = find("new-anchor");
  const filterFile = find("filter-file");
  const filterSide = find("filter-side");
  const filterText = find("filter-text");
  const anchorStatus = find("anchor-filter-status");
  const form = page.nodes.find(n => n.tag === "form");
  for (const field of [identifier, body, line, filterFile, filterSide, filterText]) {
    assert(field, "composer control must exist");
    assert(page.nodes.some(n => n.tag === "label" && n.htmlFor === field.id));
  }
  assert(anchorStatus && anchorStatus.textContent.includes(String(anchors.length)));
  if (anchors.length > 1) {
    filterText.value = "zzz-unmatched-filter-value"; filterText.fire("input");
    assert.equal(line.children.length, 0);
    assert(find("new-anchor-preview").textContent.includes("No rendered line matches"));
    identifier.value = "blocked-no-anchor"; identifier.fire("input");
    body.value = "Should fail cleanly"; body.fire("input");
    form.fire("submit");
    assert.notEqual(line.validityMessage, "");
    assert.equal(line.focused, true);
    assert.equal(page.nodes.filter(n => n.tag === "article").length, envelope.document.comments.length);
    filterText.value = ""; filterText.fire("input");
    identifier.value = ""; identifier.fire("input");
    body.value = ""; body.fire("input");
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
  filterFile.value = anchors.at(-1).path; filterFile.fire("change");
  filterSide.value = anchors.at(-1).side; filterSide.fire("change");
  assert.equal(line.value, String(anchors.length - 1), "retain the selected original anchor while filtering");
  assert(find("new-anchor-preview").textContent.includes(anchors.at(-1).commit));
  body.value = "New offline café question"; body.fire("input"); form.fire("submit");
  assert.equal(identifier.value, ""); assert.equal(body.value, "");
  assert.equal(page.nodes.filter(n => n.tag === "article").length, envelope.document.comments.length + 1);
  // Newly appended comment appears in same-line preview for its anchor.
  assert(find("new-anchor-preview").textContent.includes("offline-new-1"));
  identifier.value = "offline-new-1"; identifier.fire("input");
  body.value = "Collision"; body.fire("input"); form.fire("submit");
  assert(identifier.validityMessage);
  identifier.value = "offline-new-2"; identifier.fire("input");
  body.value = "Old or new side question"; body.fire("input");
  filterFile.value = ""; filterFile.fire("change");
  filterSide.value = ""; filterSide.fire("change");
  line.value = "0"; line.fire("change"); form.fire("submit");
  // Newly appended records use the same edit and resolution controls as originals.
  const stagedBodies = page.nodes.filter(n => n.tag === "textarea" && n.id.startsWith("comment-"));
  stagedBodies.at(-1).value += " edited"; stagedBodies.at(-1).fire("input");
  const stagedResolution = page.nodes.filter(n => n.tag === "select" && n.id.endsWith("-resolution"));
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

function exerciseRichComposer(envelope, anchors) {
  const page = setup(envelope, anchors);
  assertControlsLabeled(page);
  const find = id => page.nodes.find(n => n.id === id);
  const filterFile = find("filter-file");
  const filterSide = find("filter-side");
  const filterText = find("filter-text");
  const line = find("new-anchor");
  const preview = find("new-anchor-preview");
  // Multi-file and side filtering preserves original indices in anchors array.
  assert.equal(filterFile.children.length, 3); // All files + alpha.py + beta.py
  filterFile.value = "beta.py"; filterFile.fire("change");
  assert.equal(line.children.length, 5);
  assert.equal(line.children[0].value, "5");
  filterSide.value = "old"; filterSide.fire("change");
  assert.equal(line.children.length, 2);
  assert.equal(line.children[0].value, "5");
  filterText.value = "target"; filterText.fire("input");
  assert.equal(line.children.length, 1);
  assert.equal(line.value, "6");
  // Preview shows surrounding context lines with selected line marked.
  assert(preview.textContent.includes("> 2: old target"));
  assert(preview.textContent.includes("  1: old before"));
  // Quick reply button on anchored comment jumps composer to that exact anchor.
  const replyBtn = page.nodes.find(n => n.tag === "button" && n.textContent === "Comment on same line");
  assert(replyBtn, "anchored comment should offer Comment on same line in compose mode");
  replyBtn.fire("click");
  assert.equal(filterFile.value, "alpha.py");
  assert.equal(filterSide.value, "new");
  assert.equal(filterText.value, "");
  assert.equal(line.value, "2");
  assert(preview.textContent.includes("> 3: line three"));
  assert(preview.textContent.includes("  1: line one"));
  assert(preview.textContent.includes("  5: line five"));
  assert(preview.textContent.includes("reader-1"));
  assert.equal(find("new-id").focused, true);
}

function exerciseContextGaps(envelope) {
  for (const lines of [[1, 100], [1, 2, 4, 5, 50, 53, 54, 97, 100, 101, 103, 104]]) {
    const anchors = ["alpha.py", "beta.py"].flatMap(path => ["old", "new"].flatMap(side =>
      lines.map(line => ({commit: (side === "old" ? "a" : "b").repeat(40), path, side, line,
        text: `${path}/${side}/${line}`}))));
    const page = setup({...envelope, document: {...envelope.document, comments: []}}, anchors);
    const find = id => page.nodes.find(n => n.id === id);
    const line = find("new-anchor");
    const preview = find("new-anchor-preview");
    // Check exact inclusive +/-3 boundaries, sparse hunks, file/side isolation,
    // and previews at each edge of the available line range.
    anchors.forEach((selected, i) => {
      line.value = String(i); line.fire("change");
      const shown = preview.textContent.split("\n").filter(text => /^[ >] \d+: /.test(text));
      const expected = anchors.filter(a => a.path === selected.path && a.side === selected.side &&
        Math.abs(a.line - selected.line) <= 3);
      assert.deepEqual(shown, expected.map(a => `${a.line === selected.line ? ">" : " "} ${a.line}: ${a.text}`),
        `context for ${selected.path} ${selected.side} ${selected.line}`);
    });
    // Searching down to one option must still show nearby available context,
    // without pulling a distant hunk into the preview.
    find("filter-file").value = "beta.py"; find("filter-file").fire("change");
    find("filter-side").value = "old"; find("filter-side").fire("change");
    find("filter-text").value = "100"; find("filter-text").fire("input");
    assert.equal(line.children.length, 1);
    assert(preview.textContent.includes("> 100: beta.py/old/100"));
    assert.equal(preview.textContent.includes("  1: beta.py/old/1"), false);
    if (lines.length > 2) assert(preview.textContent.includes("  97: beta.py/old/97"));
  }
}

function exerciseSelectionFiltering(envelope, anchors) {
  const page = setup({...envelope, document: {...envelope.document, comments: []}}, anchors);
  const find = id => page.nodes.find(n => n.id === id);
  const line = find("new-anchor");
  const selected = anchors.length - 1;
  line.value = String(selected); line.fire("change");
  find("new-id").value = "keep-selected-line"; find("new-id").fire("input");
  find("new-body").value = "Question on the selected line"; find("new-body").fire("input");
  for (const [id, value, event] of [
    ["filter-text", "new", "input"],
    ["filter-file", anchors[selected].path, "change"],
    ["filter-side", anchors[selected].side, "change"],
    ["filter-text", "three", "input"],
    ["filter-text", "", "input"],
    ["filter-file", "", "change"],
    ["filter-side", "", "change"],
  ]) {
    find(id).value = value; find(id).fire(event);
    assert.equal(line.value, String(selected), `selection after ${id}=${value}`);
  }
  page.nodes.find(n => n.tag === "form").fire("submit");
  page.elements.download.fire("click");
  const saved = JSON.parse(page.blobs[0].text);
  assert.deepEqual(saved.document.comments[0].anchor, anchors[selected]);
  // If the selected anchor is excluded, select the first actual matching anchor.
  find("filter-file").value = "alpha.py"; find("filter-file").fire("change");
  assert.equal(line.value, "0");
  assert(find("new-anchor-preview").textContent.includes("alpha.py | new line 1"));
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
  const multiAnchors = [
    {commit: "b".repeat(40), path: "alpha.py", side: "new", line: 1, text: "line one"},
    {commit: "b".repeat(40), path: "alpha.py", side: "new", line: 2, text: "line two"},
    {commit: "b".repeat(40), path: "alpha.py", side: "new", line: 3, text: "line three"},
    {commit: "b".repeat(40), path: "alpha.py", side: "new", line: 4, text: "line four"},
    {commit: "b".repeat(40), path: "alpha.py", side: "new", line: 5, text: "line five"},
    {commit: "a".repeat(40), path: "beta.py", side: "old", line: 1, text: "old before"},
    {commit: "a".repeat(40), path: "beta.py", side: "old", line: 2, text: "old target"},
    {commit: "b".repeat(40), path: "beta.py", side: "new", line: 1, text: "new one"},
    {commit: "b".repeat(40), path: "beta.py", side: "new", line: 2, text: "new two"},
    {commit: "b".repeat(40), path: "beta.py", side: "new", line: 3, text: "new three"},
  ];
  const richRecord = {id: "reader-1", anchor: multiAnchors[2], body: "Check line three", resolution: "open", state: "anchored", rebased_from: null, orphan_reason: null};
  const richCompose = {
    ...compose,
    document: {format: "skein-comments", version: 2, comments: [richRecord, {...richRecord, id: "reader-2", state: "orphan", resolution: "resolved", orphan_reason: "moved", rebased_from: multiAnchors[2]}]},
  };
  exerciseRichComposer(richCompose, multiAnchors);
  exerciseContextGaps(compose);
  exerciseSelectionFiltering(compose, multiAnchors);
}
console.log("editor event/data checks passed (no browser witness)");
