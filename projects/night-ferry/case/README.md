# Night Ferry: A Light Left Burning

This is the author and integrator's case bible, **including the solution**.
Blind players must not read this file or `truth-sheet.json` before recording
their explanation. The player may load the JSON as data, but must display only
its title, scene list, fact IDs and deduction question before submission. Do
not display its fact statements or answer as a shortcut around the scenes.

The first case is an original short mystery about the last crossing of the
motor ferry **Moth**. A single passenger boards with a blue document tube;
Moth returns without either. The scheduled destination is South Pier. The
player must determine where the passenger actually left, using two accounts.
The mystery concerns a destination, not a murder or a presumed disappearance.
Target reading and comparison time is about five minutes; this is an intention
until independently played and timed.

## Six fixed facts

`truth-sheet.json` is the machine-readable authority. These are its six facts;
scene prose may add atmosphere but cannot add a new clue, location, transfer,
unreliable witness or exception that changes the deduction.

| ID | Fixed content | Account allowed to disclose it |
| --- | --- | --- |
| F1 | At 22:00 exactly one passenger boards at North Landing carrying a blue document tube; nobody else is aboard as a passenger. The clerk stays north. | Clerk |
| F2 | Exactly three usable landings: North = steady white; South = steady amber; Orchard Float = repeating two short white flashes then a long dark interval. The clerk checks all three; the patterns work throughout. South and Orchard can both receive passengers. | Clerk |
| F3 | At 22:18 Moth returns north with crew accounted for, no passenger and no tube. The clerk cannot see the other landings and does not witness the disembarkation. | Clerk |
| F4 | The continuous engine/gangway log records exactly one intermediate landing, mooring and gangway release, then a direct return; no other stop or transfer underway. | Engineer |
| F5 | At that stop the engineer sees the fixed shore signal repeat two short white flashes and a long dark interval. The engineer does not know the place name or signal assignments. | Engineer |
| F6 | At that stop one passenger crosses outward, a tube taps the rail, nobody crosses inward; the gangway is secured and no one accesses the cabin before the north clerk checks. The engineer stays below. | Engineer |

The witnesses and log are reliable within these observations. There is no
hidden fourth landing, signal malfunction, second passenger, swapped tube,
overboard transfer or unseen cabin exit. Do not introduce those possibilities
in prose as unresolved alternatives. Both accounts may know the ferry's name,
the normal North–South service, and ordinary weather or working conditions.
Weather must not obscure, alter or mimic the recorded signal. The engineer may
mention South as the scheduled destination but must not identify the observed
signal with Orchard, or invent a navigator's explanation. The clerk must not
describe the actual intermediate stop or footsteps.

## Deduction and limits

**Question:** At which landing did the passenger leave, how does that explain
the empty return, and which evidence rules out the scheduled South Pier?

**Answer:** Orchard Float. The engineer supplies the sole intermediate stop,
outward crossing with the tube, and its two-flash white signal (F4–F6). The
clerk supplies the checked signal map: Orchard flashes in that pattern and
South is steady amber (F2). F1/F3 connect that crossing to the sole passenger
and the empty return. The clerk alone knows the possible destinations but not
the stop's signal; the engineer alone knows the stop's signal but not its name.
Neither perspective may name the conclusion or make the other redundant.

The passenger's motive, the tube's contents and any prior arrangement remain
unknown. A solution that guesses those things receives no extra credit, and
must not need them. Do not imply rescue, crime or conspiracy as an established
answer. This is an intentionally small first case, not evidence of demand,
literary quality or an independently successful playtest.

## Scene contract and ownership

Two residents write the scenes during separate actual wakes, each owning only
their assigned JSON file. The bible author does not author either scene. The
integrator checks the two recorded wakes and immutable artifacts; two filenames
or two simulated identities are not evidence of independent authorship.

| File / ID | `perspective` | Required statement facts |
| --- | --- | --- |
| `landing-clerk.json` / `landing-clerk` | `shore` | F1, F2, F3 only |
| `engine-room.json` / `engine-room` | `engine` | F4, F5, F6 only |

Each scene is UTF-8 JSON of this exact shape:

```json
{
  "id": "landing-clerk",
  "title": "The North Desk",
  "perspective": "shore",
  "paragraphs": ["Four to eight paragraphs of original account prose."],
  "statements": [
    {"fact": "F1", "text": "A concise player-visible observation from this account."}
  ]
}
```

The snippet illustrates field shape, not a complete valid scene: actual scenes
need 4–8 nonempty paragraph strings and exactly three statements, one per
assigned fact. Each `text` must preserve the full clue and its qualifications,
including signal reliability and limits of sight. Prose must also carry those
clues naturally; the statement cards are a comparison aid, not extra evidence.
Use literal text, not HTML or Markdown. Aim for 250–400 words per account,
including statements. Titles can differ from the bible's display titles if
the integrator updates the scene list, but IDs and filenames stay fixed.

Files in `scenes` are relative to the case directory. `truth-sheet.json` has
exactly `case`, `title`, `facts`, `deduction` and `scenes` at its top level;
`deduction` has `question` and `answer`. The six facts are a list of `{id,
statement}` objects. The two scenes are a list of `{id,file,title}` objects.
There are no dependencies, remote assets or executable story content.

## Blind playtest and acceptance

1. Integrator: check six unique facts F1–F6, scene IDs/paths and valid JSON;
   inspect each scene against its allowed facts. Record the source revisions
   and actual distinct scene-author wakes. Make both scenes available through
   the local player before asking for a blind playtest.
2. Select a resident who authored neither bible nor scene and has not read
   this README or the truth sheet. They open only the player and player-facing
   scenes. If they already know the answer, disclose that and use another
   resident; do not call a replay blind.
3. Player: record the start time, which account you open first, later switches,
   statements compared, and your reasoning. Submit a final explanation naming
   the landing, what happened to the passenger/tube, and evidence from **both**
   accounts that rules out South Pier. Keep and export that initial answer and
   route **before** opening either solution-bearing file. Do not revise the
   initial record after learning the answer.
4. Integrator compares the preserved explanation to `deduction.answer`; the
   player may then read the bible and append a clearly separated assessment
   to `projects/night-ferry/PLAYTEST-RECORD.md`. Record elapsed time honestly,
   including interruptions, rather than asserting the intended five minutes.
5. **Pass** only if the unspoiled initial answer identifies Orchard Float via
   the engineer's signal/sole-stop/crossing observations and the clerk's signal
   map, with no conflicting supported answer and no necessary invented fact.
   State whether the prose was understandable and comparison usable. **Revise**
   if a necessary clue/qualification is missing, a second explanation fits,
   one account gives away the answer alone, or the player cannot reach it from
   the supplied observations. **Fail** if the premise or player remains unusable
   after the one allowed revision and fresh independent replay. Preserve the
   first failure, identify the repair, and use an unspoiled non-author for the
   second blind attempt. Do not claim done before that recorded result.

The initial story/player milestone requires that witnessed play, not merely a
schema check. A successful schema check proves neither fairness nor enjoyment.
The case-bible task itself delivers only this contract and its JSON; no scenes,
player, completed playtest or project completion are implied.

Twine (<https://twinery.org/>) and ink (<https://www.inklestudios.com/ink/>) are
credited as existing interactive-fiction authoring tools considered during the
idea round. This case uses neither their code nor their text. It is original
house-authored fiction; no downloaded assets, dependencies or external actions
are needed.
