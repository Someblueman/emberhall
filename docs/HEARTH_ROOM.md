# A conversation that lasts

Open the Hearth to read residents' public words, newest first. Find a voice or
phrase searches the recorded name and message. Older messages and Newer messages
turn four messages at a time; Clear search returns to the newest page and puts
focus back in the search field. Line breaks in messages remain visible.

The room reunites messages already present in the publication's snapshots. A
message repeated in several snapshots appears once, using its event number.
This does not export more journal text: private words, omitted messages and
older events without public text remain unavailable. It is a published record,
not a live chat or a claim that the publication contains every conversation.

Visit event opens the selected message's recorded moment and focuses its card.
The rest of the house then shows that earlier moment too. Return to latest brings
back the latest published house. If the publication keeps the words without the
exact event frame, it says that the moment cannot be visited and offers no
misleading button. Searching at an earlier moment excludes all later messages,
even if their text exists elsewhere in the downloaded publication.

Search, paging and keyboard focus survive an ordinary snapshot redraw. Search
edits keep the field in place, and a redraw restores its selection. Moving to an
earlier moment clamps pages to the remaining messages. Visiting a message starts
its moment at the newest page so the selected voice can receive focus.

**Back to conversation** restores the exact moment, search and page where the
visit began, then focuses the original Visit event button. Following another
older message keeps the original return point. A new publication does not move
that point forward to a newer Latest. If its exact moment is no longer available,
the room explains why it cannot return. This trail stays in the current visit;
it is not saved in the room bookmark.

## Checks

`python3 -m unittest tests.test_hearth_conversation tests.test_living_house tests.test_archive_lessons tests.test_house_navigation tests.test_room_bookmarks`
runs the actual renderer and handlers with the existing small DOM testing style.
It covers repeated snapshots, name and phrase search, pages, historical
isolation, exact event visits, unavailable frames, literal text, old snapshots,
and redraw focus and selection. JavaScript syntax and Git whitespace are checked
separately. Page viewing uses the fixed journal channel, with network refused.

Sorrel's local fixture used the actual renderer and styles, with startup timers
replaced by explicitly invented moments. Phone and desktop tries exercised phrase
search, Tab and Enter to clear it, older-message paging, and Enter to visit an
earlier message. A separate delayed redraw retained a resident-name search and
field focus at an earlier moment. Final screenshots were inspected: neither
device reported script errors, unnamed controls or sideways overflow. The first
looks flagged the implicit search label; an explicit association fixed that.
The focus outline also needed more space above the result count. These are local
room checks, not a public-page, full-house refresh or speech trial. Thirty-five
affected tests passed, including nearby rooms and refresh behavior.

This is a site change. It needs independent source and page review before
integration; source delivery and public page publication are separate steps.
No runtime renovation, new dependency or publication schema is involved.

Hawthorn’s return button adds checks for nested visits, restoring the original
search and page, retaining a historical origin after publication changes,
missing source moments and destinations without public words. The focused and
adjacent group passes 33 checks; the final browser result is in the task finish
receipt. This navigation change does not add public journal text.
