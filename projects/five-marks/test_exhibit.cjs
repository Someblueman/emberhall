'use strict';
// Independent arithmetic oracle uses occupied integers rather than the UI's difference table.
const assert = require('node:assert/strict');
const { shape, parameter, collision, attempt, lower, initialExclusions, transitions } = require('./exhibit.js');
for (const invalid of ['', ' ', 'no', 0, 2, 4, -1, 1.5, 13, Infinity]) assert.throws(() => parameter(invalid), RangeError);
for (let b = 1; b <= 11; b += 2) {
  assert.equal(parameter(String(b)), b);
  const s = [0, b + 2, 2 * b + 4, 3 * b + 4, 4 * b + 4], n = 5 * b + 4;
  assert.deepEqual(shape(b), s);
  for (let x = 0; x < n; x++) for (let y = 0; y < n; y++) {
    const common = s.map(v => v + x).filter(v => s.includes(v - y));
    const result = collision(b, x, y);
    assert.equal(Boolean(result), x !== y && common.length > 0);
    if (result) { assert.ok(common.includes(result.shared)); assert.equal(result.distance, Math.abs(x - y)); }
  }
  const starts = lower(b), occupied = new Set();
  // Five successive periods: all marks, including those beyond the last start period.
  for (let p = -2; p <= 2; p++) for (const r of starts) for (const v of s) {
    const mark = p * n + r + v; assert.ok(!occupied.has(mark), `seam collision b=${b} at ${mark}`); occupied.add(mark);
  }
  let selected = [0];
  for (const x of starts.slice(1)) { const result = attempt(b, selected, x); assert.equal(result.kind, 'added'); selected = result.selected; }
  assert.equal(selected.length, b);
  const bad = s[1], failed = attempt(b, selected, bad);
  assert.equal(failed.kind, 'clash'); assert.deepEqual(failed.selected, selected);
  assert.equal(attempt(b, selected, 0).kind, 'anchor');
  assert.throws(() => attempt(b, selected, n), RangeError);
  if (b > 1) {
    const removed = attempt(b, selected, 2); assert.equal(removed.kind, 'removed'); assert.ok(!removed.selected.includes(2));
    const columns = Array.from({ length: b }, (_, c) => s.map(v => c + v));
    const points = columns.flat(); assert.equal(new Set(points).size, 5 * b);
    assert.deepEqual(Array.from({ length: n }, (_, x) => x).filter(x => !points.includes(x)), [b, b + 1, 2 * b + 2, 2 * b + 3]);
    for (const t of [b + 1, 2 * b + 3]) for (const entry of initialExclusions(b, t)) {
      assert.equal(entry.position, columns[1][entry.row]); assert.ok(collision(b, t, entry.position));
      assert.equal(entry.distance, Math.abs(t - entry.position));
    }
    for (const entry of transitions(b)) {
      const x = 1 + s[entry.from], y = 3 + s[entry.to];
      assert.ok(collision(b, x, y)); assert.equal(entry.distance, Math.abs(x - y));
    }
    assert.ok(collision(b, 0, b - 2 + s[1])); assert.ok(collision(b, 0, b - 2 + s[2]));
    assert.ok(starts.includes(b + 1));
    assert.ok(columns[b - 2].every(x => !starts.includes(x)));
  } else {
    for (let x = 1; x < n; x++) assert.equal(attempt(b, [0], x).kind, 'clash');
  }
}
console.log('PASS: parameters, collision witnesses, refusal/removal, columns, exclusions, endpoint and five-period wraparound for every displayed odd b.');
