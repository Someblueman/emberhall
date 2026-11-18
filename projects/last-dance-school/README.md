# The Last Dance School

Moth is leaving. Give the old teacher three movements, then watch a dance
travel through a village, a broken bridge and two differently remembered
traditions. Rue grows into a teacher. Lio wears a blue thread for remembering
which arm; Bea tests whether the floor can survive the dance. They meet again
on a plank neither could have carried alone.

An original silent paper-puppet fable by Mallow, Emberhall, 2026. Open
`index.html` through a static server or the house page viewer. Everything is
local: drawing, articulated puppets, words and choreography. No accounts,
sound, storage, dependencies, remote assets or network calls.

The clearing and extended village have passed their independent encounters
and the project owner’s first two stage decisions. The full fable is now being
packaged for its final encounter and public opening. A local packet is not
proof that the public page is available.

## Playing

Press a gesture to cycle through bow, wave, stamp and turn. Ada immediately
tries it alongside Moth. The checkbox makes the phrase more extravagant.
Begin the class for timed play, or use Next still. Pause freezes the current
pose. Next scene advances through the intervening story and handoffs, then
pauses at a chapter opening; it does not invent a fresh memory at that point.
Teach another dance returns to rehearsal and focuses the first movement.

The authored route has 88 moments and reaches its held final tableau after
696 active seconds (11 minutes 36 seconds). Its admitted clearing still
occupies the first 184 seconds. These are programmed timings, not a claim of
having watched the whole performance uninterrupted. A request for less motion
starts in still mode. Leaving the tab pauses timed play without skipping time.
All controls use normal button, checkbox and disclosure keyboard operation.

Before beginning, “Who is there to see it?” chooses the first pupils and
Rue's teacher. In the village, “Who stays to watch?” can change Lio's lesson,
Lio's late arrival, Bea's lesson and whether Lio watches Bea's final offering.
Each choice closes at its particular handoff. A missed lesson stays missing.
A later witnessed offering can teach something new; it cannot resurrect an
old teacher's score. Neither branch receives a purity score.

“Remember a scene” is a spectator's look back. It pauses the story and shows a
detached past performance, with its own play, pause and still controls. Return
to the living dance resumes the present view;
looking at young Moth gives no movement back to a later performer. The optional
handoff list records what crossed at the time, even after that teacher leaves.
Keep both explanations closed when judging whether the stage carries the story.

## The performed inheritance

`dance.js` holds the same mutable character memories the puppets perform.
`village/story.js` authors the later scenes and handoffs; `village/stage.js`
draws and stages their village. The model does not read the rehearsal controls
after beginning. Each pupil receives separate movement objects with a kind,
lean, arm reach and foot lift. Ada makes room for details, Pip throws more of
the body into it, Rue makes a smaller version, and Lio and Bea carry those
branches differently. These deterministic rules are fictional choreography,
not machine learning, cultural science or a new preservation mechanism.

Moth's memory clears at departure. Ada and Pip's clear when their generation
leaves. Lio learns only Rue's current memory, and Bea only Pip's; the final gift
comes only from Bea's current performed movement if Lio watches. Empty memories
render as still bodies beside the dancer who did learn. Replay frames live in
a separate spectator archive. Its public accessor returns a detached copy;
a replay frame cannot advance as the living model or alter its choices.

Run `python3 -m unittest discover -s projects/last-dance-school -v`, or
`node --test projects/last-dance-school/dance.test.js`. The adapter runs the same
12 Node checks, including `village/story.test.js`: every three-gesture phrase,
both original teachers and both sizes for the clearing; all phrases and both
teachers down the two village branches; numeric differences in the default
bodies; independent mutable memories; invalid and inherited-property pupil names; missed and late lessons; live changes to
teachers before handoff; choice deadlines; actual gift inheritance; isolated
spectator replay, cleared teachers and final performance slots. These checks
cannot judge sustained animation, emotional connection or fun.

## Author trials — 18 November 2026

The house viewer is used on the actual page at phone 390 and desktop 1280,
with real browser clicks and keys; screenshots and responses stay private.
During building, a lesson placed Lio in the river, the reunion plank stopped
short of the dancers, and Bea's first bow was too close to standing still.
Those staging defects were repaired, along with figures overlapping the chairs. A larger wave also hid its hand behind
the head; its arm arc was repaired after the changed-phrase look.

Actual looks covered the village, the storm with Ada catching Pip, the north
lesson, reunion, ending and return to rehearsal. At the same reunion moment,
the ordinary bow, altered wave, late lesson and whole missed lesson produced
different bodies. The missing pupil stayed still beside the other dancer;
the late pupil waved while the other bowed. The optional handoff list stayed
closed for those comparisons.

Real keys started and paused ten seconds in the new north-bank scene, then
advanced one still and stayed there. A separate ten-second spectator replay
started, paused and returned to the living reunion without teaching its missed
pupil. Remembered still advance showed young Moth performing while the living
moment stayed fixed. Ending focus reached Teach another dance; Space reset to
the first gesture, Space changed it, and Tab reached the second gesture.
The successful looks reported no script errors, unnamed controls or horizontal
overflow at either size. Both devices' main screenshots were personally opened
for each look; the inputs, responses and copied screenshots remain private.

A final model review also caught a new lookup accepting inherited object keys
as pupil names. Its refusal was restored after a failing regression check;
the original valid-pupil checks remain unchanged. No browser repeat was needed
for that invalid internal-input guard.

No author trial supplies the independent artistic verdict. No uninterrupted
full-performance, speech output, physical touch, zoom, changed motion
preference, public browser or audience-size claim is made.

## Opening the full fable

The Gallery packet contains the playable page, its stylesheet, all four
scripts, this guide and the scene preview. The scene preview is a static extraction of the actual default
reunion: Lio and Bea’s second movement, held halfway through its wave. It uses
Mallow’s existing drawing and performed transforms; it invents no new scene.

For a quick encounter, choose your three movements and use Next still, then
Next scene to travel through the village and its reunion. For the whole timed
story, Begin the last class and leave it moving. Space and Enter operate the
focused buttons; Tab moves between them. There are no global shortcut keys.
Use Pause or Next still whenever you need time. Teach another dance returns
to your first gesture with keyboard focus restored.

Fern’s village encounter earned the second-stage recommendation from a particular moment: Lio’s smaller sleeve-wave meets Bea’s
larger one on the same plank. Her changed and missed lessons, and return from
spectator memory, were checked on both screens. These were sampled scenes and
short timed segments; sustained pacing remains unjudged. The final encounter
and delivery result are kept in the opening review in the source repository.
Independent source acceptance, deployment and the owner’s final decision
remain separate. This guide makes no public-availability claim.

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
