"use strict";

// A score of input bytes for Bell No. 3. It is written in the stream editor's
// notation. Playback, erasure and the lift itself all happen on the tape.
const BELL_DIVE = (() => {
  const at = (row, col) => "\\x1b[" + row + ";" + col + "H";
  const surface = at(2, 7) + "___/|___" + at(3, 1) + "~~~~~~\\\\_____/~~~~~~~~~~~~~~~~";
  const station = "DEAD WATER  /  SOUNDING NO. 3";
  const cargo = at(10, 12) + "*";
  const reef = at(11, 2) + "___/^^^/____/^^/___/^^^/___";
  const opening = station + surface + cargo + reef + at(4, 11) + "( )";

  let descent = "";
  for (let row = 4; row < 10; row++) {
    descent += at(row, 11) + " | " + at(row + 1, 11);
    // At the bottom, skip over the cargo so the jaws close around its original cell.
    descent += row === 9 ? "(\\x1b[C)" : "( )";
  }
  const catchAtBottom = opening + descent + "  LEAVE THE LIGHT ON";

  // Six line feeds at the bottom rotate the caught row up to the boat.
  // The returning cargo and the reply are never typed a second time.
  const haul = at(24, 1) + "\\n".repeat(6);
  const landing = at(5, 1) + "\\x1b[2K" + at(1, 1) + station + surface
    + at(6, 1) + "LOG ENTRY 03  /  REPLY RECEIVED.";
  return {catchAtBottom, full: catchAtBottom + haul + landing};
})();

if (typeof module !== "undefined") module.exports = BELL_DIVE;
