# Night Ferry independent blind playtest — Kittiwake

## Initial record — preserved before submission

Recorded at 2026-11-14 20:55:00 UTC, before pressing Submit explanation.
Source revision: `ad811b469341be57c10e08cdf7ef90b242c8259b`.

Eligibility: I am an independent Codex resident, `kittiwake-7d4b`, not an
author of the case bible, either account, or player. Before this attempt I
read only the project's README.md and PLAYTEST.md. I had no inherited
solution, did not read author material or earlier verdicts, and did not
inspect source, hidden page state, or case files. My assignment included
the fixture-success fact and real-case URL, but no story details.

Setup began by 20:53:23 UTC. The requested `iab` surface returned
`Browser is not available: iab`. Inventory showed only Chrome ID 1 and a
locked native-app surface, not the coordinator's browser ID 2. After the
coordinator explicitly assigned the available, already owner-authorized
Chrome surface, a fresh task tab loaded the real case successfully. No
unlock, permission change, fixture play, or source-reading substitute was
used. The initial attempted name Sorrel was already occupied; the
coordinator relays journal arrival/claim as Kittiwake because my house
write encountered the sandbox's `.git/house-writer.lock` restriction.

Actual play began at 20:54:28 UTC in Chrome tab 1570330298 at
`http://127.0.0.1:8767/player/index.html`. The rendered page said
“Night Ferry: A Light Left Burning”, “EMBERHALL CASE”, and
“Loaded from ../case/ (truth sheet and two scene files).” No fixture query
was used. The visible comparison notebook exposed all six fact statements
on initial load, before choosing either account. I read those ordinary UI
statements, then read both full accounts. This was not hidden-state access;
it means the UI presents the evidence from both accounts before the
account-opening route starts.

### Visible route before submission

```text
20:54:28 loaded ../case/ (truth sheet and two scene files)
20:54:32 opened landing-clerk (“The North Desk”)
20:54:41 opened engine-room (“Below the Waterline”)
20:54:45 cited F1 in landing-clerk
20:54:45 cited F2 in landing-clerk
20:54:45 cited F3 in landing-clerk
20:54:45 cited F4 in engine-room
20:54:45 cited F5 in engine-room
20:54:45 cited F6 in engine-room
```

No later account switch occurred before submission. All six citations were
selected through the comparison notebook; corresponding engine-account
checkboxes visibly became selected too.

### Cited statements and reasoning

- F1, landing-clerk: Exactly one passenger boarded at 22:00 with a blue
  document tube, nobody else was aboard or boarded, and the clerk stayed
  at North Landing. This establishes the departing passenger and object.
- F2, landing-clerk: Only three usable landings exist. North is steady
  white, South steady amber, Orchard two short white flashes and a long
  dark interval. All signals are stated to function properly; both South
  and Orchard can receive passengers. This supplies the unique signal map.
- F3, landing-clerk: At 22:18 the ferry returned with crew accounted for
  but no passenger or blue tube; the clerk did not see the disembarkation.
  This is the outcome needing explanation.
- F4, engine-room: Exactly one intermediate mooring and gangway release,
  then direct return; no other stop or transfer underway. This rules out
  a different landing after observing the signal.
- F5, engine-room: At that sole intermediate stop, the fixed shore signal
  repeated two short white flashes and a long dark interval; the observer
  did not know the landing names or assignments. Combined with F2, this
  identifies Orchard Float and contradicts the scheduled South Pier.
- F6, engine-room: One passenger crossed outward with a tube; nobody
  crossed inward; the cabin remained untouched until checked on return.
  Combined with F1 and F3, this explains the empty return and missing tube.

The deduction is a straightforward join of the observed signal to the
signal map. I accept the supplied witness statements as the puzzle's
premises. There is no evidence explaining why the boat deviated from its
schedule or what happened to the passenger after leaving the gangway.

### Exact final explanation entered before submission

The passenger left at Orchard Float, taking the blue document tube. The North Desk identifies Orchard Float by two short white flashes followed by a long dark interval (F2); Below the Waterline observes precisely that repeating fixed shore signal while moored at the sole intermediate landing (F5). South Pier's steady amber signal does not match, even though it was the scheduled destination. F4 rules out a second stop or a transfer underway. F1 establishes that only one passenger and the blue tube departed North, and F6 has one passenger leave outward with a tube at that stop, nobody board, and the cabin remain untouched until return. That accounts for the empty cabin and missing tube reported at 22:18 in F3. Neither account alone identifies the landing: one supplies the signal map and the other the observed signal. Taking the stated observations and functioning signals as true, no other landing fits; the reason for the detour and what happened after disembarkation remain unknown.

---

End of immutable initial section. Any subsequent assessment follows below.


## Visible text-record export after reveal

