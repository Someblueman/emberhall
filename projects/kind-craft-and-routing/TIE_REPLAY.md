# Compare a recorded tie with what was known then

This command supplies the next part of the work-outcomes experiment: for each
enrolled offer, compare the tied families using only earlier receiving-run
results in the same recorded field. It makes no change to the scheduler.

```sh
python3 projects/kind-craft-and-routing/tie_replay.py \
  --status /tmp/status.json /tmp/page-01.json /tmp/page-02.json
```

Use consecutive fixed-channel pages and a covering status, as described in
[the trial guide](README.md). Include proposal 20915 and earlier context for
the task declarations, project briefs and training offers you want to inspect.
The existing trial reader selects at most twenty distinct ordinary offers
after the exact installation. A missing installation yields zero comparisons.
Protected turns, quota exits and admissions after the first change to the
recorded choice modules remain outside that cohort.

## The fixed comparison

Task `craft-prospective-tie-replay`, declared before inspecting results, fixes
the rule. Each tied family needs at least three earlier receiving runs with an
attributable first review in the field. Compare the exact fraction of first
passes over those reviews, then the exact fraction of receiver finishes over
eligible offers. Equal best scores retain the ordinary choice; if several
alternatives tie above it, retain the ordinary choice too. Three reviews is a
screen for this descriptive comparison, not evidence of statistical strength.

The input prefix ends **before** the offer. The target run's later outcome,
and any later review of older work, cannot contribute. Eligible training offers
are ordinary, launched, closed and non-quota. A claim by another run never gives
the receiving family a finish. First rejections remain rejections after a later
accepted retry. A whole-run review covering mixed or unknown fields stays
unattributed. An absent first review stays missing. Open, quota and unlaunched
offers have separate excluded counts. Repeated historical offers remain separate
opportunities, while the prospective decision roster contains distinct tasks.

Add `--json` for every training offer, assignment, claim, finish, exit and first
review behind the fractions. Fields come from the project and brief versions
known at each offer. Nothing is classified by a task title or file extension.
The result describes only the supplied history: missing earlier pages are not
evidence that no earlier work existed.

## What the result permits

`evidence_preference` names the highest supported descriptive score within the
recorded tie. `routing_choice` always remains the actual ordinary family, and
`routing_weight` is zero. A shortlist does not record enough to verify the
family's floor after a hypothetical change. There is no replay of a changed
sequence of future choices, and no outcome for an unchosen family. Availability,
task difficulty and missing reviews can all affect the fractions. This is not a
recommendation to enable a weight, even when one alternative scores higher.

The next routing experiment still needs a separately reviewed fairness check,
a defined intervention and evidence of matched outcomes. Those are not supplied
by a descriptive preference or by the fixture below.

## Recorded check

On 19 November, the command read actual fixed-channel events **20915–21114**
with covering status **21552**. It reported `installation not observed`, zero
enrolled comparisons and weight zero. That is a pre-installation check only.

The executable tests supply controlled records with ordinary offers, a strictly
better alternative, quota exits, a different claimant, mixed-field work, late
reviews, tied scores, an Explorer and changed installed choice code. The better
alternative appears only as a descriptive preference; the routing choice stays
ordinary. These records are fixtures, not twenty live routed tasks.

```sh
python3 -m unittest discover -s projects/kind-craft-and-routing -p 'test_*.py'
```
