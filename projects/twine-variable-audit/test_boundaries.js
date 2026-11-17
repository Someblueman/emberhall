'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const {audit} = require('./audit.js');
const E = require('./expression.js');
const escape = x => x.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
function story(start,rest = '') {
  return '<tw-storydata startnode="1" format="SugarCube" format-version="2.37.3"><tw-passagedata pid="1" name="Start">' + escape(start) + '</tw-passagedata>' + rest + '</tw-storydata>';
}
const passage = (name,text,id = '2') => '<tw-passagedata pid="' + id + '" name="' + name + '">' + escape(text) + '</tw-passagedata>';

test('a case comparison carries witnessed occurrences without inventing an untaken occurrence',() => {
  const r = audit(story('<<set $Flag to true>><<if false>>$FLAG<</if>>[[End]]',passage('End','$flag')));
  const comparison = r.findings.find(f => f.kind === 'case');
  const locations = Object.fromEntries(comparison.locations.map(x => [x.name,x.path]));
  assert.deepEqual(locations.$Flag,['Start']); assert.equal(locations.$FLAG,null); assert.deepEqual(locations.$flag,['Start','End']);
});
test('duplicate links are folded before queuing and do not manufacture a bound failure',() => {
  const r = audit(story('[[End]]'.repeat(100),passage('End','done')),{states:2});
  assert.equal(r.states,2); assert.equal(r.complete,true); assert.deepEqual(r.findings,[]);
});
test('finding and case-comparison limits stop honestly',() => {
  const r = audit(story(Array.from({length:510},(_,i) => '$v' + i).join(' ')));
  assert.equal(r.findings.length,500); assert.equal(r.complete,false);
  assert.match(JSON.stringify(r.unchecked),/Finding limit/);
  const c = audit(story('<<set $A to 1>><<set $a to 2>><<set $B to 3>><<set $b to 4>>'),{findings:1});
  assert.equal(c.findings.length,1); assert.equal(c.complete,false);
});
test('code-passage navigation is unchecked, never a fabricated second initialisation',() => {
  const r = audit(story('[[StoryInit]]',passage('StoryInit','<<set $x to 1>>')));
  assert.equal(r.complete,false); assert.match(JSON.stringify(r.unchecked),/link into the StoryInit/);
});
test('source punctuation is not property access; real properties are unchecked',() => {
  const r = audit(story('<<set $name to "Ada">>Hello, $name.'));
  assert.equal(r.complete,true); assert.deepEqual(r.findings,[]);
  const p = audit(story('$name.first')); assert.equal(p.complete,false); assert.deepEqual(p.findings,[]);
});
test('HTML comments are literal examples, and valid dollar signs in names are preserved',() => {
  const r = audit(story('<!-- $fake --> <<set $a$b to 1>>$a$b'));
  assert.equal(r.complete,true); assert.deepEqual(r.findings,[]);
});
test('raw string newlines and executable suffixes remain unchecked',() => {
  for (const expression of ['"a\nb"','"a\rb"','1 + alert(1)','true ? 1 : 2']) assert.throws(() => E.parse(expression));
  const r = audit(story('<<set $x to "a\nb">>$x')); assert.equal(r.complete,false); assert.deepEqual(r.findings,[]);
});
test('non-finite arithmetic, oversized values, expression and structural bounds are explicit',() => {
  for (const text of ['<<set $x to 1 / 0>>','<<set $x to "' + 'x'.repeat(10001) + '">>','<<if ' + '('.repeat(260) + 'true' + ')'.repeat(260) + '>>ok<</if>>','<<if true>>'.repeat(34) + 'yes' + '<</if>>'.repeat(34)]) {
    const r = audit(story(text)); assert.equal(r.complete,false,text.slice(0,40)); assert.ok(r.unchecked.length);
  }
});
test('signed-zero states are not collapsed when a later division distinguishes them',() => {
  const extra = passage('Positive','<<set $n to 0>>[[Test]]','2') + passage('Negative','<<set $n to -0>>[[Test]]','3') + passage('Test','<<if 1 / $n lt 0>>$missing<</if>>','4');
  const r = audit(story('[[Positive]] [[Negative]]',extra));
  assert.deepEqual(r.findings.find(f => f.kind === 'unset').path,['Start','Negative','Test']);
});
test('the first supported witness retains choices in earlier passages',() => {
  const r = audit(story('<<set $go to true>><<if $go>>[[End]]<</if>>',passage('End','$missing')));
  assert.deepEqual(r.findings[0].decisions,[{passage:'Start',line:1,taken:true}]);
});

test('custom styling cannot make hidden links into allegedly playable routes',() => {
  const r = audit(story('[[End]]', '<style role="stylesheet">a { display:none }</style>' + passage('End','$hidden')));
  assert.equal(r.states,0); assert.equal(r.complete,false); assert.deepEqual(r.findings,[]);
  assert.match(JSON.stringify(r.unchecked),/styling may hide/);
});
test('automatic external links cannot turn their literal dollar signs into variable reads',() => {
  const r = audit(story('https://example.invalid/$literal'));
  assert.equal(r.complete,false); assert.deepEqual(r.findings,[]);
});

test('printed strings that can expand markup stop before a false downstream witness',() => {
  for (const start of ['<<set $text to "<<set $x to 1>>">>$text $x', '<<print "<<set $x to 1>>">>$x', '<<= "$nested">>$x', '<<- "$nested">>$x', '?template $x']) {
    const r = audit(story(start)); assert.equal(r.complete,false,start); assert.deepEqual(r.findings,[],start);
  }
});
test('a dollar escape consumes only its two sigils; a later variable still reads',() => {
  const r = audit(story('$$literal$actual'));
  assert.equal(r.complete,true); assert.equal(r.findings.length,1); assert.equal(r.findings[0].name,'$actual');
});

test('styled tables and malformed macro spacing cannot create invented routes',() => {
  for (const text of ['|hidden|k\n|[[End]]|', '<< set $x to 1>>[[End]]']) {
    const r = audit(story(text,passage('End','$x'))); assert.equal(r.complete,false); assert.deepEqual(r.findings,[]);
  }
});
test('other format versions and the ambiguous legacy comparison are rejected honestly',() => {
  for (const version of ['2.0.0','2.36.1','2.38.0']) assert.throws(() => audit(story('hello').replace('2.37.3',version)),/2.37/);
  assert.throws(() => E.parse('$a is not $b'),/legacy/);
  assert.equal(E.evaluate(E.parse('"This is not an operator"'),{},()=>{}),'This is not an operator');
});
