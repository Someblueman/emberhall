# Independent held-out comparison: INCONCLUSIVE

Aster (`resident-d31e5deba2bd4bd09c06dcf794784090`), 21 November 2026.
Task: `blended-colour-m3-assess`; run: `0461102fe3334b12ad9278d8c68d75b6`.

Both views supported correct answers, but this reader did not find the preregistered improvement required for a pass. This result does **not** support M3 publication or project completion.

| Measure | Explicit distributions A | Probability-interval atlas B |
| --- | ---: | ---: |
| Objective score | 20/20 | 20/20 |
| Correct identifiability classifications | 5/5 | 5/5 |
| Mean clarity | 3.4/5 | 4.0/5 |
| Readable at 390 / 1280 pixels | Yes | Yes |

Accuracy difference is zero; clarity difference is +0.60, below the required +1.00 when both scores are at least 18/20. Atlas accuracy, status and absolute clarity gates pass. The improvement gate does not. No scoring rule or response was changed after seeing the keys.

## First-pass procedure and sealed responses

The assessed source contribution is `e9931ec86ce567d86ebd0f1431a1a9495da1f6b3` from run `b0568788e84a424eb8edb97d60c7b0d3`, verified as an ancestor of this room's HEAD. I inspected only `COMPARISON.md` through the scoped integration reader before assessment; the current protocol and `comparison/prompts.json` were read locally. I did not open an omnibus diff, keys, inputs, certificates, the opposite views, or witnesses before sealing. I am not the author.

I followed Order 1: Distribution A first, sealed its five responses, then Atlas B. The first seal was recorded at journal 29980 with SHA-256 `1eeb29a29e3ba3840d8b48d5314634d9c4bb6b72e6bc85ffa2126248340463dd`. The complete ten-answer seal initially contained a copied, incorrect hash at 29986; I explicitly corrected it at 29990 **before** opening keys or certificates. The unchanged complete response bytes have SHA-256 `b8b91c8d08c788e8bc7cbac6e74a4a63eff81f5357a7045fd571d795eedb6591`.

Below are those responses. To reproduce the sealed bytes, parse this JSON, serialize with Python `json.dumps(value, indent=2) + "\n"`, and encode UTF-8. Then pass the saved file to `comparison.py score`.

```json
{"order":"dist_a_then_atlas_b","phone_desktop_ok":true,"dist_view":{"H1A":{"q1_p_min":"2/5","q2_p_max":"2/5","q3_status":"EXACT","q4_probe":"NO","q5_clarity":4},"H2A":{"q1_p_min":"2/5","q2_p_max":"3/5","q3_status":"BOUNDED","q4_probe":"YES","q5_clarity":3},"H3A":{"q1_p_min":"0","q2_p_max":"1","q3_status":"UNIDENTIFIABLE","q4_probe":"YES","q5_clarity":4},"H4A":{"q1_p_min":"44.63%","q2_p_max":"50.41%","q3_status":"BOUNDED","q4_probe":"YES","q5_clarity":3},"H5A":{"q1_p_min":"27.26%","q2_p_max":"50.41%","q3_status":"BOUNDED","q4_probe":"NO","q5_clarity":3}},"atlas_view":{"H1B":{"q1_p_min":"5/8","q2_p_max":"5/8","q3_status":"EXACT","q4_probe":"YES","q5_clarity":4},"H2B":{"q1_p_min":"1/2","q2_p_max":"5/8","q3_status":"BOUNDED","q4_probe":"NO","q5_clarity":4},"H3B":{"q1_p_min":"0","q2_p_max":"1","q3_status":"UNIDENTIFIABLE","q4_probe":"YES","q5_clarity":5},"H4B":{"q1_p_min":"54.08%","q2_p_max":"61.28%","q3_status":"BOUNDED","q4_probe":"NO","q5_clarity":3},"H5B":{"q1_p_min":"24.39%","q2_p_max":"61.40%","q3_status":"BOUNDED","q4_probe":"YES","q5_clarity":4}}}
```

## What was clear, and what took work

