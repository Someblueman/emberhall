"""Annotated-source generator for the Brainfuck terminal.

Running this file writes terminal.bf and program.js deterministically.
The generated program uses only the eight Brainfuck commands.  All screen
state (grid, cursor, scroll window) lives on its tape; see README.md for
the frozen device contract and the tape layout.

Layout (8-bit wrapping cells):
  home cells 0..62   input byte, cursor/window state, scratch
  cell 63            permanent zero guard used by the seek-home walk
  screen from 64     24 rows x 246 cells.  Each row is a 6-cell header
                     (carry counter, carry column, guard=1, carry value,
                     pad, guard=1) then 40 pairs of triples:
                     (carry counter, carry value, screen byte), alternating
                     characters and attributes encoded as attribute + 1.
Both kinds of data cell are nonzero, so the stride-3 walk stops at the guard.
"""

from pathlib import Path

from layout import (ATTR, FG, COL, COLS, CUR, DROW, DSP_DONE, DSP_F, DSP_F2, DSP_T,
                    DSP_TMP, G, GUARD, H, LT_BIT, LT_EQF, LT_F, LT_F2, LT_Q,
                    LT_TG, LT_TMP, LT_TMP2, LT_W0, LT_W1, M254, M255, PROW,
                    ROWS, SB, STRIDE, TOP, attribute, data, rcnt, rcol, rval)
from controls import process_byte


