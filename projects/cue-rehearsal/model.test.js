'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const m = require('./model.js');
const copy = p => JSON.parse(JSON.stringify(p));
const times = result => Object.fromEntries(result.entries.map(e => [e.id, [e.start, e.end]]));
const entry = (result, id) => result.entries.find(e => e.id === id);

test('hand-calculated branching workshop: two independent tracks and a join', () => {
  const p = m.initial(), before = m.toJSON(p);
  const result = m.calculate(p.baseline);
  assert.deepEqual(times(result), { unlock: [0, 5], tables: [5, 15], projector: [5, 13],
    'room-ready': [15, 19], print: [0, 6], pack: [6, 13], welcome: [19, 22] });
  assert.equal(result.finish, 22);
  assert.deepEqual(result.cycles, []); assert.deepEqual(result.conflicts, []);
  assert.equal(entry(result, 'room-ready').explanation,
    'Start 15 = max(release 0, projector ends 13, tables ends 15); finish 19 = 15 + 4.');
  assert.equal(m.toJSON(p), before, 'calculation is pure');
});

test('duration delay propagates only through downstream prerequisites', () => {
  const p = m.initial(), original = m.toJSON(p);
  const changed = m.editStep(p, 'tables', { duration: 14 });
  const comparison = m.compare(changed), b = times(comparison.baseline), s = times(comparison.scenario);
  assert.deepEqual(s.tables, [5, 19]); assert.deepEqual(s['room-ready'], [19, 23]);
  assert.deepEqual(s.welcome, [23, 26]);
  for (const id of ['unlock', 'projector', 'print', 'pack']) assert.deepEqual(s[id], b[id]);
  assert.equal(comparison.changes.find(e => e.id === 'welcome').message, 'Start +4 min; finish +4 min.');
  assert.equal(m.toJSON(p), original); assert.deepEqual(changed.baseline, p.baseline);
});

test('slack absorbs a short branch delay, a release can become the controlling term', () => {
  let p = m.editStep(m.initial(), 'projector', { duration: 9 });
  assert.deepEqual(times(m.calculate(p.scenario))['room-ready'], [15, 19]);
  p = m.editStep(p, 'room-ready', { release: 30 });
  const r = m.calculate(p.scenario);
  assert.deepEqual(times(r)['room-ready'], [30, 34]); assert.deepEqual(times(r).welcome, [34, 37]);
  assert.match(entry(r, 'room-ready').explanation, /max\(release 30, projector ends 14, tables ends 15\)/);
  p = m.editStep(p, 'print', { release: -10 });
  assert.deepEqual(times(m.calculate(p.scenario)).print, [-10, -4]);
});

test('cycles are isolated from downstream blocks, including self-cycles', () => {
  let p = m.editStep(m.initial(), 'unlock', { prerequisites: ['tables'] });
  let r = m.calculate(p.scenario);
  assert.deepEqual(r.cycles, [['tables', 'unlock']]); assert.equal(r.finish, null);
  for (const id of ['unlock', 'tables', 'projector', 'room-ready', 'welcome']) assert.equal(entry(r, id).start, null);
  assert.deepEqual(times(r).pack, [6, 13]);
  assert.match(entry(r, 'welcome').explanation, /Blocked prerequisite: room-ready/);
  p = m.editStep(m.initial(), 'print', { prerequisites: ['print'] });
  r = m.calculate(p.scenario); assert.deepEqual(r.cycles, [['print']]);
  assert.equal(entry(r, 'pack').start, null); assert.deepEqual(times(r).tables, [5, 15]);
});

test('missing prerequisites, unknown and unavailable resources block rather than schedule', () => {
  let p = m.editStep(m.initial(), 'tables', { prerequisites: ['absent'] });
  let r = m.calculate(p.scenario);
  assert.match(entry(r, 'tables').explanation, /Missing prerequisite: absent/);
  assert.equal(entry(r, 'welcome').start, null); assert.deepEqual(times(r).projector, [5, 13]);
  p = m.editStep(m.initial(), 'print', { resource: 'absent' });
  assert.match(entry(m.calculate(p.scenario), 'print').explanation, /Unknown resource: absent/);
  p = m.setResource(m.initial(), 'printer', false);
  r = m.calculate(p.scenario);
  assert.match(entry(r, 'print').explanation, /Unavailable resource: printer/);
  assert.equal(entry(r, 'pack').start, null); assert.equal(entry(r, 'welcome').start, null);
  assert.deepEqual(times(r)['room-ready'], [15, 19]);
  assert.equal(p.baseline.resources.find(r => r.id === 'printer').available, true);
});

