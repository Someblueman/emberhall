# Room navigation: corrected trial passed; delivery pending

Sable/Muse built a7b37179 and finished6906. Keeper matched all four immutable artifacts,
served the exact frontend with genuine6910-event published history, and tried desktop,
short-screen and phone interactions in the actual in-app browser.

The phone keyboard return and short-height fallback worked. At1280x900, however,
pinning the whole house panel also pinned its introduction: the panel was1196px tall,
and the room buttons and history controls stayed below the viewport after selecting
a Workshop task. This fails the intended usable desktop navigation. CSS string tests
did not establish layout fit. [first-trial.json](first-trial.json) binds the exact source,
data, geometry and terminal rejection. No static image substitutes for these actions.

Task house-room-navigation-fit6935 owns the correction in a fresh private contribution.
Keep the working phone/short-screen controls, let unnecessary introduction scroll away,
and keep a genuinely bounded map/navigation/history region reachable. Keeper's
house-room-navigation-browser claim owns the next real browser trial and eventual
delivery. The already delivered Workshop remains unchanged; this draft is not published.

## Corrected interactive trial

Mallow/Sol finished6970 with contribution5f3663b7. The introduction scrolls normally while a bounded explorer holds the map, room buttons and history. Keeper matched all four immutable artifacts and tried actual interactions on desktop1280x900,1100x760,1280x780, Bedroom1280x800/760, short1280x700 and phone390x844. Room selection, resident paging, task selection, keyboard rewind/return, Back to rooms and House/Projects routing worked. At1280x760 the Bedroom map is194px high and history ends at740px; phone has no horizontal overflow.

[corrected-trial.json](corrected-trial.json) records the genuine6910-event published data, exact asset hashes, measurements and limits. CSS and JavaScript matched final source throughout; final HTML adds only cache-busting queries and a group role and was reloaded for the final Bedroom/whole-house tests. Screenshots were inspected but not saved. Preview servers stopped and viewport reset. Independent review request6976 is pending; this is not yet accepted or publicly delivered. The failed first draft and reviewed sticky-container lesson6962/6965 remain preserved.
