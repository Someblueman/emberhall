"""Emit byte parsing, cursor movement and erasure as ordinary Brainfuck.

Nothing here runs while the terminal runs: these functions write eight-command
source. Persistent parser cells survive input waits. Workspace is disjoint from
the generator's arithmetic, dispatch and screen-carry cells.
"""
from layout import COL, COLS, CUR, DROW, G, PROW, ROWS, TOP
from colours import sgr

STATE, P1, P2, SEP = range(38, 42)
OLD, COUNT, END, SAVED_ROW, SAVED_COL, LOOP, LIMIT = range(42, 49)
DIGIT, FLAG, FLAG2, TEMP, TEMP2, NUMBER, SKIP = range(49, 56)


def reset_parser(b):
    for cell in (STATE, P1, P2, SEP):
        b.clear(cell)


def default_one(b, cell):
    b.is_zero(cell, FLAG, TEMP)
    b.if_flag(FLAG, lambda: b.setv(cell, 1))


def loop(b, cell, body):
    b.go(cell)
    b.emit('[')
    body()
    b.add(cell, -1)
    b.emit(']')


def relative(b, axis, forward):
    b.compute_drow()
    b.copy(P1, COUNT, TEMP)
    default_one(b, COUNT)

    def once():
        position, bound = (DROW, ROWS) if axis == 'row' else (COL, COLS)
        if forward:
            b.lt_const(position, bound - 1, FLAG)
        else:
            b.copy(position, FLAG, TEMP)

        def move():
            b.add(position, 1 if forward else -1)
            if axis == 'row':
                b.add(PROW, 1 if forward else -1)
                b.if_eq(PROW, ROWS if forward else 255,
                        lambda: b.setv(PROW, 0 if forward else ROWS - 1),
                        FLAG2, TEMP, TEMP2)
        b.if_flag(FLAG, move)
    loop(b, COUNT, once)


def position(b):
    b.copy(P1, NUMBER, TEMP)
    default_one(b, NUMBER)
    b.lt_const(NUMBER, ROWS + 1, FLAG)
    b.is_zero(FLAG, FLAG2, TEMP)
    b.if_flag(FLAG2, lambda: b.setv(NUMBER, ROWS))
    b.add(NUMBER, -1)
    b.copy(TOP, PROW, TEMP)
    # Add a displayed row to TOP, wrapping the physical ring.
    loop(b, NUMBER, lambda: b.add(PROW, 1))
    b.lt_const(PROW, ROWS, FLAG)
    b.is_zero(FLAG, FLAG2, TEMP)
    b.if_flag(FLAG2, lambda: b.add(PROW, -ROWS))
    b.copy(P2, COL, TEMP)
    default_one(b, COL)
    b.lt_const(COL, COLS + 1, FLAG)
    b.is_zero(FLAG, FLAG2, TEMP)
    b.if_flag(FLAG2, lambda: b.setv(COL, COLS))
    b.add(COL, -1)


def erase(b, display):
    """Write spaces with the same carried addressing used by printing.

    COUNT rows are visited in display order; END is the last row's exclusive
    column end. First row starts at COL. Save/restore cursor, leaving TOP alone.
    """
    b.copy(PROW, SAVED_ROW, TEMP)
    b.copy(COL, SAVED_COL, TEMP)
    b.compute_drow()
    b.setv(COUNT, 1)
    b.setv(END, COLS)
    if display:
        b.setv(COUNT, ROWS)
        b.copy(DROW, TEMP, TEMP2)
        loop(b, TEMP, lambda: b.add(COUNT, -1))

    def before():
        if display:
            b.copy(TOP, PROW, TEMP)
            b.copy(DROW, COUNT, TEMP)
            b.add(COUNT, 1)
        b.copy(SAVED_COL, END, TEMP)
        b.add(END, 1)
        b.clear(COL)
    b.if_eq(P1, 1, before, FLAG, TEMP, TEMP2)

    def all_cells():
        if display:
            b.copy(TOP, PROW, TEMP)
            b.setv(COUNT, ROWS)
        b.clear(COL)
    b.if_eq(P1, 2, all_cells, FLAG, TEMP, TEMP2)
    b.setv(CUR, 32)

    def row():
        b.setv(LIMIT, COLS)
        b.if_eq(COUNT, 1, lambda: b.copy(END, LIMIT, TEMP), FLAG, TEMP, TEMP2)
        b.copy(LIMIT, LOOP, TEMP)
        b.copy(COL, TEMP, TEMP2)
        loop(b, TEMP, lambda: b.add(LOOP, -1))

        def cell():
            b.write_printable()
            b.add(COL, 1)
        loop(b, LOOP, cell)
        b.add(PROW, 1)
        b.if_eq(PROW, ROWS, lambda: b.clear(PROW), FLAG, TEMP, TEMP2)
        b.clear(COL)
    loop(b, COUNT, row)
    b.copy(SAVED_ROW, PROW, TEMP)
    b.copy(SAVED_COL, COL, TEMP)