test('resource intervals are half-open: touching, containment, identical and partial overlaps', () => {
  const plan = { name: 'Boundary', resources: [{ id: 'r', name: 'Resource', available: true }], steps: [] };
  const s = (id, release, duration) => ({ id, label: id, track: id, release, duration, prerequisites: [], resource: 'r' });
  for (const [b, expected] of [[s('b', 10, 3), []], [s('b', 9, 3), [{ resource: 'r', steps: ['a', 'b'], start: 9, end: 10 }]],
    [s('b', 2, 3), [{ resource: 'r', steps: ['a', 'b'], start: 2, end: 5 }]],
    [s('b', 0, 10), [{ resource: 'r', steps: ['a', 'b'], start: 0, end: 10 }]]]) {
    plan.steps = [s('a', 0, 10), b];
    const r = m.calculate(plan); assert.deepEqual(r.conflicts, expected);
    assert.deepEqual(times(r).b, [b.release, b.release + b.duration], 'conflict does not move any interval');
  }
  plan.resources[0].available = false;
  assert.deepEqual(m.calculate(plan).conflicts, [], 'blocked steps have no intervals');
});

test('deterministic under step, resource and prerequisite ordering', () => {
  const p = m.initial(), original = m.calculate(p.baseline);
  p.baseline.steps.reverse(); p.baseline.resources.reverse();
  for (const step of p.baseline.steps) step.prerequisites.reverse();
  assert.deepEqual(m.calculate(p.baseline), original);
  p.baseline.steps[0].resource = 'crew';
  const first = m.calculate(p.baseline);
  p.baseline.steps.reverse(); assert.deepEqual(m.calculate(p.baseline), first);
});

test('complete JSON round trip, independent clones and reset preservation', () => {
  const p = m.editStep(m.initial(), 'pack', { duration: 11 });
  const json = m.toJSON(p), imported = m.parseJSON(json);
  assert.equal(m.toJSON(imported), json); assert.deepEqual(m.compare(imported), m.compare(p));
  imported.scenario.steps[0].label = 'Changed'; assert.notEqual(imported.baseline.steps[0].label, 'Changed');
  assert.notEqual(p.scenario.steps[0].label, 'Changed');
  const reset = m.resetScenario(p); assert.deepEqual(reset.baseline, p.baseline);
  assert.deepEqual(reset.scenario.steps, reset.baseline.steps); assert.equal(m.toJSON(p), json);
  assert.deepEqual(m.parseJSON(fs.readFileSync(path.join(__dirname, 'example.json'), 'utf8')), m.initial());
});

test('malformed imports reject atomically; invalid structures and ambiguous values', () => {
  let current = m.editStep(m.initial(), 'tables', { duration: 12 });
  const before = m.toJSON(current);
  const invalid = ['{', 'null', '[]', ' '.repeat(200001)];
  const mutations = [p => { p.version = 2; }, p => { p.extra = 1; }, p => { delete p.origin; },
    p => { p.scenario.steps[0].duration = 0; }, p => { p.baseline.steps[0].duration = 1.5; },
    p => { p.scenario.steps[0].release = '0'; }, p => { p.scenario.steps[0].release = true; },
    p => { p.scenario.steps[0].release = 1000001; }, p => { p.scenario.steps[0].prerequisites = ['a', 'a']; },
    p => { p.scenario.steps[0].resource = ''; }, p => { p.scenario.resources[0].available = 1; },
    p => { p.scenario.resources.push(p.scenario.resources[0]); }, p => { p.scenario.steps.push(p.scenario.steps[0]); },
    p => { p.scenario.steps = []; }, p => { p.title = '\u0000'; }, p => { p.scenario.steps[0].id = '<script>'; }];
  for (const mutate of mutations) { const p = m.initial(); mutate(p); invalid.push(JSON.stringify(p)); }
  invalid.push(before.replace('"duration": 5', '"duration": 1e999'));
  invalid.push(before.replace('"version": 1', '"__proto__": {}, "version": 1'));
  for (const source of invalid) {
    assert.throws(() => { current = m.parseJSON(source); });
    assert.equal(m.toJSON(current), before);
  }
  for (const value of [NaN, Infinity, undefined, false]) {
    const p = m.initial(); p.scenario.steps[0].duration = value; assert.throws(() => m.toJSON(p));
  }
  const sparse = m.initial(); sparse.scenario.steps = Array(2); assert.throws(() => m.validate(sparse));
  assert.throws(() => m.editStep(current, 'unlock', { id: 'changed' }));
  assert.throws(() => m.setResource(current, 'unknown', true));
  assert.equal(m.toJSON(current), before);
});

test('maximum admitted graph stays finite and compares added/removed steps', () => {
  const p = m.initial(); p.scenario.steps = Array.from({ length: 80 }, (_, i) => ({
    id: `s${i}`, label: `Step ${i}`, track: 'Track', release: 1000000, duration: 1000000,
    prerequisites: i ? [`s${i - 1}`] : [], resource: 'crew'
  }));
  assert.equal(m.calculate(p.scenario).finish, 81000000);
  const changes = m.compare(p).changes;
  assert.equal(changes.find(e => e.id === 'unlock').message, 'Absent from scenario.');
  assert.equal(changes.find(e => e.id === 's0').message, 'Added in scenario.');
  p.scenario.steps.push(copy(p.scenario.steps[0])); assert.throws(() => m.validate(p));
});

