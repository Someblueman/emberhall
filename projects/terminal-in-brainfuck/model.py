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

    def frame(self):
        cells = "".join("".join(r) for r in self.grid)
        return (cells, self.row, self.col)

    def _line_feed(self):
        if self.row == ROWS - 1:
            self.grid.pop(0)
            self.grid.append([" "] * COLS)
        else:
            self.row += 1

    def feed(self, byte):
        if byte == 13:            # carriage return: cursor only, no erase
            self.col = 0
        elif byte == 10:          # line feed: down or scroll, column kept
            self._line_feed()
        elif 32 <= byte <= 126:   # printable: store, advance, maybe wrap
            self.grid[self.row][self.col] = chr(byte)
            self.col += 1
            if self.col == COLS:
                self.col = 0
                self._line_feed()
        # every other byte is ignored; a frame is still emitted
        return self.frame()


def ref_frames(data):
    term = RefTerminal()
    frames = [term.frame()]
    for byte in data:
        if byte == 0:
            break
        frames.append(term.feed(byte))
    return frames
