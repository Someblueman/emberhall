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

test("sampleDeck provides a valid, cloned starter deck with immediately due cards", () => {
  assert.equal(typeof Cards.sampleDeck, "function");
  const first = Cards.sampleDeck();
  const second = Cards.sampleDeck();
  assert.equal(first.format, Cards.FORMAT);
  assert.equal(first.version, Cards.VERSION);
  assert.equal(first.cards.length, 4);
  assert.equal(Cards.queue(first, 0).length, 4);
  assert.equal(Cards.serialize(first), Cards.serialize(second));
  first.cards[0].front = "Mutated";
  assert.notEqual(second.cards[0].front, "Mutated");
});

test("page opens with playable sample deck, supports reveal/grade/clear/reload, and guards card edits", async () => {
  class Element {
    constructor(tag = "div") {
      this.tagName = tag;
      this.children = []; this.handlers = {}; this.value = ""; this.dataset = {};
      this.attributes = {};
      this.hiddenClass = false;
      this.classList = {
        add: (...cls) => { if (cls.includes("hidden")) this.hiddenClass = true; },
        remove: (...cls) => { if (cls.includes("hidden")) this.hiddenClass = false; },
        toggle: (cls, force) => {
          if (cls === "hidden") this.hiddenClass = force === undefined ? !this.hiddenClass : Boolean(force);
        }
      };
    }
    setAttribute(name, val) { this.attributes[name] = String(val); }
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
  let exported, confirmResult = true, prompt;
  vm.runInNewContext(source[1], {
    document: {
      getElementById: get,
      createElement: tag => new Element(tag),
      querySelector: () => null
    },
    crypto: require("node:crypto").webcrypto, Blob,
    URL: {createObjectURL(blob) { exported = blob; return "blob:test"; }, revokeObjectURL() {}},
    window: {print() {}, confirm(message) { prompt = message; return confirmResult; }}
  });
  const submit = () => get("card-form").handlers.submit({preventDefault() {}});
  const exportDeck = async () => { get("export").click(); return JSON.parse(await exported.text()); };

  assert.equal(get("card-list").children.length, 4, "starter deck renders 4 cards on open");
  assert.match(get("queue-summary").textContent, /4 due now · 4 cards total/);
  const revealBtn = get("review-card").children.find(child => child.tagName === "button");
  assert.ok(revealBtn, "Reveal back button renders immediately on open");
  revealBtn.click();
  assert.equal(get("review-actions").hiddenClass, false, "grade actions appear after reveal");
  get("review-actions").handlers.click({target: {dataset: {grade: "good"}}});
  assert.match(get("queue-summary").textContent, /3 due now · 4 cards total/);

  // A typed new-card draft and the currently revealed review card survive either cancellation.
  get("front").value = "Unfinished front"; get("back").value = "Unfinished back";
  get("review-card").children.find(child => child.tagName === "button").click();
  const before = await exportDeck();
  assert.equal(before.cards[0].state.reviews, 1);
  confirmResult = false;
  for (const control of ["clear-deck", "load-sample"]) {
    get(control).click();
    assert.match(prompt, /cards, review progress, and unfinished form will be lost/i);
    assert.deepEqual(await exportDeck(), before);
    assert.equal(get("front").value, "Unfinished front");
    assert.equal(get("back").value, "Unfinished back");
    assert.equal(get("review-card").children[0].textContent, "Back");
    assert.equal(get("review-actions").hiddenClass, false);
  }
  confirmResult = true;
  get("load-sample").click();
  assert.equal(get("front").value, ""); assert.equal(get("back").value, "");
  assert.equal((await exportDeck()).cards[0].state.reviews, 0, "confirmed sample replacement resets history");
  assert.equal(get("review-card").children[0].textContent, "Front");
  get("review-card").children.find(child => child.tagName === "button").click();
  get("review-actions").handlers.click({target: {dataset: {grade: "good"}}});
  get("front").value = "Another draft"; get("back").value = "Another answer";
  get("clear-deck").click();
  assert.equal(get("front").value, ""); assert.equal(get("back").value, "");
  assert.equal(get("card-list").children.length, 0, "Clear deck empties the deck");
  assert.match(get("queue-summary").textContent, /0 due now · 0 cards total/);

  get("front").value = "Draft to replace"; get("back").value = "Draft answer";
  get("load-sample").click();
  assert.equal(get("front").value, ""); assert.equal(get("back").value, "");
  assert.equal(get("card-list").children.length, 4, "Load sample deck restores 4 cards");
  assert.equal((await exportDeck()).cards[0].state.reviews, 0);
  assert.match(get("queue-summary").textContent, /4 due now · 4 cards total/);

  get("clear-deck").click();
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
