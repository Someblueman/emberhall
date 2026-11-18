(function (root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.DropItRig = factory();
  }
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const PUPPETS = ['A', 'B', 'C', 'D'];
  const PUPPET_META = {
    A: { id: 'A', name: 'Pip', role: 'Tall coat', color: '#2b5b6c' },
    B: { id: 'B', name: 'Bess', role: 'Pleated skirt', color: '#9c3d32' },
    C: { id: 'C', name: 'Gus', role: 'Waistcoat', color: '#b57b28' },
    D: { id: 'D', name: 'Dot', role: 'Latecomer', color: '#4c6b47' },
  };

  const SHRIKHANDE_DIFFS = new Set([
    '0,1', '0,3',
    '1,0', '3,0',
    '1,1', '3,3',
  ]);

  function listMarks(rig) {
    const marks = [];
    for (let i = 0; i < 16; i += 1) {
      const row = Math.floor(i / 4);
      const col = i % 4;
      marks.push({
        index: i,
        row,
        col,
        label: rig === 'rook' ? `R${row + 1}·${col + 1}` : `S${row}${col}`,
      });
    }
    return marks;
  }

  function hasWire(rig, a, b) {
    if (a === b || a == null || b == null) return false;
    if (a < 0 || a >= 16 || b < 0 || b >= 16) {
      throw new RangeError(`Mark out of range: ${a}, ${b}`);
    }
    const rA = Math.floor(a / 4);
    const cA = a % 4;
    const rB = Math.floor(b / 4);
    const cB = b % 4;
    if (rig === 'rook') {
      return rA === rB || cA === cB;
    }
    if (rig === 'shrikhande') {
      const dr = (rB - rA + 4) % 4;
      const dc = (cB - cA + 4) % 4;
      return SHRIKHANDE_DIFFS.has(`${dr},${dc}`);
    }
    throw new Error(`Unknown rig: ${rig}`);
  }

  function auditRigs() {
    const result = {};
    for (const rig of ['rook', 'shrikhande']) {
      const edgeCounts = {};
      let totalSubsets = 0;
      for (let a = 0; a < 16; a += 1) {
        for (let b = a + 1; b < 16; b += 1) {
          for (let c = b + 1; c < 16; c += 1) {
            for (let d = c + 1; d < 16; d += 1) {
              totalSubsets += 1;
              const verts = [a, b, c, d];
              let edges = 0;
              for (let i = 0; i < 4; i += 1) {
                for (let j = i + 1; j < 4; j += 1) {
                  if (hasWire(rig, verts[i], verts[j])) edges += 1;
                }
              }
              edgeCounts[edges] = (edgeCounts[edges] || 0) + 1;
            }
          }
        }
      }
      result[rig] = { totalSubsets, edgeCounts };
    }
    return result;
  }

  function emptyStageStatus() {
    return {
      rook: { holder: null, ended: false, landedOnDrummer: false, litWire: null, lastAction: 'idle' },
      shrikhande: { holder: null, ended: false, landedOnDrummer: false, litWire: null, lastAction: 'idle' },
    };
  }

  function createShowState(options = {}) {
    const leadRig = options.leadRig === 'shrikhande' ? 'shrikhande' : 'rook';
    const rivalRig = leadRig === 'rook' ? 'shrikhande' : 'rook';
    const state = {
      leadRig,
      rivalRig,
      castOrder: [],
      marks: {
        rook: { A: null, B: null, C: null, D: null },
        shrikhande: { A: null, B: null, C: null, D: null },
      },
      inPlay: false,
      stageStatus: emptyStageStatus(),
      beats: [],
      cursor: -1,
      lastFitReport: null,
    };

    const initialCast = options.initialCast !== undefined
      ? options.initialCast
      : { A: 0, B: 1, C: 2 };

    for (const p of PUPPETS) {
      if (initialCast[p] !== undefined && initialCast[p] !== null) {
        placePuppet(state, p, initialCast[p]);
      }
    }
    return state;
  }

  function setLeadRig(state, rig) {
    if (state.inPlay) {
      throw new Error('Cannot change leading troupe while the hat is in play.');
    }
    if (rig !== 'rook' && rig !== 'shrikhande') {
      throw new Error(`Unknown rig: ${rig}`);
    }
    state.leadRig = rig;
    state.rivalRig = rig === 'rook' ? 'shrikhande' : 'rook';
    return state;
  }

  function isOccupied(marksMap, markIndex, ignorePuppet) {
    for (const p of PUPPETS) {
      if (p !== ignorePuppet && marksMap[p] === markIndex) return p;
    }
    return null;
  }

  function compareCandidates(a, b) {
    if (a.score !== b.score) return b.score - a.score;
    if (a.topTwoScore !== b.topTwoScore) return b.topTwoScore - a.topTwoScore;
    for (let i = 0; i < Math.max(a.matches.length, b.matches.length); i += 1) {
      const ma = a.matches[i] || 0;
      const mb = b.matches[i] || 0;
      if (ma !== mb) return mb - ma;
    }
    if (a.wasPrevious !== b.wasPrevious) return (b.wasPrevious ? 1 : 0) - (a.wasPrevious ? 1 : 0);
    return a.mark - b.mark;
  }

  function placePuppet(state, puppet, markIndex) {
    if (state.inPlay) {
      throw new Error('Cannot move puppets while the hat is in play.');
    }
    if (!PUPPETS.includes(puppet)) {
      throw new Error(`Unknown puppet: ${puppet}`);
    }
    if (!Number.isInteger(markIndex) || markIndex < 0 || markIndex >= 16) {
      throw new RangeError(`Mark out of range: ${markIndex}`);
    }

    const lead = state.leadRig;
    const rival = state.rivalRig;
    const occupant = isOccupied(state.marks[lead], markIndex, puppet);
    if (occupant) {
      throw new Error(`Mark ${markIndex} on ${lead} is already occupied by ${occupant}.`);
    }

    if (!state.castOrder.includes(puppet)) {
      state.castOrder.push(puppet);
    }

    state.marks[lead][puppet] = markIndex;

    const settled = state.castOrder.filter((p) => p !== puppet);
    const prevRivalMark = state.marks[rival][puppet];

    if (settled.length === 0) {
      const chosen = prevRivalMark !== null ? prevRivalMark : markIndex;
      state.marks[rival][puppet] = chosen;
      state.lastFitReport = {
        puppet,
        rivalRig: rival,
        settled: [],
        matched: 0,
        total: 0,
        exact: true,
        missedAgainst: [],
      };
      return state;
    }

    const occupiedRival = new Set(settled.map((p) => state.marks[rival][p]));
    const candidates = [];

    for (let m = 0; m < 16; m += 1) {
      if (occupiedRival.has(m)) continue;
      const matches = settled.map((other) => {
        const wantWire = hasWire(lead, markIndex, state.marks[lead][other]);
        const gotWire = hasWire(rival, m, state.marks[rival][other]);
        return wantWire === gotWire ? 1 : 0;
      });
      const score = matches.reduce((acc, v) => acc + v, 0);
      const topTwoScore = (matches[0] || 0) + (matches[1] || 0);
      candidates.push({
        mark: m,
        matches,
        score,
        topTwoScore,
        wasPrevious: m === prevRivalMark,
      });
    }

    candidates.sort(compareCandidates);
    const best = candidates[0];
    state.marks[rival][puppet] = best.mark;

    const missedAgainst = [];
    settled.forEach((other, idx) => {
      if (best.matches[idx] === 0) missedAgainst.push(other);
    });

    state.lastFitReport = {
      puppet,
      rivalRig: rival,
      settled: settled.slice(),
      matched: best.score,
      total: settled.length,
      exact: best.score === settled.length,
      missedAgainst,
    };
    return state;
  }

  function removePuppet(state, puppet) {
    if (state.inPlay) {
      throw new Error('Cannot remove puppets while the hat is in play.');
    }
    if (!PUPPETS.includes(puppet)) {
      throw new Error(`Unknown puppet: ${puppet}`);
    }
    state.castOrder = state.castOrder.filter((p) => p !== puppet);
    state.marks.rook[puppet] = null;
    state.marks.shrikhande[puppet] = null;
    state.lastFitReport = null;
    return state;
  }

  function cloneStageStatus(status) {
    return {
      rook: {
        ...status.rook,
        litWire: status.rook.litWire ? { ...status.rook.litWire } : null,
      },
      shrikhande: {
        ...status.shrikhande,
        litWire: status.shrikhande.litWire ? { ...status.shrikhande.litWire } : null,
      },
    };
  }

  function startHatPlay(state, startingPuppet) {
    if (state.castOrder.length < 2) {
      throw new Error('Place at least two puppets before putting the hat in play.');
    }
    const starter = startingPuppet || state.castOrder[0];
    if (!state.castOrder.includes(starter)) {
      throw new Error(`Starting puppet ${starter} is not on stage.`);
    }
    state.inPlay = true;
    state.stageStatus = {
      rook: { holder: starter, ended: false, landedOnDrummer: false, litWire: null, lastAction: 'ready' },
      shrikhande: { holder: starter, ended: false, landedOnDrummer: false, litWire: null, lastAction: 'ready' },
    };
    state.beats = [{
      index: 0,
      kind: 'curtain-up',
      from: null,
      to: starter,
      note: `${PUPPET_META[starter].name} (${starter}) holds the bowler. Both drummers raise their sticks.`,
      outcomes: { rook: 'ready', shrikhande: 'ready' },
      stages: cloneStageStatus(state.stageStatus),
    }];
    state.cursor = 0;
    return state.beats[0];
  }

  function throwHat(state, targetPuppet) {
    if (!state.inPlay) {
      throw new Error('Put the hat in play before throwing.');
    }
    if (!state.castOrder.includes(targetPuppet)) {
      throw new Error(`Target puppet ${targetPuppet} is not on stage.`);
    }
    const activeRigs = ['rook', 'shrikhande'].filter((r) => !state.stageStatus[r].ended);
    if (activeRigs.length === 0) {
      throw new Error('Both stages have finished this take. Re-block or start a new take.');
    }
    const activeHolders = new Set(activeRigs.map((r) => state.stageStatus[r].holder));
    if (activeHolders.size === 1 && activeHolders.has(targetPuppet)) {
      throw new Error(`Puppet ${targetPuppet} already holds the hat.`);
    }

    const fromByRig = {};
    const outcomes = {};
    for (const rig of ['rook', 'shrikhande']) {
      const st = state.stageStatus[rig];
      if (st.ended) {
        st.litWire = null;
        st.lastAction = 'already-ended';
        outcomes[rig] = 'already-ended';
        fromByRig[rig] = null;
        continue;
      }
      const from = st.holder;
      fromByRig[rig] = from;
      if (from === targetPuppet) {
        st.litWire = null;
        st.lastAction = 'held';
        outcomes[rig] = 'held';
        continue;
      }
      const wire = hasWire(rig, state.marks[rig][from], state.marks[rig][targetPuppet]);
      if (wire) {
        st.holder = targetPuppet;
        st.litWire = { from, to: targetPuppet };
        st.lastAction = 'caught';
        outcomes[rig] = 'caught';
      } else {
        st.holder = null;
        st.ended = true;
        st.landedOnDrummer = true;
        st.litWire = null;
        st.lastAction = 'slipped';
        outcomes[rig] = 'slipped';
      }
    }

    const fromLabel = fromByRig[state.leadRig] || activeHolders.values().next().value;
    const repeatPass = state.beats.some((b) => b.kind === 'throw' && b.from === fromLabel && b.to === targetPuppet);
    const knowingLook = repeatPass ? targetPuppet : null;
    const note = describeBeat(fromLabel, targetPuppet, outcomes, knowingLook);
    const beat = {
      index: state.beats.length,
      kind: 'throw',
      from: fromLabel,
      to: targetPuppet,
      knowingLook,
      note,
      outcomes,
      stages: cloneStageStatus(state.stageStatus),
    };
    state.beats.push(beat);
    state.cursor = beat.index;
    return {
      ...beat,
      rook: { ...beat.stages.rook, outcome: outcomes.rook },
      shrikhande: { ...beat.stages.shrikhande, outcome: outcomes.shrikhande },
    };
  }

  function describeBeat(from, to, outcomes, knowingLook) {
    const r = outcomes.rook;
    const s = outcomes.shrikhande;
    const lookSuffix = knowingLook ? ` (${PUPPET_META[knowingLook].name} gives a knowing look.)` : '';
    if (r === 'caught' && s === 'caught') {
      return `${from} → ${to}: clean wire on both stages. Both drummers wait.${lookSuffix}`;
    }
    if (r === 'caught' && s === 'slipped') {
      return `${from} → ${to}: caught on Stage I, slipped on Stage II — bowler over the drummer's eyes!`;
    }
    if (r === 'slipped' && s === 'caught') {
      return `${from} → ${to}: slipped on Stage I — bowler over the drummer's eyes! Stage II catches cleanly.`;
    }
    if (r === 'slipped' && s === 'slipped') {
      return `${from} → ${to}: no wire on either stage — both drummers wear the hat.`;
    }
    if (r === 'already-ended' && s === 'caught') {
      return `${from} → ${to}: Stage II catches cleanly while Stage I's drummer stays under his hat.`;
    }
    if (r === 'caught' && s === 'already-ended') {
      return `${from} → ${to}: Stage I catches cleanly while Stage II's drummer stays under his hat.`;
    }
    return `${from} → ${to}: take ends.`;
  }

  function holdBeat(state, customNote) {
    if (!state.inPlay) {
      throw new Error('Put the hat in play before holding a beat.');
    }
    for (const rig of ['rook', 'shrikhande']) {
      const st = state.stageStatus[rig];
      st.litWire = null;
      if (!st.ended) st.lastAction = 'hold';
    }
    const beat = {
      index: state.beats.length,
      kind: 'hold',
      from: null,
      to: null,
      note: customNote || 'Hold a beat — sticks raised in the pit.',
      outcomes: {
        rook: state.stageStatus.rook.ended ? 'already-ended' : 'hold',
        shrikhande: state.stageStatus.shrikhande.ended ? 'already-ended' : 'hold',
      },
      stages: cloneStageStatus(state.stageStatus),
    };
    state.beats.push(beat);
    state.cursor = beat.index;
    return beat;
  }

  function stepTake(state, index) {
    if (state.beats.length === 0) return null;
    const clamped = Math.max(0, Math.min(state.beats.length - 1, index));
    state.cursor = clamped;
    const beat = state.beats[clamped];
    return {
      index: clamped,
      total: state.beats.length,
      kind: beat.kind,
      from: beat.from,
      to: beat.to,
      knowingLook: beat.knowingLook || null,
      note: beat.note,
      outcomes: { ...beat.outcomes },
      rook: { ...beat.stages.rook, litWire: beat.stages.rook.litWire ? { ...beat.stages.rook.litWire } : null },
      shrikhande: { ...beat.stages.shrikhande, litWire: beat.stages.shrikhande.litWire ? { ...beat.stages.shrikhande.litWire } : null },
    };
  }

  function reblockCast(state) {
    state.inPlay = false;
    state.stageStatus = emptyStageStatus();
    state.beats = [];
    state.cursor = -1;
    return state;
  }

  function pairSummary(state) {
    const seated = state.castOrder.slice();
    const pairs = [];
    for (let i = 0; i < seated.length; i += 1) {
      for (let j = i + 1; j < seated.length; j += 1) {
        const p1 = seated[i];
        const p2 = seated[j];
        const rookWire = hasWire('rook', state.marks.rook[p1], state.marks.rook[p2]);
        const shrikhandeWire = hasWire('shrikhande', state.marks.shrikhande[p1], state.marks.shrikhande[p2]);
        pairs.push({
          pair: `${p1}–${p2}`,
          p1,
          p2,
          rook: rookWire,
          shrikhande: shrikhandeWire,
          matches: rookWire === shrikhandeWire,
        });
      }
    }
    return pairs;
  }

  return {
    PUPPETS,
    PUPPET_META,
    listMarks,
    hasWire,
    auditRigs,
    createShowState,
    setLeadRig,
    placePuppet,
    removePuppet,
    startHatPlay,
    throwHat,
    holdBeat,
    stepTake,
    reblockCast,
    pairSummary,
  };
});
