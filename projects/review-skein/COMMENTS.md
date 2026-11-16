# Read the review comments

The comment viewer turns the packet's `comments.json` into readable terminal
output or a standalone offline HTML page. It uses Skein's existing strict
version-2 comment reader. It shows IDs, bodies, full commit/path/side/line anchors
and their source text, open/resolved status, orphan reasons and rebase history.
It reads the comments file only, does not change the packet, and needs neither
Git nor a bundle to display those comments.

```sh
python3 projects/review-skein/comments_view.py /path/to/packet/comments.json
python3 projects/review-skein/comments_view.py /path/to/packet/comments.json \
  --resolution open --state orphan --path src/ --search error
```

Both `--resolution` and `--state` default to `all`. Resolution is `open` or
`resolved`; anchor state is `anchored` or `orphan`. `--path` filters by exact
file path or directory prefix (repeatable), and `--search` filters
case-insensitively across comment ID, body, anchor path, anchor line text,
orphan reason and rebase origin. Filters combine: the example shows only open
orphans matching `src/` and `error`.
The first lines report shown/total counts, the selected filters, and totals for
the entire file, so an empty result does not imply that the packet has no comments.
Comments retain their stored order; nothing is reanchored, resolved or edited.
Control and direction markers in filter summaries are displayed as literal
Unicode escapes in both formats; filtering still uses the raw path values.
Terminal and HTML output display control/direction characters as literal Unicode
escapes, preserving ordinary Unicode prose, newlines and tabs.

For a page you can carry to a browser:

```sh
python3 projects/review-skein/comments_view.py /path/to/packet/comments.json \
  --format html > /path/to/comments-review.html
```

Choose a separate output file: shell redirection truncates an existing target,
so never redirect over `comments.json` or another packet member. The viewer itself
only writes to standard output. Open the result as a local file in a browser;
it has a comments index, skip link, headings, textual status, wrapped text and
visible link focus. All user text is escaped. It contains no scripts, external
resources or network links, and its CSP denies external resources. It is a
snapshot: regenerate it after using `skein.py edit-comment`, `resolve-comment`
or `reopen-comment`. Existing `review.html` remains the code diff.

A version-1 comments file fails with the existing `migrate-comments PACKET`
instruction. Migration is a separate deliberate action through `skein.py`;
the viewer never silently upgrades data. Invalid UTF-8, malformed JSON,
duplicate keys/IDs, invalid comments, missing/symlink inputs and inputs larger
than Skein's 32 MiB JSON limit fail with exit 1 and no rendered output. Invalid
CLI arguments exit 2; successful output exits 0. Every record is validated
before applying filters, so filtering cannot hide malformed comments.

This view reports what the comments file says. It does not authenticate authors,
verify the Git bundle or check that an anchor still exists in the diff. An orphan
remains visibly orphaned. The original file and comments model remain the record;
HTML is derived output. Markup and CLI tests do not establish browser rendering
or screen-reader speech. The non-author phone/desktop and screen-reader try
required by milestone 2 is still open.

Run the project's existing suite, including real-Git viewer lifecycle checks:

```sh
python3 -m unittest discover -s projects/review-skein -v
```