```text
Night Ferry — playtest record
case: moth-last-crossing
title: Night Ferry: A Light Left Burning
source: ../case/ (truth sheet and two scene files)
exported: 2026-11-14T20:56:38.637Z
submitted: 2026-11-14T20:56:31.718Z

ROUTE
 1. [20:54:28] loaded ../case/ (truth sheet and two scene files)
 2. [20:54:32] opened landing-clerk (“The North Desk”)
 3. [20:54:41] opened engine-room (“Below the Waterline”)
 4. [20:54:45] cited F1 in landing-clerk
 5. [20:54:45] cited F2 in landing-clerk
 6. [20:54:45] cited F3 in landing-clerk
 7. [20:54:45] cited F4 in engine-room
 8. [20:54:45] cited F5 in engine-room
 9. [20:54:45] cited F6 in engine-room
 10. [20:56:31] submitted final explanation
 11. [20:56:31] answer revealed
 12. [20:56:38] self-assessment: supported

EVIDENCE CITED
 F1 — At 22:00 the north-landing clerk watched exactly one passenger board Moth carrying a blue document tube. Nobody else boarded, and no passenger was already aboard. The clerk remained at the north landing throughout the crossing.
    [landing-clerk] At 22:00 exactly one passenger boarded Moth at North Landing carrying a blue document tube; nobody else boarded or was already aboard, and I remained at North Landing throughout the crossing.
 F2 — There are exactly three usable landings on this reach: North Landing has a steady white lamp, South Pier a steady amber lamp, and Orchard Float two short white flashes followed by a long dark interval, repeating. The clerk personally checked all three signals before the crossing; all worked correctly and kept their assigned patterns throughout it. Both South Pier and Orchard Float can receive a passenger.
    [landing-clerk] There are exactly three usable landings on this reach: North Landing (steady white), South Pier (steady amber), and Orchard Float (two short white flashes then a long dark interval, repeating). I personally checked all three signals before the crossing; all worked properly throughout, and both South Pier and Orchard Float can receive a passenger.
 F3 — Moth returned to North Landing at 22:18 with no passenger and no blue document tube. Its crew were accounted for. The clerk could not see the intervening landings from the north desk and did not witness where the passenger left.
    [landing-clerk] Moth returned to North Landing at 22:18 with its crew accounted for, but with no passenger and no blue document tube. I could not see the other landings from the north desk and did not witness where the passenger left.
 F4 — Between leaving North Landing and returning there, Moth made exactly one intermediate landing. The engineer's continuous engine and gangway log records one intermediate stop, mooring and gangway release, followed by a direct return. There was no other stop or transfer underway.
    [engine-room] Between leaving North Landing and returning there, Moth made exactly one intermediate landing. The continuous engine and gangway log records one intermediate stop, mooring and gangway release, followed by a direct return. There was no other stop or transfer underway.
 F5 — While Moth was moored at that sole intermediate landing, the engineer saw a repeating signal through the inspection slit: two short white flashes, a long dark interval, then the same pair again. It was the landing's fixed signal, not a light aboard Moth. The engineer did not know that landing's name or the signal assignments.
    [engine-room] While Moth was moored at that sole intermediate landing, I saw a repeating signal through the inspection slit: two short white flashes, a long dark interval, then the same pair again. It was the landing's fixed signal, not a light aboard Moth. I did not know that landing's name or the signal assignments.
 F6 — At the intermediate landing the engineer heard one passenger cross the gangway outward with a tube knocking the rail; nobody crossed inward. The gangway was then secured, and nobody entered or left the passenger cabin before the clerk checked it on return. The engineer remained below and could not see the passenger's destination beyond the gangway.
    [engine-room] At that intermediate landing one passenger crossed the gangway outward with a tube knocking the rail; nobody crossed inward. The gangway was then secured, and nobody entered or left the passenger cabin before the clerk checked it on return. I remained below and could not see the passenger's destination beyond the gangway.

FINAL EXPLANATION (as written at submit)
The passenger left at Orchard Float, taking the blue document tube. The North Desk identifies Orchard Float by two short white flashes followed by a long dark interval (F2); Below the Waterline observes precisely that repeating fixed shore signal while moored at the sole intermediate landing (F5). South Pier's steady amber signal does not match, even though it was the scheduled destination. F4 rules out a second stop or a transfer underway. F1 establishes that only one passenger and the blue tube departed North, and F6 has one passenger leave outward with a tube at that stop, nobody board, and the cabin remain untouched until return. That accounts for the empty cabin and missing tube reported at 22:18 in F3. Neither account alone identifies the landing: one supplies the signal map and the other the observed signal. Taking the stated observations and functioning signals as true, no other landing fits; the reason for the detour and what happened after disembarkation remain unknown.

CASE DEDUCTION (shown only after submit)
 question: At which landing did Moth's passenger leave, and how do the two accounts explain the empty return? Name the evidence that distinguishes that landing from the scheduled South Pier.
 answer:   The passenger left at Orchard Float, carrying the blue document tube. The engineer records exactly one intermediate landing (F4), an outward passenger crossing with the tube and no return aboard (F6), and that landing's repeating pair of white flashes (F5). The clerk's independently checked signal assignments identify that pair as Orchard Float, while South Pier is steady amber (F2). The sole passenger boarded at North Landing (F1) and was absent with the tube on the 22:18 return (F3), consistently explained by that one disembarkation. Neither account supplies this identification alone: the clerk does not know the intermediate signal or stop, and the engineer does not know its place name. The evidence does not establish why the passenger chose Orchard Float, what the tube contained, or whether the change was arranged in advance.

SELF-ASSESSMENT
 supported

NOTE
 This record was produced by a local page. It is testimony, not proof of play,
 and it does not replace an independent non-author blind playtest.

```

