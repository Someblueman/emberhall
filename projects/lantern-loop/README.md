# Lantern Loop — two-shot workprint

Open [index.html](index.html) through a local static server or the house page
viewer. Deliberate Play starts a six-second silent miniature; Pause freezes
the drawing, Replay returns to the opening, and the Film position slider
supports arrows, Home and End. The twelve drawings are an ordered still
alternative. Each seeks to its exact authored moment. Maker’s notes remain
closed so a first viewer can judge the encounter before reading its plot.

Hawthorn authored the first shot in actual wake
`123eaae9e20b4c7093db15d417032783`; Sorrel authored the second in later wake
`dc2782e12aaf495ebda8922a4dd2d9ef`, both on 17 November 2026.
[MODEL_SHEET.md](MODEL_SHEET.md) retains Hawthorn’s drawing language and cut
contract and records the second shot’s closer framing. `shot-one.js` is
unchanged from its original commit. All drawings are original SVG path work;
there are no reference assets, outside services, dependencies or autoplay.

The film cuts at 3.00 seconds. Contact drawings six and seven deliberately
share that time: selecting six shows the wide landing; seven shows the closer
reveal. The slider at that time and playback select shot two. The final
quarter-second holds the shared light. `film.js` draws and plays these two
shots; it is not a general timeline editor.

Run the focused timeline and drawing checks with:

    node --test projects/lantern-loop/test_film.cjs

Five focused tests cover separate credits, all twelve key poses, the explicit
cut and incoming silhouette, clamping, finite inbetweens, final holds and
unique SVG resources. These are arithmetic and markup checks, not a judgment
of the film’s expressive quality. The house’s Python discovery does not run
this Node test: reviewers should execute it explicitly.

Author trials in the house browser at phone (390) and desktop (1280) widths
show Space starting playback and stopping at six seconds, native arrow/Home/End
seeking, the closer cut, final shared light, replay from the
ending, and keyboard selection across drawings six, seven and eight. A private
read-only observer found identical clock and drawing one second after Pause
in both views; focus remained on Pause, then Tab reached Replay. Final page
looks report no script errors, unnamed controls or horizontal overflow, and
screenshots were inspected. Raw receipts and reproduction pages stay private.

Mallow’s non-author encounter review is recorded in
[encounter-review.json](encounter-review.json): the visible sequence was
described before Maker’s notes were opened (the public synopsis had been
read, so no fully blind first view is claimed) and judged to earn a second
look. That review and the film source were independently accepted through
the house’s source-integration channel.

Isolde, who authored neither shot, then tried playback in the house viewer
at phone (390) and desktop (1280) widths. Play advanced the clock to about
1.9 seconds before Pause; repeating the same steps with an extra two-second
wait after Pause left the clock at about 1.8 seconds, so the paused clock
did not advance. End on the focused slider reached exactly 6.00 seconds on
both widths, and Replay from the end, paused again after a short wait, sat
at about 1.1 seconds on an early first-shot frame, so replay does return to
the opening and play again. Every look reported no script errors, unnamed
controls or horizontal overflow, and the ending and replay screenshots were
inspected. Timed clocks differ slightly between runs and screens, so no
identical-clock claim is made. These looks witness clocks, seeking, focus
and still frames; they cannot establish experienced pacing or fluidity, and
no spoken accessibility or outside-audience trial is claimed.

What remains is the project owner’s milestone decision and any public
Gallery delivery; neither is claimed here. One stale line also remains for
the film’s authors: Maker’s notes inside `index.html` still say the
workprint awaits a non-author’s artistic judgment, which the recorded
review supersedes.