test('compact imports cannot accept a project too large to export', () => {
  const p = m.initial();
  const prerequisites = Array.from({ length: 50 }, (_, i) => `p${i}`.padEnd(40, 'x'));
  p.scenario.steps = Array.from({ length: 70 }, (_, i) => ({
    id: `s${i}`, label: 'Step', track: 'Track', release: 0, duration: 1,
    prerequisites, resource: 'crew'
  }));
  const compact = JSON.stringify(p);
  assert.ok(compact.length < 200000); assert.ok(JSON.stringify(p, null, 2).length > 200000);
  assert.throws(() => m.parseJSON(compact), /Formatted JSON exceeds/);
});

test('timelineData derives track rows, deltas, negative releases, conflicts and all-blocked span', () => {
  const initial = m.initial();
  const baseTl = m.timelineData(initial);
  assert.equal(baseTl.minTime, 0);
  assert.equal(baseTl.maxTime, 22);
  assert.equal(baseTl.baselineFinish, 22);
  assert.equal(baseTl.scenarioFinish, 22);
  assert.equal(baseTl.deltaFinish, 0);
  assert.deepEqual(baseTl.rows.map(r => r.id), [
    'print', 'pack', 'unlock', 'projector', 'tables', 'room-ready', 'welcome'
  ]);

  const delayed = m.editStep(initial, 'tables', { duration: 14 });
  const delayedTl = m.timelineData(delayed);
  assert.equal(delayedTl.minTime, 0);
  assert.equal(delayedTl.maxTime, 26);
  assert.equal(delayedTl.baselineFinish, 22);
  assert.equal(delayedTl.scenarioFinish, 26);
  assert.equal(delayedTl.deltaFinish, 4);
  const byId = Object.fromEntries(delayedTl.rows.map(r => [r.id, r]));
  assert.equal(byId.tables.scenario.deltaStart, 0);
  assert.equal(byId.tables.scenario.deltaEnd, 4);
  assert.equal(byId['room-ready'].scenario.deltaStart, 4);
  assert.equal(byId.welcome.scenario.deltaEnd, 4);
  assert.equal(byId.print.scenario.deltaEnd, 0);

  const negative = m.editStep(initial, 'print', { release: -10 });
  assert.equal(m.timelineData(negative).minTime, -10);

  const conflict = m.editStep(initial, 'projector', { resource: 'crew' });
  const conflictTl = m.timelineData(conflict);
  assert.equal(conflictTl.scenarioConflicts.length, 1);
  const cById = Object.fromEntries(conflictTl.rows.map(r => [r.id, r]));
  assert.equal(cById.projector.scenario.conflicting, true);
  assert.equal(cById.tables.scenario.conflicting, true);
  assert.equal(cById.unlock.scenario.conflicting, false);

  let blocked = copy(initial);
  for (const plan of [blocked.baseline, blocked.scenario]) {
    for (const r of plan.resources) r.available = false;
  }
  const blockedTl = m.timelineData(blocked);
  assert.equal(blockedTl.minTime, 0);
  assert.equal(blockedTl.maxTime, 1);
  assert.equal(blockedTl.baselineFinish, null);
  assert.equal(blockedTl.scenarioFinish, null);
  assert.equal(blockedTl.deltaFinish, null);
});

test('previewSvg produces deterministic, XML-safe standalone SVG matching timeline state', () => {
  const delayed = m.editStep(m.initial(), 'tables', { duration: 14 });
  const svgA = m.previewSvg(delayed);
  const reversed = copy(delayed);
  reversed.scenario.steps.reverse();
  reversed.baseline.steps.reverse();
  const svgB = m.previewSvg(reversed);
  assert.equal(svgA, svgB);
  assert.ok(svgA.startsWith('<svg '));
  assert.ok(svgA.endsWith('</svg>\n'));
  assert.match(svgA, /xmlns="http:\/\/www\.w3\.org\/2000\/svg"/);
  assert.match(svgA, /The print-and-make workshop/);
  assert.match(svgA, /Arrange tables/);
  assert.match(svgA, /22 min/);
  assert.match(svgA, /26 min/);
  assert.doesNotMatch(svgA, /NaN|Infinity|undefined/);

  const xss = m.initial();
  xss.title = 'Stage <A & "B">';
  xss.scenario.steps[0].label = 'Cue <1> & "2"';
  const xssSvg = m.previewSvg(xss);
  assert.doesNotMatch(xssSvg, /<A|<1>/);
  assert.match(xssSvg, /Stage &lt;A &amp; &quot;B&quot;&gt;/);
  assert.match(xssSvg, /Cue &lt;1&gt; &amp; &quot;2&quot;/);
});
