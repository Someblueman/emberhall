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
  assert.throws(() => step(s, 'not-a-choice'), /not available/);
  assert.equal(new Set(page.choices.map(c => c.id)).size, page.choices.length);
  for (const c of page.choices) {
    const next = step(s, c.id);
    assert.ok(view(next), `broken link ${s.scene}/${c.id}`);
    queue.push(next);
  }
}
assert.deepEqual([...scenes].sort(), ['after', 'crossing', 'dan', 'draft', 'edda', 'end',
  'ivo', 'meal', 'meeting', 'names', 'opening', 'quay', 'sava', 'signed', 'timing'].sort());
for (const bad of ['{', 'null', '[]', '{}', JSON.stringify({...fresh(), scene: '__proto__'}),
  JSON.stringify({...fresh(), scene: 'draft'}), JSON.stringify({...fresh(), revising: true}),
  JSON.stringify({...fresh(), heard: ['unknown']}), JSON.stringify({...fresh(), scene: 'constructor'})]) {
  assert.deepEqual(plain(restore(bad)), plain(fresh()), `unsafe bookmark: ${bad}`);
}
console.log(`PASS: ${seen.size} reachable states; ${scenes.size} scenes; four distinct consequence combinations; revisions, restart and bookmarks.`);
console.log(wordCounts.join('\n'));
