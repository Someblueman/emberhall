'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const D = require('./dance.js');
const choices = {ada: true, pip: true, teacher: 'ada', late: false};
const phrase = kinds => kinds.map(k => D.gesture(k));
function through(s, beat) { while (s.beat < beat) assert.equal(D.next(s), true); return s; }

test('two real handoffs inherit the performed variant, with no surviving master', () => {
  const initial = phrase(['bow', 'wave', 'stamp']);
  const s = through(D.start(initial, choices), 4);
  assert.deepEqual(s.memories.ada.map(g => g.kind), ['bow', 'wave', 'stamp']);
  assert.notDeepEqual(s.memories.ada, s.memories.pip);
  initial[0].kind = 'turn';
  const ada = structuredClone(s.memories.ada);
  through(s, 12);
  assert.deepEqual(s.memories.moth, []);
  through(s, 23);
  assert.deepEqual(s.memories.rue, D.learn(ada, 'rue', [0, 1, 2]));
  assert.equal(s.memories.rue[0].tilt, 22);
  assert.equal(s.memories.rue[0].foot, 5.25);
  assert.ok(Math.abs(s.memories.rue[0].reach - .5576) < 1e-12);
  const pipRoute = through(D.start(phrase(['bow','wave','stamp']), {...choices,teacher:'pip'}),23);
  assert.equal(pipRoute.memories.rue[0].tilt, 11);
  assert.equal(pipRoute.memories.rue[0].foot, 9.75);
  assert.ok(Math.abs(pipRoute.memories.rue[0].reach - .85034) < 1e-12);
  assert.deepEqual(s.handoffs.map(h => [h.from, h.to]), [['moth', 'ada'], ['moth', 'pip'], ['ada', 'rue']]);
  assert.equal(D.next(s), false);
});

test('every offered phrase and both teachers produce their own inherited dance', () => {
  const signatures = new Set();
  for (const a of D.kinds) for (const b of D.kinds) for (const c of D.kinds) {
    for (const teacher of ['ada', 'pip']) for (const big of [false, true]) {
      const input = [a,b,c].map(k => D.gesture(k,big));
      const s = through(D.start(input, {...choices, teacher}), 23);
      assert.deepEqual(s.memories.rue.map(g => g.kind), [a,b,c]);
      assert.deepEqual(s.memories.rue, D.learn(D.learn(input,teacher,[0,1,2]),'rue',[0,1,2]));
      signatures.add(JSON.stringify(s.memories.rue));
    }
  }
  assert.equal(signatures.size, 256);
});

test('an unwatched class and a late arrival lose movements rather than restore them', () => {
  for (const teacher of ['ada', 'pip']) {
    const s = through(D.start(phrase(['bow','wave','turn']), {...choices, [teacher]:false, teacher}), 23);
    assert.deepEqual(s.memories[teacher], []);
    assert.deepEqual(s.memories.rue, []);
    assert.match(D.caption(s), /Perhaps tomorrow/);
  }
  const late = through(D.start(phrase(['bow','wave','turn']), {...choices, late:true}), 23);
  assert.deepEqual(late.memories.rue.map(g => g.kind), ['wave','turn']);
  assert.equal(late.memories.rue.some(g => g.kind === 'bow'), false);
  const s = through(D.start(phrase(['bow','wave','turn']), choices), 16);
  s.memories.ada = [D.gesture('stamp')];
  through(s,23);
  assert.deepEqual(s.memories.rue.map(g=>g.kind), ['stamp']);
});

test('performed slots, empty pauses and total authored duration are explicit', () => {
  const s = D.start(phrase(['bow','wave','stamp']), choices);
  through(s,1); assert.deepEqual(D.performance(s),{who:'moth',slot:0});
  through(s,7); assert.deepEqual(D.performance(s),{who:'ada',slot:2});
  through(s,12); assert.equal(D.performance(s),null);
  through(s,16); assert.deepEqual(D.performance(s),{who:'ada',slot:2});
  through(s,20); assert.deepEqual(D.performance(s),{who:'rue',slot:2});
  // The final tableau holds until the visitor starts another class.
  assert.equal(D.beats.slice(0,-1).reduce((n,b)=>n+b.seconds,0),184);
  assert.throws(()=>D.gesture('invented'));
  assert.throws(()=>D.start([],choices));
});
