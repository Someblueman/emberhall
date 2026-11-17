# Catch up in the Parlor

The Parlor collects finished tasks, room changes and project choices from the
selected history range. By default it covers the latest fifty recorded events
through the moment being viewed. This is a visitor's range, not a resident's
saved reading cursor or an acknowledgement of the journal.

Each group shows eight changes at a time. **Earlier** and **Later** controls
reach the rest, with a visible range such as “9–16 of 18”. Each group keeps its
own page. Turning a page focuses that group's results; each **Jump** has an
accessible name identifying the change and event it opens. A jump keeps the
Parlor selected while moving the house history to the recorded event, then
focuses the group's historical results. Several room or project changes at
one event have distinct control identifiers for focus restoration.

**Update** and **Latest 50** reset all three groups to their first page and
return focus to the range input. Ordinary redraws retain the group pages.
When an earlier historical moment has fewer changes, the page is clamped to
its last available page. Later changes never enter that earlier digest.
Ranges with eight or fewer changes need no paging controls. Names are rendered
as text, including names that look like markup.

The earlier renderer counted every change but silently stopped each group
after the first eight. The room now exposes those previously unreachable
entries without adding another room or changing the journal or its protocols.

## Verification

The focused tests in `tests/test_catchup_paging.py` execute the actual renderer
JavaScript against a small simulated document. They cover eighteen changes in
each group, independent paging, range resets, historical clamping, a jump from
a later page, focus, labels and text safety. Existing catch-up, refresh,
bookmark, navigation, living-house and Gallery tests cover adjacent behavior.
These are logic tests, not browser rendering or speech evidence.

Twenty-five focused and adjacent tests passed, as did JavaScript syntax and
whitespace checks. The fixed-channel viewer separately exercised all three
groups' later pages and a native Enter jump to an earlier moment at phone
and desktop widths. Both devices reported no script errors, unlabelled
controls or horizontal overflow. The first jump exposed lost focus after
redraw; the repaired jump focused the historical results on both devices.
Several rooms changing at one event also exposed duplicate Jump identifiers;
the focused regression now checks their uniqueness. The final phone and
desktop screenshots were opened and inspected.
The shorter-range trial also caught the shared flex style overriding the
native hidden attribute. The renderer now explicitly hides short groups'
page controls; this does not change that shared style for other rooms.

Those browser checks use an explicitly labelled local fixture with invented
changes. Viewer results and screenshots stay in the resident's private mailbox.
A local fixture is not a visit to the current public house, and the viewer does not establish browser
Back or screen-reader behavior. Independent source review and publication
remain separate from this private-room implementation.
