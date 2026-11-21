# Second prospective comparison: selected observation models

Status: frozen instrument, **not an assessment result**. The first experiment
remains [INCONCLUSIVE](COMPARISON_RESULT.md): both views 20/20, clarity 3.4 versus
4.0, below the required improvement of 1.0. It is neither erased nor rescored.
This revision responds to the witnessed exact/rounded scope conflict. Building
it supplies no evidence that readers benefit and does not complete M3.

## Fixed design

Ten new cases V2-1A through V2-5B use fern_violet_v2, copper_ice_v2 and
plum_lime_ramp_v2. These palettes, inputs and case IDs differ from experiment
one and the standard atlas. Each set has an exact determinate case, an exact
bounded case, an unidentifiable case, an srgb8 case and a linear8 case. Set B's
unidentifiable case is a non-stop mixture on a collinear ramp. Weights, event
membership and probes are fixed by comparison_v2.py before any response.

Both views supply the same target event, displayed sRGB swatch, observation
scope and extremal distributions for exact, srgb8 and linear8 models. Each
starts on the case's queried scope; both allow the same scope and case changes.
The distributions are exact fractions for exact models and rounded percentages
for byte models. Both round distribution weights half-up to the nearest hundredth of a
percent; the per-stop error is below the scoring tolerance even after
summing five stops. Stop labels name
the event membership. The atlas additionally computes the event interval and
classification, and offers a vector reading of that information. Those are the
treatments being compared. The baseline gives both endpoint distributions in
fixed alternating order; it does not label which endpoint is lower.

Bounds for byte models refer to the conservative **closed rational outer box**,
not to the exact inverse half-open rounding cell. A displayed swatch is always
sRGB; linear8 bytes are data, not an alternative displayed-light swatch.

## Reader eligibility and order

Use exactly one fresh non-author reader, with no exposure to this instrument's
source, keys, input weights, certificates or answer-bearing atlas before the
baseline responses are sealed. Use a reader who did not assess experiment one. The builder cannot participate.
Do not open an omnibus integration inspection: it contains answers. If needed,
redirect its output without reading it, and inspect only this protocol by path.
A reader who sees answers early is ineligible; preserve the incident rather
than presenting their responses as blind. No explanatory coaching is allowed.

1. Read this protocol and comparison_v2/prompts.json only.
2. Open comparison_v2/dist_a/index.html with the house viewer at actual 390 and
   1280 widths. Answer V2-1A through V2-5A in that fixed order. Record actual
   clipping, keyboard access, script errors and clarity. Seal the five baseline
   answers as an immutable artifact and post their SHA-256 in the journal.
3. Only after that seal, open comparison_v2/atlas_b/first_legend.html at both
   widths. Answer V2-1B through V2-5B in order. Try scope/case selection by
   keyboard and the vector view. Seal all ten answers and post their SHA-256.
4. Only after both seals, open keys or certificates, score, verify certificates,
   and regenerate into a temporary directory. Record all failures honestly.

A builder's layout views are development checks, not reader responses.
No second reader, changed order, modified prompt or retest is authorized by
this protocol. FAIL or INCONCLUSIVE stops this instrument. Any later experiment
requires an explicit new prospective plan with its own reason and gate;
never repeat readers until one passes.

## Questions and response file

For every item, use the model named in prompts.json:
Q1 minimum probability, Q2 maximum probability (fraction or percent);
Q3 EXACT if min=max, UNIDENTIFIABLE if [0,1], otherwise BOUNDED;
Q4 YES/NO to its fixed threshold probe; Q5 clarity integer 1 (unusable) to
5 (immediately clear), with an optional note explaining difficulty.

```json
{
  "order": "dist_a_then_atlas_b",
  "phone_desktop_ok": true,
  "dist_view": {
    "V2-1A": {"q1_p_min":"...", "q2_p_max":"...", "q3_status":"...", "q4_probe":"...", "q5_clarity":3}
  },
  "atlas_view": {
    "V2-1B": {"q1_p_min":"...", "q2_p_max":"...", "q3_status":"...", "q4_probe":"...", "q5_clarity":3}
  }
}
```

Include all five cases in each view. Set phone_desktop_ok false if either
assigned view has material clipping, unreadable content or script errors.

## Unchanged success and stop rules

Each view has 20 objective points: Q1 and Q2 each within 1/200 absolute
probability, exact Q3, exact Q4, across five cases. All conditions apply:

- PASS: readable phone/desktop views; atlas >=17/20, all five Q3 correct,
  mean atlas clarity >=4.0; and either atlas beats baseline by >=2 points,
  or both score >=18/20 and atlas clarity beats baseline by >=1.0.
- FAIL: unreadable view, atlas <17, any atlas Q3 error, atlas clarity <4.0,
  or baseline objective score greater than atlas.
- INCONCLUSIVE: neither FAIL nor PASS, including a tie without sufficient
  clarity improvement. Stop; retain the result and leave M3 open.

comparison_v2.score uses the unchanged first-experiment scoring function,
with stricter boolean and clarity-type validation and this one fixed order.
This is a structured single-model-reader comparison. Different matched cases
confound view effects with difficulty; it is not a population study, a human
trial, a calibrated-screen study or a timing claim. A PASS only supports the
bounded M3 criterion, not universal superiority.

## Freeze and reproduction

comparison_v2/freeze.json hashes every instrument artifact and the generator,
renderer, protocol, scorer and mathematical dependencies. Verify it before
assessment; a mismatch invalidates the instrument, rather than silently
renewing the seal. The CLI refuses to overwrite an existing frozen pack.

```sh
python3 projects/what-a-blended-colour-can-say/comparison_v2.py verify
python3 projects/what-a-blended-colour-can-say/comparison_v2.py generate --out /tmp/colour-v2-reproduced
python3 projects/what-a-blended-colour-can-say/comparison_v2.py score RESPONSES.json
python3 -m unittest discover -s projects/what-a-blended-colour-can-say -p 'test_*.py'
```

Compare every file in the temporary regenerated pack against comparison_v2/.
Verification checks the seal, exact and box certificates without optimization,
and key bounds/status against the selected certificate. A non-author still
reconstructs extremal witnesses independently before recommending acceptance.
The original experiment is reproducible with its original commands and data.
