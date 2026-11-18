# Colour on the tape: the next device contract

Sorrel, 18 November 2026. Prepared under `terminal-colour-contract`, after
Linnet's completed cursor/erase slice. **This is an executable target, not
colour support in the current terminal.** The current page still consumes
964-byte monochrome frames. Do not load the new frames into that decoder.

## The small colour language

Keep the 24-row, 40-column ASCII device and the control/recovery rules in
`CONTROL_CONTRACT.md`. Add only these CSI `m` (SGR) parameters:

| Parameter | Effect on subsequent printed or erased cells |
| --- | --- |
| omitted or 0 | foreground 7, background 0, normal intensity |
| 1 / 22 | bright / normal foreground intensity |
| 30–37 / 39 | foreground 0–7 / default foreground 7 |
| 40–47 / 49 | background 0–7 / default background 0 |

The colour names in order are black, red, green, yellow, blue, magenta, cyan
and white. Bright is an intensity bit, not a font-weight or animation request.
The renderer will choose a fixed, documented readable palette. Exact display
RGB values are a rendering decision; the emitted colour indices are exact.

At most two parameters are accepted, consistent with the existing bounded
parser. Apply them left to right, once the final `m` arrives. Empty fields
mean 0. Thus `ESC[;m` resets twice, and `ESC[0;34m` ends with blue foreground.
Every parameter must be supported: `ESC[31;99m` changes nothing, including
the current foreground. This atomic rule prevents half-applied rejected SGR.
Three parameters are discarded under the existing second-semicolon rule.
Numbers still saturate at 99; private forms, intermediate bytes, cancellation,
restarted escapes and unsupported final bytes retain the cursor contract's
recovery. This deliberately bounded subset is not ANSI/VT100 compatibility.

An SGR byte does not move the cursor or recolour existing cells. A printable
byte overwrites both the character and its attribute. Backspace, tab and all
cursor moves leave attributes alone. Erasure writes a space **with the current
attribute**, inclusively using the existing J/K selection. Scrolling moves
character and attribute together; the newly blank bottom row receives the
current attribute. Wrapping at the bottom has exactly that scroll effect.
The initial grid is spaces with default attribute 7.

## One new frame, installed with its decoder

Replace the 964-byte frame in the colour implementation; do not keep a second
decoder or guess a format from its contents. Each frame is **1,924 bytes**:

| Offsets (zero based) | Bytes |
| --- | --- |
| 0 | FF (255), start marker |
| 1–960 | 960 ASCII characters, displayed row-major order |
| 961–1920 | 960 attributes, in the same displayed order |
| 1921 / 1922 | zero-based cursor row / column |
| 1923 | FE (254), end marker |

An attribute is `foreground + 8*background + 64*bright`, in 0–127. For example,
red on blue is `1 + 8*4 = 33`; its bright version is 97. A black-on-black cell
has attribute **0**, a valid value, not EOF or a delimiter. Characters remain
32–126, row 0–23 and column 0–39. Thus no payload byte equals either marker.
The decoder must validate exact length, markers and all four payload ranges
before displaying a frame. It must never infer colour from input bytes.

Initial blank output, one frame per nonzero input byte, input starvation and
NUL termination stay unchanged. A partial CSI retains its parser state across
any input split. NUL halts with no extra frame or partial SGR application.
SGR state must live on the Brainfuck tape with the per-cell attributes. The
implementer must document and test its new tape layout and exact bound; these
fixtures do not prescribe an addressing algorithm or pretend the existing
3,100 cells already contain an attribute plane. Preserve parser state cells
38–41 so the existing inspector/reconstruction contract remains meaningful.

## Read and run the independent examples

`colour-cases.json` contains 20 literal inputs and 38 named expected pictures. Row
and span indices are zero based. Unlisted characters are spaces; unlisted
attributes are 7. Each attribute span is `[start, length, value]` in displayed
cell order. Spans never overlap. Checkpoints occur after a named input chunk;
chunk boundaries have no device meaning. The expected pictures were worked
out from the rules above, not captured from a proposed implementation.

For example, **overwrite-keeps-neighbours** prints red `RED`, moves left twice,
selects green and writes `!`. Its picture is `R!D`; the attributes are `1,2,1`.
**erase-tail** leaves red `AB`, then spaces from column 2 to 39 with red-on-blue
attribute 33. **wrap-scroll** puts a red `X` in the old bottom-right cell:
it becomes cell 919 (row 22, column 39); the newly blank bottom row is red,
and a following `Y` appears at cell 920. These are different from recolouring
the entire row, leaving old ink on erased spaces, or moving only characters.

From this directory:

```sh
python3 test_colour_cases.py
python3 test_colour_cases.py --show overwrite-keeps-neighbours
```

The default checks validate the fixtures and verifier, including intentional
bad frames. They do **not** claim that the current Brainfuck program passes.
After implementing colour, run the actual eight-command program:

```sh
python3 test_colour_cases.py --program terminal.bf --tape-cells NEW_BOUND
```

That mode runs the existing generic browser VM in Node (no screen shortcuts),
checks every frame's structure, and compares complete bytes at each named
checkpoint. It repeats each case with the declared chunks, every possible
two-way split and one byte at a time. All resulting frames must be identical,
not just the final picture. NUL/unread tails are included. There is a finite
operation budget and a per-process timeout. The test is a conformance sample,
not a proof for arbitrary input or a phone/desktop usability trial. The colour
implementation still needs those trials and the project's final reconstruction.

### Preparation checks

All 38 expected pictures also matched a disposable display-order oracle built
on the cursor reference (source SHA-256
`9c1fa6552033ad7fe9e5602d9a01d09bece72e76629c6100baf9f0fad63edf59`).
That oracle added a parallel attribute grid and the rules above; it did not
generate these fixtures or execute a colour Brainfuck program. Its code and
output stay in this run's private evidence, not in the production model.

The verifier accepts an independently constructed literal blank-frame program
at its input-wait/EOF boundary. Against the current 964-byte program,
`overwrite-keeps-neighbours` is rejected with output length 18,316 instead of
the required 36,556. This is the expected missing colour implementation, not
a passed tape conformance test. Do not substitute these preparation checks for
running the new generator when it exists.
