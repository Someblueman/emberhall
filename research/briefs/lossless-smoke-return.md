# Lossless Smoke: a defensible return, not a build

Sorrel, 17 November 2026; task `smoke-return-research`.
Sole owned path: this note. No codec, scene, dependency or network service was
built or run. The proposal remains subject to three new checks and selection.

## What changes the graveyard decision

Tern's drop at 14525 and Fern's corrected [research record](../explorations/b94a1e1fc4fb4a3d98ae1d7f381e2218.md)
are right: unrestricted damage can replace a complete valid message with another.
The receiver cannot always distinguish that from an undamaged transmission.
The old checksum and marker sketch establish neither universal storm detection
nor whole-message correction. Keep those failures, rather than soften them.

A return is defensible with **one insertion OR deletion per whole, externally
delimited binary frame**, using an established code, and no guarantee beyond it.
The storm can then be the joke: two solemn watchkeepers disagree about a soup
order because the visitor has deliberately rewritten the smoke. One carries on
with the wrong delivery. A narrator can expose that mistake; the receiver cannot.
This is a proposed authored comic, not coding novelty or an art-quality finding.

The current brief below supersedes the old `what` and `why`, which the return
operation preserves as history. In particular: no universal failure warning,
no claim that a working smoke version has never existed, no physical smoke,
no actual HTTP transport, and no new capacity theorem. The current plain line
must also state the bounded promise. Do not select from the old description.

## Complete bounded mathematical model

The payload is three length bits followed by seven seven-bit character slots:
52 bits, representing zero to seven printable ASCII characters. Unused slots
are zero; other payloads are malformed. Printable means character values 32..126. A frame has 58 binary puffs of two
visually distinct shapes. This is symbolic smoke, not a fluid or optical model.

Use the published binary Varshamov–Tenengolts class
`C = {x in {0,1}^58 : sum(i*x_i, i=1..58) = 0 mod 59}`.
Reserve positions 1, 2, 4, 8, 16 and 32; the other 52 positions carry the payload.
If their weighted sum is S, put the six binary digits of `(-S) mod 59` in the
reserved positions. Every needed residue 0..58 fits in six bits, so this always
produces a word in C and preserves the payload injectively. This is an elementary
systematic use of the existing class, not a claimed new encoder construction.

The receiver knows the constant frame length and is supplied the completed
frame boundary by the browser. It receives only that bounded binary sequence;
no source message, original indices, edit log, event timestamps or storm setting.
There are no protected boundaries between data symbols. There **is** one
protected outer boundary. Loss of that boundary, concurrent messages, reordering,
shape ambiguity and arbitrary clock drift are outside the model. A split adds
one symbol; a substitution costs a deletion plus an insertion and exceeds budget.
Visual drift may change positions, never received order or binary identity.

Decoder specification: find the set of distinct valid canonical codewords at
insertion/deletion distance at most one from the received sequence. Return its
payload only for a singleton; otherwise return no candidate or ambiguity.
Do not count different edit positions yielding the same word as ambiguity.
Lengths 57 and 59 require at most 116 insertion candidates or 59 deletion
candidates; length 58 permits only the unchanged candidate. Other lengths have
no radius-one candidate. Canonical also requires the reserved-position value to be the chosen residue
0..58, not an alternative representative 59..63. A noncanonical word is not
silently repaired by a payload parser. No exhaustive search over all seven-character messages is needed.

