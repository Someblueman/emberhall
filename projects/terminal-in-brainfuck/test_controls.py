"""Control contract checks against real generated Brainfuck and hand results."""
import unittest

from test_terminal import bf_frames, row_text
import model


class ControlTests(unittest.TestCase):
    def check(self, data):
        frames = bf_frames(data)
        expected = model.ref_frames(data)
        self.assertEqual(len(frames), len(expected))
        for i, (actual, ref) in enumerate(zip(frames, expected)):
            self.assertEqual(actual, ref, f"frame {i}, prefix {data[:i]!r}")
        return frames[-1]

    def test_backspace_never_erases_and_tab_never_writes(self):
        frame = self.check(b"ABC\bX\t!")
        self.assertEqual(row_text(frame, 0)[:9], "ABX     !")
        self.assertEqual(frame[1:3], (0, 9))
        frame = self.check(b"\bX\x1b[40G")  # G is unsupported, consumes its digits
        self.assertEqual(frame[1:3], (0, 1))
        frame = self.check(b"\x1b[1;39H\tX")
        self.assertEqual(row_text(frame, 0)[-1], "X")
        self.assertEqual(frame[1:3], (1, 0))  # X, not tab, triggers wrap

    def test_cursor_defaults_bounds_and_no_erase(self):
        frame = self.check(b"ABCDE\x1b[2DX\x1b[0D!")
        self.assertEqual(row_text(frame, 0)[:5], "ABC!E")
        self.assertEqual(frame[1:3], (0, 4))
        for sequence, cursor in ((b"\x1b[999999B\x1b[999C", (23, 39)),
                                 (b"\x1b[99A\x1b[99D", (0, 0)),
                                 (b"\x1b[0;0H", (0, 0)),
                                 (b"\x1b[;5f", (0, 4)),
                                 (b"\x1b[99;9999H", (23, 39))):
            with self.subTest(sequence=sequence):
                self.assertEqual(self.check(sequence)[1:3], cursor)

    def test_cursor_moves_through_rotated_screen_without_scrolling(self):
        data = b"".join(b"r%02d\r\n" % n for n in range(26))
        frame = self.check(data + b"\x1b[1;1HX\x1b[B!\x1b[A?")
        self.assertEqual(row_text(frame, 0)[:3], "X0?")
        self.assertEqual(row_text(frame, 1)[:3], "r!4")
        self.assertEqual(frame[1:3], (0, 3))

    def test_all_line_erase_modes_include_cursor_and_keep_position(self):
        for mode, expected in ((0, "AB   "), (1, "   DE"), (2, "     ")):
            with self.subTest(mode=mode):
                frame = self.check(b"ABCDE\x1b[1;3H\x1b[" + str(mode).encode() + b"K")
                self.assertEqual(row_text(frame, 0)[:5], expected)
                self.assertEqual(frame[1:3], (0, 2))

    def test_all_display_erase_modes_after_scroll(self):
        data = b"".join(b"%02d-ABCDE\r\n" % n for n in range(26))
        base = bf_frames(data)[-1]
        for mode in (0, 1, 2):
            with self.subTest(mode=mode):
                frame = self.check(data + b"\x1b[3;4H\x1b[" + str(mode).encode() + b"J")
                split = 2 * 40 + 3
                before = base[0]
                expected = (before[:split] + " " * (960 - split) if mode == 0 else
                            " " * (split + 1) + before[split + 1:] if mode == 1 else " " * 960)
                self.assertEqual(frame, (expected, 2, 3, [7] * 960))

    def test_erase_does_not_reset_scroll_window_or_subsequent_print(self):
        data = b"\n" * 28 + b"Z\x1b[2JY\x1b[1;1HX"
        frame = self.check(data)
        self.assertEqual(row_text(frame, 0)[:2], "X ")
        self.assertEqual(row_text(frame, 23)[:3], " Y ")
        self.assertEqual(frame[1:3], (0, 1))

    def test_recovery_and_unsupported_commands(self):
        cases = [b"A\x1b[1;2;3HX", b"A\x1b[?25hB", b"A\x1b[1\x01XB",
                 b"A\x1b[99\x1b[D!", b"A\x1b[99\x18B", b"A\x1b[\x1aB",
                 b"A\x1bzB", b"A\x1b[2;3KB", b"A\x1b[9KB",
                 b"A\x1b[31mB", b"A\x1b[2J\x00ignored", b"A\x1b[12;"]
        for data in cases:
            with self.subTest(data=data):
                self.check(data)
        self.assertEqual(row_text(bf_frames(cases[0])[-1], 0)[:2], "AX")
        self.assertEqual(row_text(bf_frames(cases[1])[-1], 0)[:2], "AB")
        self.assertEqual(row_text(bf_frames(cases[3])[-1], 0)[:2], "! ")


if __name__ == '__main__':
    unittest.main()