class Builder:
    def __init__(self):
        self.out = []
        self.ptr = 0

    def emit(self, s):
        self.out.append(s)

    def go(self, i):
        d = i - self.ptr
        self.emit(">" * d if d > 0 else "<" * (-d))
        self.ptr = i

    # -- basic macros (all cells distinct unless stated) -----------------
    def clear(self, i):
        self.go(i)
        self.emit("[-]")

    def add(self, i, n):
        self.go(i)
        self.emit("+" * n if n > 0 else "-" * (-n))

    def setv(self, i, n):
        self.clear(i)
        self.add(i, n)

    def copy(self, src, dst, tmp):
        """dst = src, preserving src; tmp ends 0."""
        self.clear(dst)
        self.clear(tmp)
        self.go(src)
        self.emit("[")
        self.add(dst, 1)
        self.add(tmp, 1)
        self.add(src, -1)
        self.emit("]")
        self.go(tmp)
        self.emit("[")
        self.add(src, 1)
        self.add(tmp, -1)
        self.emit("]")

    def is_zero(self, src, flag, tmp):
        """flag = 1 iff src == 0, preserving src; tmp ends 0."""
        self.clear(tmp)
        self.setv(flag, 1)
        self.go(src)
        self.emit("[")
        self.clear(flag)
        self.add(tmp, 1)
        self.add(src, -1)
        self.emit("]")
        self.go(tmp)
        self.emit("[")
        self.add(src, 1)
        self.add(tmp, -1)
        self.emit("]")

    def if_flag(self, flag, body):
        """Run body() once iff flag != 0; flag ends 0."""
        self.go(flag)
        self.emit("[")
        body()
        self.clear(flag)
        self.emit("]")

    def eq_const(self, src, k, flag, t1, t2):
        """flag = 1 iff src == k, preserving src.

        The zero test is destructive on the disposable copy: testing a
        wrapped difference (src - k can be near 255) with the
        preserving is_zero would transfer it out and back for nothing.
        """
        self.copy(src, t1, t2)
        self.add(t1, -k)
        self.setv(flag, 1)
        self.go(t1)
        self.emit("[")
        self.clear(flag)
        self.clear(t1)
        self.emit("]")

    def dispatch_small(self, src, bodies):
        """Run bodies[src]() for a src below len(bodies), by counting a
        copy of src down to zero.  Bodies must not use the DSP_* cells.
        Cheaper than len(bodies) equality checks when src is small.
        """
        self.copy(src, DSP_T, DSP_TMP)
        self.clear(DSP_DONE)
        for body in bodies:
            self.is_zero(DSP_T, DSP_F, DSP_TMP)
            self.is_zero(DSP_DONE, DSP_F2, DSP_TMP)

            def outer(body=body):
                def inner():
                    body()
                    self.setv(DSP_DONE, 1)
                self.if_flag(DSP_F2, inner)

            self.if_flag(DSP_F, outer)
            self.copy(DSP_T, DSP_F, DSP_TMP)
            self.if_flag(DSP_F, lambda: self.add(DSP_T, -1))

    def if_eq(self, src, k, body, flag, t1, t2):
        self.eq_const(src, k, flag, t1, t2)
        self.if_flag(flag, body)

    # -- less-than via bit extraction (dedicated LT_* workspace) --------
    def divmod2(self, a, q, bit):
        """q = a // 2, bit = a % 2, a ends 0.

        LT_TG is a 0/1 toggle flipped per unit; every second flip adds
        one to q, and the leftover toggle is the remainder bit.  All
        zero tests here are on the toggle itself, never on a wrapped
        difference, so they stay tiny.
        """
        tg = LT_TG
        self.clear(q)
        self.clear(tg)
        self.go(a)
        self.emit("[")
        self.add(a, -1)
        self.is_zero(tg, LT_F, LT_TMP)
        self.copy(tg, LT_F2, LT_TMP)
        self.if_flag(LT_F, lambda: self.setv(tg, 1))

        def second():
            self.clear(tg)
            self.add(q, 1)

        self.if_flag(LT_F2, second)
        self.go(a)
        self.emit("]")
        self.copy(tg, bit, LT_TMP)

    def lt_const(self, src, k, flag):
        """flag = 1 iff src < k (0 <= k <= 255), preserving src."""
        self.copy(src, LT_W0, LT_TMP)
        cur_w, nxt_w = LT_W0, LT_W1
        for i in range(8):
            self.divmod2(cur_w, nxt_w, LT_BIT[i])
            cur_w, nxt_w = nxt_w, cur_w
        self.clear(flag)
        self.setv(LT_EQF, 1)
        for i in range(7, -1, -1):
            bit = LT_BIT[i]
            if (k >> i) & 1:
                # if eqf and bit == 0: less = 1, eqf = 0
                self.is_zero(bit, LT_F, LT_TMP)

                def body(f=LT_F, fl=flag):
                    def inner():
                        self.setv(fl, 1)
                        self.clear(LT_EQF)
                    self.if_flag(f, inner)

                self.copy(LT_EQF, LT_F2, LT_TMP)
                self.if_flag(LT_F2, body)
            else:
                # if eqf and bit == 1: eqf = 0
                def body(bit=bit):
                    self.copy(bit, LT_F, LT_TMP)
                    self.if_flag(LT_F, lambda: self.clear(LT_EQF))

                self.copy(LT_EQF, LT_F2, LT_TMP)
                self.if_flag(LT_F2, body)

    # -- whole-program pieces --------------------------------------------
    def compute_drow(self):
        """DROW = (PROW - TOP) mod ROWS, the cursor's display row."""
        self.copy(PROW, DROW, G[0])
        self.add(DROW, ROWS)
        self.copy(TOP, G[0], G[1])
        self.go(G[0])
        self.emit("[")
        self.add(G[0], -1)
        self.add(DROW, -1)
        self.go(G[0])
        self.emit("]")
        self.lt_const(DROW, ROWS, G[2])
        self.is_zero(G[2], G[3], G[0])
        self.if_flag(G[3], lambda: self.add(DROW, -ROWS))

    def clear_physical_row(self, r):
        # Bring the current attribute to this row once; copying it from home
        # for every cell would inflate both generated source and pointer work.
        self.copy(ATTR, rval(r), G[0])
        for c in range(COLS):
            cell = data(r, c)
            self.clear(cell)
            self.add(cell, 32)
            self.copy(rval(r), attribute(r, c), rcnt(r))
        self.clear(rval(r))

    def line_feed(self):
        self.compute_drow()
        self.eq_const(DROW, ROWS - 1, G[4], G[0], G[1])
        self.is_zero(G[4], G[5], G[0])

        def scroll():
            self.dispatch_small(
                TOP,
                [(lambda r=r: self.clear_physical_row(r)) for r in range(ROWS)])
            self.copy(TOP, PROW, G[0])
            self.add(TOP, 1)
            self.if_eq(TOP, ROWS, lambda: self.clear(TOP), G[6], G[0], G[1])

        def advance():
            self.add(PROW, 1)
            self.if_eq(PROW, ROWS, lambda: self.clear(PROW), G[6], G[0], G[1])

        self.if_flag(G[4], scroll)
        self.if_flag(G[5], advance)

    def emit_frame(self):
        self.go(M255)
        self.emit(".")

        def make_body(r):
            order = list(range(r, ROWS)) + list(range(0, r))

            def body():
                for pr in order:
                    for c in range(COLS):
                        self.go(data(pr, c))
                        self.emit(".")
                # Attributes travel in the same displayed order as characters.
                # Decode only while emitting, then restore the nonzero guard.
                for pr in order:
                    for c in range(COLS):
                        self.go(attribute(pr, c))
                        self.emit("-.+")
            return body

        self.dispatch_small(TOP, [make_body(r) for r in range(ROWS)])
        self.compute_drow()
        self.go(DROW)
        self.emit(".")
        self.go(COL)
        self.emit(".")
        self.go(M254)
        self.emit(".")

    def write_printable(self):
        """Overwrite the character and its ink together on the tape."""
        self.write_cell(CUR, False)
        self.write_cell(ATTR, True)

    def write_cell(self, source, is_attribute):
        """Store one of the cell's two planes via the existing carries.

        The carries are raw relative snippets: the row carry walks the
        (count, column, value) triple down the row headers, the element
        carry walks (count, value) across one row.  After storing, a
        stride-3 walk left over nonzero data cells stops at GUARD, so
        the builder's pointer is known again.
        """
        self.copy(PROW, rcnt(0), G[0])
        self.copy(COL, rcol(0), G[0])
        self.copy(COL, G[0], G[1])
        self.go(G[0])
        self.emit('[')
        self.add(rcol(0), 1)
        self.add(G[0], -1)
        self.emit(']')
        if is_attribute:
            self.add(rcol(0), 1)
        self.copy(source, rval(0), G[0])
        self.go(rcnt(0))
        mv = "[-" + ">" * STRIDE + "+" + "<" * STRIDE + "]"
        row_carry = ("[" + "-" + mv + ">" + mv + "<" + ">>>" + mv
                     + "<<<" + ">" * STRIDE + "]")
        self.emit(row_carry)
        # header triple -> element 0 (count at +6, value at +7)
        self.emit(">" + "[->>>>>+<<<<<]" + ">>" + "[->>>>+<<<<]" + ">>>")
        self.emit("[-[->>>+<<<]>[->>>+<<<]>>]")          # element carry
        self.emit(">>[-]<<")                             # clear data cell
        self.emit(">" + "[->+<]")                        # value -> data
        self.emit(">" + "[<<<]")                         # seek the guard
        self.ptr = GUARD

    def process_byte(self):
        process_byte(self)


