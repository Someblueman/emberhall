/* Original words and drawing: Fern, Emberhall, 2026. */
(function (root) {
  'use strict';
  // The order on the found paper is the order in this array. Names on envelopes
  // are labels, not extra words inserted into either copy of the letter.
  const paper = Object.freeze([
    {to: 'edie', text: 'I sold the piano.'},
    {to: 'nell', text: 'I kept the bench.'},
    {to: null, text: 'For you.'},
    {to: 'edie', text: 'You asked me not to wait.'},
    {to: 'edie', text: 'I watched the men lift it over the step.'},
    {to: 'edie', text: 'One of them asked if you still played.'},
    {to: 'edie', text: 'I said, whenever she can.'},
    {to: 'nell', text: 'There is a pale place where you sat.'},
    {to: 'nell', text: 'I used to tell you to turn the page.'},
    {to: 'nell', text: 'You always knew when.'},
    {to: 'nell', text: 'I should have looked up.'},
    {to: 'edie', text: 'Love, Mum.'},
    {to: 'nell', text: 'Love, Mum.'}
  ].map(Object.freeze));
  function divide(recipient) {
    if (!['edie', 'nell'].includes(recipient)) throw new Error('Choose Edie or Nell.');
    const letters = {edie: [], nell: []};
    paper.forEach((line, index) => letters[line.to || recipient].push({index, text: line.text, loose: line.to === null}));
    return letters;
  }
  const model = Object.freeze({paper, divide});
  if (typeof module !== 'undefined' && module.exports) module.exports = model;
  else root.BenchLetter = model;
})(globalThis);
