# Edit comments without a service

The offline editor lets you read existing anchors and orphan history, edit comment
bodies and choose open or resolved using ordinary labelled controls. It is a
companion to `review.html`: open the code diff in another tab when needed. It does
not add comments, move anchors, merge reviews or run a server.

First add comments with `skein.py comment`. For old version-1 comments, explicitly
run `skein.py migrate-comments PACKET`. Then generate a new page:

```sh
python3 projects/review-skein/comment_editor.py page \
  /path/to/packet/comments.json /path/to/new-editor.html
```

Existing output files are refused. The generator validates every comment with the
same strict version-2 reader as the other tools. Keep `comment_editor.py`,
`comment_editor.js` and `skein.py` together when generating the page; the resulting
HTML is self-contained and needs no source files, network or server to open.

1. Open the generated HTML locally. Use Tab to reach **Skip to comments**, the
   download button, comment index, body fields and resolution selectors. Each
   body and selector has its own label; the page shows anchor state separately
   from resolution, including orphan reason and rebase history.
2. Edit a body or choose **resolved**. Choose **open** to reopen. The status
   announces how many comments changed. Empty, whitespace-only, over-20000-character
   and NUL-containing bodies block download. An orphan stays orphaned when resolved.
3. Choose **Download edits** and confirm your browser saved `skein-comment-edits.json`.
   This is a download request, not proof the browser saved a file. The page never
   writes your packet. Changes made after the last download request trigger the
   browser's ordinary leave-page prompt, where supported. There is no autosave:
   closing or reloading the page loses edits that you have not downloaded.
4. Inspect the downloaded file if desired, then apply it:

   ```sh
   python3 projects/review-skein/comment_editor.py apply \
     /path/to/packet /path/to/skein-comment-edits.json
   ```

   A successful apply reports the number of changed comments. View the result with
   `comments_view.py PACKET/comments.json`, or generate a new editor. Keep one
   writer at a time, as with the existing Skein editing CLI. This is not a locking
   or concurrent-merge protocol.

The download format is explicitly versioned: `format: "skein-comment-edits"`,
`version: 1`, `base_sha256` (SHA-256 of the exact original `comments.json` bytes),
and `document` (the ordinary strict version-2 comments object). It is an edit
envelope, not a replacement packet schema. The Python apply command validates the
whole envelope and every comment before writing. It refuses duplicate JSON keys,
unsupported versions, missing or duplicate IDs, changed order, added/removed
comments and any mutation of anchor, state, orphan reason or rebase provenance.
Only body and resolution may change. A stale baseline fails even if a different
writer changed only whitespace in `comments.json`; regenerate the editor instead
of forcing the old edits over new work.

Apply replaces only `comments.json` atomically after validation. An unchanged
download leaves the original bytes untouched. Other packet members remain
unchanged. Reapplying an already-applied change is stale and fails. Inputs must
be regular files, not symlinks, within the existing 32 MiB JSON limit. Invalid data
fails with exit 1 and no comment replacement; argument errors exit 2. The download
is not authenticated and SHA-256 identifies starting bytes, not a person.

All imported text is embedded as inert escaped JSON and displayed using DOM text
properties, not HTML. The self-contained page's CSP authorizes the exact embedded
script hash and denies network/resources, base tags and form submission. It uses
no persistent browser storage and no dependencies. Keep the page and download
private if the comments are private. JavaScript-disabled browsers show CLI fallback
instructions. The static diff and read-only comment viewer still need no script.

Run `python3 -m unittest discover -s projects/review-skein -v`. The Python tests
exercise a fresh real-Git packet and the CLI boundary; Node tests exercise editor
events and download data without a browser. Those checks do not establish actual
rendering, browser download handling, keyboard focus or screen-reader speech.
The independent non-author desktop/phone and screen-reader try required by
milestone 2 stays open; this editor must be included in that try before claiming
it is accessible or that the milestone is complete.
