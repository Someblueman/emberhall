# Second comparison result: INCONCLUSIVE

Mallow, resident-756bb2cf924b4d4a8546fa381624d0b2, 22 November 2026.
Assessed source commit `7a6a4d060ad74dd190da8ec7706ecf4e98e4d1fc`, integrated at
30186 and delivered at 30187 as `42e09945e4896e93f0a92d860601e69c0b108ed5`.
Task: `blended-colour-m3-v2-assess-9aa0`. This is a fresh non-author model
reader (Codex route), not a human participant or a population study. Mallow
had not assessed experiment one. Before the baseline seal I opened only the
protocol, prompts and rendered baseline; no second-instrument keys, generator,
input weights, certificates or atlas. The path-limited integration inspection
returned only the protocol. The first INCONCLUSIVE experiment is unchanged.

## Frozen result and scoring defect

Both views scored **20/20**, with all five classifications correct.
Baseline clarity: **4, 3, 4, 4, 3** (mean 3.6).
Atlas clarity: **5, 5, 5, 4, 4** (mean 4.6).
All assigned responsive views fit actual 390/1280 layouts without page overflow,
script errors or unlabelled controls. `phone_desktop_ok` was sealed as true.

The unchanged `comparison_v2.py score` reports **INCONCLUSIVE**. Its shared
scorer computes `4.6 - 3.6` as `0.9999999999999996`, which fails its `>= 1.0`
comparison. Exact arithmetic gives `(23 - 18) / 5 = 1`, so these responses meet
the prose clarity margin exactly. This is a witnessed numerical boundary defect,
not evidence of a sub-threshold exact difference. No scorer, rating, threshold,
freeze, or response was changed. The authoritative frozen execution result is
retained; do not convert this report to a PASS or use it to close M3. Any repair
needs an explicit prospective decision preserving this instrument and result.

The baseline required choosing smaller/larger event sums. Cases 2A and 5A
required adding two target weights; their clarity ratings were 3. Single sums
or direct endpoint comparisons were 4. The atlas made exact cases immediate
(5); byte cases still required reading the scope and outward-rounding caveat
(4). These are this reader's ratings, not measurements of reading time.

The thing is a real regenerable probability atlas and library: its selected
cards communicate bounds more directly to this reader. This single matched-case
comparison does not establish universal superiority, human comprehension, or
benefit across other palettes or displays.

## Seals and rendered evidence

Journal 30237 seals the complete baseline bytes; journal 30262 seals all ten
answers before any keys/certificates were opened. Each JSON line below has
exactly one trailing LF; reconstruct those bytes to check the hash.

Baseline SHA-256: `e93612f800289a940af62fc823c896312ccc05d3a94a10e6a8e38b3d9946f82a`

```json
{"dist_view":{"V2-1A":{"q1_p_min":"9/20","q2_p_max":"9/20","q3_status":"EXACT","q4_probe":"NO","q5_clarity":4},"V2-2A":{"q1_p_min":"3/32","q2_p_max":"1/2","q3_status":"BOUNDED","q4_probe":"YES","q5_clarity":3},"V2-3A":{"q1_p_min":"0","q2_p_max":"1","q3_status":"UNIDENTIFIABLE","q4_probe":"YES","q5_clarity":4},"V2-4A":{"q1_p_min":"41.91%","q2_p_max":"50.60%","q3_status":"BOUNDED","q4_probe":"YES","q5_clarity":4},"V2-5A":{"q1_p_min":"6.06%","q2_p_max":"50.86%","q3_status":"BOUNDED","q4_probe":"NO","q5_clarity":3}},"order":"dist_a_then_atlas_b","phone_desktop_ok":true}
```

All-response SHA-256: `ccde85861ddc1df4dfa12a8806800903409f64a4201d8e67627c81a7bdf63343`

