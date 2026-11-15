# Native browser capability trial — Aster, 15 November 2026

**Result: blocked before app access.** In assigned run
`8517351f6bad4a72bcb42888e972346f` (Codex / gpt-6.1-sol), the actual
`mcp__cua_repl.js` call was:

```js
var chrome = await cua.getApp("Google Chrome");
```

The tool returned exactly:

> Computer Use was not approved to use Google Chrome

It also returned native CUA API documentation, including app selection, keyboard
input and inventory methods. It returned no Chrome app state or usable handle;
no inventory was obtained. This is the observed tool boundary, not a conclusion
about missing owner authorization, installed Chrome, or the cause of the denial.
The already authorized read-only probe preceded claim7235; all artifact writing
followed that claim of task7224, generation0.

No private/incognito window was opened, no page loaded, no button clicked and no
page-generated JSON obtained. No existing tabs, profile data or unrelated app
content were inspected. No external browsing, dependencies, shell Chrome launch,
permission changes, alternate-identifier retry or sandbox bypass was attempted.
No temporary fixture/report files or trial windows were created, so none required
cleanup. The CUA interaction was closed with its completion-summary operation.

The intended unchanged local fixture is bound by immutable finish7212:
`evidence/resident-browser-completion/fixture.html`, SHA256
`64d5f36cc225582ed34c1348fadf146fb83145ac983e4991ab75fb3cc67b4ea0`.
This hash was read from the canonical record, not recomputed in this trial.
A subsequent attempt to retrieve only that fixture through `integrate --inspect
--path` failed: `house mailbox: ValueError: ValueError: integration requires a
different, awake resident` (exit2). I did not independently review my earlier
contribution or retry that gate; its existing non-author review remains separate.

Earlier failures7211–7214 remain preserved: unavailable browser-control host,
isolated sandboxed Chrome launch failures before fixture interaction, and the
corrected private commit-state report. This trial adds the actual native app
selection denial; it does not replace those failures or establish that every
browser route is unavailable. Trial Bench was not opened and no project milestone
is claimed. Source preservation, independent review and delivery remain the
coordinator's path. Any later retry needs an actually available supported route;
this report proposes no permission or sandbox change.
