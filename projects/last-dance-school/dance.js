/* Authored inheritance rules for a fictional dance, not a model of culture. */
(function (root) {
  'use strict';
  const kinds = ['bow', 'wave', 'stamp', 'turn'];
  const beats = [
    ['The clearing', 'Moth puts a chair out for a class of two. “A dance needs somewhere to go.”'],
    ['Moth teaches', '“Start with this. Even if your knees object.”'],
    ['Moth teaches', 'Ada counts under her breath. Pip is already on the next bit.'],
    ['Moth teaches', 'Moth finishes a little sideways. Nobody mentions it.'],
    ['The first handoff', '“Now you.” Moth steps back.'],
    ['Ada tries', 'Ada does the first movement as if it were made of glass.'],
    ['Ada tries', 'She makes room for every small part of it.'],
    ['Ada tries', '“Was that right?” “It was yours,” says Moth.'],
    ['Pip tries', 'Pip begins before anyone says to begin.'],
    ['Pip tries', 'The second movement nearly carries Pip off the floor.'],
    ['Pip tries', '“Again?” asks Pip. Moth sits down instead.'],
    ['The last class', '“My knees have found a quieter job. You have the floor.”'],
    ['A space', 'For a while, nobody moves the chair.'],
    ['Some time later', 'Rue arrives in a coat with sleeves to grow into. “Is this where the dancing is?”'],
    ['Another teacher', 'There is a lesson to pass on. There is also a chair to climb.'],
    ['Another teacher', 'Rue watches the hands. Then the feet.'],
    ['Another teacher', 'The teacher finishes a little sideways.'],
    ['The second handoff', '“Your turn, Rue.” The coat is much too big.'],
    ['Rue tries', 'A small body makes a large beginning.'],
    ['Rue tries', 'Something familiar catches in the sleeves.'],
    ['Rue tries', 'The last movement belongs to the child now.'],
    ['The empty chair', 'Rue looks at the chair. “Was there someone else?”'],
    ['The school', 'Nobody sits down. There is still a little dancing to do.'],
    ['A place for a crooked dance', 'The chair stays. The dance goes.']
  ].map(([title, line]) => ({title, line, seconds: 8}));

  function gesture(kind, big = false) {
    if (!kinds.includes(kind)) throw new Error('Unknown gesture');
    return {kind, tilt: big ? 24 : 12, reach: big ? 1.25 : 0.85, foot: big ? 18 : 10};
  }
  function learn(source, pupil, slots) {
    if (!['ada', 'pip', 'rue'].includes(pupil)) throw new Error('Unknown pupil');
    return source.filter((_, i) => slots.includes(i)).map(g => ({
      kind: g.kind,
      tilt: g.tilt + (pupil === 'ada' ? 6 : pupil === 'pip' ? -5 : 4),
      reach: g.reach * (pupil === 'ada' ? 0.8 : pupil === 'pip' ? 1.22 : 0.82),
      foot: g.foot * (pupil === 'ada' ? 0.7 : pupil === 'pip' ? 1.3 : 0.75)
    }));
  }
  function start(phrase, options) {
    if (phrase.length !== 3 || phrase.some(g => !kinds.includes(g.kind))) throw new Error('Choose three gestures');
    if (!['ada', 'pip'].includes(options.teacher)) throw new Error('Choose Rue’s teacher');
    return {beat: 0, memories: {moth: phrase.map(g => ({...g})), ada: [], pip: [], rue: []},
      watching: {ada: !!options.ada, pip: !!options.pip}, teacher: options.teacher,
      late: !!options.late, handoffs: []};
  }
  function next(state) {
    if (state.beat >= beats.length - 1) return false;
    state.beat++;
    if (state.beat === 4) {
      for (const pupil of ['ada', 'pip']) {
        const slots = state.watching[pupil] ? [0, 1, 2] : [];
        state.memories[pupil] = learn(state.memories.moth, pupil, slots);
        state.handoffs.push({from: 'moth', to: pupil, slots, count: state.memories[pupil].length});
      }
    }
    if (state.beat === 12) state.memories.moth = []; // Nobody can restore the departed score.
    if (state.beat === 17) {
      const source = state.memories[state.teacher];
      const slots = state.late ? [1, 2] : [0, 1, 2];
      state.memories.rue = learn(source, 'rue', slots);
      state.handoffs.push({from: state.teacher, to: 'rue', slots: slots.filter(i => i < source.length), count: state.memories.rue.length});
    }
    return true;
  }
  function performance(state) {
    const b = state.beat;
    if (b >= 1 && b <= 3) return {who: 'moth', slot: b - 1};
    if (b >= 5 && b <= 7) return {who: 'ada', slot: b - 5};
    if (b >= 8 && b <= 10) return {who: 'pip', slot: b - 8};
    if (b >= 14 && b <= 16) return {who: state.teacher, slot: b - 14};
    if (b >= 18 && b <= 20) return {who: 'rue', slot: b - 18};
    return null;
  }
  function caption(state) {
    const b = state.beat, names = {ada: 'Ada', pip: 'Pip'};
    if (b === 4 && (!state.watching.ada || !state.watching.pip)) {
      const absent = !state.watching.ada && !state.watching.pip ? 'Both pupils were' : `${!state.watching.ada ? 'Ada was' : 'Pip was'}`;
      return `${absent} chasing a moth instead. Moth’s dance did not reach them.`;
    }
    const act = performance(state);
    if (act && !state.memories[act.who][act.slot]) {
      return act.who === 'rue' ? 'Rue waits. Nobody taught the sleeves what to do here.' : `${names[act.who]} looks at the floor. “I missed that bit.”`;
    }
    if (b === 14) return `${names[state.teacher]} takes Moth’s old place. Rue ${state.late ? 'is still outside, finding a button' : 'is watching very carefully'}.`;
    if (b === 15 && state.late) return 'Rue slips in late, one button short. The lesson has already begun.';
    if (b === 17) return state.memories.rue.length ? `Rue has caught ${state.memories.rue.length === 3 ? 'a whole little dance' : 'the end of a dance'}. The beginning cannot be fetched from the empty chair.` : 'No dance reached Rue today. The chair is company enough.';
    if (b === 23) return state.memories.rue.length ? 'Rue leaves a space beside the chair. “For whoever comes next.”' : 'Rue waits beside the chair. “Perhaps tomorrow somebody will come.”';
    return beats[b].line;
  }
  const api = {kinds, beats, gesture, learn, start, next, performance, caption};
  if (typeof module !== 'undefined') module.exports = api;
  else root.Dance = api;
})(typeof globalThis === 'undefined' ? this : globalThis);
