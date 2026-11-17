'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {audit} = require('./audit.js');
const {build} = require('./build.js');
const E = require('./expression.js');
const esc = s => s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
function story(passages,extra = '') {
  return '<tw-storydata name="Test" startnode="1" format="SugarCube" format-version="2.37.3">' + extra + Object.entries(passages).map(([name,text],i) => '<tw-passagedata pid="' + (i+1) + '" name="' + esc(name) + '" tags="">' + esc(text) + '</tw-passagedata>').join('') + '</tw-storydata>';
}
const fixture = name => fs.readFileSync(path.join(__dirname,'fixtures',name + '.html'),'utf8');
const unset = r => r.findings.filter(f => f.kind === 'unset');
function checked(passages) { const r = audit(story(passages)); assert.equal(r.complete,true,JSON.stringify(r.unchecked)); return r; }

test('clean two-branch preparation and finite loop have no false findings',() => {
  const r = audit(fixture('clean'));
  assert.equal(r.complete,true); assert.deepEqual(r.findings,[]); assert.equal(r.states,7);
});
test('case drift includes both exact names, source lines and a real unset witness',() => {
  const r = audit(fixture('case'));
  assert.deepEqual(r.findings.find(f => f.kind === 'case').names,['$Job','$job']);
  assert.equal(unset(r)[0].passage,'Bank'); assert.equal(unset(r)[0].line,1);
  assert.deepEqual(unset(r)[0].path,['Start','Bank']); assert.equal(r.complete,true);
});
test('the uninitialised flag is witnessed only on the route which skipped its assignment',() => {
  const r = audit(fixture('branch'));
  assert.equal(unset(r).length,1); assert.equal(unset(r)[0].name,'$hasKey');
  assert.deepEqual(unset(r)[0].path,['Start','Garden','Gate']);
});
test('condition outcomes are concrete; contradictory branches cannot invent routes',() => {
  const r = checked({Start:'<<set $n to 2>><<if $n is 1>>$ghost<<elseif $n is 2>><<set $ready to true>><<else>>$phantom<</if>><<if $ready>>[[End]]<</if>>',End:'$ready'});
  assert.deepEqual(r.findings,[]);
});
test('short-circuit, def, ndef, typeof and explicit undefined comparisons are intentional guards',() => {
  const r = checked({Start:'<<if false and $a>>ignored<</if>><<if true or $b>>yes<</if>><<if ndef $c>><<set $c to 1>><</if>><<if def $d and $d>>no<</if>><<if typeof $e is "undefined">>yes<</if>><<if $f is undefined>>yes<</if>><<if null eq $g>>yes<</if>>$c'});
  assert.deepEqual(r.findings,[]);
});
test('quoted expression strings, escaped examples and comments do not read variables',() => {
  const r = checked({Start:'<<set $text to "$quoted">><<print "literal words">> $$escaped """$literal""" <nowiki>$other</nowiki> {{{$code}}} /* $comment */ /% $comment2 %/'});
  assert.deepEqual(r.findings,[]);
});
test('quoted closing macro marks and escapes do not end an expression early',() => {
  const r = checked({Start:'<<set $s to ">> hi">><<set $q to "a\\\"b">>$s $q'});
  assert.deepEqual(r.findings,[]);
});
test('temporary variables survive within a passage and reset on navigation and after StoryInit',() => {
  const r = checked({Start:'<<set _x to 1>>_x [[End]]',End:'_x _boot',StoryInit:'<<set _boot to true>>'});
  assert.deepEqual(unset(r).map(f => f.name),['_x','_boot']);
});
test('links use the completed rendering state, including sets after the link',() => {
  assert.deepEqual(checked({Start:'[[End]]<<set $x to 3>>',End:'$x'}).findings,[]);
});
test('pipe, right-arrow and left-arrow literal links preserve their actual targets',() => {
  const r = checked({Start:'[[label|North]] [[label->East]] [[West<-label]]',North:'$a',East:'$b',West:'$c'});
  assert.deepEqual(unset(r).map(f => f.path),[['Start','North'],['Start','East'],['Start','West']]);
});
test('same-state loops reach a fixed point without claiming an exhausted bound',() => {
  const r = checked({Start:'<<set $x to 1>>[[Loop]]',Loop:'$x [[Loop]]'});
  assert.equal(r.states,2); assert.deepEqual(r.findings,[]);
});
test('growing loops hit explicit route, state, step and queued-choice limits',() => {
  const html = story({Start:'<<set $x to 0>>[[Loop]]',Loop:'<<set $x to $x + 1>>[[Loop]]'});
  for (const limits of [{depth:3},{states:2},{steps:3}]) {
    const r = audit(html,limits); assert.equal(r.complete,false); assert.match(JSON.stringify(r.unchecked),/limit reached/);
  }
  const r = audit(story({Start:'[[A]]'.repeat(30),A:'done'}),{states:1});
  assert.equal(r.complete,false);
});
test('unsupported effects are named and cannot produce downstream guesses',() => {
  for (const text of ['<<run $x = 1>>$x [[End]]','<<set $x to random(1,2)>>[[End]]','<<include "Init">>[[End]]','[[End][$x to 1]]','[[$destination]]','<a data-passage="End">go</a>','<<set $x to {a:1}>>','<<set $x to 1, $y to 2>>','$object.key','_list[0]','<<textbox "$x" "">>']) {
    const r = audit(story({Start:text,End:'$downstream'}));
    assert.equal(r.complete,false,text); assert.ok(r.unchecked.some(n => n.passage === 'Start'),text);
    assert.ok(!unset(r).some(f => f.name === '$downstream'),text);
  }
});
test('story scripts and every supported detection of a global hook halt route analysis',() => {
  for (const extra of ['<script role="script" type="text/twine-javascript">State.variables.x=1</script>','<tw-passagedata pid="9" name="PassageHeader">&lt;&lt;set $x to 1&gt;&gt;</tw-passagedata>','<tw-passagedata pid="9" name="Init" tags="init">&lt;&lt;set $x to 1&gt;&gt;</tw-passagedata>']) {
    const r = audit(story({Start:'$x'},extra)); assert.equal(r.complete,false); assert.equal(r.states,0); assert.deepEqual(unset(r),[]);
  }
});
test('runtime shell scripts outside the story container are never read or run',() => {
  const r = audit('<script>throw new Error("executed")</script>' + story({Start:'hello'}));
  assert.equal(r.complete,true); assert.deepEqual(r.findings,[]);
});
test('missing targets and unreachable passages always prevent a clear report',() => {
  const r = audit(story({Start:'[[Absent]]',Unused:'$ghost'}));
  assert.equal(r.complete,false); assert.ok(r.unchecked.some(n => n.reason.includes('Missing link target')));
  assert.ok(r.unchecked.some(n => n.passage === 'Unused')); assert.deepEqual(unset(r),[]);
});
test('unsupported syntax is disclosed even on an untaken branch',() => {
  const r = audit(story({Start:'<<if false>><<custom>><<else>><<set $x to 1>><</if>>$x'}));
  assert.equal(r.complete,false); assert.deepEqual(unset(r),[]);
});
test('malformed structure, format, attributes, identifiers, entities and limits fail safely',() => {
  const base = story({Start:'hello'});
  for (const html of ['',base + base,base.replace('SugarCube','Harlowe'),base.replace('startnode="1"','startnode="9"'),base.replace('pid="1"','pid="1" pid="2"'),base.replace('hello','<img>'),base.replace('hello','&madeup;'),base.replace('</tw-passagedata>',''),base.replace('format-version="2.37.3"','format-version="1.0"'),' '.repeat(2000001),story({Start:'x'.repeat(60001)})]) assert.throws(() => audit(html));
  const r = audit(story({Start:'<<if true>>oops'})); assert.equal(r.complete,false); assert.match(JSON.stringify(r.unchecked),/closing if/);
});
test('HTML entities decode once; hostile source text stays inert data with accurate line numbers',() => {
  const r = audit(story({'Start':'literal\n$missing\n<svg onload="throw 1">'}));
  assert.equal(unset(r)[0].line,2); assert.match(r.passages[0].text,/<svg onload=/); assert.equal(r.complete,false);
  assert.equal(audit(story({Start:'&lt;not markup&gt;'})).passages[0].text,'&lt;not markup&gt;');
});
test('prototype-looking variable names are ordinary map entries and signed zero stays distinct',() => {
  const r = checked({Start:'<<set $__proto__ to 1>><<set $constructor to 2>>$__proto__ $constructor'});
  assert.deepEqual(r.findings,[]);
});
test('expression interpreter honours precedence, strict/loose equality and rejects executable constructs',() => {
  for (const [src,want] of [['1 + 2 * 3',7],['"1" eq 1',true],['"1" is 1',false],['not false and 2 gte 1',true],['-2 + 3',1]]) assert.equal(E.evaluate(E.parse(src),Object.create(null),()=>{}),want);
  for (const src of ['window.alert(1)','($x = 2)','random()','[1,2]','$a.b','new Date()','1; throw 1']) assert.throws(() => E.parse(src));
});
test('generated standalone page is current and runs the exact tested engine without DOM parsing or eval',() => {
  const html = fs.readFileSync(path.join(__dirname,'index.html'),'utf8'); assert.equal(html,build());
  const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)]; assert.equal(scripts.length,1);
  const engine = scripts[0][1].split('(function () {')[0];
  const context = vm.createContext({}); vm.runInContext(engine,context);
  const report = context.TwineAudit.audit(fixture('branch'));
  assert.equal(JSON.stringify(unset(report)[0].path),JSON.stringify(['Start','Garden','Gate']));
  for (const filename of ['expression.js','story.js','audit.js','ui.js']) assert.doesNotMatch(fs.readFileSync(path.join(__dirname,filename),'utf8'),/\b(?:eval|Function|DOMParser|fetch)\s*\(|\.innerHTML\s*=/);
});
