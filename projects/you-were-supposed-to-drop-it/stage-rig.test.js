'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');

const rig = require('./stage-rig.js');

test('both rigs have 16 marks, degree 6, lambda 2, and mu 2 (srg(16, 6, 2, 2))', () => {
  for (const name of ['rook', 'shrikhande']) {
    const marks = rig.listMarks(name);
    assert.equal(marks.length, 16);
    for (let a = 0; a < 16; a += 1) {
      assert.equal(rig.hasWire(name, a, a), false, `${name} must have no self-loop at ${a}`);
      let deg = 0;
      for (let b = 0; b < 16; b += 1) {
        assert.equal(rig.hasWire(name, a, b), rig.hasWire(name, b, a), `${name} symmetry (${a},${b})`);
        if (rig.hasWire(name, a, b)) deg += 1;
      }
      assert.equal(deg, 6, `${name} degree at ${a}`);
    }
    for (let a = 0; a < 16; a += 1) {
      for (let b = a + 1; b < 16; b += 1) {
        let common = 0;
        for (let c = 0; c < 16; c += 1) {
          if (rig.hasWire(name, a, c) && rig.hasWire(name, b, c)) common += 1;
        }
        assert.equal(common, 2, `${name} common neighbors for (${a},${b})`);
      }
    }
  }
});

test('all 1,820 four-mark sets give 8x6/0x5 on rook and 48x5/0x6 on shrikhande', () => {
  const audit = rig.auditRigs();
  assert.equal(audit.rook.totalSubsets, 1820);
  assert.equal(audit.shrikhande.totalSubsets, 1820);
  assert.equal(audit.rook.edgeCounts[6] || 0, 8);
  assert.equal(audit.rook.edgeCounts[5] || 0, 0);
  assert.equal(audit.shrikhande.edgeCounts[5] || 0, 48);
  assert.equal(audit.shrikhande.edgeCounts[6] || 0, 0);
});

test('up to three puppets: moving one leaves others planted and rival matches all pairs', () => {
  for (const lead of ['rook', 'shrikhande']) {
    const state = rig.createShowState({ leadRig: lead, initialCast: {} });
    rig.placePuppet(state, 'A', 0);
    rig.placePuppet(state, 'B', 1);
    rig.placePuppet(state, 'C', 5);
    assert.deepEqual(state.castOrder, ['A', 'B', 'C']);
    assertPairsMatch(state);

    const plantedA = state.marks[state.rivalRig].A;
    const plantedB = state.marks[state.rivalRig].B;
    rig.placePuppet(state, 'C', 15);
    assert.equal(state.marks[state.rivalRig].A, plantedA, 'A stayed planted when C moved');
    assert.equal(state.marks[state.rivalRig].B, plantedB, 'B stayed planted when C moved');
    assertPairsMatch(state);

    const plantedA2 = state.marks[state.rivalRig].A;
    const plantedC2 = state.marks[state.rivalRig].C;
    rig.placePuppet(state, 'B', 7);
    assert.equal(state.marks[state.rivalRig].A, plantedA2, 'A stayed planted when B moved');
    assert.equal(state.marks[state.rivalRig].C, plantedC2, 'C stayed planted when B moved');
    assertPairsMatch(state);
  }
});

