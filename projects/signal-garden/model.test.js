"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const { encode, decode, mapping, run, outcome, trace } = require("./model.js");
const nibble = n => [3, 2, 1, 0].map(shift => (n >> shift) & 1);
const picture = [0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0];

test("known even-parity words pin the codec convention", () => {
  assert.deepEqual(encode([1, 0, 1, 1]), [0, 1, 1, 0, 0, 1, 1]);
  assert.deepEqual(encode([0, 0, 0, 0]), [0, 0, 0, 0, 0, 0, 0]);
  assert.deepEqual(encode([1, 1, 1, 1]), [1, 1, 1, 1, 1, 1, 1]);
});

test("all 16 payloads survive clean and every single-bit corruption", () => {
  for (let n = 0; n < 16; n++) {
    const data = nibble(n);
    const encoded = encode(data);
    assert.deepEqual(decode(encoded).data, data);
    assert.equal(decode(encoded).syndrome, 0);
    for (let i = 0; i < 7; i++) {
      const damaged = encoded.slice(); damaged[i] ^= 1;
      const result = decode(damaged);
      assert.equal(result.syndrome, i + 1);
      assert.deepEqual(result.corrected, encoded);
      assert.deepEqual(result.data, data);
      assert.deepEqual(encoded, encode(data), "decoder must not mutate input");
    }
  }
});

test("both layouts are exact permutations, with the intended row/column order", () => {
  for (const layout of ["consecutive", "interleaved"]) {
    const order = mapping(layout);
    assert.equal(new Set(order.map(({ row, column }) => `${row}:${column}`)).size, 28);
    assert.deepEqual(run(picture, 0, 0, layout).recovered, picture);
  }
  assert.deepEqual(mapping("interleaved").slice(0, 5), [
    { row: 0, column: 0 }, { row: 1, column: 0 }, { row: 2, column: 0 },
    { row: 3, column: 0 }, { row: 0, column: 1 }
  ]);
  assert.deepEqual(mapping("consecutive")[7], { row: 1, column: 0 });
});

test("all 106 non-wrapping bursts of length 1..4 spread to at most one error per block", () => {
  let cases = 0;
  for (let length = 1; length <= 4; length++) {
    for (let start = 0; start + length <= 28; start++) {
      // Repeated nibbles exercise all input values in every block, for every burst.
      for (let n = 0; n < 16; n++) {
        const input = Array.from({ length: 4 }, () => nibble(n)).flat();
        const a = run(input, start, length, "consecutive");
        const b = run(input, start, length, "interleaved");
        for (const result of [a, b]) {
          assert.equal(result.sent.length, 28);
          assert.deepEqual(result.rows.flat(), input);
          assert.equal(result.sent.reduce((count, bit, i) => count + (bit !== result.received[i]), 0), length);
          assert.equal(result.errors.reduce((sum, n) => sum + n, 0), length);
        }
        assert.ok(b.errors.every(count => count <= 1));
        assert.deepEqual(b.recovered, input);
      }
      cases++;
    }
  }
  assert.equal(cases, 106);
});

test("consecutive counterexample and over-limit interleaver failure remain visible", () => {
  const a = run(picture, 0, 4, "consecutive");
  const b = run(picture, 0, 4, "interleaved");
  assert.deepEqual(a.errors, [4, 0, 0, 0]);
  assert.deepEqual(b.errors, [1, 1, 1, 1]);
  assert.equal(outcome(a, b), "interleaved");
  const over = run(picture, 0, 5, "interleaved");
  assert.deepEqual(over.errors, [2, 1, 1, 1]);
  assert.equal(over.matches, false);
  // Two parity-bit flips imply a false correction of the third (data) bit.
  const damaged = encode([0, 0, 0, 0]); damaged[0] ^= 1; damaged[1] ^= 1;
  assert.equal(decode(damaged).syndrome, 3);
  assert.deepEqual(decode(damaged).data, [1, 0, 0, 0]);
  // Three errors can even have zero syndrome: this decoder cannot certify success.
  assert.equal(decode([1, 1, 1, 0, 0, 0, 0]).syndrome, 0);
  assert.deepEqual(decode([1, 1, 1, 0, 0, 0, 0]).data, [1, 0, 0, 0]);
});

test("reject malformed bits, unknown layouts and wrapping/nonfinite bursts", () => {
  for (const value of [[], Array(4), [0, 1, 2, 0], [false, 0, 0, 0], "0110"]) {
    assert.throws(() => encode(value), TypeError);
  }
  assert.throws(() => decode([0, 0, 0]), TypeError);
  assert.throws(() => run([], 0, 1, "interleaved"), TypeError);
  assert.throws(() => mapping("random"), TypeError);
  for (const [start, length] of [[-1, 1], [28, 0], [27, 2], [0, -1], [0.5, 1], [NaN, 1], [0, Infinity]]) {
    assert.throws(() => run(picture, start, length, "interleaved"), RangeError);
  }
});

test("trace is deterministic and names simulator-only knowledge and decoding limits", () => {
  const result = run(picture, 24, 4, "interleaved");
  const text = trace(result);
  assert.equal(text, trace(run(picture, 24, 4, "interleaved")));
  assert.match(text, /positions \(1-based\): 25\.\.28/);
  assert.match(text, /0 changed pixel/);
  assert.match(text, /decoder sees only received bits/);
  assert.match(text, /silently decode to the wrong data/);
});
