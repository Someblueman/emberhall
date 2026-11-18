"""Follow the caught cell from sea floor to boat in the ordinary interpreter."""
import json
from pathlib import Path
import subprocess
import unittest

from test_terminal import bf_frames, row_text

HERE = Path(__file__).parent


class BellDiveTests(unittest.TestCase):
    def test_the_bell_hauls_the_original_editable_mark(self):
        script = """
          const score = require('./bell-dive.js');
          const {encodeStream} = require('./input.js');
          console.log(JSON.stringify({
            catchBytes: encodeStream(score.catchAtBottom),
            full: encodeStream(score.full),
            edited: encodeStream(score.full.replace('*', '?'))
          }));
        """
        run = subprocess.run(["node", "-e", script], text=True, cwd=HERE,
                             capture_output=True, check=True)
        score = json.loads(run.stdout)
        caught = bytes(score["catchBytes"])
        for key, mark in (("full", "*"), ("edited", "?")):
            with self.subTest(mark=mark):
                data = bytes(score[key])
                self.assertEqual(data.count(ord(mark)), 1)
                self.assertEqual(data.count(b"LEAVE THE LIGHT ON"), 1)
                self.assertEqual(data[:len(caught)], caught.replace(b"*", mark.encode()))
                frames = bf_frames(data)
                reply = "(" + mark + ")  LEAVE THE LIGHT ON"
                self.assertEqual(row_text(frames[len(caught)], 9)[10:].rstrip(), reply)
                haul = data.index(b"\x1b[24;1H", len(caught)) + len(b"\x1b[24;1H")
                self.assertEqual(data[haul:haul + 6], b"\n" * 6)
                for lift in range(1, 7):
                    self.assertEqual(row_text(frames[haul + lift], 9 - lift)[10:].rstrip(), reply)
                self.assertEqual(row_text(frames[-1], 3)[10:].rstrip(), reply)
                self.assertIn("REPLY RECEIVED", row_text(frames[-1], 5))


if __name__ == "__main__":
    unittest.main()
