"""Reference model of the frozen device contract, in display terms.

The Brainfuck program keeps a ring of physical rows; this model keeps
the displayed grid directly.  The tests require the two to produce
identical frames, so a shared misunderstanding would have to be written
twice in two different shapes to pass.
"""

ROWS = 24
COLS = 40


class RefTerminal:
    def __init__(self):
        self.grid = [[" "] * COLS for _ in range(ROWS)]
        self.row = 0
        self.col = 0
        self.state = "text"
        self.params = [0]

    def frame(self):
        cells = "".join("".join(r) for r in self.grid)
        return (cells, self.row, self.col)

    def _line_feed(self):
        if self.row == ROWS - 1:
            self.grid.pop(0)
            self.grid.append([" "] * COLS)
        else:
            self.row += 1

    def parser_state(self):
        states = {"text": 0, "escape": 1, "csi": 2, "discard": 3}
        return (states[self.state], self.params[0],
                self.params[1] if len(self.params) == 2 else 0,
                int(len(self.params) == 2))

    def _reset_parser(self, state="text"):
        self.state, self.params = state, [0]

    def _command(self, final):
        first = self.params[0]
        count = first or 1
        if final in (72, 102):
            self.row = min(ROWS, count) - 1
            self.col = min(COLS, (self.params[1] if len(self.params) == 2 else 0) or 1) - 1
        elif len(self.params) == 1:
            if final == 65:
                self.row = max(0, self.row - count)
            elif final == 66:
                self.row = min(ROWS - 1, self.row + count)
            elif final == 67:
                self.col = min(COLS - 1, self.col + count)
            elif final == 68:
                self.col = max(0, self.col - count)
            elif final in (74, 75) and first in (0, 1, 2):
                # Select cells in display order, without physical-ring logic.
                cursor = self.row * COLS + self.col
                for row in range(ROWS):
                    for col in range(COLS):
                        if final == 75 and row != self.row:
                            continue
                        offset = row * COLS + col
                        if first == 2 or (first == 0 and offset >= cursor) or (first == 1 and offset <= cursor):
                            self.grid[row][col] = " "
        self._reset_parser()

    def feed(self, byte):
        if byte == 27:
            self._reset_parser("escape")
        elif byte in (24, 26):
            self._reset_parser()
        elif self.state == "escape":
            self._reset_parser("csi" if byte == 91 else "text")
        elif self.state == "discard":
            if 64 <= byte <= 126:
                self._reset_parser()
        elif self.state == "csi":
            if 48 <= byte <= 57:
                self.params[-1] = min(99, self.params[-1] * 10 + byte - 48)
            elif byte == 59 and len(self.params) == 1:
                self.params.append(0)
            elif 64 <= byte <= 126:
                self._command(byte)
            else:
                self.state = "discard"
        elif byte == 13:
            self.col = 0
        elif byte == 10:
            self._line_feed()
        elif byte == 8:
            self.col = max(0, self.col - 1)
        elif byte == 9:
            self.col = min(COLS - 1, (self.col // 8 + 1) * 8)
        elif 32 <= byte <= 126:
            self.grid[self.row][self.col] = chr(byte)
            self.col += 1
            if self.col == COLS:
                self.col = 0
                self._line_feed()
        return self.frame()


def ref_frames(data):
    term = RefTerminal()
    frames = [term.frame()]
    for byte in data:
        if byte == 0:
            break
        frames.append(term.feed(byte))
    return frames
