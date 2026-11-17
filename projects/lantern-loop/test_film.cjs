'use strict';
const assert = require('node:assert/strict');
const {test} = require('node:test');
const shot = require('./shot-one.js');
const film = require('./film.js');
test('six ordered authored poses bound the unfinished three-second shot', () => {
  assert.equal(shot.poses.length, 6);
  assert.equal(shot.poses[0].time, 0);
  assert.equal(shot.poses.at(-1).time, shot.duration);
  shot.poses.forEach((p,i) => {
    if (i) assert.ok(p.time>shot.poses[i-1].time);
    assert.deepEqual(film.poseAt(p.time).wing,p.wing);
    assert.equal(film.poseAt(p.time).x,p.x);
  });
});
test('seeking clamps at both ends and invalid time returns the opening', () => {
  for(const t of [-1,NaN,Infinity]) assert.equal(film.poseAt(t).time,0);
  assert.equal(film.poseAt(200).time,3);
  assert.equal(film.poseAt(200).x,shot.poses.at(-1).x);
});
test('intermediate drawings stay finite and the final landing holds', () => {
  for(let i=0;i<=300;i++) {
    const p=film.poseAt(i/100);
    for(const v of Object.values(p).filter(v=>typeof v==='number')) assert.ok(Number.isFinite(v));
    assert.ok(p.shutter>=0 && p.shutter<=1);
    assert.equal(p.wing.length,12);
  }
  assert.deepEqual(film.poseAt(2.9).wing,film.poseAt(3).wing);
  assert.equal(film.poseAt(2.9).x,film.poseAt(3).x);
});
test('each frame has unique referenced drawing resources, no network or active SVG content', () => {
  for(let i=0;i<shot.poses.length;i++) {
    const text=film.frameSVG(shot.poses[i],`frame-${i}`);
    const ids=[...text.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]);
    assert.equal(new Set(ids).size,ids.length);
    for(const m of text.matchAll(/url\(#([^)]+)\)/g)) assert.ok(ids.includes(m[1]));
    assert.doesNotMatch(text,/<script|<foreignObject|href=|NaN|undefined/);
    assert.match(text,/role="img"/);
  }
});