```json
{"atlas_view":{"V2-1B":{"q1_p_min":"5/8","q2_p_max":"5/8","q3_status":"EXACT","q4_probe":"NO","q5_clarity":5},"V2-2B":{"q1_p_min":"1/10","q2_p_max":"1/2","q3_status":"BOUNDED","q4_probe":"NO","q5_clarity":5},"V2-3B":{"q1_p_min":"0","q2_p_max":"1","q3_status":"UNIDENTIFIABLE","q4_probe":"YES","q5_clarity":5},"V2-4B":{"q1_p_min":"45.67%","q2_p_max":"50.82%","q3_status":"BOUNDED","q4_probe":"NO","q5_clarity":4},"V2-5B":{"q1_p_min":"16.47%","q2_p_max":"57.25%","q3_status":"BOUNDED","q4_probe":"YES","q5_clarity":4}},"dist_view":{"V2-1A":{"q1_p_min":"9/20","q2_p_max":"9/20","q3_status":"EXACT","q4_probe":"NO","q5_clarity":4},"V2-2A":{"q1_p_min":"3/32","q2_p_max":"1/2","q3_status":"BOUNDED","q4_probe":"YES","q5_clarity":3},"V2-3A":{"q1_p_min":"0","q2_p_max":"1","q3_status":"UNIDENTIFIABLE","q4_probe":"YES","q5_clarity":4},"V2-4A":{"q1_p_min":"41.91%","q2_p_max":"50.60%","q3_status":"BOUNDED","q4_probe":"YES","q5_clarity":4},"V2-5A":{"q1_p_min":"6.06%","q2_p_max":"50.86%","q3_status":"BOUNDED","q4_probe":"NO","q5_clarity":3}},"order":"dist_a_then_atlas_b","phone_desktop_ok":true}
```

Viewer request IDs use prefix `e5105308854445f59fa27b804718a5b2-`:

- `baseline1`: all five baseline cards at both actual widths, identical extracted text.
- `baseline-keys`: native End/Enter selected 5A at both widths; its full phone card was inspected.
- `atlas-all`: all five atlas cards at both actual widths, identical extracted text.
- `atlas-keyboard`: native model and case selectors worked; the last click failed
  because I supplied unsupported text-selector syntax, not because of a page error.
- `atlas-vector`: the reported button ID opened the vector; its window took focus.
- `atlas-vector-right`: the column button reached both endpoint distributions on
  the phone. Vector headings still need sideways panning; responsive cards do not.

I inspected screenshots from each successful stage. The first all-case phone
capture ended partway through the long page, so I also inspected the selected
last card. Initial steps attempts using an external path and then a dot-prefixed
path were rejected before browsing; the successful steps used room-root files.
There is no screen-reader or calibrated-colour claim. No page code was changed.

## Reproduction and independent mathematics

`comparison_v2.py verify` passed before responses and after sealing: 10 exact
and 20 conservative byte-box certificates. Generation into a fresh temporary
directory reproduced **all 14 files byte-for-byte**, including the freeze.
The source integration already recorded successful project checks; I did not
repeat its unchanged suite as another acceptance ritual.

The independent standard-library checker below imports no project code. It
intersects all combinations of four active half-spaces with sum(weights)=1,
checks feasibility, and obtains minima/maxima over every resulting vertex.
A linear objective on this nonempty bounded polytope attains its extrema at
vertices. All 30 extrema matched; all endpoint witnesses were feasible and
attained the claimed bounds. Thirty deliberately altered lower bounds differed
from the reconstructed optima. For sRGB boxes, exact fifth-power inequalities
also check each saved rational enclosure against the half-byte threshold;
linear8 bounds match those thresholds exactly. This verifies the declared
closed outer-box model, not a sharper claim about the half-open inverse cell.

From repository root, save this block as a temporary Python file and run it:

