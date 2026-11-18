'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const {paper, divide} = require('./letter.js');

test('both offered divisions conserve every original line once, in order', () => {
  for (const recipient of ['edie', 'nell']) {
    const letters = divide(recipient);
    const all = [...letters.edie, ...letters.nell].sort((a,b) => a.index-b.index);
    assert.deepEqual(all.map(line => line.text), paper.map(line => line.text));
    assert.equal(new Set(all.map(line => line.index)).size, paper.length);
    for (const name of ['edie', 'nell']) {
      const indices = letters[name].map(line => line.index);
      assert.deepEqual(indices, [...indices].sort((a,b) => a-b));
      assert.equal(letters[name].filter(line => line.loose).length, name === recipient ? 1 : 0);
    }
  }
});

test('both complete reading copies match the original draft', () => {
  const endings = {
    edie: ['You asked me not to wait.', 'I watched the men lift it over the step.', 'One of them asked if you still played.', 'I said, whenever she can.', 'Love, Mum.'],
    nell: ['There is a pale place where you sat.', 'I used to tell you to turn the page.', 'You always knew when.', 'I should have looked up.', 'Love, Mum.']
  };
  for (const recipient of ['edie','nell']) {
    const letters = divide(recipient);
    for (const name of ['edie','nell']) {
      const expected = [name === 'edie' ? 'I sold the piano.' : 'I kept the bench.'];
      if (name === recipient) expected.push('For you.');
      expected.push(...endings[name]);
      assert.deepEqual(letters[name].map(line => line.text), expected);
    }
  }
  // These assertions pin the reading copy, not a claim that an algorithm can
  // decide whether a poem is moving. A non-author must judge that separately.
});

test('unassigned and unknown recipients cannot silently lose the loose line', () => {
  for (const value of [null, undefined, '', 'both', 'Edie', '<script>']) {
    assert.throws(() => divide(value), /Choose Edie or Nell/);
  }
});