test('on four puppets, rival keeps settled puppets planted and ties favour two longest-serving', () => {
  // Shrikhande leads: place A=(0,0)=0, B=(0,1)=1 (wire), C=(1,0)=4 (wire to A, gap to B? Check!).
  // Wait: in Z4xZ4, (0,1) and (1,0) differ by (3,1) -> NOT in difference set, so B-C is a gap!
  // Let's seat A=0, B=1, C=4 on Shrikhande, then bring D=(1,1)=5:
  // On Shrikhande, D=(1,1) has wires to A=(0,0) [diff (1,1)], B=(0,1) [diff (1,0)], C=(1,0) [diff (0,1)].
  // That is 3 wires! On Rook, A', B', C' have A'-B' wire, A'-C' wire, B'-C' gap (L-shape).
  // Any unoccupied mark on Rook can match at most 2 of 3 (cannot match all 3 because Rook has 0 K4-e? Wait: K4-e has 5 wires!).
  // Wait: the corner of the L-shape on Rook is the 4th mark of the 2x2 square, which joins B' and C' (NOT A').
  // Another mark in A''s row joins A' and B' (or A' and C'), matching 2 of 3!
  // Since A and B are the two longest-serving cast members (castOrder = ['A', 'B', 'C']),
  // the tie between matching (A, B), (A, C), and (B, C) MUST favour (A, B)!
  const state = rig.createShowState({ leadRig: 'shrikhande', initialCast: {} });
  rig.placePuppet(state, 'A', 0);
  rig.placePuppet(state, 'B', 1);
  rig.placePuppet(state, 'C', 4);
  const settledRival = { ...state.marks.rook };

  rig.placePuppet(state, 'D', 5);
  assert.equal(state.marks.rook.A, settledRival.A);
  assert.equal(state.marks.rook.B, settledRival.B);
  assert.equal(state.marks.rook.C, settledRival.C);

  const dRook = state.marks.rook.D;
  assert.equal(rig.hasWire('rook', dRook, settledRival.A), true, 'tie favours longest-serving A');
  assert.equal(rig.hasWire('rook', dRook, settledRival.B), true, 'tie favours second longest-serving B');
  assert.equal(rig.hasWire('rook', dRook, settledRival.C), false, 'only C wire is dropped on Rook');
});

test('fourth entrance does not always trigger a drop when configuration fits both rigs', () => {
  // Seat A, B, C, D in a simple 4-cycle or sparse set that exists identically on both rigs.
  // On Rook: 0=(0,0), 1=(0,1), 5=(1,1), 4=(1,0) -> wires (0,1), (1,5), (5,4), (4,0), gaps (0,5), (1,4).
  const state = rig.createShowState({ leadRig: 'rook', initialCast: {} });
  rig.placePuppet(state, 'A', 0);
  rig.placePuppet(state, 'B', 1);
  rig.placePuppet(state, 'C', 5);
  rig.placePuppet(state, 'D', 4);
  assertPairsMatch(state);

  rig.startHatPlay(state, 'A');
  rig.throwHat(state, 'B');
  rig.throwHat(state, 'C');
  rig.throwHat(state, 'D');
  rig.throwHat(state, 'A');
  assert.equal(state.stageStatus.rook.ended, false);
  assert.equal(state.stageStatus.shrikhande.ended, false);
});

test('first_step rook K4 sequence: first 6 throws work on both stages, 7th slips on shrikhande only', () => {
  const state = rig.createShowState({ leadRig: 'rook', initialCast: {} });
  rig.placePuppet(state, 'A', 0); // (0,0)
  rig.placePuppet(state, 'B', 1); // (0,1)
  rig.placePuppet(state, 'C', 2); // (0,2) - common neighbor of A and B
  rig.placePuppet(state, 'D', 3); // (0,3) - remaining common neighbor of A and B

  rig.startHatPlay(state, 'A');
  // Throws: A -> B -> C -> A -> D -> B -> C -> D
  for (const target of ['B', 'C', 'A', 'D', 'B', 'C']) {
    const beat = rig.throwHat(state, target);
    assert.equal(beat.rook.outcome, 'caught', `rook caught throw to ${target}`);
    assert.equal(beat.shrikhande.outcome, 'caught', `shrikhande caught throw to ${target}`);
  }
  rig.holdBeat(state);
  const finalBeat = rig.throwHat(state, 'D');
  assert.equal(finalBeat.rook.outcome, 'caught');
  assert.equal(finalBeat.shrikhande.outcome, 'slipped');
  assert.equal(state.stageStatus.rook.ended, false);
  assert.equal(state.stageStatus.shrikhande.ended, true);
  assert.equal(state.stageStatus.shrikhande.landedOnDrummer, true);

  // Subsequent throw on already-ended shrikhande does not un-end it or throw on shrikhande
  const afterBeat = rig.throwHat(state, 'A');
  assert.equal(afterBeat.rook.outcome, 'caught');
  assert.equal(afterBeat.shrikhande.outcome, 'already-ended');

  // Cannot move puppets while hat is in play
  assert.throws(() => rig.placePuppet(state, 'D', 7), /hat is in play/i);

  // Stills match every recorded beat faithfully
  const still0 = rig.stepTake(state, 0);
  assert.equal(still0.rook.holder, 'A');
  assert.equal(still0.shrikhande.holder, 'A');
  const stillSlip = rig.stepTake(state, finalBeat.index);
  assert.equal(stillSlip.rook.holder, 'D');
  assert.equal(stillSlip.rook.litWire.from, 'C');
  assert.equal(stillSlip.rook.litWire.to, 'D');
  assert.equal(stillSlip.shrikhande.landedOnDrummer, true);
  assert.equal(stillSlip.shrikhande.litWire, null);
});