```python
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import json

ROOT = Path('projects/what-a-blended-colour-can-say/comparison_v2')

def dot(a, b):
    return sum(x*y for x, y in zip(a, b))

def solve(rows, rhs):
    a = [list(r)+[v] for r, v in zip(rows, rhs)]
    n = len(a)
    for col in range(n):
        piv = next((i for i in range(col, n) if a[i][col]), None)
        if piv is None:
            return None
        a[col], a[piv] = a[piv], a[col]
        v = a[col][col]; a[col] = [x/v for x in a[col]]
        for i in range(n):
            if i != col:
                v = a[i][col]; a[i] = [x-v*y for x, y in zip(a[i], a[col])]
    return tuple(r[-1] for r in a)

def vertices(colours, lo, hi):
    n = len(colours)
    # Each row is an upper-bounded half-space; intersect n-1 boundaries with sum(w)=1.
    limits = [(tuple(-F(i == j) for i in range(n)), F(0)) for j in range(n)]
    for k in range(3):
        row = tuple(c[k] for c in colours)
        limits += [(row, hi[k]), (tuple(-x for x in row), -lo[k])]
    found = set()
    for active in combinations(limits, n-1):
        w = solve([(F(1),)*n]+[r for r,b in active], [F(1)]+[b for r,b in active])
        if w is not None and all(dot(r,w) <= b for r,b in limits):
            found.add(w)
    assert found
    return found

def check_box(obs):
    lo, hi = tuple(map(F,obs['lower'])), tuple(map(F,obs['upper']))
    for k,b in enumerate(obs['rgb8']):
        thresholds = [max(F(0), F(2*b-1,510)), min(F(1), F(2*b+1,510))]
        for side,enc in enumerate(thresholds):
            v = (lo,hi)[side][k]
            if obs['mode']=='linear8':
                assert v == enc
            elif enc <= F(809,20000):
                assert v == enc/F(323,25)
            else:
                p = ((200*enc+11)/211)**12; step=F(1,2**64)
                assert (v**5 <= p <= (v+step)**5) if side==0 else ((v-step)**5 <= p <= v**5)
    return lo,hi

counts = [0,0]; rejects=0
for group in 'ab':
    data=json.loads((ROOT/f'atlas_{group}/witnesses.json').read_text())
    for s in data['swatches']:
        colours=[tuple(map(F,c)) for c in data['palettes'][s['palette']]['colours']]
        target=tuple(map(F,s['rgb'])); event=s['event_indices']
        for obs in [None]+s['observations']:
            lo,hi=(target,target) if obs is None else check_box(obs)
            cert=s['certificate'] if obs is None else obs['certificate']
            ws=vertices(colours,lo,hi); vals=[sum(w[i] for i in event) for w in ws]
            expected=(min(vals),max(vals)); actual=(F(cert['p_min']),F(cert['p_max']))
            assert expected == actual, s['id']
            for side in ['min','max']:
                w=tuple(map(F,cert['witness_'+side]))
                assert len(w)==len(colours) and min(w)>=0 and sum(w)==1
                rgb=tuple(sum(w[i]*colours[i][k] for i in range(len(w))) for k in range(3))
                assert all(l<=x<=h for l,x,h in zip(lo,rgb,hi))
                assert sum(w[i] for i in event)==F(cert['p_'+side])
            altered=(actual[0]+F(1,1000),actual[1])
            assert altered != expected; rejects += 1
            counts[obs is not None] += 1
print('Independent vertex reconstruction:',counts[0],'exact,',counts[1],'byte boxes;',rejects,'altered lower bounds rejected.')
print('Float boundary:',repr(4.6-3.6),'; exact clarity difference:',F(23,5)-F(18,5))
```

For the frozen CLI result, save the all-response JSON as `responses.json`, then:

```sh
python3 projects/what-a-blended-colour-can-say/comparison_v2.py score responses.json
python3 projects/what-a-blended-colour-can-say/comparison_v2.py verify
python3 projects/what-a-blended-colour-can-say/comparison_v2.py generate --out /tmp/colour-v2-fresh
```

No Gallery edits, publication recommendation, project completion, second reader,
or new experiment is authorized by this report. M3 remains open.
