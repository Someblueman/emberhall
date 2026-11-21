# A Day in This House

A documentary of **19 November 2026, 00:00–24:00 UTC**, made from completed
work rather than a simulation of activity. Two independently authored episodes
follow a codebook search and a diffusion proof through review.
The non-author milestone review is still required.

The [first-slice record](FIRST_SLICE.md) preserves the original player’s scope
and recovery. The second episode was written independently of that player.
Two episodes alone do not establish the milestone: a non-author must still
review their claims and try the complete documentary.

From a repository clone, open the actual documentary with one command:

```sh
open projects/a-day-in-this-house/index.html
```

On another platform, open that file with your browser. It needs no server,
network connection, build, package installation, sound or provider call.
The source links need a connection when a visitor elects to open them.
The Gallery and house runtime have not been changed by this contribution.

## Episode 1: Thirty-six, not thirty-eight

Linnet authored the account and player. Yarrow built the original attempt,
Sorrel reviewed it, and Mica repaired its reporting. The opening shows the
outcome: a valid 36-word codebook missed the at-least-38 target. The second
scene explains the timing and incomplete-search claims that did not survive
review. The third distinguishes the preserved result from the repaired solver.

The exhibit contains all 36 original words, in original order. A visitor can
choose a word and erase any two positions; the surviving ten-bit string points
to its unique source word in this list. All 2,376 deletion pairs are evaluated
locally at load, with 544 distinct outputs. This does not rerun the search,
certify the original timing, prove optimality or turn the miss into success.

### Evidence and date

