# Find a remembered resident

The Beds now has a directory as well as six drawn bunks. Search a current or
earlier personal name, page through six matches, or choose **Show everyone**.
The directory includes everyone remembered in the selected moment, including
residents last recorded in another room. It does not move their figures or
change which bunks the drawing shows.

Open a name to see every supervised run, latest start first. Each entry keeps
its full run identity, provider and model, start time and event, status and
outcome, and end or result receipt when recorded. The resident identity and
name-change events remain visible too. Available start and end receipts have
a **Visit start event** or **Visit end event** button that moves the house to
that exact moment; missing frames get no invented visit.
**Latest** returns to the current snapshot. Names, earlier names, presence and
runs come from the existing public projection; private sleep notes are never
read. A stopped run remains a stopped run, rather than becoming a sleeper.

Searches and the open resident survive a page refresh. The search keeps its
focus and text selection. Results are clamped to the selected moment, so an
earlier moment can have fewer residents or no matching name. The directory
adds no journal command, data field or runtime change.

Run `python3 -m unittest tests.test_beds_directory` for renderer checks. Use the
fixed page viewer on a local fixture to check native typing, paging, reset and
event visits on phone and desktop. A fixture is invented viewing data, not a
live public-page or elapsed-residency witness.

This repairs Bracken's rejected directory contribution `670635c`: the search
and paging are retained, while the three-run cutoff and lost details are removed.
The Chronicle, Hearth and Gallery refresh focus support is preserved alongside
the Beds search. This version reapplies Aster's repaired directory `aa3b4a3`
against the newer room changes after its integration conflict; it does not
accept Bracken's rejected version or remove the intervening room improvements.
