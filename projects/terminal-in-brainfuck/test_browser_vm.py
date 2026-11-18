"""Replay the real browser machine against the independent display model.

Node provides no DOM here; it executes the exact VM used by the page. Real
page interaction is checked separately through the house page viewer.
"""
import json
from pathlib import Path
import random
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
for (const chunks of streams) {
  const frames = []; let partial = []; let vm;
  vm = new BrainfuckMachine(code, b => {
    partial.push(b);
    if (partial.length === 964) {
      if (partial[0] !== 255 || partial[963] !== 254) throw Error('framing');
      frames.push([String.fromCharCode(...partial.slice(1, 961)), partial[961], partial[962],
                   Array.from(vm.tape.slice(38, 42))]);
      // At the final output instruction, visible cursor equals tape state.
      if (vm.ptr !== 6 || vm.tape[2] !== partial[962] || vm.tape[4] !== partial[961]) throw Error('tape/frame mismatch');
      partial = [];
    }
  });
  // Queue each chunk only after an actual comma wait. Alternate literal and
  // counted execution at boundaries to catch partial-run stepping mistakes.
  let next = 0, loops = 0;
  while (!vm.halted) {
    vm.step();
    vm.run(10000);
    if (vm.waiting) {
      if (next < chunks.length) vm.feed(chunks[next++]);
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
    def compare_chunkings(self, cases):
        result = subprocess.run(
            ["node", "-e", RUN], cwd=HERE,
            input=json.dumps([[list(chunk) for chunk in chunks] for chunks in cases]),
            text=True, capture_output=True, check=True, timeout=60)
        for chunks, frames in zip(cases, json.loads(result.stdout), strict=True):
            term = model.RefTerminal()
            expected = [[*term.frame(), list(term.parser_state())]]
            for byte in b"".join(chunks):
                if byte == 0:
                    break
                expected.append([*term.feed(byte), list(term.parser_state())])
            with self.subTest(stream=b"".join(chunks)[:40], chunk_lengths=list(map(len, chunks))[:12]):
                self.assertEqual(len(frames), len(expected))
                for index, (actual, reference) in enumerate(zip(frames, expected)):
                    self.assertEqual(actual, reference, f"frame {index}")

    def test_chunked_browser_execution_matches_every_reference_frame(self):
        streams = [b"", b"A\rB\nC", b"A" * 40 + b"B", b"\n" * 23 + b"z" * 40,
                   b"A\0ignored", bytes(range(1, 256)),
                   b"".join(b"r%02d\r\n" % n for n in range(50))]
        self.compare_chunkings([[bytes([byte]) for byte in data] for data in streams])

    def test_every_split_of_cursor_erase_and_interrupted_sequences(self):
        streams = [b"abc\x1b[2DX", b"xy\x1b[12;39HZ", b"abc\r\x1b[0K",
                   b"x\x1b[2J", b"x\x1b[1;2;3Hq", b"\x1b[999\x1b[;f!",
                   b"\x1b[9;\x00ignored"]
        cases = [[data[:cut], data[cut:]] for data in streams for cut in range(len(data) + 1)]
        self.compare_chunkings(cases)

    def test_seeded_mixed_controls_with_irregular_input_chunks(self):
        rng = random.Random(18640)
        tokens = [b"text", b"\r", b"\n", b"\t", b"\x08", b"\x1b", b"\xff", b"\x18"]
        cases = []
        for _ in range(5):
            data = bytearray()
            for _ in range(18):
                if rng.randrange(2):
                    data.extend(rng.choice(tokens))
                else:
                    params = rng.choice([b"", b";", b"0", b"2", b"9;40", b"12345", b"1;2;3", b"?"])
                    data.extend(b"\x1b[" + params + bytes([rng.choice(b"ABCDHfJKm")]))
            chunks = []
            while data:
                width = rng.randint(1, 9)
                chunks.append(bytes(data[:width]))
                del data[:width]
            cases.append(chunks)
        self.compare_chunkings(cases)


if __name__ == "__main__":
    unittest.main()