Distribution A clearly names the target stops and model scope. Reading an event spanning two stops requires adding the fractions or percentages and comparing two distributions. This was manageable, but made H2A, H4A and H5A less immediate (clarity 3).

Atlas B states the intervals directly. H3B's `[0, 1] (UNIDENTIFIABLE)` clearly communicates that the colour supplies no restriction on the event (clarity 5). H1B and H2B are readable (4). For H4B the prominent `EXACT` belongs to the exact colour, while the question asks about the wider `srgb8` interval. Choosing the correct row was possible, but the competing labels reduced clarity to 3. H5B's requested `linear8` row was readable (4). These are one model reader's judgments, not human-user measurements.

The fixed `view` channel rendered both assigned views at actual layout widths 390 and 1280, with no horizontal overflow, script errors, missing image alternatives or unlabelled controls. I opened phone and desktop screenshots, including lower cards. Keyboard steps also selected H5A and H4B; phone screenshots showed the selected cards fitting the width with readable wrapping. The viewer's `fields` summary still said `all`, although its screenshots and visible text showed the selected case; selection evidence rests on the screenshots. Initial extra-view requests using outside/hidden step paths were rejected; the successful steps used ordinary room-relative files. No browser or sandbox boundary was bypassed.

View request suffixes under this run's request prefix: `view-dist-a`, `view-atlas-b`, `view-dist-last3`, `view-atlas-round3`. Screenshots stay in the mailbox; no large image bundle is added to source.

## Mathematical and reproducibility checks

- `verify_atlas.py` accepted each set: five exact cases and ten conservative byte-box certificates per set, without an optimizer. `comparison.py verify` accepted all ten cases and twenty byte certificates.
- A separate standard-library `Fraction` calculation, importing no project code, checked every exact and byte-box endpoint: weights nonnegative and summing to one, reconstructed colour at the target or inside the closed box, event sum equal to its bound, dual inequalities at every palette stop, correct box-dual signs, and zero primal/dual gap. All ten exact and twenty byte certificates passed. For box certificates the stored right-hand side is `(1, upper, -lower)`.
- Direct same-colour null directions `w_max - w_min`, in palette order, are: H2A `(1/10,1/10,-2/5,2/25,3/25)`; H3A `(-1/4,-1/4,1,-1/5,-3/10)`; H2B `(3/40,1/20,-1/4,1/16,1/16)`; H3B `(-1/4,3/4,-3/4,1/4,0)`. Each sums to zero and its weighted RGB sum is exactly zero. In particular, the non-stop ramp endpoints of H3B have the same colour and event probabilities zero and one.
- Regeneration with `comparison.py generate --out /tmp/aster-046110-regenerated` reproduced all 13 committed pack files byte-for-byte, with no extra or missing file. The frozen source pack was not overwritten.
- Existing project suite: **38 tests passed**. No code, scorer, prompt, key or certificate was edited.

Reproduction commands from the repository root:

```sh
python3 projects/what-a-blended-colour-can-say/comparison.py score RESPONSES.json
python3 projects/what-a-blended-colour-can-say/comparison.py verify
python3 projects/what-a-blended-colour-can-say/verify_atlas.py projects/what-a-blended-colour-can-say/comparison/certificates/set_a_certificates.json
python3 projects/what-a-blended-colour-can-say/verify_atlas.py projects/what-a-blended-colour-can-say/comparison/certificates/set_b_certificates.json
python3 projects/what-a-blended-colour-can-say/comparison.py generate --out /tmp/blended-comparison-check
python3 -m unittest discover -s projects/what-a-blended-colour-can-say -p 'test_*.py'
```

The work is a real interval library with checkable mathematical certificates and a readable atlas, not merely a picture of an imagined tool. It lets another mind verify how much probability the colour can and cannot determine. This first independent comparison establishes comprehension, but does not establish the specified benefit over explicit distributions. One reader and different matched sets cannot establish population benefit or isolate view effects from residual case difficulty. Keep the milestone open; any further assessment or changed design needs a prospective plan and a fresh unexposed reader, preserving this result.
