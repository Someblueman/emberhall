# Skein probe — reading a packet without a browser

`probe.py` looks at an exported Skein packet the way a careful reader would
look at the markup: it never opens a browser, never uses the network and never
changes the packet. It exists because milestone 2 of the great work needs an
independent phone/desktop and screen-reader try, and because a review packet
that travels by hand should be checkable by the person who receives it.

The probe is a **pre-flight check, not a screen reader**. See the honest
boundary below.

## Run it

```sh
python3 projects/review-skein/probe.py audit /path/to/packet
python3 projects/review-skein/probe.py audit /path/to/standalone.html
python3 projects/review-skein/probe.py audit /path/to/packet --json
python3 projects/review-skein/probe.py transcript /path/to/packet --max-rows 200
```

`audit` prints one line per finding and exits **1** when it finds an error,
**0** when it does not, and **2** when the packet or HTML file cannot be read at
all. `transcript` prints the reading and exits 0. When given a packet directory,
both read only `review.html` and `packet.json`; `changes.bundle`, `anchors.json`
and `comments.json` are left alone. When given a standalone regular HTML file
(such as saved `review_view.py --format html` or `comments_view.py --format html`
output), both probe that file directly and record a `standalone-html` notice.

## What the audit checks

Errors are defects a reader would trip over:

| code | what it means |
| --- | --- |
| `missing-html` / `missing-lang` | the page has no `<html>`, or it does not declare its language |
| `script-element` / `inline-handler` | the page runs code, which a static packet must not |
| `form-element` | the page asks for input, which a static packet must not |
| `external-reference` | a link, image, media or form target (`href`, `src`, `srcset`, `action`, `data`, `poster`, `formaction`) uses anything other than an in-page `#fragment`, leaving the self-contained `review.html` boundary |
| `duplicate-id` | two elements share one id, so a name points at the wrong thing |
| `broken-reference` | an `aria-labelledby`, `aria-describedby`, `aria-controls` or `for` names an id that is not there |
| `broken-fragment` | an in-page link points at an id that is not there |
| `heading-skip` | a heading jumps a level (`h1` straight to `h3`) |
| `empty-heading` | a heading says nothing (or is hidden from assistive technology) |
| `table-without-caption` | a table has no accessible caption, so its meaning is unstated |
| `table-without-column-headers` | a table has no accessible column header cells (`<th scope="col">`) |
| `row-without-words` | a diff row lacks an accessible `<th scope="row">` header with spoken status words (for example when status text or `scope="row"` is missing, or when the cell/row/ancestor is hidden with `aria-hidden="true"`, `hidden` or `display:none`) |
| `packet-json-unreadable` | `packet.json` is present but cannot be read or parsed as a JSON object |

Notices are worth a human glance but are not defects on their own:
`odd-lang`, `unlabelled-nav`, `unlabelled-section`, `shared-row-label` (two
row classes that read the same way), `packet-json-missing`,
`unexpected-format` and `packet-identity`.

**Supported URL boundary.** A Skein `review.html` page is a single self-contained
HTML document whose Content Security Policy is `default-src 'none'; style-src 'unsafe-inline'`.
Only in-page `#fragment` links (`#files`, `#file-1`, …) stay inside that page.
Any scheme (`http:`, `https:`, `data:`, `javascript:`, `file:`), protocol-relative
URL (`//...`), root path (`/...`), parent traversal (`../...`) or relative file
reference (`outside.png`) is diagnosed as `external-reference` without opening
targets on disk or using the network.

The `row-without-words` check is the one that matters most for this project.
Every non-header diff row must carry its status (`Added`, `Removed`, `Changed`,
`Unchanged` or `Note`) in an accessible `<th scope="row">` cell that is not
excluded by `aria-hidden="true"`, `hidden`, `display:none` or `visibility:hidden`
on the cell, row or any ancestor. A row whose status is hidden from assistive
technology is reported as an error by `audit` and excluded from `transcript`.

## What the transcript is

`transcript` walks the page in document order and prints what a screen reader
would meet: the document language and title, the skip link, headings, the
changed-files index, each file section with its name, and every table row with
its spoken status and its old and new text. A reviewer with no browser can
read the packet's content this way, and can see at once whether the page
announces what it shows.

```text
Document language: en
Title: Skein review packet
Skip link: Skip to changed files -> #files
Heading 1: Skein review packet
Navigation Changed files:
  - Modified: src/greet.py
Section Modified: src/greet.py:
Heading 2: Modified: src/greet.py
Table: Old line and new line; 2 old / 2 new
  Old | New | Base text | Head text
  Unchanged. 1 | 1 | first | first
  Added. | 2 |  | second
```

The transcript is bounded by `--max-rows` so a large packet cannot flood a
terminal, and it says how many rows it left out.

## The honest boundary

The probe reads the markup. It cannot see a rendered page. It does not judge
contrast, real focus order, how speech actually sounds, whether a table scrolls
on a phone, or how a person feels reading the diff. A transcript of a document
order is an approximation of a reading order, not the reading order itself.

So the probe is **not** the milestone-2 independent try, and it does not
complete it. Milestone 2 still needs a real browser and screen-reader try by
someone who did not write the page: a phone and a desktop, a screen reader,
and the packet in front of them. What the probe does is make that try
possible for anyone, and make its result easier to argue about, by turning the
page's own claims into checks that can be run anywhere, including on a machine
with no browser at all.

## Tests

```sh
python3 -m unittest discover -s projects/review-skein -v
```

`test_probe.py` feeds the probe static pages — one clean and one for each
defect, including missing `scope="row"` headers, `aria-hidden="true"` status
cells/rows/ancestors, and relative or `..` references leaving `review.html` —
and also exports a real Git fixture packet through `skein.export_packet` to
verify that a real export audits with 0 errors, produces a complete spoken
transcript, and leaves all exported packet bytes unchanged.

## Ownership

This probe belongs to `review-skein-milestone-2-probe` and its boundary repair
`review-skein-probe-boundary-repair`: it owns `projects/review-skein/probe.py`,
`projects/review-skein/test_probe.py` and `projects/review-skein/PROBE.md`
(alongside `projects/review-skein/TRIAL.md`). It does not touch `skein.py`,
`test_skein.py` or `README.md`, and it does not change the packet format, the
comment model or the exporter.
