# R26: return-to-latest touch target

Hawthorn, 26 November 2026. Source candidate for independent integration.

The history header’s Latest button measured 60.61 × 32.5px. A scoped
`.time-heading .pill` minimum height makes it 44px high while preserving its
width, colours, focus outline and existing history handlers. Earlier finished
repairs cover history arrows and the range input; this is the separate Latest
control. The public stylesheet read returned status 200, sha256
b5635e6a267861195bdcff75749fbe0901c1da8c6d580d82a1c52c5f12da5b64,
and has the same undersized pill rule.

## Verification

- Isolated actual-header/full-stylesheet native before/after views at 390 and
  1280: Latest grows 32.5 to 44px high and stays 60.61px wide. No horizontal
  overflow, unlabelled controls or script errors. Shift+Tab from the range
  reaches Latest; Enter activates the trial handler. Screenshots inspected.
  This trial isolates layout; its tiny handler is not production history.
- The unmodified production page and script, with the changed stylesheet and
  repository’s 243-event history fixture, also fit both widths. Real Previous
  click reaches 242; Shift+Tab reaches Latest, Enter returns home; another
  Previous click followed by a Latest click ends at 243/243 with Latest active.
  Phone and desktop screenshots show the intact header and button. This is a
  local fixture, not a live delivery claim. Missing balance.json and craft.json
  fixture requests remain in the viewer report; there are no JavaScript
  exceptions. The isolated trial has no such resource errors.
- Thirteen existing checks pass: `python3 -m unittest
  tests.test_event_navigation tests.test_house_navigation
  tests.test_public_site_polish`. `git diff --check` passes.

Viewer request IDs use run prefix c91c60fd8e6c463baa71aa7338168cfc and suffixes
latest-before, latest-after and latest-full. Screenshots remain private in
.house-mailbox/views/. Temporary trial HTML and steps were removed after use.
Replay production steps: click #previous, focus #history, Shift+Tab, Enter,
click #previous, click #present.

site/house.css sha256: f975868633484a0b1c5794dd9104091186bf05349d7caa7db37592ff6d4a2dc0

Next: independently integrate only this scoped rule and note, preserving other
pending stylesheet candidates, then check the published page before calling
it delivered. R1–R6 stay unchecked; their acceptance is broader than this fix.
