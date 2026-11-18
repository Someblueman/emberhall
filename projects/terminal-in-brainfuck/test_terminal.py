"""Differential tests: replay terminal.bf in bf.py's ordinary
interpreter and compare every emitted frame with model.py, plus a few
hand-derived expectations that share no code with either.
"""

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bf
import build_terminal
import model

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "terminal.bf")) as f:
    SOURCE = f.read()
ROWS, COLS = model.ROWS, model.COLS


def bf_frames(data):
    out = bf.run_bf(SOURCE, data)
    frames = []
    i = 0
    while i < len(out):
        assert out[i] == 0xFF, f"frame does not start with 0xFF at {i}"
        end = i + 1 + ROWS * COLS
        cells = out[i + 1:end].decode("ascii")
        attributes = list(out[end:end + ROWS * COLS])
        end += ROWS * COLS
        row, col = out[end], out[end + 1]
        assert out[end + 2] == 0xFE, "frame does not end with 0xFE"
        frames.append((cells, row, col, attributes))
        i = end + 3
    return frames


def row_text(frame, r):
    return frame[0][r * COLS:(r + 1) * COLS]


class TerminalTests(unittest.TestCase):
    def check(self, data):
        self.assertEqual(bf_frames(data), model.ref_frames(data))

    def test_generated_files_are_current(self):
        fresh = build_terminal.build()
        self.assertEqual(SOURCE.strip(), fresh)
        with open(os.path.join(HERE, "program.js")) as f:
            program_js = f.read()
        self.assertIn("const BF_PROGRAM = `" + fresh + "`;", program_js)

    def test_plain_text(self):
        self.check(b"HELLO, WORLD")
        last = bf_frames(b"HELLO, WORLD")[-1]
        self.assertTrue(row_text(last, 0).startswith("HELLO, WORLD"))
        self.assertEqual(last[1:3], (0, 12))

    def test_carriage_return_overwrites_without_erasing(self):
        self.check(b"HELLO\rbye")
        last = bf_frames(b"HELLO\rbye")[-1]
        self.assertTrue(row_text(last, 0).startswith("byeLO"))
        self.assertEqual(last[1:3], (0, 3))

    def test_line_feed_keeps_the_column(self):
        self.check(b"AB\nCD")
        last = bf_frames(b"AB\nCD")[-1]
        self.assertTrue(row_text(last, 1).startswith("  CD"))
        self.assertEqual(last[1:3], (1, 4))

    def test_wrap_at_the_row_end(self):
        data = b"A" * COLS + b"B"
        self.check(data)
        last = bf_frames(data)[-1]
        self.assertEqual(row_text(last, 0), "A" * COLS)
        self.assertTrue(row_text(last, 1).startswith("B"))
        self.assertEqual(last[1:3], (1, 1))

    def test_bottom_row_scrolls(self):
        data = b"".join(b"L%02d\r\n" % i for i in range(25))
        self.check(data)
        last = bf_frames(data)[-1]
        # Each labelled line returns to column 0 then feeds.  The feed
        # after L23 scrolls once and the one after L24 scrolls again,
        # so L02 is on top and the fresh bottom row is blank.
        self.assertTrue(row_text(last, 0).startswith("L02"))
        self.assertTrue(row_text(last, 22).startswith("L24"))
        self.assertEqual(row_text(last, 23).strip(), "")

    def test_wrap_into_scroll_at_the_last_cell(self):
        # 23 feeds reach the bottom row, 40 letters fill it and wrap
        # into a scroll, so z lands at the start of the fresh bottom.
        data = b"\n" * 23 + b"y" * COLS + b"z"
        self.check(data)
        last = bf_frames(data)[-1]
        self.assertEqual(row_text(last, 22), "y" * COLS)
        self.assertTrue(row_text(last, 23).startswith("z"))

    def test_unsupported_bytes_are_ignored_but_framed(self):
        data = b"A\x01\x07\x0b\x0c\x7fB"
        self.check(data)
        frames = bf_frames(data)
        self.assertEqual(len(frames), len(data) + 1)
        last = frames[-1]
        self.assertTrue(row_text(last, 0).startswith("AB"))
        self.assertEqual(last[1:3], (0, 2))

    def test_seeded_random_stream_matches_the_reference(self):
        rng = random.Random(20261118)
        # Byte 0 is end-of-input for the Brainfuck program, not a
        # screen byte, so it stays out of the random alphabet.
        alphabet = (b"abcXYZ 09.,!" * 6 + b"\r" * 4 + b"\n" * 4
                    + b"\x07\x1b\x7f")
        data = bytes(rng.choice(alphabet) for _ in range(400))
        self.check(data)

    def test_empty_stream_emits_the_initial_frame(self):
        frames = bf_frames(b"")
        self.assertEqual(frames, [(" " * (ROWS * COLS), 0, 0, [7] * (ROWS * COLS))])

    def test_zero_ends_input_without_emitting_an_extra_frame(self):
        self.check(b"A\x00B\n")
        self.assertEqual(bf_frames(b"A\x00B"), bf_frames(b"A"))

    def test_every_nonzero_byte_and_repeated_ring_rotation(self):
        self.check(bytes(range(1, 256)))
        self.check(b"".join(b"row%02d\r\n" % n for n in range(53)))


if __name__ == "__main__":
    unittest.main()
