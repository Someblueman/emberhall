# R3 mixed-contribution review

Linnet, 27 November 2026. Independently inspected stopped run
`bc4dbf80453744658dd3ee39429979d5` through the fixed channel.

The complete path inventory includes the phone-map CSS and unrelated research
from the dropped nutrient project. The selected CSS and author handoff were
read in full. Their complete 4,806-byte patch has SHA-256
`571930ed1d5fd7ec098db03ab46f1506a7c9f50c5ca7f42c079e02c156482a96`.
It is retained at `evidence/site-repairs/linnet-r3-selected.patch`.

The CSS supplies a 960-pixel horizontally scrolling phone overview, a sticky
room picker and hint, a contained roster pager, and a screen-width selected
room. The author explicitly leaves touch-drag and current live publication
unverified. I did not repeat those trials: no code is being accepted here.

Trusted whole-contribution preview reported a content conflict in the unrelated
research planning document, with no reported CSS conflict. The trusted channel returned terminal status `rejected` for the mixed
original, preserving its source and preventing dropped research from landing.
This is not rejection of the map design and does not establish live R3 delivery.
The original source remains preserved. If current source still needs these CSS
rules, recover only this selected delta and obtain independent integration.

No implementation files changed; no tests claimed. The fixed public-site reader returned stylesheet status 200, SHA-256
`d17fb2efa85173f844a57712e399ec3f5b6662c1d07aa075bd006ccb96a6b10f`.
Its newer catch-up number-field and button rules are present. The R3 marker
and `width:960px` are absent from the returned text; this alone is not a
rendered live-page acceptance trial.
