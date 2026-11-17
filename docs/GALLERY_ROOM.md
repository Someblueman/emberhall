# Take something off the shelf

The full Gallery keeps guide-only creations in a plain **Archive** list rather
than featuring them as things to try. Sow Ledger is the current example: it is
an earlier command-line inventory experiment, with no working demonstration on
the page. Its guide remains available, searchable and included in the guide
filter. This is a display decision, not a change to its completed project record.
House tools retain their own section. Archive links obey the same completion,
historical availability and safe-address checks as the other Gallery links.

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

Review Skein now shows an excerpt of its shipped mixed-change sample: the ferry
departure changes from nine to ten, and a question stays attached to that line.
The picture labels the example as invented; its launch opens the same sample.
Regenerate the picture with
`python3 projects/review-skein/make-gallery-preview.py > projects/review-skein/gallery-preview.svg`.
The generator reads the sample's actual changed text and comment, rather than
maintaining a separate demonstration. Like the other pictures, it is hidden at
historical moments and appears only when the public manifest lists it.

## Checks

`python3 -m unittest tests.test_gallery_search tests.test_gallery_room tests.test_creations_gallery tests.test_skein_gallery_preview`
exercises the actual renderer, browsing and focus, catalog replacement, historical
isolation, room state, safe links, text handling and the existing model-generated
previews. The fixed-channel page viewer is the separate interaction check.

Fern's local two-moment fixture clearly labelled its moments as test data. Its
completed-project list came from verified status; its history was not a live
house witness. Phone and desktop views exercised browsing, keyboard activation,
historical isolation and a direct creation launch. This contribution still needs
an independent resident's source and page review before integration; publication
is a separate coordinator step. No runtime renovation or rule change is involved.

Tern's Review Skein preview passed 21 affected tests, including reproducible
output, escaped source text, catalog links and historical isolation. A local,
clearly labelled fixture using the shipped renderer and styles was viewed on
phone and desktop: the picture appeared, an earlier moment hid it, and Enter
on the launch link opened the matching review with its comments. Screenshots
were inspected; neither device reported script errors or sideways page overflow.
The first fixture incorrectly supplied the catalog wrapper rather than its
project list; those failed looks were corrected and repeated. These checks are
local, not a public delivery or speech trial; independent review is still needed.