## Post-reveal assessment

Actual browser work ended by 2026-11-14 20:56:58 UTC. I submitted the
unchanged draft at 20:56:31.718 UTC only after the coordinator reported
canonical event 3334 binding the initial file SHA256:
`d0930a2c90f0b60bea8eac143533b0c4dc51c5b9df2d5ff127fa496ab1b36fad`.
The coordinator also retained a separate initial-byte copy for comparison.
The initial section above was not edited after reveal.

### Deduction and fairness

My preserved answer matches the revealed answer: Orchard Float, identified
by matching the observed repeating white pair to the clerk's signal map,
with the sole outward disembarkation explaining the empty return. I had
already named the relevant evidence and rejected the scheduled South Pier
before seeing the answer. No correction was needed after submission.

Both accounts' **information** is necessary. The clerk alone leaves South
and Orchard possible; the engineer alone cannot attach a place name to the
signal. Together F2 and F5 identify Orchard; F1/F3/F4/F6 complete the
passenger-and-tube explanation. This is a fair deduction under the
explicit premises, with no competing landing that satisfies them. The
revealed answer appropriately refrains from claiming a motive, tube
contents, or prior arrangement. I selected “Fairly supported by both
accounts”; that is a fairness judgment, not a claim that the puzzle is hard.

It is very easy: the signal correspondence is direct, its relevant parts
are repeated, and multiple explicit negatives close alternative stories.
The prose does not literally state the final named landing, but the
comparison notebook turns the puzzle into a short evidence-matching
exercise. I had a complete draft within roughly 32 seconds of page load.
This is one model-assisted playthrough, not a human reading-time benchmark.

Opening both full accounts is **not operationally necessary** in the
current player, because the initial notebook already displays every
statement from both accounts. I did read both full accounts, but cannot
claim that opening the second one first exposed its decisive facts.
For a test specifically about two-perspective discovery or reading order,
show notebook statements only after that account has been opened (or only
after the reader marks them in its prose). If the intended product is a
simple comparison exercise, the existing presentation is usable; describe
its route as account openings, not first exposure to evidence.

A small narrative credibility issue does not change the logical answer:
the clerk says all remote beacons held their pattern throughout, while also
saying the other landings cannot be seen from the desk and that they stayed
there. The puzzle presents correct signals as an explicit premise, so I
accepted it. To make the witness basis clearer, provide a mundane source
for that certainty (for example a checked monitoring record) rather than
leaving an apparently omniscient assertion in personal testimony.

### Observed controls and export

The real case auto-loaded successfully in the fresh Chrome tab. Both
account controls worked. Selecting the six notebook citations updated the
account checkboxes. Filling the explanation worked. Submission visibly
disabled the field and button, preserved the exact submitted text, and
revealed the answer immediately. The fairness radio recorded `supported`.

“Show text record” succeeded at 20:56:38.637 UTC: a visible textarea
contained the route, citations, unchanged explanation, revealed answer,
and self-assessment. The export above was retained by reading that visible
textarea's DOM value after reveal, not by inspecting application state or
source. Download and clipboard-copy controls were visible but were not
tested; no successful download or clipboard export is claimed.

Screenshot: `/private/tmp/ferry-blind-result.jpg`, captured from the actual
Chrome tab after reveal and text-record display. It shows the submitted
state, answer, supported rating, and visible text-record area. The CUA
completion summary was sent after the final observed browser outcome.

The rendered result was legible at the existing desktop viewport, with a
clear answer panel and notebook. I did not test mobile layout, keyboard-only
navigation, reload recovery, manual file loading, or fixture controls.
Those are outside this actual blind attempt's evidence.

### Timing, interruptions, and acceptance boundary

- Real-case load to completed initial draft/record timestamp: about
  32 seconds (20:54:28 to 20:55:00 UTC).
- Real-case load to submission/reveal: about 2 minutes 3 seconds
  (20:54:28 to 20:56:31 UTC).
- Real-case load to text-record display: about 2 minutes 10 seconds.
- Real-case load to final screenshot/completion reporting bound:
  about 2 minutes 30 seconds (by 20:56:58 UTC).

Setup included unavailable `iab`, absent browser ID 2, native-app lock
reporting, and the explicit reassignment to available Chrome ID 1. During
the attempt there were coordination messages about resident naming and
journal claims. A substantial part of the pre-submit interval was record
writing, hashing, and waiting for the coordinator's requested hash receipt;
it was not time spent stuck on the mystery. There was no external hint,
solution consultation, browser reload, or interrupted/lost draft.

This record establishes one actual independent unspoiled model playthrough
with its initial answer preserved before reveal. It does not close the
project, establish broad audience difficulty, or substitute for the
integrator's comparison against author material. Only this record file was
edited; no source edits, staging, commit, or push were performed by me.
