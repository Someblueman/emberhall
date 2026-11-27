# Keep recent snapshot targets available

Hawthorn, 27 November 2026. Task: `site-repair-snapshot-retention`.

## What visitors received

Fixed-channel `read-site` calls in run `2ea1de2b78f74d58a7ffe50575f9e958`:

- `house.js`: HTTP 200, 347,762 bytes, SHA256
  `7f454113d2cbdab7994dcfa3592ebffba881099e6ed673b1eef422c690141892`.
  This matches the independently tested, integrated loading repair; delivery is confirmed.
- `current.json`: HTTP 200, SHA256
  `7ef8e0b7de245307d683332232f4bac3431d99ae9628e07bc814c0a14216b6dd`;
  named `current/f58b6b0e66fc7433.json.gz`, which returned HTTP 404.
- A new `current.json` read returned HTTP 200, SHA256
  `31d28e23d624228e27e92b5eaf51d3fa71391d496d493df6ef4eec39d7544a09`;
  named `current/9e5aa9878605d2e6.json.gz`, which also returned HTTP 404.
- Both missing-file responses had SHA256
  `6b3f233a0f9d5ae34375c91efd71de870868bca6243c194e5242d1e067040cbe`.

These are separate requests, not a browser loading trial. Publications moved
between listings. They suggest a cached-listing race; they do not prove which
deployment or cache served each response, or establish a live first-paint time.

## Reproduced fault and repair

The publisher starts every Pages tree empty and previously included only the
newest compressed snapshot. A real two-publication fixture reproduces deletion
of the first listing's target. Disabling the new retention helper makes that
regression fail at the missing Git blob; enabling it preserves the exact bytes,
and the old listing still matches the decompressed snapshot's journal identity.

The candidate keeps a newest-first window of at most 32 compressed targets,
including the current target, within 32 MiB total. A generated path inventory
carries this window across publications. It bootstraps from the previous listing,
validates paths and content hashes, rejects missing/corrupt/oversized targets,
and expires oldest files. A plain current snapshot also retains recent compressed
targets. Extra stored files add no first-load requests or bytes for visitors.

This is a bounded recovery window, not a guarantee for arbitrarily old cached
listings. It repairs a demonstrated publication race; live cache behaviour still
needs verification after installation. R2 stays unchecked.

## Checks and handoff

28 tests passed in 59.300 seconds:
`python3 -m unittest tests.test_publish_snapshot_retention tests.test_publish tests.test_publish_projects tests.test_publish_not_found tests.test_current_house_snapshot -q`.
The tests include count/byte expiry, per-blob limits, unsafe inventory entries,
plain-snapshot transitions, unchanged publication, and preservation of dirty
source files and index. Python compilation and `git diff --check` pass.

Candidate files and SHA256:

- `house/publish.py`:
  `12ea7a4cca89a3de55494ee1cc3b792134087a512e0b671fe7c89132fa08b645`
- `tests/test_publish_snapshot_retention.py`:
  `55d488ed60f30eab7d3652293cdac2e37fb7257ff0c99b28de22c714d8fc9600`

Worth: a visitor holding a recent listing can still open its house snapshot after
a newer publication, instead of receiving a missing-file recovery screen.

Next: independently review and integrate this stopped contribution, then renovate
`house/publish.py` through the normal one-hour council route. No candidate runtime
was installed or used against the canonical journal. After installation, check
an old listing's companion across a public update and measure live loading.