test('cannot throw hat over an absent wire on the lead stage without dropping it there too', () => {
  const state = rig.createShowState({ leadRig: 'rook', initialCast: {} });
  rig.placePuppet(state, 'A', 0); // (0,0)
  rig.placePuppet(state, 'B', 5); // (1,1) -> no wire between 0 and 5 on Rook!
  rig.startHatPlay(state, 'A');
  const beat = rig.throwHat(state, 'B');
  assert.equal(beat.rook.outcome, 'slipped');
  assert.equal(beat.shrikhande.outcome, 'slipped');
  assert.equal(state.stageStatus.rook.ended, true);
  assert.equal(state.stageStatus.shrikhande.ended, true);
});

test('exhaustive: every 3-puppet placement on either stage is exactly matched while keeping others planted', () => {
  for (const lead of ['rook', 'shrikhande']) {
    for (let a = 0; a < 16; a += 1) {
      for (let b = 0; b < 16; b += 1) {
        if (b === a) continue;
        for (let c = 0; c < 16; c += 1) {
          if (c === a || c === b) continue;
          const state = rig.createShowState({ leadRig: lead, initialCast: {} });
          rig.placePuppet(state, 'A', a);
          rig.placePuppet(state, 'B', b);
          rig.placePuppet(state, 'C', c);
          assertPairsMatch(state);
        }
      }
    }
  }
});

test('shrikhande lead: 5-wire cast drops hat on rook drummer while shrikhande catches, and can avoid drop', () => {
  const state = rig.createShowState({ leadRig: 'shrikhande', initialCast: {} });
  rig.placePuppet(state, 'A', 0);
  rig.placePuppet(state, 'B', 1);
  rig.placePuppet(state, 'C', 4);
  rig.placePuppet(state, 'D', 5);
  // On Shrikhande: D=5 has wires to A, B, and C. On Rook: D' matched A' and B', dropped C'-D'.
  rig.startHatPlay(state, 'C');
  const safeBeat = rig.throwHat(state, 'A');
  assert.equal(safeBeat.shrikhande.outcome, 'caught');
  assert.equal(safeBeat.rook.outcome, 'caught');

  // Avoiding the miss: throw A -> B -> D -> A stays on matched wires!
  assert.equal(rig.throwHat(state, 'B').rook.outcome, 'caught');
  assert.equal(rig.throwHat(state, 'D').rook.outcome, 'caught');
  assert.equal(rig.throwHat(state, 'A').rook.outcome, 'caught');

  // Now reblock and throw C -> D directly: Shrikhande catches, Rook slips onto drummer!
  rig.reblockCast(state);
  rig.startHatPlay(state, 'C');
  const slipBeat = rig.throwHat(state, 'D');
  assert.equal(slipBeat.shrikhande.outcome, 'caught');
  assert.equal(slipBeat.rook.outcome, 'slipped');
  assert.equal(state.stageStatus.rook.landedOnDrummer, true);
  assert.equal(state.stageStatus.shrikhande.ended, false);
});

function assertPairsMatch(state) {
  const seated = state.castOrder;
  for (let i = 0; i < seated.length; i += 1) {
    for (let j = i + 1; j < seated.length; j += 1) {
      const p1 = seated[i];
      const p2 = seated[j];
      const wLead = rig.hasWire(state.leadRig, state.marks[state.leadRig][p1], state.marks[state.leadRig][p2]);
      const wRival = rig.hasWire(state.rivalRig, state.marks[state.rivalRig][p1], state.marks[state.rivalRig][p2]);
      assert.equal(wRival, wLead, `wire mismatch between ${p1} and ${p2}`);
    }
  }
}
