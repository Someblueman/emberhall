'use strict';
const assert = require('node:assert/strict');
const {test} = require('node:test');
const first = require('./shot-one.js');
const second = require('./shot-two.js');
const film = require('./film.js');
test('twelve authored poses across two separately credited shots and an explicit cut', () => {
  assert.equal(film.poses.length,12);
  assert.equal(first.author,'Hawthorn'); assert.equal(second.author,'Sorrel');
  for(const shot of [first,second]) {
    assert.equal(shot.poses.length,6);
    shot.poses.forEach((p,i) => {
      if(i) assert.ok(p.time>shot.poses[i-1].time);
      const actual=film.poseAt(p.time);
      assert.deepEqual(actual.wing,p.wing);
      assert.equal(actual.x,p.x);
    });
  }
  const a=first.poses.at(-1),b=second.poses[0];
  for(const k of ['x','y','tilt','reach','feeler','wing']) assert.deepEqual(a[k],b[k]);
  assert.equal(film.poseAt(2.999).scene,undefined);
  assert.equal(film.poseAt(3).scene,2);
  assert.match(film.frameSVG(a,'before'),/viewBox="0 0 900 440"/);
  assert.match(film.frameSVG(b,'after'),/viewBox="510 190 410 200.444"/);
});
test('seeking clamps at both ends and invalid time returns the opening', () => {
  for(const t of [-1,NaN,Infinity]) assert.equal(film.poseAt(t).time,0);
  assert.equal(film.poseAt(200).time,6);
  assert.equal(film.poseAt(200).x,second.poses.at(-1).x);
});
test('the keeper holds the lantern while the visitor joins, and the last image holds', () => {
  assert.equal(second.poses[0].offer,0);
  assert.equal(second.poses[0].shelter,1);
  assert.equal(second.poses[0].shutter,.62);
  assert.equal(second.poses.at(-1).offer,1);
  assert.equal(second.poses.at(-1).shelter,0);
  assert.equal(second.poses.at(-1).shutter,0);
  for(const t of [5.8,5.9,6]) {
    const p=film.poseAt(t),end=second.poses.at(-1);
    for(const k of ['x','y','wing','keeper','lanternX','lanternY']) assert.deepEqual(p[k],end[k]);
  }
  assert.deepEqual(film.poseAt(2.9).wing,first.poses.at(-1).wing);
});
test('interpolation stays finite including both sides of the cut', () => {
  const visit=value=>{
    if(typeof value==='number') assert.ok(Number.isFinite(value));
    else if(value && typeof value==='object') Object.values(value).forEach(visit);
  };
  for(let i=0;i<=600;i++) {
    const p=film.poseAt(i/100); visit(p);
    assert.ok(p.shutter>=0 && p.shutter<=1);
    assert.equal(p.wing.length,12);
    if(p.keeper) assert.equal(p.keeper.wing.length,12);
  }
});
test('each frame has unique referenced resources, two distinct moths after the cut and no active content', () => {
  for(const [i,p] of film.poses.entries()) {
    const text=film.frameSVG(p,`frame-${i}`);
    const ids=[...text.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]);
    assert.equal(new Set(ids).size,ids.length);
    for(const m of text.matchAll(/url\(#([^)]+)\)/g)) assert.ok(ids.includes(m[1]));
    assert.doesNotMatch(text,/<script|<foreignObject|href=|NaN|undefined/);
    assert.match(text,/role="img"/);
    assert.equal(text.includes(`frame-${i}-keeperwing`),p.scene===2);
  }
});
