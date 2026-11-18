'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const D = require('../dance.js');
const V = require('./story.js');
const options = {ada:true, pip:true, teacher:'ada', late:false};
const phrase = kinds => kinds.map(k => D.gesture(k));
const start = changes => D.start(phrase(['bow','wave','stamp']), {...options,...changes});
function through(s, beat) { while (s.beat < beat) assert.equal(D.next(s), true); return s; }

test('every phrase passes down two distinct branches, then a witnessed gift', () => {
  const signatures = new Set();
  for (const a of D.kinds) for (const b of D.kinds) for (const c of D.kinds) {
    for (const teacher of ['ada','pip']) {
      const input = phrase([a,b,c]);
      const s = through(D.start(input,{...options,teacher}),72);
      const left = D.learn(D.learn(D.learn(input,teacher,[0,1,2]),'rue',[0,1,2]),'lio',[0,1,2]);
      const right = D.learn(D.learn(input,'pip',[0,1,2]),'bea',[0,1,2]);
      assert.deepEqual(s.memories.lio,left); assert.deepEqual(s.memories.bea,right);
      assert.notDeepEqual(left,right);
      assert.deepEqual(s.memories.moth,[]); assert.deepEqual(s.memories.ada,[]); assert.deepEqual(s.memories.pip,[]);
      through(s,87);
      assert.deepEqual(s.memories.lio,[...left,...D.learn(right,'lio',[2])]);
      assert.deepEqual(s.memories.bea,right);
      signatures.add(JSON.stringify(s.memories.lio));
      assert.equal(D.next(s),false);
    }
  }
  assert.equal(signatures.size,128);
});

test('the two default traditions have explicit different body shapes', () => {
  const s = through(start(),72);
  assert.equal(s.memories.lio[0].tilt,29);
  assert.equal(s.memories.bea[0].tilt,17);
  assert.ok(Math.abs(s.memories.lio[0].foot-4.305)<1e-12);
  assert.ok(Math.abs(s.memories.bea[0].foot-15.34)<1e-12);
});

test('unwatched and late lessons leave actual holes in the reunion', () => {
  const north = through(start({lio:false,exchange:false}),87);
  assert.deepEqual(north.memories.lio,[]); assert.equal(north.memories.bea.length,3);
  const south = through(start({bea:false}),87);
  assert.deepEqual(south.memories.bea,[]); assert.equal(south.memories.lio.length,3);
  const lost = through(start({ada:false,pip:false}),87);
  assert.deepEqual(lost.memories.lio,[]); assert.deepEqual(lost.memories.bea,[]);
  const late = through(start({lioLate:true,exchange:false}),72);
  assert.deepEqual(late.memories.lio.map(g=>g.kind),['wave','stamp']);
  assert.match(D.caption(late),/sleeve-wave.*crooked bow/);
  through(late,74); assert.match(D.caption(late),/Lio keeps a space/);
  const absentFirstTeacher = through(start({ada:false}),72);
  assert.deepEqual(absentFirstTeacher.memories.lio,[]); assert.equal(absentFirstTeacher.memories.bea.length,3);
});

test('each lesson and the reunion gift read the actual current teacher', () => {
  const s = through(start(),42);
  s.memories.rue = [D.gesture('turn',true)];
  through(s,50); s.memories.pip = [D.gesture('wave')];
  through(s,72);
  assert.deepEqual(s.memories.lio,D.learn([D.gesture('turn',true)],'lio',[0]));
  assert.deepEqual(s.memories.bea,D.learn([D.gesture('wave')],'bea',[0]));
  const oldBea = structuredClone(s.memories.bea);
  through(s,77);
  assert.deepEqual(s.gift,D.learn(oldBea,'lio',[0]));
  s.memories.lio[1].kind='stamp'; assert.equal(s.memories.bea[0].kind,'wave');
});

test('watching choices close at their own handoff, never rewrite the past', () => {
  const s = through(start(),40);
  assert.equal(D.audience(s,'lioLate',true),true);
  assert.equal(D.replay(s,40).audience.lioLate,true);
  through(s,43); assert.equal(s.memories.lio.length,2);
  assert.equal(D.audience(s,'lio',false),false);
  assert.equal(D.audience(s,'bea',false),true);
  through(s,51); assert.deepEqual(s.memories.bea,[]);
  assert.equal(D.audience(s,'bea',true),false);
  assert.equal(D.audience(s,'exchange',false),true);
  through(s,77); assert.deepEqual(s.gift,[]);
  assert.equal(D.audience(s,'exchange',true),false);
});

test('spectator replay owns detached past frames and cannot restore any teacher', () => {
  const s = through(start({lio:false,exchange:false}),56);
  const before = structuredClone(s);
  const opening = D.replay(s,0);
  assert.equal(opening.memories.moth.length,3);
  opening.memories.moth[0].kind='turn'; opening.memories.lio=opening.memories.moth;
  assert.throws(()=>D.next(opening),/living dance/);
  assert.equal(D.audience(opening,'exchange',true),false);
  assert.deepEqual(s,before);
  assert.equal(D.replay(s,0).memories.moth[0].kind,'bow');
  assert.throws(()=>D.replay(s,57),/not happened/);
  assert.throws(()=>D.replay(s,-1),/not happened/);
  through(s,87); assert.deepEqual(s.memories.moth,[]); assert.deepEqual(s.memories.lio,[]);
  const firstPip = s.handoffs.find(h=>h.to==='pip');
  assert.deepEqual(firstPip.movements,['bow','wave','stamp']);
});

test('the whole arc has live performers, reachable chapters and an explicit duration', () => {
  assert.equal(D.beats.length,88); assert.equal(V.beats.length,64);
  const s = start();
  for (let beat=0;beat<88;beat++) {
    through(s,beat);
    assert.equal(typeof D.caption(s),'string'); assert.ok(D.caption(s).length);
    for (const act of D.performances(s)) assert.ok(Object.hasOwn(s.memories,act.who));
  }
  assert.deepEqual(D.performances(D.replay(s,72)),[{who:'lio',slot:0},{who:'bea',slot:0}]);
  assert.deepEqual(V.chapters.map(([beat])=>beat),[24,32,40,48,56,64,72,80]);
  assert.equal(D.beats.slice(0,-1).reduce((n,b)=>n+b.seconds,0),696);
});


test('only named pupils may learn; inherited keys cannot become pupils', () => {
  const source = [D.gesture('bow')];
  for (const pupil of ['constructor','toString','__proto__','not-a-pupil',null,undefined,{toString:()=> 'ada'}]) {
    assert.throws(()=>D.learn(source,pupil,[0]),/Unknown pupil/);
  }
});
