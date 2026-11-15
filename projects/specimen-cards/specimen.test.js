"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const html = fs.readFileSync(require.resolve("./index.html"), "utf8");
const source = html.match(/<script>([\s\S]*?)<\/script>/);
assert.ok(source, "the page has one inline application script");
const context = {module: {exports: {}}, crypto: require("node:crypto").webcrypto};
vm.runInNewContext(source[1], context, {filename: "specimen-cards-inline.js"});
const Cards = context.module.exports;
const card = (id, due, box = 0) => ({id, front: `front ${id}`, back: `back ${id}`,
  state: {box, due, reviews: 0, lastReviewed: null, lastGrade: null, history: []}});
const deck = (...cards) => ({format: Cards.FORMAT, version: Cards.VERSION, cards});

test("inline model creates cards and serializes the complete review history losslessly", () => {
  const created = Cards.createCard("stable-1", "A front", "A back", 1000);
  const first = Cards.grade(created, "good", 1000);
  const reviewed = Cards.grade(first, "hard", first.state.due);
  const original = deck(reviewed, Cards.createCard("stable-2", "Unicode 🌱", "line one\nline two", 1000));
  const encoded = Cards.serialize(original);
  const imported = Cards.parse(encoded);
  assert.deepEqual(JSON.parse(JSON.stringify(imported)), JSON.parse(JSON.stringify(original)));
  assert.equal(Cards.serialize(imported), encoded);
});

test("due queue sorts by due timestamp then stable ID and grading follows fixed intervals", () => {
  const a = card("a", 0), b = card("b", 0), later = card("later", 2);
  assert.deepEqual(Cards.queue(deck(later, b, a), 1).map(item => item.id), ["a", "b"]);
  assert.deepEqual(Cards.queue(deck(later), 1), []);
  const hard = Cards.grade(a, "hard", 0);
  assert.equal(hard.state.box, 1);
  assert.equal(hard.state.due, 10 * 60_000);
  const good = Cards.grade(card("g", 0, 1), "good", 0);
  assert.equal(good.state.box, 2);
  assert.equal(good.state.due, 7 * 24 * 60 * 60_000);
  const easy = Cards.grade(card("e", 0, 4), "easy", 0);
  assert.equal(easy.state.box, 4);
  assert.equal(easy.state.due, 60 * 24 * 60 * 60_000);
  const again = Cards.grade(good, "again", good.state.due);
  assert.equal(again.state.box, 0);
  assert.equal(again.state.due, good.state.due + 5 * 60_000);
  assert.equal(again.state.history.length, 2);
  assert.throws(() => Cards.grade(a, "good", -1), /not due/);
});

test("strict version 1 validation rejects malformed, duplicate, unsupported, and nonfinite state", () => {
  const valid = deck(card("x", 0));
  for (const value of ["{", "null", JSON.stringify({...valid, version: 2}),
    JSON.stringify({...valid, surprise: true}),
    JSON.stringify(deck(card("same", 0), card("same", 0))),
    JSON.stringify(deck({...card("x", 0), front: ""})),
    JSON.stringify(deck({...card("x", 0), state: {...card("x", 0).state, due: 1.5}})),
    JSON.stringify(deck({...card("x", 0), state: {...card("x", 0).state, box: 5}})),
    JSON.stringify(deck({...card("x", 0), state: {...card("x", 0).state, extra: 0}}))]) {
    assert.throws(() => Cards.parse(value));
  }
  const infinity = deck(card("x", 0)); infinity.cards[0].state.due = Infinity;
  assert.throws(() => Cards.validate(infinity), /finite/);
});

test("a rejected hostile-text import leaves the current deck untouched and text stays data", () => {
  const original = deck(Cards.createCard("safe", "<img src=x onerror=alert(1)>", "<script>bad()</script>", 0));
  let current = original;
  try { current = Cards.parse(JSON.stringify({...original, version: 999})); } catch (_) { /* UI commits only after parse succeeds. */ }
  assert.equal(current, original);
  const imported = Cards.parse(Cards.serialize(original));
  assert.equal(imported.cards[0].front, "<img src=x onerror=alert(1)>");
  assert.equal(imported.cards[0].back, "<script>bad()</script>");
  assert.match(html, /textContent = text/);
  assert.doesNotMatch(html, /innerHTML\s*=/);
});

test("deleting an edited card permits a new save, and a missing edit target preserves the draft", async () => {
  class Element {
    constructor() {
      this.children = []; this.handlers = {}; this.value = ""; this.dataset = {};
      this.classList = {add() {}, remove() {}, toggle() {}};
    }
    append(...items) { this.children.push(...items); }
    replaceChildren(...items) { this.children = items; }
    addEventListener(type, handler) { this.handlers[type] = handler; }
    focus() {}
    click() { this.handlers.click?.({target: this}); }
  }
  const elements = new Map();
  const get = id => {
    if (!elements.has(id)) elements.set(id, new Element());
    return elements.get(id);
  };
  get("card-form").reset = () => { get("front").value = ""; get("back").value = ""; };
  let exported;
  vm.runInNewContext(source[1], {
    document: {getElementById: get, createElement: () => new Element()},
    crypto: require("node:crypto").webcrypto, Blob,
    URL: {createObjectURL(blob) { exported = blob; return "blob:test"; }, revokeObjectURL() {}},
    window: {print() {}}
  });
  const submit = () => get("card-form").handlers.submit({preventDefault() {}});
  const exportDeck = async () => { get("export").click(); return JSON.parse(await exported.text()); };
  get("front").value = "Original"; get("back").value = "Answer"; submit();
  const buttons = get("card-list").children[0].children[1].children;
  buttons[0].click();
  const deletedId = get("card-id").value;
  buttons[1].click();
  assert.equal(get("card-id").value, "", "deleting the edit target clears its selection");
  get("front").value = "Replacement"; get("back").value = "New answer"; submit();
  const saved = await exportDeck();
  assert.equal(saved.cards.length, 1);
  assert.equal(saved.cards[0].front, "Replacement");
  assert.equal(saved.cards[0].back, "New answer");
  assert.notEqual(saved.cards[0].id, deletedId);

  get("card-id").value = deletedId;
  get("front").value = "Unsaved draft"; get("back").value = "Keep this answer"; submit();
  assert.match(get("status").textContent, /no longer exists/i);
  assert.equal(get("front").value, "Unsaved draft");
  assert.equal(get("back").value, "Keep this answer");
  assert.deepEqual(await exportDeck(), saved, "missing-target submission cannot alter the deck");
});
