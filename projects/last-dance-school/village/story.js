/* Original second act. These are authored lives, not a simulation of culture. */
(function (root) {
  'use strict';
  const chapters = [
    [24, 'A village'], [32, 'The river divides'], [40, 'The north lesson'],
    [48, 'The south lesson'], [56, 'The years'], [64, 'A way across'],
    [72, 'The reunion'], [80, 'Somewhere to go']
  ];
  const lines = [
    'The clearing acquires two doors. Nobody remembers deciding to build a village.',
    'Ada measures a doorstep with the length of one careful movement.',
    'Pip tests the other doorstep. A pot falls off the shelf.',
    'Rue is allowed to carry the smallest pot. It contains a tree.',
    'They dance at the opening of the bridge. The bridge is not impressed.',
    'Ada leaves space between movements. Pip fills it.',
    'Rue tries to fill the space and leave it at the same time.',
    'For a summer, this is how the evenings go.',
    'Then the river takes the middle of the bridge.',
    'Pip catches a plank. Ada catches Pip. Neither counts it as a dance.',
    'The north door closes against the rain.',
    'The south door closes against the same rain.',
    '“We will meet when the water is low.”',
    'The water takes its time.',
    'Across the river, the lamps begin to look like stars.',
    'Rue puts Moth’s chair by the north door. Nobody has to explain why.',
    'Lio arrives with a blue thread tied round one sleeve.',
    '“For remembering which arm,” says Lio. Rue does not laugh.',
    'The thread remembers. The rest takes practice.',
    'Rue steps aside. There is only what Lio was here to see.',
    'Lio begins so carefully that the blue thread gets there first.',
    'The sleeve is too long. Lio decides the hand can wait inside it.',
    'Lio finishes. The little tree is taller now.',
    'Rue unties the thread. “You can keep it if you like.”',
    'On the south bank, Bea arrives carrying the plank Pip saved.',
    'Pip puts it down. “First, the floor must survive us.”',
    'Bea tests the floor. Somewhere, a pot trembles.',
    'Pip steps aside. Bea has only what reached this bank.',
    'Bea makes a beginning large enough for two.',
    'One foot nearly leaves without the rest of Bea.',
    'Bea finishes. Pip applauds with both sleeves.',
    'The plank becomes a bench. It has learned to stay.',
    'Years go through the village without knocking.',
    'Ada’s door opens. This time Ada does not come out.',
    'Pip’s scarf hangs from the south bench.',
    'Rue sits down in Moth’s chair. The knees have found the same quiet job.',
    'Lio is taller. The blue thread no longer reaches round the sleeve.',
    'Bea is taller too. The bench is still a very small audience.',
    'Across the river, two evenings begin with different movements.',
    'Nobody can ask the old teachers to settle the difference.',
    'One dry morning, the river leaves a row of stones.',
    'Lio finds the first stone by almost falling off it.',
    'Bea finds the next by catching the blue thread.',
    'Between them they carry the plank to the gap.',
    'It is too short to be a bridge. It is long enough to be a beginning.',
    'Lio offers a movement across the water.',
    'Bea answers with the one this bank kept.',
    'For once, neither starts again to correct the other.',
    'They meet on the plank, where there is room for one and a half people.',
    'One remembered movement travels in two differently sized bodies.',
    'One goes carefully. The other nearly knocks the moon off its hook.',
    'They stop in different places. Then they both laugh.',
    'Bea offers one last movement. Lio may watch, or look back towards home.',
    'A movement crosses only if there is someone there to catch it.',
    'Lio tries what just arrived, in a body that has its own opinions.',
    'Bea recognizes something. It is not quite Bea any more.',
    'They take the plank back to the clearing.',
    'The little tree has found enough sky for itself.',
    'Rue comes as far as the chair, then lets the younger knees continue.',
    'Lio leaves a space in the dance. Bea does not fill it.',
    'Bea leaves another. Lio has learned to notice.',
    'They do the ending differently, side by side.',
    'The blue thread is tied to the empty chair. It moves when nobody does.',
    'There is somewhere for the dance to go.'
  ];
  const beats = lines.map((line, i) => ({
    title: chapters[Math.floor(i / 8)][1], line, seconds: 8
  }));
  function chapter(beat) { return [...chapters].reverse().find(([n]) => beat >= n); }
  function apply(state, learn) {
    const b = state.beat, m = state.memories, a = state.audience;
    if (b === 43) {
      const slots = a.lio ? (a.lioLate ? [1, 2] : [0, 1, 2]) : [];
      m.lio = learn(m.rue, 'lio', slots);
      state.handoffs.push({from: 'rue', to: 'lio', slots: slots.filter(i => i < m.rue.length), count: m.lio.length, movements: m.lio.map(g => g.kind)});
    }
    if (b === 51) {
      const slots = a.bea ? [0, 1, 2] : [];
      m.bea = learn(m.pip, 'bea', slots);
      state.handoffs.push({from: 'pip', to: 'bea', slots: slots.filter(i => i < m.pip.length), count: m.bea.length, movements: m.bea.map(g => g.kind)});
    }
    if (b === 56) { m.ada = []; m.pip = []; }
    if (b === 77) {
      const slots = a.exchange && m.bea.length ? [m.bea.length - 1] : [];
      state.gift = learn(m.bea, 'lio', slots);
      m.lio.push(...state.gift);
      state.handoffs.push({from: 'bea', to: 'lio', slots, count: state.gift.length, movements: state.gift.map(g => g.kind)});
    }
  }
  function acts(state) {
    const b = state.beat, m = state.memories;
    const act = (who, slot) => ({who, slot});
    if (b === 25) return [act('ada', 0)];
    if (b === 26) return [act('pip', 2)];
    if (b === 27 || b === 30) return [act('rue', 0)];
    if (b >= 28 && b <= 29) return [act('ada', b - 28), act('pip', b - 28)];
    if (b >= 40 && b <= 42) return [act('rue', b - 40)];
    if (b >= 44 && b <= 46) return [act('lio', b - 44)];
    if (b >= 48 && b <= 50) return [act('pip', b - 48)];
    if (b >= 52 && b <= 54) return [act('bea', b - 52)];
    if (b === 60 || b === 62) return [act('lio', 0)];
    if (b === 61 || b === 63) return [act('bea', 0)];
    if (b === 69) return [act('lio', 0)];
    if (b === 70) return [act('bea', 0)];
    if (b >= 72 && b <= 74) return [act('lio', b - 72), act('bea', b - 72)];
    if (b === 76) return [act('bea', m.bea.length - 1)];
    if (b === 78 && state.gift.length) return [act('lio', m.lio.length - 1)];
    if (b === 83) return [act('lio', 0)];
    if (b === 84) return [act('bea', 0)];
    if (b >= 85) return [act('lio', m.lio.length - 1), act('bea', m.bea.length - 1)];
    return [];
  }
  function caption(state, words) {
    const b = state.beat, m = state.memories;
    if (b === 43 && !m.lio.length) return 'Lio missed the lesson. Rue leaves room for a dance that did not arrive.';
    if (b === 43 && state.audience.lioLate) return 'Lio caught the end of Rue’s dance. The blue thread cannot remember the beginning.';
    if (b === 51 && !m.bea.length) return 'Bea was away. The plank keeps the place where the lesson would have been.';
    if (b === 77 && !state.gift.length) return state.audience.exchange ? 'Bea has no movement to pass here. Lio waits without inventing one.' : 'Lio looks towards home. This offered movement does not cross.';
    if (b === 78 && !state.gift.length) return 'The offered place in the dance stays empty. Neither of them tries to mend it with a memory they do not have.';
    if (b >= 72 && b <= 74) {
      const slot = b - 72, left = m.lio[slot], right = m.bea[slot];
      return left && right ? `Lio’s ${words[left.kind]} meets Bea’s ${words[right.kind]}. Neither has to become the other.`
        : left ? 'Lio dances. Bea leaves that part open.' : right ? 'Bea dances. Lio keeps a space beside it.' : 'Both leave this part open. The river moves between them.';
    }
    const missing = acts(state).find(a => !m[a.who][a.slot]);
    if (missing) return `${missing.who === 'lio' ? 'Lio' : missing.who === 'bea' ? 'Bea' : 'Rue'} holds still. That movement never reached this lesson.`;
    return beats[b - 24].line;
  }
  const api = {chapters, beats, chapter, apply, acts, caption};
  if (typeof module !== 'undefined') module.exports = api;
  else root.Village = api;
})(typeof globalThis === 'undefined' ? this : globalThis);
