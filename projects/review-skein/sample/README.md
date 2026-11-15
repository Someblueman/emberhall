# Skein sample page (milestone 2, small pair)

A page to inspect, **not a verifiable full packet**: `changes.bundle`
is deliberately not committed (it was 18,555,885 bytes in the export
below), so packet verification cannot run without it
on this committed sample (`skein.py verify` needs the bundle).
Verification was run on the full export in a temporary directory
before the bundle was excluded; see Reproduction.

## Commits

- Base: `aba06b970c1ddd2544cda6030e20cefd1aa517ec`
- Head: `d0bf39549b9d6a1e76c5740d834554cde6e881dc`

This pair adds only the compact comment viewer:
`projects/review-skein/COMMENTS.md`, `comments_view.py`, and
`test_comments_view.py` (370 added lines). `packet.json` records
exactly the base and head above.

## Files and sizes

| File | Bytes | SHA256 |
| --- | ---: | --- |
| `milestone-2/review.html` | 100518 | `91ae47c281e4fc591c45619b6ec2a458fccbb92652b35c71563ea8ebedc6c845` |
| `milestone-2/packet.json` | 944 | `12a359fea9198ca5742ff6241a8cca84d7abf1554ccf8c89a3d05d8f71b048de` |
| `milestone-2/anchors.json` | 87404 | `25a5d6fcaf3451f9c03b6b6511a9f311ecfa6d22ac8a4b9218061e6da8724c3c` |
| `milestone-2/comments.json` | 74 | `29d6a5d00a728f1491d13a054663c7b5fd74641178b20bf5e31fc203cad2f9fb` |
| `README.md` (this file) | 3679 | — |
| **Total (all five)** | **192619** | — |

The total is strictly under the 200,000-byte cap. The four generated
files are untrimmed exporter output; none was hand-edited.

## Reproduction

In a clean temporary clone, using the head commit's own exporter:

```sh
git clone <this-repository> /tmp/skein-sample-clone
git -C /tmp/skein-sample-clone checkout d0bf39549b9d6a1e76c5740d834554cde6e881dc
python3 /tmp/skein-sample-clone/projects/review-skein/skein.py export \
  /tmp/skein-sample-clone \
  aba06b970c1ddd2544cda6030e20cefd1aa517ec \
  d0bf39549b9d6a1e76c5740d834554cde6e881dc \
  /tmp/skein-sample-export
```

This was run twice into two fresh output directories; all four
generated files above were byte-identical across both exports
(SHA256 in the table). The export also writes `changes.bundle`
(18,555,885 bytes, not committed); on that full temporary export,
`python3 skein.py verify /tmp/skein-sample-export` exited 0.
Compare a fresh export's four generated files against
`milestone-2/` with `cmp` or `shasum -a 256`.

## Open it

No server, network, or JavaScript is needed.

- Desktop: open `milestone-2/review.html` in any browser
  (double-click it, or use a `file://` URL).
- Phone: copy the `sample/` folder to the phone and open
  `milestone-2/review.html` in the phone browser.

## What to inspect

- The heading identity (base/head commits) and the skip link to
  the changed-files list.
- The three added files, each a side-by-side table with line
  numbers and status words, readable without colour or a mouse.
- `packet.json`: `format`, `version`, exact base/head, file list.
- `anchors.json`: one anchor per new line (commit/path/side/line/text).
- `comments.json`: format `review-skein-comments`, version 2,
  empty comment list.

Parsed-HTML checks on `review.html`: `<html lang="en">`, a
Content-Security-Policy meta (`default-src 'none'; style-src
'unsafe-inline'`), no `<script>` element, no `src` attribute, and
every `href` is an in-page `#fragment`; no attribute contains an
`http` reference. The literal text `https://example.invalid`
appears only as escaped, inert code text inside the diff of
`test_comments_view.py`, never as a tag or attribute.

This sample makes no real-browser, screen-reader, or
milestone-2-completion claim; the non-author try remains separate.
The rejected oversized candidate `e4c28d90` is preserved elsewhere
and is not duplicated here.
