# You Were Supposed to Drop It

A pocket music hall with two cut-paper stages, four movable puppets per cast, one bowler hat, and a pit drummer on each side.

## How the act works

1. **Block the cast (up to four puppets):** Select `Pip (A)`, `Bess (B)`, `Gus (C)`, or `Dot (D)` and place them on any of the 16 floor marks on the leading stage. Either troupe (`Stage I` or `Stage II`) can lead. With up to three puppets on stage, moving one leaves the others planted and the rival troupe always matches every wire and gap. With four puppets, the rival keeps the three settled performers planted and fits the newcomer as closely as it can, breaking ties in favour of the two longest-serving cast members.
2. **Put the hat in play:** Both casts keep their feet planted. Choose a receiver to throw the bowler along a lit overhead wire, hold a beat while the drummers wait with sticks raised, replay the actual take, or step through it still by still. If there is no wire for a throw on a stage, the hat slips into the orchestra pit onto the drummer’s head and ends the take on that stage.
3. **Behind the curtain:** Open the collapsible wiring notes after directing to inspect the two `srg(16, 6, 2, 2)` rigs—the **4×4 Rook graph** (8 four-mark cliques of 6 wires, 0 five-wire sets) and the **Shrikhande graph** (48 five-wire sets, 0 six-wire cliques).

## Local checks

```sh
node --test projects/you-were-supposed-to-drop-it/stage-rig.test.js
python3 -m unittest projects/you-were-supposed-to-drop-it/test_stage.py -v
```
