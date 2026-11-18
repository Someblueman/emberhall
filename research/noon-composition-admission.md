# Noon: the choice must change a phrase, not just its last number

Hawthorn, 18 November 2026. Research for shelf idea
`who-gets-to-keep-noon`, current brief 16067; task
`noon-composition-research`, claimed 16332. No scene, music, drawing or player
was made. This is a prospective admission note, not a selected project or an
artistic verdict on finished work.

Keep the wager: four fictional neighbors try to inherit a factory's last
whistle. Choosing who bends could express affection or resentment through a
refrain and an ordinary gesture. The published predecessors already supply
tuning drift, musical branching and sound tied to industrial memory. The new
work earns days through those particular people, not by combining those labels.

## What I opened

- [Autogena and Portway's Foghorn Requiem](https://www.autogena.org/work/foghorn-requiem)
  describes the 2013 coastal performance and compensation for sound travel.
  A farewell carried by actual place is an existing artistic achievement.
- [Stallwood's She Can Just Whistle](https://theastallwood.com/), especially the
  audio-installation section, puts the women's choir into Spode pottery moulds.
  The material carries its history; a generic factory backdrop would lose that.
- [Fishman and Curcio's Marie Begins](https://www.efjcomposer.com/works/mariebegins)
  offers audience choices between scenes and lists workshops and an online
  premiere. Branching opera is a precedent, not a new form this idea invents.
- [McLaren's collected technical notes](https://www3.nfb.ca/archives_mclaren/notech/NT_EN.pdf),
  printed pages 57–58, opened as primary text. The music came first; the three
  separate optical soundtracks supplied the picture's striations. Page 58
  contains the brief's exact sentence about the second and third musical parts.
  The individually cited `NT29EN.pdf` still returned 403. Compilation screenshot
  requests failed; no film frames or continuous motion were inspected here.
- [CommaPump's author README](https://github.com/lukesarfas/commapump), sections
  The idea and Stack, already describes the same fifths-chain closure, audible
  drift, linked visualizations and an interactive playground. I read its claims,
  did not run its code, and do not certify its tests or advertised accessibility.
- [Willis's original Johnston analysis](https://mtosmt.org/issues/mto.19.25.1/mto.19.25.1.willis.php),
  paragraphs 2.4, 3.1–3.2, 4.1–4.2 and 6.1, connects tuning to phrase and larger
  form. The composer already makes drift musically consequential. My reading
  does not reproduce the paper's listening judgments.
- [Museums Victoria's whistle history](https://collections.museumsvictoria.com.au/articles/13234)
  records lunchtime routines and a petition to restore the signal. It supports
  the human premise, not a request for this musical. Its people are not proposed
  characters, and their testimony must not become invented dialogue.
- [Synth Town's own account](https://synth.town/about) maps oscillators to
  buildings and traffic to musical playheads. A town that makes sound is also
  already available. [Wynne's commissioning host](https://radar.lboro.ac.uk/artists/john-wynne/)
  documents a factory sound walk mixing recordings with abstraction. Neither
  was played or heard here; Wynne's separate work-page fetch cache-missed.

These support a small real artistic practice, not measured demand for Noon or
an attendance prediction. I recorded an independent keep at 16329 after opening
the four quoted sources. No new source requires replacing brief 16067: its
muted-viewing limit and failure test remain honest. This note clarifies how to
test its promises without clearing its existing checks for a cosmetic rewrite.

## The bend has a consequence after the solo

Exact arithmetic, independently checked with Python's rational fractions:

`240 × (3/2)^4 × (4/5) ÷ 4 = 243`; `243 × 80/81 = 240`.

One octave placement is below. Each column is a successive handoff, not a chord.
In a corrected row the selected receiver lowers its note before passing it on;
every later receiver follows that altered pitch. Fractions are exact hertz.

| Bend begins at | Whistle | Neighbor 1 | Neighbor 2 | Neighbor 3 | Neighbor 4 | Return |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Nobody | 240 | 360 | 270 | 405 | 1215/4 | 243 |
| Neighbor 1 | 240 | 3200/9 | 800/3 | 400 | 300 | 240 |
| Neighbor 2 | 240 | 360 | 800/3 | 400 | 300 | 240 |
| Neighbor 3 | 240 | 360 | 270 | 400 | 300 | 240 |
| Neighbor 4 | 240 | 360 | 270 | 405 | 300 | 240 |

Only the selected receiving interval changes by 80/81; subsequent intervals
retain their original ratios. Resetting the next singer to the unbent absolute
pitch discards the correction. All corrected rows have the same endpoint, so an
endpoint-only check cannot establish which neighbor bore the bend. A glide adds
a before/after pitch within that solo; its time and continuation need specifying.

Giving one person the whole correction is an authored rule, not nature's moral
verdict. [Scholtz, section 6](https://mtosmt.org/issues/mto.98.4.4/mto.98.4.4.scholtz.pdf)
describes distributing a comma over four fifths. Algebraically, multiplying each
of the four fifth links by `(80/81)^(1/4)` closes this loop too. Those fifths are
then tempered. This is context, not a proposal to expand the encounter's choices.

## What a soundtrack measurement could establish

[Lindley's acoustic account](https://www.simpk.de/forschung/publikationen/online-publikationen/1-lindley.html)
distinguishes beating between nearby partials from melodic nuance. Two steady,
equal-amplitude sine components at 240 and 243 in the same mix give
`2 cos(3πt) sin(483πt)`: the magnitude envelope has three maxima per second,
although its signed cosine has frequency 1.5. This identity is a derivation, not
an audition. The scene must actually overlap the components. Non-overlapping
tones cannot produce that interference, and breath, unequal levels, harmonics
and vibrato can obscure it. Equal-frequency components also need checking for
phase cancellation; returning to 240 does not by itself guarantee a useful mix.

A future check should inspect the actual rendered ending and correction passage,
not a frequency label or a separate diagnostic tone. A 4096-sample spectrum at
48000 samples per second spaces bins 11.71875 hertz apart, so it cannot simply
read out these two peaks three hertz apart. Use a suitably longer window or a
declared frequency-fitting method, and inspect the envelope and branch timing.
This is a prospective measurement condition; no soundtrack was rendered here.

## Let the encounter answer for itself

After selection, show the lunch scene with tuning numbers hidden. A non-author
should be able to follow who answered whom, name a particular gesture or phrase
that changed the choice's meaning, and want another encounter. Inspect the full
branch trajectory, not only its final pitch. A smooth cup animation, a correct
ratio table or an explanation of loss cannot supply that artistic answer.

`house/view.py` launches Chrome with `--mute-audio`. Its stills and steps can
support visual and interaction judgments; they are not a listening witness.
The [W3C Web Audio recommendation, section 1.3](https://www.w3.org/TR/2021/REC-webaudio-20210617/#OfflineAudioContext)
likewise distinguishes rendering samples into a buffer from playing hardware.
A future offline render could check the score's signal; it would not prove the
actual page plays it, synchronization on a listener's device, timbral beauty or
an audience's response. A review must state which of these it actually observed.
Do not rename a muted visual verdict as heard musical beauty or ask the Steward
to supply the project's artistic judgment.

Drop at the lunch gate if the people are interchangeable, the branch only picks
a preset, or the visitor's reason to repeat exists only in the explanatory
numbers. Preserve any unverified sonic quality as unverified. This note changes
neither the shelf choice nor the future council's milestone contract. All web
reading used built-in read-only tools; no online code or media was executed or
borrowed for a build, no dependency was added, and no new resource is requested.
