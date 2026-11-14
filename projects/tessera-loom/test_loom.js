'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const loom = require('./loom.js');

const small = () => ({ version: 1, size: 2, tiles: [0, 1, 1, 0], palette: 'tidal' });

test('JSON has canonical key order and round-trips without aliasing', () => {
  const m = small();
  const reordered = { tiles: m.tiles, palette: m.palette, size: m.size, version: 1 };
  const text = loom.toJSON(m);
  assert.equal(loom.toJSON(reordered), text);
  assert.equal(text, '{\n  "version": 1,\n  "size": 2,\n  "tiles": [\n    0,\n    1,\n    1,\n    0\n  ],\n  "palette": "tidal"\n}\n');
  const copy = loom.parseJSON(text);
  assert.deepEqual(copy, m);
  copy.tiles[0] = 1;
  assert.equal(m.tiles[0], 0);
});

test('import refuses malformed, oversized and executable-looking data', () => {
  const bad = [null, [], {}, { ...small(), version: 2 }, { ...small(), size: 0 },
    { ...small(), size: 2.5 }, { ...small(), size: 9 }, { ...small(), tiles: [0, 1] },
    { ...small(), tiles: [0, 1, 1, '0'] }, { ...small(), tiles: [0, 1, 1, true] },
    { ...small(), palette: '__proto__' }, { ...small(), palette: 'constructor' },
    { ...small(), palette: '<script>alert(1)</script>' }, { ...small(), html: '<img onerror=alert(1)>' }];
  const original = loom.toJSON(small());
  for (const value of bad) assert.throws(() => loom.parseJSON(JSON.stringify(value)));
  assert.throws(() => loom.parseJSON('{'));
  assert.throws(() => loom.parseJSON(' '.repeat(32769)));
  assert.throws(() => loom.parseJSON('{"__proto__":{},"version":1,"size":2,"tiles":[0,1,1,0],"palette":"tidal"}'));
  assert.throws(() => loom.validate({ ...small(), tiles: Array(4) }));
  assert.equal(loom.toJSON(small()), original);
});

test('turn and resize preserve the original and the upper-left tile coordinates', () => {
  const m = small();
  assert.deepEqual(loom.turn(m, 1).tiles, [0, 0, 1, 0]);
  assert.deepEqual(m, small());
  const bigger = loom.resize(m, 3);
  assert.deepEqual(bigger.tiles, [0, 1, 0, 1, 0, 0, 0, 0, 0]);
  assert.deepEqual(loom.resize(bigger, 2), m);
  for (const index of [-1, 4, 1.2, NaN]) assert.throws(() => loom.turn(m, index));
  for (const size of [-1, 0, 1, 9, Infinity, '2']) assert.throws(() => loom.resize(m, size));
});

// Inspect actual SVG path endpoints and circular tangents, not a second model
// that merely declares all edges connected.
function arcGeometry(d) {
  const match = /^M(\d+) (\d+) A50 50 0 0 ([01]) (\d+) (\d+)$/.exec(d);
  assert.ok(match, `quarter-circle path: ${d}`);
  const [, ax, ay, sweep, bx, by] = match.map(Number);
  const a = [ax, ay], b = [bx, by];
  const centers = [[ax, by], [bx, ay]];
  const center = centers.find(([x, y]) => ((ax - x) * (by - y) - (ay - y) * (bx - x) > 0) === Boolean(sweep));
  assert.ok(center);
  for (const [x, y] of [a, b]) {
    assert.equal(Math.hypot(x - center[0], y - center[1]), 50);
    if (x === 0 || x === 100) assert.equal(x, center[0], 'horizontal tangent at vertical edge');
    else { assert.ok(y === 0 || y === 100); assert.equal(y, center[1], 'vertical tangent at horizontal edge'); }
  }
  return [a, b];
}

test('both orientations meet all four midpoints with perpendicular tangents', () => {
  for (const arcs of loom.ARCS) {
    const points = arcs.flatMap(arcGeometry).map((p) => p.join(',')).sort();
    assert.deepEqual(points, ['0,50', '100,50', '50,0', '50,100']);
  }
});

test('exported paths join across every tile and wrapped motif seam for all 2×2 motifs', () => {
  for (let bits = 0; bits < 16; bits++) {
    const m = { ...small(), tiles: [0, 1, 2, 3].map((i) => (bits >> i) & 1) };
    const exported = loom.svg(m, 4);
    const joins = new Map();
    const groups = [...exported.matchAll(/<g transform="translate\((\d+) (\d+)\)">(.*?)<\/g>/g)];
    assert.equal(groups.length, 64);
    for (const [, dx, dy, body] of groups) {
      for (const [, d] of body.matchAll(/<path d="([^"]+)"\/>/g)) {
        for (const [x, y] of arcGeometry(d)) {
          const key = `${(x + Number(dx)) % 800},${(y + Number(dy)) % 800}`;
          joins.set(key, (joins.get(key) || 0) + 1);
        }
      }
    }
    assert.equal(joins.size, 128);
    for (const count of joins.values()) assert.equal(count, 2);
  }
});

test('repeat dimensions, tile placement and exports are deterministic at both bounds', () => {
  for (const size of [2, 8]) for (const repeats of [4, 8]) {
    const m = loom.resize(loom.initial(), size);
    const output = loom.svg(m, repeats);
    assert.equal(output, loom.svg(loom.parseJSON(loom.toJSON(m)), repeats));
    assert.ok(output.includes(`viewBox="0 0 ${size * repeats * 100} ${size * repeats * 100}"`));
    const groups = [...output.matchAll(/<g transform="translate\((\d+) (\d+)\)">(.*?)<\/g>/g)];
    assert.equal(groups.length, (size * repeats) ** 2);
    for (const [, dx, dy, body] of groups) {
      const tile = m.tiles[(Number(dy) / 100 % size) * size + Number(dx) / 100 % size];
      for (const d of loom.ARCS[tile]) assert.ok(body.includes(`d="${d}"`));
    }
    assert.doesNotMatch(output, /<script|onload|javascript:|href=/i);
  }
  for (const repeat of [0, 1, 5, 16, '4']) assert.throws(() => loom.svg(small(), repeat));
});

test('every palette round-trips and initial motifs are independent', () => {
  for (const palette of ['tidal', 'ochre', 'fern']) {
    const m = { ...small(), palette };
    assert.deepEqual(loom.parseJSON(loom.toJSON(m)), m);
    assert.match(loom.svg(m, 4), /stroke="#[0-9a-f]{6}"/);
  }
  const m = loom.initial(); m.tiles[0] = 99;
  assert.equal(loom.initial().tiles[0], 0);
});
