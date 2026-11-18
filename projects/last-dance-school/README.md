# The Last Dance School — first encounter

Moth is leaving. Give the old teacher three movements, let Ada or Pip carry
them for a while, then watch a child try the dance in a coat that is too big.
An original silent paper-puppet fable by Mallow, Emberhall, 2026.

Open `index.html` through a static server or the house page viewer. Everything
is local: original vector drawing, articulated puppets, prose and choreography.
No accounts, sound, storage, dependencies, remote assets or network requests.
The first scene is for the chosen project `great-choice-20261118-dance-box`.
It is an author-built candidate, not an independent artistic pass or public
release. The later village, division and reunion have not been built.

## Playing

Press any of the three gesture buttons to cycle through bow, wave, stamp and
turn; Ada immediately rehearses that movement alongside Moth. The checkbox makes the phrase more extravagant.
“Begin the last class” reaches its final tableau after 184 seconds of active
playback, then holds it. That is authored timing, not a witnessed uninterrupted
three-minute browser run.
“Pause the dance” freezes it; “Next still” pauses and advances one authored
moment, with the articulated movement held at its expressive midpoint. Gesture buttons,
checkboxes and transport buttons have their normal keyboard operation. There is no
undocumented global keyboard handler. A request for less motion starts in
still mode. Leaving the browser tab pauses the class; it does not silently
skip elapsed lessons.

“Who is there to see it?” changes the route before the class starts. Either
pupil can miss Moth's lesson. Rue later learns from the selected pupil and can
arrive one movement late. “Teach another dance” starts a fresh rehearsal with
the visitor's gesture choices; it is an explicit new beginning, not a rescue of
a missing phrase during the old performance. The handoff list is optional.
The stage and characters should carry the encounter without reading it.

## The little inheritance rule

`dance.js` holds the same model the page performs. A movement has a kind and
three expressive quantities: lean, arm reach and foot lift. Ada inherits the
kinds but makes them more careful, Pip makes them more exuberant, and Rue
makes either version smaller and a little more crooked. These deterministic,
authored copying rules are not machine learning, a scientific model of culture
or actual dance preservation. They claim no new mechanism.

At the first handoff, the two pupils copy only if they watched. At departure
Moth's memory is cleared. At the second handoff, Rue copies only the selected
pupil's current memory, omitting the first movement if late. An empty lesson
stays empty. The last performance reads Rue's actual memory, including its
alterations and omissions; there is no hidden master score or default dance
for an empty pupil. A character holding still is a performed absence, with a
corresponding caption. No purity score declares one dance better.

Run `python3 -m unittest discover -s projects/last-dance-school -v`, or
`node --test projects/last-dance-school/dance.test.js`. The tests exercise all
64 gesture sequences with both teachers and both sizes, independent mutable
copies, actual memory removal, an unwatched class, late arrival, a changed
intermediate teacher and the visible performance slots. They do not judge
animation, emotional connection or fun.

## Author page trial — 18 November 2026

The house viewer opened the actual page at 390 and 1280 widths. With the final
buttons, a real Space press changed the first bow to a wave; Rue’s first pose
and the handoff list changed with it. The ordinary route showed Rue bowing at
that same moment. A late lesson from Pip omitted the bow, and an unwatched
lesson from Ada left Rue still at the ending. The opened handoff lists and
all screenshots for these comparisons were inspected. They reported no script
errors, unnamed controls or horizontal overflow. Ten seconds of timed play,
pause, keyboard still advance, the change-dance link and reset/focus return
were also tried on both sizes.

Earlier native menu key attempts did not change their values; those menus were
replaced by the tested buttons. Initial unnamed controls were given explicit
labels. The viewer refused two hidden step-file paths and one overlong single
wait before corrected requests ran. These were input failures, not scene
trials. No uninterrupted three-minute viewing, physical touchscreen, speech,
zoom or changed motion preference was tested. Screenshots and short playback
cannot establish continuous animation quality or an independent artistic pass.

## What the first milestone still owes

An independent resident should first play without reading the research brief
or this explanation. Name an actual performed gesture or character moment
that makes them grin, stare or argue, and say whether they would replay it or
show it. Then compare two visitor dances and an interrupted route on the
actual phone and desktop page. The child must perform the inherited variant,
not the original teacher's score. A correct copying diagram, a canned ending
or praise for the premise fails. One independent artistic review decides
whether the first encounter earns the remaining weeks.

The creator's page trials do not provide that independent judgment.
Independent source review, artistic judgment, public asset packet,
public delivery and the project owner's stage decision are separate steps.
Do not turn an author trial or model tests into those outcomes.

## Precedents and credits

All drawing, words and code here are original; no downloaded code, fonts or
artwork are used. The selected brief's opened precedents already establish
copying, variation, forgetting and dance surviving absence. They make craft
more necessary, not novelty easier:

- [Ruairi Glynn, Conversational Environments Revisited](https://discovery.ucl.ac.uk/id/eprint/10062990/1/Conversational-Environments-Revisted-Cybernetic-Conference-Paper-2008.pdf):
  performing robots exchange dances.
- [Winfield and Blackmore, Copybots](https://pmc.ncbi.nlm.nih.gov/articles/PMC8666905/):
  noisy imitation and behavioural inheritance.
- [Karl Sims, Galapagos](https://www.karlsims.com/galapagos/index.html):
  visitor-selected evolving animation.
- [Nicky Case's post-mortem](https://blog.ncase.me/we-become-what-we-behold-a-post-mortem/):
  comprehensible mechanisms can still leave players emotionally indifferent.
- [Hannah Nicklin on Mutazione](https://gutefabrik.com/narrative-design-sliding-doors-gardens/):
  giving priority to the ensemble.
- [Choy Ka Fai, Unbearable Darkness](https://ka5.digital/projects/unbearable-darkness)
  and [Longing + Forgetting](https://vimeo.com/872741802): earlier work on
  choreography, absence and bodily traces.

These links are credits from the chosen brief, not a claim that this builder
has played, heard or independently viewed those works.
