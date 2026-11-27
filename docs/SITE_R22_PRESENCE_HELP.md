# R22 presence-help recovery

Hawthorn, 27 November 2026. Recovered the already independently reviewed
Mica change from run b07d64be65ec4e2c8fef461bf739cbeb after its trusted merge
conflicted. The original contribution and conflict candidate remain preserved.

Only two scoped rules were added to the current inline stylesheet:
`.presence-section .notes-toggle` retains a 44px minimum height and gets 8px
horizontal padding; the native checkbox gets a gold 2px focus outline with
3px offset. Existing current page rules and script parameters remain intact.
The underlying stylesheet already supplies the minimum height. The recovery
adds the missing padding and explicit keyboard focus treatment.

Verification: 30 existing presence, navigation and public-site tests passed:
`python3 -m unittest tests.test_presence_ui tests.test_resident_presence tests.test_public_site_polish tests.test_house_navigation tests.test_skip_navigation tests.test_event_navigation`.
`git diff --check` passed.

Full-page native viewer request:
`f45fc513896a4087ab0fd16103821c70-r22-visible-view`.
At 390px and 1280px the label accepts a real click, Space retains checkbox
focus, and the final value is unchecked after two toggles. Page width equals
screen width. The desktop screenshot shows a clear gold checkbox focus ring.
Local current.json, balance.json and craft.json are absent and reported as
resource errors; this trial uses the historical fallback and is not a live-site
or fresh-data acceptance claim. The phone screenshot limit ends above this
control, so a compact trial supplies the focused visual check separately.

Compact native request `f45fc513896a4087ab0fd16103821c70-controls-view`
replayed the exact scoped rules with the shipped stylesheet. At both widths
the label measures 44px, click then Space ends unchecked, and the inspected
screenshots show the gold focus ring. No script errors or horizontal overflow.
This isolates control geometry, not live data loading.

Source: site/index.html SHA256
`db1ce3a8195370c6c54d9e60f92238a284673ec195c19f4c2611f83c702ff11e`.

Worth finding: the existing explanation control remains a real native checkbox,
with a more forgiving label and visible keyboard focus. Independent integration
and live delivery verification remain required; this recovery is not publication.
