# R19: recorded-event press targets

Hawthorn, 26 November 2026. Source repair; independent integration and live
verification remain separate.

The Counting Room’s recorded-event buttons measured 73.265625 by 28.5 pixels
at both 390 and 1280 pixels. The scoped `.counting-jump` rule now requires
44 pixels of height and width. Text, event selection and handler code are unchanged.

The controlled trial uses the actual page, stylesheet and room renderer with
its existing 243-frame sample record. A Counting Room is added to those sample
frames so its real controls can be exercised. It is a fixture, not a live record.
Before view: no horizontal overflow; the unrelated missing balance file reports
an existing resource error. Desktop screenshot inspected: three short event
buttons beside their run descriptions.

Verification receipts use this run’s prefix and `r19-before`, `r19-verified`.
After view: buttons measure 73.265625 by 44 pixels on both screens. Real Enter
selects event 208; focus stays on that event button and real Tab moves to event
191. Both screens retain their exact viewport widths with no horizontal overflow.
Phone and desktop after screenshots inspected: the three event buttons have
comfortable height, separate rows, and a clear focus outline. Surrounding drawing
and summary sections are hidden only in this targeted after fixture to keep the
room visible in screenshots. The existing missing balance resource still reports
a resource error; no new script exception is reported. Two rejected viewer calls
used an absolute and then hidden steps path; the successful call uses a regular
room-relative JSON path.
The 23 existing counting-room, history-return and work-trail tests pass;
`git diff --check` passes. Temporary trial files are removed before handoff.
