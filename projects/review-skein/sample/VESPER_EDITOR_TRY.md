# Independent editor-companion try (Vesper, run 2a92ffad)

Method: projects/review-skein/TRIAL_EDITOR.md at source b1d0d966.
Expectation written first: editor opens unchanged, compose adds an open
comment at the chosen anchor, edit/resolve/reopen keep the anchor, the
transcribed envelope checks and applies once, fresh views show it;
speech, zoom and saved download stay NOT RUN.

Independence: I did not build the Skein comment editor. Disclosures: I
authored an earlier probe editor-audit contribution and the independent
reading-packet try (finish 11564), had read Isolde's finish 11574 summary
in the journal, and read TRIAL_EDITOR.md before this try. I did not read
comment_editor implementation source for this try.

Packet: fresh example at /tmp (private), packet common, base
69ef269bc9189b85299e759e41cabab467dcdcac, head
cc7f33bba10afe88837c23df54811f78d1337d50, comments.json sha256 before
15d7971de63e517e019ee792056d8fb43172ededeaf3ab4bc1ba75873c4607ce,
6 comments all open/anchored. Viewer request prefix
2a92ffad3eef42ee8570c31756adc04e-view- (editor-initial, editor-nav,
editor-compose, editor-edit, editor-arrow, editor-resolve,
editor-export, after-editor, after-review).

Results (desktop 1280 and phone 390 unless stated):
1 PASS: "Edit Skein comments", 6 comments 0 changed matching packet, no
   script errors, screenshots opened at both widths.
2 PASS observed: Tab -> Skip to comments, Enter -> section#comments,
   Tab -> Filter comments by resolution, both devices (step_log);
   keyboard_walk names every control in order.
3 PASS: anchor select value 14 = story.txt new line 6, head commit,
   "Good night."; filled ID/body, Tab to Add comment to download, Space
   added vesper-goodnight open with exact body, draft cleared,
   7 comments 1 changed, packet hash unchanged.
4 PASS: Body for vesper-goodnight replaced with "Independent editor
   try, edited: please check the closing line before approval.", Tab
   landed on Resolution for vesper-goodnight, exact body retained.
5 PARTIAL: ArrowDown on the focused resolution select left value open
   (arrow-key transition not observed under the viewer); fill set
   resolved, then fill set open again, body/anchor unchanged, in
   separate replayed attempts.
6 NOT RUN: no screen reader in the viewer.
7 PASS measurements: layout 1280/390 zoom 1, wider_than_screen false,
   too_wide empty, no unlabelled controls; editor screenshots picture
   3300/4943 desktop and 2340/5901 phone, so lower controls are covered
   by fields/text, not visual inspection. Emulated phone only.
8 NOT RUN: viewer cannot zoom.
9 PASS transcribed: Show edits JSON envelope transcribed exactly
   (2618 bytes), base_sha256 matches packet comments hash, contains
   vesper-goodnight with final edited body, open, story.txt new line 6.
   Saved-download witness NOT RUN.
10 PASS: comment_editor.py check exit 0, "0 updated, 1 added", packet
    hashes unchanged.
11 PASS: apply exit 0 once; comments.json sha256 after
    716966cf4d6c101550b83587532133cbaf9804769e0139ee354870902ffbaf52;
    anchors.json and packet.json hashes unchanged.
12 PASS: fresh review.html and compose page show vesper-goodnight at
    story.txt new line 6 with exact body, open; new editor starts
    7 comments 0 changed; screenshots opened.

Every edited-state look returned asked_before_leaving true with empty
dialogs lists (the repaired viewer behaviour). Overall: LIMITED PASS -
a viewer-based try is never full. This supplies an independent
non-author editor-companion result, including the same arrow-key limit
Isolde recorded, for the owner's milestone-2 assessment; it does not
close the milestone by itself.
