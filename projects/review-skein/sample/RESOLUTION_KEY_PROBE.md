# Resolution-menu keyboard probe (Isolde)

Question: both recorded editor tries left TRIAL_EDITOR step 5 PARTIAL
because ArrowDown alone on the focused resolution menu did not change
its value under the house page viewer, while setting the value directly
did. Was that an editor defect, the wrong key sequence, or a viewer
limit? This probe is a diagnostic, not an independent try: I ran an
earlier editor try and had read the editor source for this question.
The resolution control is a plain native select element whose only
listener is `change` (`comment_editor.js`, last changed at c8b8e10).

Setup: fresh disposable packet from `example.py` (base
69ef269bc9189b85299e759e41cabab467dcdcac, head
cc7f33bba10afe88837c23df54811f78d1337d50, comments.json sha256
15d7971de63e517e019ee792056d8fb43172ededeaf3ab4bc1ba75873c4607ce —
the same packet identity as both tries), compose page generated at
source 8519312. Each look started from the original page; a `focus`
step placed focus on Resolution for greeting (an assisted starting
position, so this says nothing about keyboard reachability, which both
tries already observed). Viewer requests:
`802dbb43c9054dc1830fe09327809e62-view-` plus the suffixes below.
Desktop and phone agreed in every look; no script errors.

On the editor page, the greeting resolution stayed `open` with
"6 comments. 0 changed" and `asked_before_leaving: false` after each of:

- `arrow-alone`: focus, ArrowDown (replicates both tries);
- `space-open`: focus, Space, ArrowDown, Enter;
- `enter-open`: focus, Enter, ArrowDown, Enter;
- `arrow-enter`: focus, ArrowDown, Enter.

Discriminating control: a minimal static page holding one plain
two-option select (`open`/`resolved`), no editor code and no content
policy, which writes its value, change count and received keys into
the page text. The same viewer returned value `open`, changes 0 after
focus+ArrowDown (`min-arrow`), focus+Space+ArrowDown+Enter
(`min-space`), click+ArrowDown+Enter (`min-click`) and focus+End
(`min-end`). The page's own key log shows the keys were delivered as
keydown/keyup events in every listed sequence; none of these four
attempts changed the value or produced a `change` event.

Bounded conclusion: all four listed editor sequences and all four
minimal-page sequences left the select unchanged in these viewer
looks. Reproducing that result without editor code suggests viewer
behaviour contributes, but does not establish the cause or rule out
an effective sequence on either page. Other sequences and pages
remain untested. For these recorded trials, step 5 has two results:
resolve/reopen is PASS by direct value setting in both tries, while
keyboard menu operation remains NOT RUN because no transition was
observed. Speech, zoom and the saved download also remain NOT RUN.
A keyboard witness would need an actually observed transition with
its exact keys recorded, through the viewer or another capable tool.
The project owner assesses these limits for milestone 2.
Generated packet and pages stayed private; no screenshots or view
dumps are committed.

Sorrel narrowed this conclusion after independent rejection 11805 of
the original contribution. The setup, listed actions and observed
values above are retained; this correction adds no new trial.
