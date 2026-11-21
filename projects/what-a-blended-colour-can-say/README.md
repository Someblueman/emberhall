# What a Blended Colour Can Say

Exact finite-palette colour-blending model, primal–dual probability-interval certificates, and regenerable vector legend (Milestone 1 of Great Work `great-rook-20261121`).

## Quick Start (One Command After Cloning)

Regenerate the vector legend (`legends/first_legend.svg`), inspection sheet (`legends/first_legend.html`), and exact rational certificates (`legends/witnesses.json`):

```sh
python3 projects/what-a-blended-colour-can-say/render_legend.py
```

Run the independent verification and corruption-rejection test suite:

```sh
python3 -m unittest discover -s projects/what-a-blended-colour-can-say -p "test_*.py" -v
```

Print the checked showcase witnesses directly from the CLI:

```sh
python3 projects/what-a-blended-colour-can-say/blended_colour.py
```

## Importable Library Example

```python
from fractions import Fraction
import sys
sys.path.insert(0, "projects/what-a-blended-colour-can-say")

import blended_colour as bc

palette = bc.builtin_palettes()["five_colour_tetra_3d"]
rgb = bc.blend_colour(palette, (Fraction(1, 4), Fraction(0), Fraction(1, 4), Fraction(1, 2), Fraction(0)))
cert = bc.solve_event_bounds(palette, rgb, event_indices=(3, 4))
bc.verify_certificate(palette, rgb, (3, 4), cert)
print(cert.p_min, cert.p_max, cert.status)  # 1/2 3/5 BOUNDED
```

## Recorded Run Output

```text
S1 [two_colour_diverging] #af5848 P(High) -> [3/4, 3/4] (EXACT)
S2 [five_colour_tetra_3d] #996b70 P(Level >= 4) -> [3/5, 3/5] (EXACT)
S3 [five_colour_tetra_3d] #955c72 P(Level >= 4) -> [1/2, 3/5] (BOUNDED)
S4 [five_colour_tetra_3d] #707396 P(Level >= 4) -> [0, 2/5] (BOUNDED)
S5 [five_colour_ramp] #809f9f P(Level >= 4) -> [0, 2/3] (BOUNDED)
S6 [five_colour_tetra_3d] #707396 P(Level = 3) -> [0, 1] (UNIDENTIFIABLE)
```

## Files

- `blended_colour.py`: Exact rational weighted-average model, RREF nullspace analyzer, two-phase rational Simplex solver, primal–dual `BoundCertificate` verifier, and CLI.
- `render_legend.py`: Regenerates `legends/first_legend.svg`, `legends/first_legend.html`, and `legends/witnesses.json`.
- `test_blended_colour.py`: Unit tests covering exact 2-colour recovery, 5-colour ambiguous/unidentifiable witnesses, 1D vs 3D bounds, out-of-gamut rejection, certificate corruption rejection, and SVG/CLI generation.
- `MODEL.md`: Mathematical formulation, Radon-partition identifiability, and primal–dual verification theorem.
- `PRIOR_ART.md`: Milestone 1 gate comparison against VSUP, *Colour Blinded by the Noise*, `ggdibbler`, `bootplot`, and Bertsimas–Popescu (2005).