def build():
    b = Builder()
    b.setv(FG, 7)
    b.setv(ATTR, 8)
    # frame markers (cells start at 0; wrapping decrement gives 255/254)
    b.go(M255)
    b.emit("-")
    b.go(M254)
    b.emit("--")
    # screen: guards = 1, data cells = space
    for idx in range(SB, SB + ROWS * STRIDE):
        off = (idx - SB) % STRIDE
        if off in (2, 5):
            b.go(idx)
            b.emit("+")
        elif off >= H and (off - H) % 3 == 2:
            b.go(idx)
            b.emit("+" * (32 if (off - H) % 6 == 2 else 8))
    b.emit_frame()
    b.go(CUR)
    b.emit(",[")
    b.process_byte()
    b.emit_frame()
    b.go(CUR)
    b.emit(",]")
    return "".join(b.out)


def main():
    bf = build()
    assert set(bf) <= set("><+-.,[]"), set(bf)
    root = Path(__file__).resolve().parent
    with (root / "terminal.bf").open("w") as f:
        f.write(bf + "\n")
    with (root / "program.js").open("w") as f:
        f.write("// Generated by build_terminal.py; do not edit by hand.\n")
        f.write("const BF_PROGRAM = `" + bf + "`;\n")
    print(f"terminal.bf: {len(bf)} commands")


if __name__ == "__main__":
    main()
