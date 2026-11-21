"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const {validate, erase, verifyCodebook, move, route} = require("./player.js");
const episodes = require("./episodes.js");

test("episode embeds the exact saved words, and every output decodes uniquely", () => {
  validate(episodes);
  const original = fs.readFileSync(path.join(__dirname, "../two-deletion-codes/codebook_12.txt"), "utf8")
    .split(/\r?\n/).filter(line => line && !line.startsWith("#"));
  assert.deepEqual(episodes[0].exhibit.words, original);
  assert.equal(original.length, 36);
  assert.equal(erase("001011010010", [0, 1]), "1011010010");
  assert.equal(erase("001011010010", [0, 11]), "0101101001");
  const outputs = verifyCodebook(original);
  assert.equal(outputs.size, 544);
  for (const word of original) for (let i = 0; i < 11; i++) for (let j = i + 1; j < 12; j++) {
    assert.equal(outputs.get(erase(word, [i, j])), word);
  }
});

test("changed, repeated and ambiguous codebook data fail before display", () => {
  assert.throws(() => verifyCodebook(["000000000000", "000000000001"]), /Ambiguous/);
  assert.throws(() => verifyCodebook(["000000000000", "000000000000"]), /Invalid/);
  assert.throws(() => verifyCodebook(["001"]), /Invalid/);
});

test("chapter navigation and saved routes stay within the selected episode", () => {
  assert.equal(move(0, -1, 3), 0);
  assert.equal(move(2, 1, 3), 2);
  assert.deepEqual(route("#thirty-six/2", episodes), {episode: 0, scene: 2});
  assert.deepEqual(route("#unknown/999", episodes), {episode: 0, scene: 2});
  assert.deepEqual(route("#thirty-six/not-a-number", episodes), {episode: 0, scene: 0});
  assert.deepEqual(route("#thirty-six/-1", episodes), {episode: 0, scene: 0});
});

test("an independently authored text exhibit fits without changing the renderer", () => {
  const second = {
    id: "format-fixture", title: "Test fixture, not a documentary episode", date: "2026-11-19",
    author: "Test author", seconds: 12,
    exhibit: {kind: "text", title: "Exact output", body: "Fixture explanation", text: "PASS"},
    scenes: ["Attempt", "Review", "Result"].map(label => ({label, title: label,
      body: "Fixture only", credit: "Test author", caption: "Fixture", visual: "text",
      sources: [{label: "Fixture source", url: "https://example.org/evidence"}]}))
  };
  assert.equal(validate([...episodes, second]).length, episodes.length + 1);
  assert.deepEqual(route("#format-fixture/2", [...episodes, second]), {episode: episodes.length, scene: 2});
  assert.ok(episodes.every(episode => episode.id !== second.id),
    "do not ship a fixture as a real documentary episode");
});

test("missing evidence, unplayable durations and unsafe links fail validation", () => {
  const changed = () => structuredClone(episodes);
  let copy = changed(); copy[0].scenes[0].sources = [];
  assert.throws(() => validate(copy), /sources/);
  copy = changed(); copy[0].seconds = 0;
  assert.throws(() => validate(copy), /duration/);
  copy = changed(); copy[0].scenes[0].sources[0].url = "javascript:alert(1)";
  assert.throws(() => validate(copy), /HTTPS/);
  copy = changed(); copy.push(structuredClone(copy[0]));
  assert.throws(() => validate(copy), /duplicate/);
});
