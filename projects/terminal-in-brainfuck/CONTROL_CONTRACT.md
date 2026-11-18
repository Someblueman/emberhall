# Cursor and erasure device contract

Pinned by Aster before the second-stage implementation, 18 November 2026.
The generated terminal implements these rules. [Builder checks](BUILDING.md)
record the interpreter comparisons and page trials.
It extends the admission device; it is a deliberately small selection, not
VT100 compatibility. The 24 by 40 screen, immediate wrap, ring scrolling,
3,100 wrapping byte cells, ASCII input and 964-byte frame remain unchanged.
The first stage was admitted at journal 18639 from Rook's independent encounter
18607. This slice is not the whole second milestone: attributes and colour
still follow.

## Bytes and defaults

- Backspace (8) moves left one column, stopping at zero. It never erases or
  crosses to the preceding row.
- Horizontal tab (9) moves to the next multiple-of-eight column (zero-based),
  stopping at column 39. It never writes spaces, wraps or scrolls.
- ESC (27) begins an escape. ESC followed by `[` begins a control sequence
  (CSI). Any other following byte is consumed, returning to ordinary text.
- CSI `A`, `B`, `C`, `D` move up, down, right, left. Omitted or zero count means
  one; movement clamps at the edge without erasing or scrolling.
- CSI `H` or `f` sets row and column, one-based. Omitted or zero parameters mean
  one. Values beyond the screen clamp to its last row or column.
- CSI `J` erases the display; CSI `K` erases the current line. Mode omitted or
  zero erases from the cursor through the end; 1 erases from the beginning
  through the cursor; 2 erases the whole display or line. Erasure writes spaces
  and leaves the cursor and scroll window unchanged. Other modes do nothing.
- Parameters are decimal digits and at most one semicolon. Each accumulated
  number saturates at 99; it does not wrap. A second parameter is valid only
  for `H` and `f`. For all other final bytes a semicolon invalidates the command.

## Partial and malformed sequences

Every nonzero input byte emits a frame, even if it merely updates parser state.
A queue that runs dry leaves that state intact; feeding the same bytes in any
chunks must produce the same frames. NUL still halts immediately, even inside
a sequence, with no extra frame.

An ESC in any state abandons the old sequence and begins a fresh escape.
CAN (24) or SUB (26) cancels any pending sequence and returns to ordinary text.
Within CSI, an unrecognised final byte in 64..126 ends the sequence without an
action. A second semicolon, private/intermediate byte, non-ASCII byte or other
control puts the parser in discard state; it consumes bytes through the next
final byte. CAN, SUB and ESC still act while discarding. No byte from a rejected
sequence is printed. This simple recovery policy is explicit, not a claim to
implement every terminal's control handling.

## Inspecting the tape

Cells 38..41 hold parser state (0 text, 1 escape, 2 CSI, 3 discard), first
parameter, second parameter and whether a semicolon occurred. They are reset
at a new escape and after a completed or cancelled sequence. Cells 42..55 are
transient control workspace. The existing grid begins at 64 and is unchanged.
The host may display these cells but may not interpret the incoming sequences.
EOF, input waiting and literal stepping retain their first-stage meanings.
EOF while a sequence is pending halts without applying it.
