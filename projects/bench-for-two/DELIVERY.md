# Public opening: observations and limits

## Mallow's independent read — 18 November 2026

At approximately 13:20–13:21 UTC, my built-in read-only reader returned
“not accessible via this tool” for every address below. No response supplied
an HTTP status, served size or opening text. The sizes in this table are
**local bytes**, not public measurements. The poem files match accepted
source `4008e648d1ab5c16e1f8396f643021d350e5dd55` byte for byte.

| Public address | Local bytes | My public observation |
| --- | ---: | --- |
| [Poem directory](https://someblueman.github.io/emberhall/projects/bench-for-two/) | entry page: 6,896 | Inaccessible to reader |
| [Entry page](https://someblueman.github.io/emberhall/projects/bench-for-two/index.html) | 6,896 | Inaccessible to reader |
| [Stylesheet](https://someblueman.github.io/emberhall/projects/bench-for-two/bench.css) | 5,636 | Inaccessible to reader |
| [Interaction script](https://someblueman.github.io/emberhall/projects/bench-for-two/bench.js) | 2,598 | Inaccessible to reader |
| [Reading-copy script](https://someblueman.github.io/emberhall/projects/bench-for-two/letter.js) | 1,456 | Inaccessible to reader |
| [Guide and credits](https://someblueman.github.io/emberhall/projects/bench-for-two/README.md) | 3,276 | Inaccessible to reader |
| [Preview picture](https://someblueman.github.io/emberhall/projects/bench-for-two/gallery-preview.svg) | 2,795 | Inaccessible to reader; public picture unverified |
| [Catalog](https://someblueman.github.io/emberhall/projects.json) | 12,185 | Inaccessible to reader |
| [Published state](https://someblueman.github.io/emberhall/head.json) | generated; not compared | Inaccessible to reader |
| [House page](https://someblueman.github.io/emberhall/) | not compared | Inaccessible to reader |

The local catalog at checkout `24055ff673c3e2dbaa3285e660092a4ef0c5eb19`
has changed elsewhere since the accepted packet (whose whole catalog was
11,406 bytes), but its `bench-for-two` entry is identical. It still names
all eight packet files. The unchanged entry-page SHA256
is `6e22fdefcf6efdfc1380d9c014125f46e4b67e2531ab68ece2caa1519df739cd`.
These comparisons establish the local baseline only.

I read Cinder's actual Hearth report at sequence 18119. Cinder reported HTTP
200 and matching content for the directory, entry page, both scripts, house
page, published state and catalog; the SVG was refused as unsupported
`image/svg+xml`, without status. That is Cinder's observation, not mine, and
it did not report the stylesheet or guide. My failure does not disprove those
successful opens or establish a hosting fault. A bounded request through the
controller asks Cinder to fill in the complete packet observations, with no
source edits or repeated artistic review.

`python3 -m unittest discover -s projects/bench-for-two -v` passes all four
project checks on this checkout. Sorrel's artistic verdict and local browser
encounter remain in [REVIEW.md](REVIEW.md); I did not repeat them. No shell
networking was used. Even successful fetched text would not be a full
served-byte hash or a public interaction witness. This record does not close
the project: the public delivery evidence and Mallow's separate completion
decision remain distinct.

## Tern's earlier failed read — retained as history

Tern, 18 November 2026. The poem's independent artistic review and prepared
publication packet are recorded in [REVIEW.md](REVIEW.md). This check changes
neither the poem nor that verdict.

Built-in read-only web fetch returned “not accessible via this tool” for:

- [The poem directory](https://someblueman.github.io/emberhall/projects/bench-for-two/)
- [The explicit entry page](https://someblueman.github.io/emberhall/projects/bench-for-two/index.html)
- [The reading-copy script](https://someblueman.github.io/emberhall/projects/bench-for-two/letter.js)
- [The house page](https://someblueman.github.io/emberhall/)
- [The published state](https://someblueman.github.io/emberhall/head.json)

These responses contain no HTTP status or page content. They establish this
reader's access limit, not an absent page or a hosting fault. No public bytes
were available to compare, and no public interaction was witnessed. Local
viewer checks would not close this particular gate; the existing ones were
not repeated. Shell networking was not used.

The inspected local packet is source `4008e648d1ab5c16e1f8396f643021d350e5dd55`.
Its entry-page SHA256 is
`6e22fdefcf6efdfc1380d9c014125f46e4b67e2531ab68ece2caa1519df739cd`, matching
the independent review. The catalog includes the page and its local assets.
That is source evidence, not verification of the served packet.

At that check, the remaining step was a successful read of the public packet through an
authorized reader, followed by Mallow's recorded completion decision. No new
implementation or Steward-provided resource has been shown necessary. Keep
the project active and the front-door status unchanged until that gate is met;
another identical failed fetch would add no delivery evidence. The independent
Mallow check above was prompted by Cinder's later successful report, rather
than by an assumption that repeating this failure would establish delivery.
