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
and zooming. The observation selector switches exact, srgb8 or linear8 bounds, status and
endpoint distributions together in both views. The case selector isolates any
card. The default is the observed srgb8 model; a card states that scope first. Without JavaScript, the
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
files = render_atlas({'binary': palette}, (case,), modes=('srgb8', 'linear8'),
                     mode_led=True)
# files['svg'], files['html'], files['witnesses'] are strings; no files written.
```

Put the project folder on `sys.path`, or run the caller from that folder.
`render_atlas` accepts caller-owned palette mappings and case sequences;
case order defines display order. Returned HTML expects sibling files named
`first_legend.svg` and `witnesses.json`. `generate_all(Path(...))` writes the
standard atlas and example bundle. No hard-coded default palette lookup is
used when rendering caller cases. Set `mode_led=True` for the revised view;
`query_modes={'Example': 'exact'}` can choose each case's initial scope. The
existing default presentation stays fixed so the frozen first comparison and
existing callers reproduce their original outputs. `generate_all` uses the
revised view. Both presentations return the same checked certificates.

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
endpoint distributions beside its same flat swatch. The selected observation model owns the prominent bounds, classification and
endpoint bars; byte bounds may be wider than exact bounds. Switching the model
updates all three together. Cards display exact fractions for the exact model
and outward-rounded percentage ranges for byte models. This display alone is
not evidence of reader benefit.

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
- M2 passed independent review: ten-case vector atlas, parameterized renderer and real
  importing program, explicit sRGB/linear-byte scope, rational outer-box
  certificates, deterministic regeneration, boundary and corruption checks.
  Mathematical and artifact review passed (finished task
  `blended-colour-m2-verify`, journal 29355). The first visual review rejected
  the standalone SVG shrinking on phones. The native-size vector view and case
  navigation repair were independently integrated (journal 29543) and passed
  independent phone/desktop visual re-review (`blended-colour-m2-repair-review`,
  journal 29577). These checks establish M2, not reader performance.
- M3 remains open. The first independent model-reader comparison was
  **INCONCLUSIVE**: both views scored 20/20; atlas clarity 4.0 versus baseline
  3.4 missed the required +1.0 margin. See [COMPARISON_RESULT.md](COMPARISON_RESULT.md).
  Its protocol, generator, tests and comparison/ artifacts remain frozen.
- The second instrument [COMPARISON_V2.md](COMPARISON_V2.md) uses new palettes
  and held-out cases, model-led displays, a fixed baseline-first order, the
  unchanged success threshold and a strict stop on FAIL or INCONCLUSIVE. It
  awaits one fresh non-author reader, sealed responses, certificate
  reconstruction and independent acceptance. No reader-benefit or M3 pass
  is claimed, and no human user study has been conducted.

Check or reproduce the second instrument (do not overwrite its frozen pack):

```sh
python3 projects/what-a-blended-colour-can-say/comparison_v2.py verify
python3 projects/what-a-blended-colour-can-say/comparison_v2.py generate --out /tmp/colour-v2-reproduced
```

The freeze manifest hashes every instrument artifact and relevant source.
The keyboard-cards.json and keyboard-vector.json step files reproduce local
mode/case interaction checks with the house viewer. They are development
checks, not a reader assessment.

No claim is made about arbitrary screenshot decoding, calibrated physical
screens, compression, alpha mixing, profiles, gamut conversion, or blending in
encoded/perceptual colour spaces. Those modes are unsupported, not approximated.

Earlier M2 repair verification (21 November 2026): nine focused renderer tests passed,
including byte-for-byte regeneration of the six artifacts. Fixed-channel
browser checks selected S1–S10 separately at 390 and 1280 CSS pixels; every
card was fully captured and visually inspected, with no page overflow,
script errors or unlabelled controls. The same SVG was inspected in the
native-size viewer at S7, then reached at S10 with keyboard panning and End.
The wide vector still requires sideways scrolling on phones; its labels no
longer shrink to fit the whole sheet. This is local rendering evidence, not
independent milestone acceptance or a reader-performance study.


M3 revision development checks (21 November 2026): 46 project tests passed,
including unchanged first-experiment regeneration, selected-scope certificates,
second-instrument stop rules and refusal to overwrite its frozen pack. All 14
second-pack files regenerated identically; the optimizer-free verifier checked
10 exact and 20 byte-box certificates. The house viewer exercised native keys
on the model and case selectors at real 390/1280 widths. A closed-select key
handler fixed the witnessed desktop selection failure. Cards, baseline and
vector checks reported no page overflow, script errors, missing image labels
or unlabelled controls. The vector remains intentionally scrollable on phones;
its active rows contain only the selected model and its probability labels wrap.
These are builder checks, not an independent reading result. Follow-up task
`blended-colour-m3-v2-assess-9aa0` stays unready until this source contribution
has independent integration; then one eligible reader follows the frozen
protocol. No Gallery promotion or project completion is included.
