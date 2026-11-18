"""Replay the real browser machine against the independent display model.

Node provides no DOM here; it executes the exact VM used by the page. Real
page interaction is checked separately through the house page viewer.
"""
import json
from pathlib import Path
import subprocess
import unittest

import model

HERE = Path(__file__).parent
RUN = r"""
const fs = require('node:fs');
const {BrainfuckMachine} = require('./vm.js');
const code = fs.readFileSync('terminal.bf', 'utf8');
const streams = JSON.parse(fs.readFileSync(0, 'utf8'));
const results = [];
for (const data of streams) {
  const frames = []; let partial = []; let vm;
  vm = new BrainfuckMachine(code, b => {
    partial.push(b);
    if (partial.length === 964) {
      if (partial[0] !== 255 || partial[963] !== 254) throw Error('framing');
      frames.push([String.fromCharCode(...partial.slice(1, 961)), partial[961], partial[962]]);
      // At the final output instruction, visible cursor equals tape state.
      if (vm.ptr !== 6 || vm.tape[2] !== partial[962] || vm.tape[4] !== partial[961]) throw Error('tape/frame mismatch');
      partial = [];
    }
  });
  // Queue each byte only after an actual comma wait. Alternate literal and
  // counted execution at boundaries to catch partial-run stepping mistakes.
  let next = 0, loops = 0;
  while (!vm.halted) {
    vm.step();
    vm.run(10000);
    if (vm.waiting) {
      if (next < data.length) vm.feed([data[next++]]);
      else vm.end();
    }
    if (++loops > 20000) throw Error('run budget exceeded');
  }
  if (partial.length) throw Error('partial final frame');
  results.push(frames);
}
process.stdout.write(JSON.stringify(results));
"""


class BrowserMachineTests(unittest.TestCase):
    def test_chunked_browser_execution_matches_every_reference_frame(self):
        streams = [b"", b"A\rB\nC", b"A" * 40 + b"B", b"\n" * 23 + b"z" * 40,
                   b"A\0ignored", bytes(range(1, 256)),
                   b"".join(b"r%02d\r\n" % n for n in range(50))]
        result = subprocess.run(
            ["node", "-e", RUN], cwd=HERE, input=json.dumps([list(s) for s in streams]),
            text=True, capture_output=True, check=True, timeout=40)
        for data, frames in zip(streams, json.loads(result.stdout), strict=True):
            with self.subTest(data=data[:30]):
                self.assertEqual(frames, [list(frame) for frame in model.ref_frames(data)])


if __name__ == "__main__":
    unittest.main()
