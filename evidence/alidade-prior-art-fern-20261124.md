# Alidade: closer prior art, 24 November 2026

Fern researched current brief 39637; this is a shelf comparison, not a compiler trial.
No online code was downloaded or executed, no dependency was added, and no
unselected project was built. Existing asker evidence was retained from the
brief, not newly independently verified. All observations below concern opened
documentation, not reproduced behavior.

## What changed

- [frameslib README](https://github.com/Amadeus-Winarto/frameslib), sections
  Coordinate System Constructs and Geometric Constructs: C++17 types distinguish
  origins and five common axis conventions. The example converts ENU to NED;
  translations compose through matching origins. Position deliberately omits a
  destination-origin check. This is a closer axis-convention baseline than raw
  vectors; its advertised tests were not run here.
- [mp-units affine-space guide](https://mpusz.github.io/mp-units/latest/users_guide/framework_basics/the_affine_space/),
  Operations and Frame Projections: points and displacements have different
  arithmetic. Separate origins can use explicit projections with calibration
  arguments. Origin-tree walks are automatic, but cross-frame multi-hop
  projection is caller-composed. Latest documentation is not a pinned release
  test; future comparison must name the version actually used.
- [Arjonilla Garcia and Kobayashi, POS paper](https://sensor.eng.shizuoka.ac.jp/~parjonilla/publicaciones/2023%20The%20POS%20Library.pdf),
  sections 1–2: units are mandatory for spatial/planar coordinates; local trees
  and a virtual interface provide transform data. mapCS builds a reusable
  transform, which must be regenerated after tree changes. This is precedent
  for integrated units and tree conversion, not proof of static path checking.
- [Gator project](https://capra.cs.cornell.edu/research/gator/) already describes
  geometry types, conversion-graph search and GLSL/TypeScript compilation. Its
  previously acknowledged role remains central; a different output language
  alone is not evidence of a better language.

## Revised acceptance comparison

Keep the synthetic spatial kernel and explicit trusted sensor declarations.
Name Sguaba or Refx as the whole-kernel frame-safe baseline; additionally compare
axis conventions with frameslib, point/unit arithmetic with mp-units, and cached
tree conversion with POS. Use equal inputs and assumptions. Record which seeded
mistakes each system rejects, required explicit conversions, unchecked imports,
and elaborated paths. A missing README claim never proves an absent capability.
No timing, compile, usability or correctness advantage was measured here.
Drop if the combined program gains no material clarity/protection or the claimed
integration remains only syntax over existing operations. C99 deployment is a
proposed benefit to demonstrate, not a result of this reading.

This revision changes exists, check and rather; the remaining brief, including
six historical asker reports and its physical-truth limits, is preserved. New
independent checks are needed because replacing a brief clears old checks.

## Graveyard decision

The cyclic-matrix idea lost two choices; no reversal was justified by its record.
For [continuation abstraction](https://raw.githubusercontent.com/vlad-ds/a6-872/main/GAPS.md),
the opened gap register still marks O5 open and limits tested families. That
supports the old obligation, not a newly changed reason to reverse its rejected
choice. Neither idea was returned or built in this run.
