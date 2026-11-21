// Run: node projects/every-promise-two-endings/test_chapter.cjs
// Execute the actual embedded story engine without a browser or a second copy.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const html = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');
const script = html.match(/<script id="chapter">([\s\S]*?)<\/script>/)[1];
const sandbox = {module: {exports: {}}};
vm.runInNewContext(script, sandbox);
const {fresh, view, step, restore} = sandbox.module.exports;
const plain = value => JSON.parse(JSON.stringify(value));
const walk = (state, actions) => actions.reduce((s, a) => step(s, a), state);
const prologue = ['quay', 'ask-edda', 'back', 'ask-dan', 'back',
  'ask-sava', 'back', 'ask-ivo', 'back', 'meeting', 'timing'];
const text = state => view(state).prose.join('\n').replace(/<[^>]*>/g, '');

const endings = new Set();
const wordCounts = [];
for (const timing of ['dawn', 'daylight']) {
  for (const names of ['chairs', 'pages']) {
    const actions = [...prologue, `choose-${timing}`, `choose-${names}`,
      'sign', 'crossing', 'meal', 'after', 'end'];
    let s = fresh(), words = 0, result = '';
    for (const action of actions) {
      // Optional questions return to the same table; count that passage only once.
      if (s.scene !== 'quay' || action === 'ask-edda') words += text(s).split(/\s+/).length;
      if (['crossing', 'meal', 'after'].includes(s.scene)) result += text(s);
      const before = JSON.stringify(s);
      const next = step(s, action);
      assert.equal(JSON.stringify(s), before, 'a choice must not mutate the previous bookmark');
      s = next;
    }
    assert.equal(s.scene, 'end');
    assert.ok(words >= 2700, `complete reading too short: ${words} words`);
    endings.add(result);
    wordCounts.push(`${timing}/${names}: ${words} words including optional conversations`);
    let revised = walk(s, ['return-draft', 'revise-time',
      `choose-${timing === 'dawn' ? 'daylight' : 'dawn'}`]);
    assert.equal(revised.scene, 'draft');
    assert.equal(revised.names, names, 'timing revision preserves the other promise');
    revised = walk(revised, ['revise-names', `choose-${names === 'chairs' ? 'pages' : 'chairs'}`]);
    assert.equal(revised.scene, 'draft');
    assert.match(text(revised), revised.timing === 'dawn' ? /at first light/ : /inspected the timbers/);
    assert.match(text(revised), revised.names === 'chairs' ? /keep a place/ : /read the names/);
    assert.deepEqual(plain(walk(revised, ['sign', 'crossing', 'meal', 'after', 'end', 'start-over'])), plain(fresh()));
  }
}
assert.equal(endings.size, 4, 'both promises must change lived scenes independently');

// Explore every reachable story state, including question orders and revisions.
const queue = [fresh()], seen = new Set(), scenes = new Set();
while (queue.length) {
  const s = queue.pop();
  // The heard list is a set; canonicalize it so question order adds no false states.
  const key = JSON.stringify({...s, heard: [...s.heard].sort()});
  if (seen.has(key)) continue;
  seen.add(key); scenes.add(s.scene);
  const page = view(s);
  assert.ok(page.title && page.prose.length && page.choices.length, `empty scene ${s.scene}`);
  assert.deepEqual(plain(restore(JSON.stringify(s))), plain(s), `bookmark fails at ${s.scene}`);
  if (!s.access && !s.shelter && !s.objects) {
    const {access, shelter, objects, ...legacy} = s;
    if (!['second','yard','mara','pet','runa','access'].includes(s.scene)) {
      assert.deepEqual(plain(restore(JSON.stringify(legacy))), plain(s), 'chapter-one bookmark migration');
    }
  }
  assert.throws(() => step(s, 'not-a-choice'), /not available/);
  assert.equal(new Set(page.choices.map(c => c.id)).size, page.choices.length);
  for (const c of page.choices) {
    const next = step(s, c.id);
    assert.ok(view(next), `broken link ${s.scene}/${c.id}`);
    queue.push(next);
  }
}
assert.deepEqual([...scenes].sort(), ['after', 'crossing', 'dan', 'draft', 'edda', 'end',
  'ivo', 'meal', 'meeting', 'names', 'opening', 'quay', 'sava', 'signed', 'timing',
  'second', 'yard', 'mara', 'pet', 'runa', 'access', 'shelter', 'middleDraft',
  'invitation', 'mill', 'binding', 'carrying', 'register', 'middleEnd',
  'third', 'storeDoor', 'objects', 'objectDraft', 'returning', 'violin', 'dinner', 'thirdEnd'].sort());
