# Public house snapshot and history

The page opens on `current.json` and draws the latest frame. This snapshot
shares the journal head, source head and event count in `head.json`. The
publisher resolves only the latest frame and its referenced scar descriptions.
The checked-in `site/history.json` is a test fixture.

The archived 52,519-event publication expands to 5.86 MB for the latest
projection alone. For projections over 1,400,000 bytes, `current.json` points to
a hash-named gzip file containing the full projection. The archived snapshot
takes about 1.32 MB across both files. The publisher fails before changing the
Pages ref if the files together exceed 1,400,000 bytes. The browser decompresses
the companion with `DecompressionStream("gzip")`.

The slider, Previous and Next, Home on the focused slider, and event-number
jumps use the full record after the first history action. Sealed parts decode
one at a time and the browser caches their immutable files. The page polls
`head.json` every ten seconds. A changed head reloads the current snapshot
until the full record has been opened. After that, a changed head reloads the
full record and keeps the selected moment if you are browsing the past.
Unchanged polls advance clock and lease cues locally. Gallery images load
lazily, and the Signal Garden exhibit waits until the Gallery opens.

## Build and check locally

Run this from a checkout with the fix committed and the verified journal
available. The publisher reads the site files from source HEAD and updates
the local `codex/house-pages` branch.

```sh
python3 -m house.publish --repo .
page_dir=$(mktemp -d /tmp/emberhall-pages.XXXXXX)
git archive codex/house-pages | tar -xf - -C "$page_dir"
python3 -m http.server 8000 --bind 127.0.0.1 --directory "$page_dir"
```

Serve the entire extracted tree. It includes `index.html`, `house.js`,
`house.css`, `current.json`, the optional `current/*.json.gz`, `head.json`,
`history.json`, the `history/` parts and the published assets.

In a fresh Playwright context at 390 px, open `http://127.0.0.1:8000/`.
Check that the latest event renders, the response total stays below 2 MB and
Chromium's JS heap stays below 150 MB after settling. Wait at least 65 seconds
and check again. Only `head.json` should repeat while the publication is
unchanged. Then focus the history slider and press Home, click Next and
Previous, submit an event number, and return to Latest. Check that the first
history action fetches the full record and later actions reuse it. To verify
the live update path, rebuild and re-extract a newer journal publication while
a fresh tab stays open. The tab should fetch the new snapshot after the next
head poll and show the new latest event.
