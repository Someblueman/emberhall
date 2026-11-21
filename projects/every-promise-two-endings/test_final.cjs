// Called by test_chapter.cjs; exercise the complete work in the actual HTML engine.
module.exports = ({fresh, view, step, restore}) => {
  const assert = require('node:assert/strict');
  const walk = (state, actions) => actions.reduce((s, a) => step(s, a), state);
  const text = s => view(s).prose.join('\n');
  const normal = s => JSON.parse(JSON.stringify(s));
  const finals = new Set(), closures = new Set();
  let minimum = Infinity, maximum = 0;
  for (const timing of ['dawn', 'daylight']) for (const names of ['chairs', 'pages'])
  for (const access of ['lead', 'together']) for (const shelter of ['school', 'bakery'])
  for (const objects of ['open', 'quiet']) for (const aftermath of ['hold', 'witness']) {
    const fourth = walk(fresh(), ['quay', 'meeting', 'timing', `choose-${timing}`,
      `choose-${names}`, 'sign', 'crossing', 'meal', 'after', 'end', 'second',
      'yard', 'access', `choose-${access}`, `choose-${shelter}`, 'agree-middle',
      'mill', 'binding', 'carrying', 'register', 'middleEnd', 'third', 'storeDoor',
      'objects', `choose-${objects}`, 'agree-objects', 'violin', 'dinner', 'thirdEnd',
      'fourth', 'courtyard', 'dispute', `choose-${aftermath}`, 'agree-aftermath',
      'mending', 'fourthEnd']);
    // An actual old ending bookmark can continue without having a new field.
    const {duty, ...oldBookmark} = fourth;
    assert.deepEqual(normal(restore(JSON.stringify(oldBookmark))), normal(fourth));
    for (const duty of ['hours', 'handover']) {
      let s = fourth, prose = '', words = 0;
      const actions = ['fifth','rosin','letter','tollhouse','schoolGate','wrongDoor',
        'fifthEnd','sixth','capacity','limits','duty',`choose-${duty}`,'agree-duty',
        'sixthEnd','seventh','ordinaryWork','sunday','news','reviewDay',
        'seventhEnd','eighth','highFold','homeward'];
      for (const action of actions) {
        const before = JSON.stringify(s);
        s = step(s, action);
        assert.equal(JSON.stringify(restore(before)), before);
        assert.deepEqual(normal(restore(JSON.stringify(s))), normal(s));
        prose += text(s);
        words += text(s).replace(/<[^>]*>/g, '').split(/\s+/).length;
      }
      minimum = Math.min(minimum, words); maximum = Math.max(maximum, words);
      assert.equal(s.scene, 'homeward');
      assert.match(text(s), duty === 'hours' ? /copying face down/ : /countinghouse yard/);
      assert.match(prose, /Neither entry can be matched to Ivo or Neri/);
      assert.match(prose, shelter === 'school' ? /scorched/ : /six people's coats/);
      assert.match(prose, aftermath === 'hold' ? /two remain disputed/ : /slips the street witnesses/);
      assert.match(prose, access === 'lead' ? /teaching Pell to use the brace/ : /temporary board together/);
      assert.match(text(s), names === 'chairs' ? /cup has a chip/ : /feet are splendid/);
      assert.match(prose, /Lise has agreed to the Saturday, not to every Saturday/);
      finals.add(prose); closures.add(text(s));
      const revision = walk(s, ['return-duty','revise-duty',
        `choose-${duty === 'hours' ? 'handover' : 'hours'}`]);
      assert.equal(revision.scene, 'finalDraft');
      assert.equal(revision.aftermath, aftermath);
      assert.equal(revision.objects, objects);
      assert.equal(revision.shelter, shelter);
      for (const action of ['return-draft','return-middle','return-objects','return-aftermath']) {
        assert.equal(step(s, action).duty, null, `${action} clears the later promise`);
      }
      assert.deepEqual(normal(step(s, 'start-over')), normal(fresh()));
      for (const bad of [{...s, duty:null},{...s, duty:'forever'},
        {...s, aftermath:null},{...s, access:null},{...s, objects:null}]) {
        assert.deepEqual(normal(restore(JSON.stringify(bad))), normal(fresh()));
      }
    }
  }
  // All prior promises affect the full reading; the final page has four variants.
  assert.equal(finals.size, 64); // timing is recalled in accepted chapters; the other six choices shape the final acts.
  assert.equal(closures.size, 4);
  const count = require('./story_words.cjs')({fresh, view, step});
  assert.ok(count.words >= 20000 && count.words <= 30000, `edited story count ${count.words}`);
  console.log(`Final acts: 128 complete paths; ${minimum}–${maximum} words per reading; both endings, revisions and legacy restores pass.`);
  console.log(`Edited story: ${count.words} words in ${count.paragraphs} distinct prose paragraphs.`);
};
