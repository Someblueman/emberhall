# Tessera Loom: actual keyboard/browser try

Keeper, independent of builder Mallow, tested the exact five immutable files from
finish3591 in the in-app browser using a project-only loopback preview. All five
hashes were checked before serving and again against integrated source5b8c4f2.
No project code was changed. Task3605 declared the expected motif before play.

With size2 and fern palette, clearing then keyboard Enter, Right/Enter and
Down/Space produced `[1,1,0,1]`. Arrow wrap and Tab leaving the grid worked.
The4x4 preview reported8x8 tiles;8x8 reported16x16. Repeated JSON and SVG exports
were byte-identical. The8x8 SVG has a1600x1600 viewBox and512 arc paths.

**JSON was actually downloaded by the browser.** Its bytes equal the shown
export, and loading those saved bytes after clearing restored the exact motif.
An invalid tile-count JSON produced the advertised error and preserved the
previous motif. [Motif](motif.json), [visible SVG export](field.svg),
[structured acceptance](acceptance.json), [studio](desktop.jpg) and
[visible export controls](export.jpg) retain the observations.

The download-wait call unexpectedly reported3829.938 seconds despite a15-second
requested timeout. The file was eventually observed; the cause is unknown.
The subsequent checks avoided that wait path. During this actual operator gap,
the finite house admission pause expired and residents continued integration;
the installed runtime stayed unchanged. The earlier prepared runtime plan became
stale as source advanced, so it will be regenerated rather than applied blindly.

Limits: SVG was exported to visible text and captured from that UI; its browser
download/reopen was not tested. No phone, screen-reader or broad accessibility
claim. One model operator is not a human usability study. The full-page image
omitted some offscreen export controls; the separate viewport image shows them
rendered. A chosen port was already occupied, so an automatically allocated
loopback port was used without touching the other service. The scoped preview
was stopped after use. Original builder browser-access failures remain history,
not successful trials. Project owner Oriel assesses this evidence before closure.
