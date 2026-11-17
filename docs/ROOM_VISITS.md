# Visiting rooms without losing your place

Opening a room from the drawing or the room buttons focuses its contents and
brings them into view. The next Tab reaches **Back to rooms**. That button returns
to the selected room in the doorway list, so another Tab continues the walk.
Escape does the same while the room contents themselves have focus. Escape
inside a search field, selector or other control keeps its ordinary behavior.
Returning focus keeps the current room bookmark and historical moment.

Room drawing targets and doorway buttons have stable, encoded identifiers.
The normal page refresh restores either target, or the room contents, when it
still exists after the redraw. A room absent from the selected moment is still
absent; this does not add rooms or expose later history.

## Verification, 17 November 2026

Tern reproduced the earlier failure with the unchanged renderer: Enter on the
Hearth drawing dropped focus to the page body on both phone and desktop.
The repaired renderer passed 26 focused and adjacent Python/Node checks,
JavaScript syntax and whitespace checks. Existing bookmark, upper-floor,
missing-room, browser history and skip-navigation behavior stays covered.

House browser trials at phone and desktop widths exercised Enter, Space, Tab,
Escape, the return button and real renderer refreshes while the drawing,
doorway and contents held focus. A search field retained focus on Escape.
Read-only trial observations placed the phone contents below the sticky
navigation and the returned doorway inside the screen. Screenshots were
inspected. Passing trials had no script errors, unnamed controls or horizontal
overflow. Early previews lacked an optional accounts data file; that private
fixture was corrected before the clean trials. No screen-reader or public
publication trial is claimed.

Trials use the repository's dated 243-event history, plus a separately labelled
room-list stress fixture; they are not a new journal export. Raw receipts,
pictures and small trial pages stay in the private mailbox, outside Git.
A different resident must review and integrate the source before delivery.
