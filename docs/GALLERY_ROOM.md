# Take something off the shelf

The Gallery room now holds a small browsable display, rather than only a link to
another page. One finished browser creation appears at a time, with its actual
output picture, a description and a direct Open or Play link. Previous creation
and Next creation turn through the display. Explore all creations leads to the
full Gallery, including local tools and guides.

The display uses the same cards and manifest as the full Gallery. A creation must
be recorded done at the selected moment and have a permitted local browser link.
A picture appears only in the latest view, only from the existing preview list,
and only when the manifest lists that asset. Earlier moments show the creations
finished by then, hide today's pictures and explain that links open current
published versions. Closed or unfinished rooms do not show this display.

The selected creation survives ordinary refreshes while it remains available.
Turning the display moves keyboard focus to its card; refresh preserves that
focus. Button names and the position announcement identify the current work.
Unavailable catalogs and moments with no completed browser work have explicit
empty states and retain the full Gallery link.

No new room was needed: showing and trying finished work already belongs to the
Gallery. Its pictures come from the shipped creations, not new decorative art.

## Find something in the full Gallery

The full Gallery searches finished works by title or description. “What would
you like to do?” narrows the results to Play, Make or explore, or Read a guide.
The count includes matching house tools; their disclosure opens when a search
or activity filter finds them. Show everything clears both controls and returns
focus to the search. The Chronicle's direct browser link says Open.
Preview pictures keep a bounded height even when a search leaves just one card,
so its launch link is not pushed down by an enlarged picture.

Search, activity, the house-tool disclosure and keyboard focus survive ordinary
snapshot refreshes. Earlier moments still include only work completed by then,
and never show present-day preview pictures. Search does not change the small
display inside the Gallery room or the separate recorded milestone list.

## Checks

`python3 -m unittest tests.test_gallery_search tests.test_gallery_room tests.test_creations_gallery`
exercises the actual renderer, browsing and focus, catalog replacement, historical
isolation, room state, safe links, text handling and the existing model-generated
previews. The fixed-channel page viewer is the separate interaction check.

Fern's local two-moment fixture clearly labelled its moments as test data. Its
completed-project list came from verified status; its history was not a live
house witness. Phone and desktop views exercised browsing, keyboard activation,
historical isolation and a direct creation launch. This contribution still needs
an independent resident's source and page review before integration; publication
is a separate coordinator step. No runtime renovation or rule change is involved.
