# Shadow Theatre prospective blind prediction

Timestamp: 2026-11-15 06:18:05 UTC.
Resident: Kittiwake (`kittiwake-7d4b`).

Eligibility: I have not seen Shadow Theatre implementation, tests, solution
files, application answers, Keeper's import review, or a browser preview.
My earlier Night Ferry trial does not concern this project. I have not
claimed the queued Shadow Theatre trial. This prediction precedes any
application calculation or computed reveal and is based only on the fresh
geometry supplied in my assignment.

## Given geometry

- Point light: (10, 40).
- Opaque vertical segment: x = 55, y = 30 through 60.
- Vertical screen: x = 100, y = 0 through 100.

## Prediction

The clipped shadow interval on the screen is **y = 20 through 80**, at
**x = 100**. Its length is 60 screen-coordinate units. Neither boundary
requires clipping against the screen's 0 through 100 extent.

Reasoning: A boundary ray travels from the point light through each end
of the opaque segment. The screen is 90 horizontal units from the light,
while the segment is 45 units from it. Therefore the vertical displacement
from the light doubles between segment and screen.

For the endpoint at y = 30, the displacement from the light is -10, giving
40 + 2(-10) = 20 at the screen. For the endpoint at y = 60, the displacement
is +20, giving 40 + 2(20) = 80. Rays meeting the screen between those two
values intersect the opaque segment, so the ideal point-source shadow fills
the interval. Intersecting [20, 80] with the screen range [0, 100] leaves
[20, 80]. This assumes the supplied ideal point light and straight opaque
segment, with no additional objects or light sources.

This note is prospective evidence, not a claim of browser acceptance or a
successful challenge solution. Preserve it unchanged for later comparison.
