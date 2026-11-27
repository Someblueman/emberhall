# R21: history slider touch area

Hawthorn, 26 November 2026. Candidate for independent integration.

The published history slider is only20px high. One existing CSS declaration
now makes its input box44px high, giving fingers more room to select history.
The browser still draws its native thumb and track. No navigation code changes.

Live house.css returned200 with sha256
b5635e6a267861195bdcff75749fbe0901c1da8c6d580d82a1c52c5f12da5b64;
its range rule explicitly set height20px.

Verification uses an isolated copy of the actual history card markup and
production stylesheet, with an enabled1–100 range. A small local readout reports
its bounding box and selected value; this fixture does not load house history.
Before:390px screen target320 by20;1280px screen target568 by20.
Native ArrowRight, End, Home, ArrowRight selects51,100,1,2 on both devices.

After:390px screen target320 by44;1280px screen target568 by44.
The same key sequence selects51,100,1,2 on both devices. No horizontal
overflow, unlabelled controls or script errors. Phone before/after and desktop
after screenshots inspected: clear native focus ring and readable spacing.
The history card gains24px of vertical room, intentionally.

Thirteen existing tests pass:
`python3 -m unittest tests.test_public_site_polish tests.test_house_navigation tests.test_event_navigation`.
`git diff --check` passes. Full historical loading and live delivery are not
claimed by this bounded CSS trial. Independent integration and live checking
remain; do not mark the repair list done before that.

Candidate site/house.css sha256: d5084f24ce78a7d8bb479447be726ec3236cff5f0ed838783be9c40941617d19.
Viewer request prefix: b84cb6e932e34ab9824ed9e4e5ce7a1d, suffixes r21-before
and r21-after. Trial pages and steps are removed after screenshot inspection;
viewer screenshots remain private. To replay, copy the time-machine card from
site/index.html into a viewport-aware page, enable its range with max100 and
value50, link house.css, and play the four keys above.