for (const bad of ['{', 'null', '[]', '{}', JSON.stringify({...fresh(), scene: '__proto__'}),
  JSON.stringify({...fresh(), scene: 'draft'}), JSON.stringify({...fresh(), revising: true}),
  JSON.stringify({...fresh(), heard: ['unknown']}), JSON.stringify({...fresh(), scene: 'constructor'})]) {
  assert.deepEqual(plain(restore(bad)), plain(fresh()), `unsafe bookmark: ${bad}`);
}
// The new chapter has sixteen paths: both old promises and both new promises matter.
const middleEndings = new Set();
let middleRange = [], thirdRange = [];
const thirdEndings = new Set(), completeReadings = new Set();
for (const timing of ['dawn', 'daylight']) for (const names of ['chairs', 'pages']) {
  const opening = walk(fresh(), ['quay', 'meeting', 'timing', `choose-${timing}`,
    `choose-${names}`, 'sign', 'crossing', 'meal', 'after', 'end']);
  for (const access of ['lead', 'together']) for (const shelter of ['school', 'bakery']) {
    let s = opening, words = 0, reading = '';
    const actions = ['second', 'yard', 'ask-mara', 'yard', 'ask-pet', 'yard',
      'ask-runa', 'yard', 'access', `choose-${access}`, `choose-${shelter}`,
      'agree-middle', 'mill', 'binding', 'carrying', 'register', 'middleEnd'];
    let yardSeen = false;
    for (const action of actions) {
      s = step(s, action);
      if (s.scene === 'yard' && yardSeen) continue;
      if (s.scene === 'yard') yardSeen = true;
      words += text(s).split(/\s+/).length;
      reading += text(s);
    }
    assert.equal(s.scene, 'middleEnd');
    for (const objects of ['open', 'quiet']) {
      let third = s, prose = '', count = 0;
      for (const action of ['third', 'storeDoor', 'objects', `choose-${objects}`,
        'agree-objects', 'violin', 'dinner', 'thirdEnd']) {
        third = step(third, action); prose += text(third);
        count += text(third).split(/\s+/).length;
      }
      thirdEndings.add(prose); completeReadings.add(reading + prose); thirdRange.push(count);
      assert.equal(third.scene, 'thirdEnd');
      assert.ok(prose.includes(objects === 'open' ? 'photograph face down' : 'seen four households'), 'returning mode changes the afternoon');
      const changed = walk(third, ['return-objects', 'revise-objects',
        `choose-${objects === 'open' ? 'quiet' : 'open'}`]);
      assert.equal(changed.scene, 'objectDraft');
      assert.equal(changed.access, access); assert.equal(changed.shelter, shelter);
      assert.equal(step(third, 'return-middle').objects, null);
      assert.equal(step(third, 'return-draft').objects, null);
    }
    middleEndings.add(reading); middleRange.push(words);
    assert.match(reading, timing === 'dawn' ? /sets her end down at once/ : /marks the seam before we lift/);
    assert.match(reading, names === 'chairs' ? /An ordinary chair/ : /what things don't mean/);
    assert.match(reading, access === 'lead' ? /key out of her pocket/ : /moves his end to the stone/);
    assert.match(reading, shelter === 'school' ? /no beds in it/ : /Four people came from the school/);
    const revised = walk(s, ['return-middle', 'revise-access',
      `choose-${access === 'lead' ? 'together' : 'lead'}`]);
    assert.equal(revised.scene, 'middleDraft');
    assert.equal(revised.shelter, shelter);
    const rehomed = walk(revised, ['revise-shelter',
      `choose-${shelter === 'school' ? 'bakery' : 'school'}`]);
    assert.equal(rehomed.access, revised.access);
    assert.equal(rehomed.scene, 'middleDraft');
    const firstDraft = step(s, 'return-draft');
    assert.equal(firstDraft.access, null); assert.equal(firstDraft.shelter, null);
    assert.equal(firstDraft.timing, timing); assert.equal(firstDraft.names, names);
    assert.deepEqual(plain(step(s, 'start-over')), plain(fresh()));
  }
}
assert.equal(middleEndings.size, 16);
// Chapter three remembers each middle decision and the meal, while the full story
// also retains the crossing's consequences in chapter two.
assert.equal(thirdEndings.size, 16);
assert.equal(completeReadings.size, 32);
for (const bad of [
  {...fresh(), access: 'unknown'}, {...fresh(), objects: 'unknown'},
  {...fresh(), scene: 'third', timing:'dawn', names:'chairs'},
  {...fresh(), scene: 'dinner', timing:'dawn', names:'chairs', access:'lead', shelter:'school'}, {...fresh(), shelter: 'unknown'},
  {...fresh(), scene: 'second'},
  {...fresh(), scene: 'shelter', timing:'dawn', names:'chairs'},
  {...fresh(), scene: 'middleEnd', timing:'dawn', names:'chairs', access:'lead'}
]) assert.deepEqual(plain(restore(JSON.stringify(bad))), plain(fresh()));
console.log(`Third chapter: ${Math.min(...thirdRange)}–${Math.max(...thirdRange)} words; both return routes and revisions pass.`);
console.log(`Middle chapter: 16 distinct readings; ${Math.min(...middleRange)}–${Math.max(...middleRange)} words including conversations.`);
console.log(`PASS: ${seen.size} reachable states; ${scenes.size} scenes; four distinct consequence combinations; revisions, restart and bookmarks.`);
console.log(wordCounts.join('\n'));