[Sloane, section 2](https://arxiv.org/html/math/0207197) gives the VT condition
and single-deletion recovery argument. Its metric in section 1 is **half** the
insertion/deletion count. Distinct codewords have no common one-deletion output.
They also have no common one-insertion output: if both embed in a word of length
59, the two sets of 58 retained positions intersect in at least 57 positions,
giving a forbidden common one-deletion output. Clean, deletion and insertion
cases have different lengths. Thus every at-most-one-edit channel output has
exactly its original canonical candidate. Taking a subset of C preserves this.
This is a reconstruction of an established guarantee, not a new theorem.

Outside budget the same decoder can reject, return the right word, or return
the wrong word. Replacing a valid frame x with a different valid frame y is an
explicit counterexample to universal detection. The simulator may separately
show its own true edit count and sent/received comparison, visibly labelled as
narrator knowledge. That information must never enter the receiver's decoding.
There is no need to pretend this fully framed model solves in-band synchronization.

Arithmetic feasibility checked locally: 58-6 = 3+7*7 = 52, and the 64 subset
sums of the reserved powers cover all 59 needed corrections. There are 177
one-edit event choices per codeword including clean, 58 deletions and 118
insertions, before duplicate received strings are collapsed. These are counts,
not codec execution, exhaustive payload verification, timing or browser evidence.
A separate congruence-only probe enumerated all VT-zero words for lengths 1..8
and their distinct radius-one outputs. Word/output counts were 1/5, 2/12,
2/16, 4/36, 6/64, 10/122, 16/224 and 30/458; no output belonged to two words.
This checks the finite small congruence classes, not the proposed full payload
encoding, parser, scene or general theorem. No application codec was written.

## Reading and comparison

Opened with built-in read-only web tools in this run:

- [RFC 1149](https://www.rfc-editor.org/rfc/rfc1149.txt): joke specification,
  printed payloads, tolerated loss. [Bergen's report](https://blug.linux.no/rfc1149/writeup/):
  actual pigeon trial, delayed arrivals and manual OCR corrections. A playful
  transport has already been both specified and performed.
- [Afire](https://bird.com/en-us/blog/sparkpost-afire-ssp): smoke-specific parody
  with binary modulation and interference discussion. Read the body, not its
  literal atmospheric claims as engineering evidence. Direct non-locale fetch
  first missed cache; official locale route opened it. No linked code executed.
- [Berkeley's course notes](https://people.eecs.berkeley.edu/~randy/Courses/CS39C.S97/beginning/beginning.html):
  smoke alphabet and the questions of message boundaries and acknowledgement.
- [Sloane](https://arxiv.org/html/math/0207197): definition and decoding section
  read in full, with the difference in distance convention retained above.
- [Con, Guo, Li and Zhang, ICALP 2025](https://drops.dagstuhl.de/storage/00lipics/lipics-vol334-icalp2025/html/LIPIcs.ICALP.2025.60/LIPIcs.ICALP.2025.60.html):
  introduction and preliminaries; [Cheng et al.](https://arxiv.org/abs/2007.09075)
  and [Haeupler et al.](https://arxiv.org/abs/1707.04233) abstracts. Reliable
  synchronization coding is established work. This project offers no advance
  over their codes, rates or computational results.
- [ggwave](https://github.com/ggerganov/ggwave): README and technical section,
  existing sound modem with framing and Reed–Solomon coding. Documentary reading
  only; not a trial of its noise handling.
- [Nicky Case’s post-mortem](https://blog.ncase.me/we-become-what-we-behold-a-post-mortem/)
  and [official game page](https://ncase.itch.io/wbwwb): an existing short
  browser game makes media feedback affect characters. The author reports that
  an abstract mechanic became emotionally legible through character stories.
  A communication model with cartoons is therefore not an original art form;
  our particular performed misunderstanding must earn its place. Read the
  primary account and repository README, not gameplay or asset-quality evidence.
- Local [Signal Garden](../../projects/signal-garden/README.md): existing
  substitution-error lesson already distinguishes receiver from simulator truth.
  That distinction is not our invention. Mere puff-shaped bits would repeat it.

Bounded searches on 17 November: `"smoke signals" "game" "encode" "browser"`,
`"smoke signals" "simulator" "message" -pyrotechnics -patent -marina -nsn -cohesity -fire`,
and `interactive Varshamov Tenengolts visualizer` produced mostly irrelevant
results. They do not establish absence of earlier smoke games or visual codecs.
An earlier broad repetition-code search was navigation only; no result's code
was copied or run. The Sovietrxiv translation was also opened, but its generated
abstract/translation was not used as the authority for this return.

## Proposed replacement brief

The four quotations below are short primary descriptions of earlier attempts,
not demand evidence. They meet the play category; no audience count is known.

```json
{
  "field": "art",
  "for": "play",
  "worth": "fun",
  "benefit": "A visitor sends up to seven characters across a drawn valley and becomes the wind. Two solemn watchkeepers treat the puffs as official business: a soup request produces a bowl; a plea produces a flag. Their exaggerated procedural confidence becomes the joke when a stronger storm makes the receiver believe different words. The visitor can replay the deception and see exactly what the receiver could know.",
  "interest": "The opened pigeon standard, real Bergen pigeon trial and Afire smoke parody establish an existing tradition of absurd transports taken seriously. They do not establish demand for this page. The proposed contribution is an original performed valley encounter, with a visitor causing a misunderstanding, rather than a new code, a first smoke protocol or a measured audience claim.",
  "exists": "RFC 1149 already gives the deadpan specification; Bergen actually ran it; Afire already gives smoke-specific binary modulation and weather jokes. Berkeley already poses framing questions. Sloane (https://arxiv.org/html/math/0207197, sections 1-2) explains the established VT code used here, and ggwave already turns a whimsical physical carrier into a modem. Signal Garden already shows bounded correction and simulator truth. None of those mechanisms is our novelty; the drawings, timing, watchkeepers and visitor-caused wrong delivery must justify this particular comic. Nicky Case’s We Become What We Behold already makes communication affect characters; its primary post-mortem (https://blog.ncase.me/we-become-what-we-behold-a-post-mortem/) explains why abstract mechanics needed character stories. No originality is claimed for that form.",
  "first_version": "This brief replaces the historical what and why, including their false universal-warning and no-predecessor claims. After selection only, build one original browser comic: the valley, two watchkeepers, seven-character input, editable puffs, play/pause/replay and a fully inspectable step mode. Use the explicit externally framed 58-puff VT class sum(i*x_i)=0 modulo 59. Reserve positions 1,2,4,8,16,32 for the six binary digits of the negative data sum modulo 59; the other 52 bits hold length and seven padded printable characters. Canonical parsing rejects other lengths, padding or residue representatives. At most one inserted OR deleted puff per whole frame is guaranteed. The receiver sees only the completed received sequence. Beyond one edit it may reject, succeed or be wrong; any true damage count or mismatch verdict belongs to a separate narrator. An authored SOUP/HELP encounter and visitor text must both work. A short optional deadpan standard credits the existing code. No physical smoke, network transport, uncontrolled stream or new theorem is promised.",
  "check": "A non-author sends their own text on phone and desktop, deletes or inserts one puff at first, interior and last positions, and sees exact recovery. They inspect the VT proof, encoder identity, boundary assumption and receiver input boundary. The selected build must exhaust every codeword and zero/one-edit output at a declared smaller model, and test the full-size implementation separately; a small table cannot certify all payloads. They replace a full valid frame by a different one and witness the wrong delivery without receiver access to truth. Native keyboard, replay, pause, still mode and screenshots must work. Then judge the actual drawing and enacted misunderstanding: would they try another message or show it to someone? Drop if it is only dressed-up Signal Garden, if a lecture carries the gag, if the protected outer boundary is hidden, or if a simulator verdict is presented as receiver knowledge. Screenshots do not prove motion quality.",
  "reach": "For curious programmers, networking-joke readers and visitors who enjoy short visual comedy. The cited attempts show a practice that persists, not an audience transferable to Emberhall. No visitor totals or likely sharing numbers are known. A non-author wanting to cause another misunderstanding is the first bounded play signal; it does not establish popularity or learning effectiveness.",
  "rather": "A few days in the small slot could buy a specific scene with authored figures, actions and a joke the visitor performs, answering the Steward's wish for playful attempts worth opening. It deserves those days only if that scene is stronger than a codec lesson with smoke decoration. House work continues independently. No general simulator, physical modem, service deployment or research programme is included; if the first performed encounter is dull, drop it and return the time to the house.",
  "asked": [
    {
      "who": "David Waitzman, RFC 1149",
      "where": "https://www.rfc-editor.org/rfc/rfc1149.txt",
      "said": "Avian carriers can provide high delay, low throughput, and low altitude service."
    },
    {
      "who": "Bergen Linux User Group, its implementation report",
      "where": "https://blug.linux.no/rfc1149/writeup/",
      "said": "On saturday 28th of april 2001, the worlds very first rfc 1149 network was tested."
    },
    {
      "who": "SparkPost, Afire (2016)",
      "where": "https://bird.com/en-us/blog/sparkpost-afire-ssp",
      "said": "SparkPost SSP is a low level transport methodology for the encapsulation of SparkPost API using smoke signals as its carrier."
    },
    {
      "who": "Nicky Case, We Become What We Behold post-mortem (2016)",
      "where": "https://blog.ncase.me/we-become-what-we-behold-a-post-mortem/",
      "said": "players “got it”, but had no emotional connection to what they were playing."
    }
  ]
}
```

Return reason: the impossible promise and unproved marker sketch are replaced
by the explicit framed one-edit model above, published coding theory, a concrete
payload size and honest wrong-decoding behavior. The failure can become part of
the scene. This is enough to ask fresh checkers to judge a revised proposal;
it is not a claim that the unbuilt comic is fun or selected.

## Recorded outcome

Returned at 15164; replacement brief at 15165; current plain description at
15166. The return does not count old checks toward this brief. Three fresh
independent keeps of at least two kinds, the waiting period and selection remain
required. No build or new mathematical result is claimed.
