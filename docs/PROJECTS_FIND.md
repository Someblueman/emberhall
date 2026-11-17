# Finding a project or idea on the Projects page

The Projects view lists what is being built now and the ideas waiting for a
council choice. The find box above those lists lets a visitor reach one entry
without reading everything.

- The box filters active project cards and shelved idea entries by title and
  the plain description shown on the card.
- The status line counts what matches, and an empty result says so with a way
  back ("Show everything").
- Filtering only hides cards on the page. Links, needs, the graveyard and
  finished-project entries are untouched.
- The query survives redraws and the background refresh, with focus preserved,
  matching the Gallery find box's behaviour.

Implementation: `site/house.js` (shelf renderer), `site/house.css` (controls
and hidden-card rule) and `tests/test_projects_find.py`.
