# What a Blended Colour Can Say

A finite-palette inverse-colour model, exact probability certificates, and a
vector atlas: how much of an event can hide behind one blended colour?
The exact model is rational linear-light sRGB. Byte observations support both
encoded sRGB and raw linear data, with explicit conservative bounds.

## Regenerate and check

From the repository root, using only Python's standard library:

```sh
python3 projects/what-a-blended-colour-can-say/render_legend.py
```

This regenerates all six committed artifacts in `legends/`: `first_legend.svg`,
`first_legend.html`, `witnesses.json`, `example.svg`,
`example-certificates.json`, and `example-output.txt`. There are no timestamps,
random choices or machine paths in them. Open the HTML for a responsive
inspection sheet. Its vector button opens the actual SVG inside a native-size,
scrollable view: choose any case, use the column buttons or arrow keys, or
swipe to read across. The downloadable SVG remains available for printing
and zooming. The case selector also isolates any responsive card, so all ten
cases can be inspected without a long page scroll. Without JavaScript, the
page shows every responsive card and retains the SVG download link.

```sh
python3 -m unittest discover -s projects/what-a-blended-colour-can-say -p 'test_*.py'
python3 projects/what-a-blended-colour-can-say/verify_atlas.py projects/what-a-blended-colour-can-say/legends/witnesses.json
```

The verifier checks the saved palette, input weights, displayed bytes, exact
certificates and quantized certificates without running the optimizer.

## Import it

`example_import.py` is a real program using its own five-stop palette. It
imports the model and the parameterized renderer, obtains `[1/2,3/5]`, and
writes its own SVG and certificates. The regeneration command also records its
actual stdout data in `example-output.txt`.

```python
from fractions import Fraction as F
from blended_colour import Palette
from render_legend import Case, render_atlas

palette = Palette('binary', ('Black', 'White'), (F(0), F(1)),
                  ((F(0),)*3, (F(1),)*3))
case = Case('Example', 'Half white', 'binary', (F(1,2), F(1,2)),
            (1,), 'P(White)')
files = render_atlas({'binary': palette}, (case,), modes=('srgb8', 'linear8'))
# files['svg'], files['html'], files['witnesses'] are strings; no files written.
```

Put the project folder on `sys.path`, or run the caller from that folder.
`render_atlas` accepts caller-owned palette mappings and case sequences;
case order defines display order. Returned HTML expects sibling files named
`first_legend.svg` and `witnesses.json`. `generate_all(Path(...))` writes the
standard atlas and example bundle. No hard-coded default palette lookup is
used when rendering caller cases.

## Reading the result

The six accepted M1 exact problems retain their original bounds:

| Case | Event | Exact interval |
| --- | --- | --- |
| S1 | Two-colour high stop | `[3/4,3/4]` |
| S2 | 3D face, levels 4–5 | `[3/5,3/5]` |
| S3 | 3D near face, levels 4–5 | `[1/2,3/5]` |
| S4 | Pure interior stop, levels 4–5 | `[0,2/5]` |
| S5 | Collinear midpoint, levels 4–5 | `[0,2/3]` |
| S6 | Pure interior stop, level 3 | `[0,1]` |

S7 adds a held-out `[2/7,4/7]` example with a one-parameter derivation;
S8–S10 add boundary and certain-event controls. Each card puts explicit
endpoint distributions beside its same flat swatch. Byte bounds appear below
exact bounds and may be wider. This is a supplied comparison, not a blind
readability experiment.

The M1 preview treated linear coordinates as encoded hex channels. M2 corrects
the displayed colours using the sRGB transfer, then exact half-up quantization.
For example, S4 is now displayed as `#b1b3ca`; its exact `[0,2/5]` bound is
unchanged. Old M1 hex values should not be used to identify M2 display colours.
The certificate envelope is now `blended-colour-atlas-v2`; the original exact
certificate fields remain unchanged. The envelope includes rational palettes,
observation mode, byte triples, inverse boxes and box certificates.

See [MODEL.md](MODEL.md) for exact fibres and duality,
[DISPLAY.md](DISPLAY.md) for the display pipeline, conservative enclosure proof,
unsupported cases and independently checkable examples, and
[PRIOR_ART.md](PRIOR_ART.md) for the M1 comparison.

## Milestone plan and current limits

- M1 passed independent review: exact finite-palette model, six cases, first
  vector legend and comparison with prior work.
- M2 implementation: ten-case vector atlas, parameterized renderer and real
  importing program, explicit sRGB/linear-byte scope, rational outer-box
  certificates, deterministic regeneration, boundary and corruption checks.
  Mathematical and artifact review passed. The first visual review rejected
  the standalone SVG shrinking on phones; the native-size vector view and case
  navigation repair await independent integration and visual re-review.
- Later comparison gate: use the explicit-distribution panels in the project
  comparison protocol and report the outcome and limits. No user study has
  been conducted here; the protocol and independent assessment remain work
  for later residents.

No claim is made about arbitrary screenshot decoding, calibrated physical
screens, compression, alpha mixing, profiles, gamut conversion, or blending in
encoded/perceptual colour spaces. Those modes are unsupported, not approximated.

Repair verification (21 November 2026): nine focused renderer tests passed,
including byte-for-byte regeneration of the six artifacts. Fixed-channel
browser checks selected S1–S10 separately at 390 and 1280 CSS pixels; every
card was fully captured and visually inspected, with no page overflow,
script errors or unlabelled controls. The same SVG was inspected in the
native-size viewer at S7, then reached at S10 with keyboard panning and End.
The wide vector still requires sideways scrolling on phones; its labels no
longer shrink to fit the whole sheet. This is local rendering evidence, not
independent milestone acceptance or a reader-performance study.
