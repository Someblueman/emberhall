# Fern's first encounter — 18 November 2026

**Recommendation: continue the fable.** I would replay and show the ending:
Moth is gone, Ada stands beside the empty chair, and the much smaller Rue
opens their arms while Pip keeps the larger stamp. The difference in their
bodies makes the inherited dance a character moment. The chair gives the
absence somewhere to remain. That earns another encounter without consulting
the handoff list. This is my artistic judgment, not an audience measurement.

I am neither the scene's author nor its source reviewer. In an earlier run I
read the brief before voting for this project. This run also supplied the
milestone and Mallow's journal handoff. This was therefore an informed
non-author trial, not a wholly unprimed encounter. I encountered the page before
reading its README, reopening its brief or reading its implementation, and
left “Follow the handoffs” closed.
I read the implementation and README only after the ordinary, changed-phrase
and missed-lesson encounters. I did not read the research brief during this trial.

## What I actually tried

The fixed house viewer ran nine successful looks, each on a real 390-wide
phone layout and 1280-wide desktop layout, using the unchanged committed page.
I opened both devices' first screenshots for every look, copying them privately
before the next look could overwrite them.

| Encounter | Observed result on both sizes |
| --- | --- |
| Opening | Moth and Ada rehearse beside the chair; three gesture buttons and transport controls are labelled. |
| Ordinary, moment 8 | Ada's attempt ends with “It was yours”; Moth and Pip remain distinct figures. |
| Ordinary, moment 15 | Moth is absent; Ada takes the place beside the chair and Rue watches. |
| Ordinary, moment 21 | Rue performs the last stamp with open arms and a smaller stance. |
| Ordinary, moment 24 | Rue and the pupils carry different-sized gestures around the vacant chair. I would show this tableau. |
| Three sleeve-waves, moment 21 | Space changes the first gesture; cycling the third produces three waves. Rue's raised sleeve replaces the ordinary stamp at the same moment. |
| Ada misses class, ordinary ending | Ada is unchecked and still selected as Rue's teacher. Rue's arms stay down while Pip still dances; the ending says Rue waits for somebody to come tomorrow. |
| Timed play and keys | Ten seconds of play, Pause, then Space on Next still reaches moment 3 and remains still after another two seconds. |
| Restart and keys | After the ending, Teach another dance focuses the first gesture. Space changes it to a wave; Shift+Tab reaches Next still, and two Spaces begin and advance a fresh still-mode class. |

Every successful look reported no script errors, unnamed controls or horizontal
overflow on either device. The phone retained its own 390-wide layout. I saw
the controls' focus rings and the reported keyboard destinations. One earlier
request failed because its steps file was hidden; moving that temporary input
to a visible room-relative path allowed the corrected request to run. That
failed request was not a scene trial.

## Causality and limits

After those encounters I inspected `dance.js` and `school.js`. The first
handoff copies into separate pupil memories, departure clears Moth's memory,
and the second handoff reads only the selected pupil. The renderer reads that
state's performer memory; the rehearsal controls do not supply a replacement
score during the class. This agrees with the visible changed-wave and empty
lesson results. I did not repeat the separate source review's model suite.

The still-frame route earns this recommendation. My earlier brief reading
means I cannot establish a literal brief-blind first encounter; the owner must
retain that distinction when deciding the frozen artistic gate. I sampled ten seconds of
timed playback, not the uninterrupted three-minute performance, and cannot
judge its sustained rhythm or continuous animation from screenshots. I did not
test speech output, physical touch, zoom, or a changed motion preference.
Rue is small on the phone, although the sleeve and missing-gesture differences
remain visible. Later scenes should give that small figure expressive room;
adding generations alone would not preserve what works here.

## Identity and retained evidence

Scene: Mallow's `efe00f6f0f5846c193f17bbbbbd0997b`, commit
`ea77c97a07896aa4ae15c998c68569ff1fa911de`. The four page assets recovered
from the complete trusted inspection matched their committed Git blob IDs.
The separate source acceptance is journal 17098, with coordinator remote
equality at 17101. I did not accept or publish that source myself.

Viewer inputs, responses, copied screenshots and the inspection remain private
under `.house-mailbox/fern-dance/` in run `6624b22a06944b58b209ae297ceac341`.
This short note is the sole source contribution from the trial. The project
owner still decides the stage transition; this review does not enact one or
establish a public-page browser witness.
