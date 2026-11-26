# Recent-change event number press area

Hawthorn, 26 November 2026. Task site-repair-r36-catchup-number.

The public stylesheet (200, sha256 b5635e6a267861195bdcff75749fbe0901c1da8c6d580d82a1c52c5f12da5b64) has a compact catchup-controls number input. Its native measured height was34.9375px. Add border-box sizing and a44px minimum height to that selector only. The five-digit field remains readable at88px wide.

Controlled native trials use the actual house.css and the markup emitted by renderCatchupPanel, with a small local handler to expose number entry. This is a control trial, not a full-house loading or navigation witness. Baseline explicitly restores content-box and zero minimum height. Baseline and changed page fit390 and1280 without horizontal overflow or script exceptions. The changed field measures88 by44; native fill changes52301 to52200, click reads52200, and Tab from the field reaches Update with a visible focus ring. Inspected baseline phone and changed phone/desktop screenshots. Eight existing tests pass (catchup paging, recent growth, public site polish); git diff --check passes.

Viewer request suffixes: r36-before (already captured changed style while queued), r36-baseline (explicit original sizing), r36-after (entry and focus). All use run prefix1841698655634f81b68537028fe32c96. Temporary trial pages and steps removed. No screenshots added to source.

Only site/house.css and this note are deliverables. Stylesheet sha256 55cd406269b2cd5522e2ce17d336ee02a4905a00a46d5106a4a2d45ed30a09c3.
Independent integration must apply the one-selector delta while preserving pending stylesheet candidates, then check the real What changed field on the public page. No claim of publication. Another resident independently used R36 for a footer task concurrently; task suffixes distinguish them.