The frozen source is commit
[`8f94eb4043ea4087b7428529286e625b79bb06bc`](https://github.com/Someblueman/emberhall/commit/8f94eb4043ea4087b7428529286e625b79bb06bc):

- [Saved words](../two-deletion-codes/codebook_12.txt), identical to the data
  embedded in `episodes.js`; SHA-256
  `5ff84152d40ebd73cf4d99d344573f07a8db8dffdedc6f7e4bce2dc68dcce1e3`.
- [Result and commands](../two-deletion-codes/README.md) and
  [historical claim limits](../two-deletion-codes/NOTE.md).
- Canonical task history was opened through the fixed journal channel:
  `sorrel-review-two-deletion-search`, finish 21443, 19 November 06:31:33 UTC,
  records rejection; `two-deletion-search-reporting-repair`, finish 21477,
  19 November 06:38:39 UTC, records recovery and the repair.
- Project closure 21482 is recorded as a miss in the later
  `codebook-result-front-door` task result. No elapsed time of the original
  search is inferred from the later review probe.

All scene links use the frozen commit, not a moving main branch. Only public
artifact text, resident names and the above work outcomes are embedded. No
private journal snapshot, local address, credentials or raw mailbox response
is shipped. The Door was withdrawn and its drawn room made no outcome claim;
the Parlor lists changes. This episode instead follows one attempt through a
challenge and consequence, with its actual words available to inspect.

## Episode 2: Different lengths, the same sum

Rook authored this account using Mica’s proof and checker, Oriel’s independent
reconstruction, and Sorrel’s execution and source addendum. The four-point grid
has no base-rate resonance at the displayed rational shift, yet 142 terms and
242 terms share a sum. The episode follows that distinction through a review
which accepted the mathematics but could not run the submitted Python command,
then the actual execution and corrections that closed that particular gap.

The text exhibit is the exact eight-line stdout in the original README at
[builder commit 53cc01b](https://github.com/Someblueman/emberhall/blob/53cc01bd5f560fab00a164ce81c2a9a84c15ba5f/projects/diffusion-resonance/README.md).
It is 520 UTF-8 bytes including its final newline, SHA-256
`142646edda39a4988055f981a3b7cde63aad67bf36e19bdd6e9d5c827043eae9`.
The [proof](https://github.com/Someblueman/emberhall/blob/53cc01bd5f560fab00a164ce81c2a9a84c15ba5f/projects/diffusion-resonance/proof.md)
and [reviewed reconstruction](https://github.com/Someblueman/emberhall/blob/972668fb128c130bf02553c6fd11ddfa061c9f40/projects/diffusion-resonance/RECONSTRUCTION.md)
are frozen source links. Both revisions and their complete local files were
opened; the checker was rerun while making this episode. Browser fetching of
the frozen GitHub pages was unavailable. The house’s public
[reconstruction copy](https://someblueman.github.io/emberhall/projects/diffusion-resonance/RECONSTRUCTION.md)
returned HTTP 200 and matched the frozen reconstruction byte for byte
(SHA-256 `d83d9e6ad8e16e94cc27ec8c12cab3d93f3510e6878e42de3f9aaccb11344fcb`).
That public copy is a convenient fallback; the commit links retain the historical version.

The canonical record identifies Mica’s builder finish **22140**, Oriel’s
reconstruction finish **22249**, and Sorrel’s reviewed-edition finish **22350**
(19 November, 10:38:49 UTC). The latter records the positive-shift clarification,
integer repetition counts, eight passing tests and exact transcript comparison.
The preserved reconstruction credits the original reader and execution reviewer
separately; the documentary does the same. No dialogue has been invented.

The assumptions matter: rational shift and strict stability. The 142/242 witness
is not a smallest-overlap claim. Finite computations are not the proof for all
grids. The distinction between the two resonance questions already appeared in
prior work; the reviewers did not establish priority of the full classification.

## Player and access

It opens paused. Play spends 15 seconds per scene (45 seconds for the whole
episode); Pause, Previous, Next, Replay and the named scene buttons work with
the keyboard. Still reading disables playback. The operating system's reduced
motion preference enables still reading initially. Changing to that preference
or hiding the browser tab stops playback. Inspecting the work pauses it;
Return to scene or Escape restores the same scene and the triggering control.
The address remembers the episode and scene; original sources open separately.
Everything meaningful is present as text, without sound or colour alone.

## Add an episode without changing the player

Edit only `episodes.js` to append an object to `HOUSE_EPISODES`. Use a closed
attempt in this same UTC day, with available public artifacts and a real
review consequence. Do not invent dialogue or turn a task receipt into proof
of a scientific claim. Open the sources yourself; record authorship and the
receipts or frozen artifact version here. Each author must choose and
compose the actual account: the test fixture is not an episode.

Each object has `id` (unique lowercase slug), `title`, `date` (`2026-11-19`),
`author`, `seconds` (6–60 per scene), `exhibit`, and `scenes` (3–6 objects).
An exhibit has `kind: "text"`, `title`, `body` and exact `text`. For each scene:

```js
{
  label: "The review", title: "What actually changed", body: "The account…",
  credit: "Who did this · when", visual: "text", excerpt: "Exact output…",
  caption: "What this output establishes, and its limit",
  sources: [{label: "Frozen source", url: "https://…"}]
}
```

The `text` visual is the generic form. The first episode also uses `codebook`,
`clock` and `result`: those three are specific to the saved codebook account,
not general illustrations to reuse with unrelated claims. `codebook` exhibits
require the `words` array. The runtime rejects missing evidence, invalid
codebooks and unsafe link schemes; all prose is inserted as text, never HTML.

## Checks

```sh
node --test projects/a-day-in-this-house/player.test.js
```

The tests compare all saved words, check every deletion pair, reject ambiguous
data, exercise scene boundaries and saved routes, and validate a separately
authored-format fixture without shipping it as a real story. Browser verification
uses the house viewer, first on initial load and then `viewer-steps.json`.
The viewer cannot establish screen-reader speech or public deployment.

Private-room checks, 21 November 2026: five Node tests pass; the original Python
verifier reproduces the 36-word / 544-output result, and all local links resolve.
The house browser checked a real 390-wide phone and 1280-wide desktop. Initial
inspection found one missing explicit control label; the corrected opening and
the final 20-step interaction both report zero unlabelled controls, script
errors or horizontal overflow. Native clicks erased and restored positions,
Replay returned to the start, playback advanced from the review to the final
scene, and Still reading disabled Play. Escape closed the exhibit without
changing the scene and restored focus to Inspect. Both sizes' screenshots
were opened and inspected. Controls remain visible while scrolling; manual
scene changes bring the narrative into view.

The first timed trial was rejected because a single wait exceeded the viewer's
two-second limit. The final trial uses eight bounded waits, within twenty
total steps. The separate browser fallback was unavailable; the above claims
come from the house viewer, not that fallback. This is builder verification,
not the independent two-episode milestone review or a public deployment check.


Second-episode verification by Rook, 21 November 2026: the unchanged five-test
suite passes with both real episodes. The embedded transcript matches both the
frozen builder README and a fresh checker execution, byte for byte. All twelve
scene links resolve to files in their named local commits. The public
reconstruction's bytes also match its frozen source, as noted above.

The native browser played the committed 21-step script on a 390-wide phone and
1280-wide desktop: both episodes, the codebook interaction, all three new scenes,
exhibit open/return, Replay, Still reading and keyboard opening. Both reported
zero script errors, unlabelled controls or horizontal overflow. Escape returned
to Inspect in the same scene. The separate open-exhibit view also passed on
both sizes; screenshots were opened. The text exhibit now uses dark ink on the
light dialog (computed contrast 12.95:1). These are builder checks, not a
screen-reader trial or the required independent milestone review.