def execute_csi(b):
    # A semicolon is meaningful only for cursor position. Read CUR before
    # erasure replaces it with a space; no later dispatch may then print it.
    b.is_zero(SEP, FLAG, TEMP)

    def single():
        for command, axis, forward in ((65, 'row', False), (66, 'row', True),
                                       (67, 'col', True), (68, 'col', False)):
            b.if_eq(CUR, command, lambda a=axis, f=forward: relative(b, a, f),
                    G[6], G[0], G[1])
        for command, display in ((74, True), (75, False)):
            def erasure(display=display):
                b.lt_const(P1, 3, FLAG2)
                b.if_flag(FLAG2, lambda: erase(b, display))
            b.if_eq(CUR, command, erasure, G[6], G[0], G[1])
    b.if_flag(FLAG, single)
    for command in (72, 102):
        b.if_eq(CUR, command, lambda: position(b), G[6], G[0], G[1])
    b.if_eq(CUR, 109, lambda: sgr(b, P1, P2, SEP), G[6], G[0], G[1])
    reset_parser(b)


def accumulate(b, parameter):
    # Saturate decimal parameters at 99, including arbitrarily long input.
    b.lt_const(parameter, 10, FLAG)
    b.is_zero(FLAG, FLAG2, TEMP)
    b.if_flag(FLAG2, lambda: b.setv(parameter, 99))

    def append():
        b.copy(parameter, NUMBER, TEMP)
        b.clear(parameter)
        loop(b, NUMBER, lambda: b.add(parameter, 10))
        b.copy(DIGIT, NUMBER, TEMP)
        loop(b, NUMBER, lambda: b.add(parameter, 1))
    b.if_flag(FLAG, append)


def csi(b):
    b.copy(CUR, DIGIT, TEMP)
    b.add(DIGIT, -48)
    b.lt_const(DIGIT, 10, G[4])
    b.is_zero(G[4], G[5], G[0])

    def digit():
        b.copy(SEP, G[6], G[0])
        b.is_zero(SEP, G[7], G[0])
        b.if_flag(G[6], lambda: accumulate(b, P2))
        b.if_flag(G[7], lambda: accumulate(b, P1))
    b.if_flag(G[4], digit)

    def other():
        # Start in discard; the recognized cases below override it.
        b.setv(STATE, 3)
        def separator():
            b.is_zero(SEP, FLAG, TEMP)
            def first():
                b.setv(SEP, 1)
                b.setv(STATE, 2)
            b.if_flag(FLAG, first)
        b.if_eq(CUR, 59, separator, G[6], G[0], G[1])
        b.copy(CUR, DIGIT, TEMP)
        b.add(DIGIT, -64)
        b.lt_const(DIGIT, 63, FLAG)
        b.if_flag(FLAG, lambda: execute_csi(b))
    b.if_flag(G[5], other)


def normal(b):
    b.if_eq(CUR, 13, lambda: b.clear(COL), G[6], G[0], G[1])
    b.if_eq(CUR, 10, b.line_feed, G[6], G[0], G[1])

    def backspace():
        b.copy(COL, FLAG, TEMP)
        b.if_flag(FLAG, lambda: b.add(COL, -1))
    b.if_eq(CUR, 8, backspace, G[6], G[0], G[1])
    b.if_eq(CUR, 9, lambda: b.dispatch_small(COL, [
        lambda col=col: b.setv(COL, min((col // 8 + 1) * 8, COLS - 1))
        for col in range(COLS)]), G[6], G[0], G[1])

    def printable():
        b.write_printable()
        b.add(COL, 1)
        def wrap():
            b.clear(COL)
            b.line_feed()
        b.if_eq(COL, COLS, wrap, G[6], G[0], G[1])
    b.copy(CUR, G[0], G[1])
    b.add(G[0], -32)
    b.lt_const(G[0], 95, G[2])
    b.if_flag(G[2], printable)


def process_byte(b):
    b.copy(STATE, OLD, TEMP)
    b.clear(SKIP)
    def escape():
        reset_parser(b)
        b.setv(STATE, 1)
        b.setv(SKIP, 1)
    b.if_eq(CUR, 27, escape, G[6], G[0], G[1])
    for byte in (24, 26):
        def cancel():
            reset_parser(b)
            b.setv(SKIP, 1)
        b.if_eq(CUR, byte, cancel, G[6], G[0], G[1])
    b.is_zero(SKIP, FLAG, TEMP)

    def dispatch():
        def escaped():
            reset_parser(b)
            b.if_eq(CUR, 91, lambda: b.setv(STATE, 2), G[6], G[0], G[1])
        def discard():
            b.copy(CUR, DIGIT, TEMP)
            b.add(DIGIT, -64)
            b.lt_const(DIGIT, 63, FLAG2)
            b.if_flag(FLAG2, lambda: reset_parser(b))
        for state, body in ((0, lambda: normal(b)), (1, escaped),
                            (2, lambda: csi(b)), (3, discard)):
            b.if_eq(OLD, state, body, G[6], G[0], G[1])
    b.if_flag(FLAG, dispatch)
