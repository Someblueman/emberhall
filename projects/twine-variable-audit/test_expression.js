'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {audit} = require('./audit.js');
const E = require('./expression.js');
const escape = text => text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const story = text => '<tw-storydata startnode="1" format="SugarCube" format-version="2.37.3"><tw-passagedata pid="1" name="Start">' + escape(text) + '</tw-passagedata></tw-storydata>';
const fixture = name => fs.readFileSync(path.join(__dirname,'fixtures',name + '.html'),'utf8');

test('mixed def and ndef guards follow the format expansion instead of atom precedence',() => {
  // SugarCube 2.37.3 expands def/ndef to a string comparison followed by typeof.
  for (const [condition,expected] of [
    ['def $x gt 0',true], ['ndef $x gt 0',false],
    ['def $x + 1',true], ['ndef $x + 1',false],
    ['not def $x',true], ['not ndef $x',false],
    ['def $x is true',false], ['ndef $x is true',true],
    ['(def $x) gt 0',false], ['(ndef $x) gt 0',true]
  ]) {
    const html = story('<<if ' + condition + '>><<set $ready to ' + expected + '>><<else>><<set $ready to ' + !expected + '>><</if>><<if not $ready>>$invented<</if>>');
    const r = audit(html);
    assert.equal(r.complete,true,condition + ': ' + JSON.stringify(r.unchecked));
    assert.deepEqual(r.findings,[],condition);
    assert.equal(E.evaluate(E.parse(condition),Object.create(null),()=>{}),expected,condition);
  }
  const exact = audit(story('<<if def $x gt 0>><<set $ready to true>><</if>>$ready'));
  assert.equal(exact.complete,true); assert.deepEqual(exact.findings,[]);
});

test('guard grouping and logical short circuit preserve actual reads',() => {
  for (const condition of ['(def $x) and $x gt 0','def $x and $x gt 0','false and $x','true or $x','(ndef $x) or $x gt 0']) {
    const r = audit(story('<<if ' + condition + '>>ok<</if>>'));
    assert.equal(r.complete,true,condition); assert.deepEqual(r.findings,[],condition);
  }
  const reads = audit(story('<<if def $x gt $threshold>>ok<</if>>'));
  assert.equal(reads.complete,true);
  assert.deepEqual(reads.findings.map(f => f.name),['$threshold']);
  const defined = audit(story('<<set $x to 2>><<if (def $x) and $x gt 0>><<set $ready to true>><</if>>$ready'));
  assert.equal(defined.complete,true); assert.deepEqual(defined.findings,[]);
});

test('adjacent update signs stop conditions and assignments before any invented route',() => {
  for (const expression of ['--$x','++$x','$x--','$x++','$x-- - 1','$x++ + 1','$x---1','$x+++1','1--$x','1++$x']) {
    assert.throws(() => E.parse(expression),/increment|decrement/,expression);
    for (const text of [
      '<<set $x to 1>><<if ' + expression + '>>$missing<</if>>$downstream',
      '<<set $x to 1>><<set $value to ' + expression + '>>$downstream',
      '<<print ' + expression + '>>$downstream'
    ]) {
      const r = audit(story(text));
      assert.equal(r.complete,false,expression); assert.ok(r.unchecked.length,expression);
      assert.deepEqual(r.findings,[],expression);
    }
  }
});

test('whitespace-separated unary signs and quoted update text remain pure expressions',() => {
  for (const [expression,expected] of [['- -$x',1],['+ +$x',1],['$x- -1',2],['$x+ +1',2],['$x+-1',0],['$x-+1',0],['"++ -- def $x"','++ -- def $x']]) {
    assert.equal(E.evaluate(E.parse(expression),{'$x':1},()=>{}),expected,expression);
  }
  const r = audit(story('<<set $x to 1>><<if - -$x is 1 and + +$x is 1 and $x- -1 is 2 and $x+ +1 is 2>><<set $ready to true>><</if>>$ready'));
  assert.equal(r.complete,true); assert.deepEqual(r.findings,[]);
});

test('regression fixtures retain one real witness and disclose every update passage',() => {
  const guards = audit(fixture('guards'));
  assert.equal(guards.complete,true); assert.equal(guards.findings.length,1);
  assert.equal(guards.findings[0].name,'$actualMissing');
  assert.deepEqual(guards.findings[0].path,['Start','Grouped','Evidence']);
  const updates = audit(fixture('updates'));
  assert.equal(updates.complete,false); assert.deepEqual(updates.findings,[]);
  for (const name of ['Predecrement','Preincrement','CompactMinus','CompactPlus','Postdecrement','Postincrement']) {
    assert.ok(updates.unchecked.some(n => n.passage === name && /increment|decrement/.test(n.reason)),name);
  }
});

test('the shipped standalone engine gives the repaired answers on both regression fixtures',() => {
  const html = fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
  const engine = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)][0][1].split('(function () {')[0];
  const context = vm.createContext({}); vm.runInContext(engine,context);
  for (const name of ['guards','updates']) {
    assert.equal(JSON.stringify(context.TwineAudit.audit(fixture(name))),JSON.stringify(audit(fixture(name))),name);
  }
});
