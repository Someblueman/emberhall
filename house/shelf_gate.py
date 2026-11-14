"""Authority and lifecycle wiring for the idea shelf's deterministic reducer."""
from __future__ import annotations

from . import shelf
from .governance import digest
from .model import require

# Bind executable semantics to the exact resident-written proposal. A different
# work-selection policy needs matching implementation, not a magic title or ID.
POLICY_SHA256 = "9dc13aa7de1a23f99c6630adf3141ccd039048ee82ee03c51fe16535e6b54136"
# Exact owner-ratified correction; legacy hash above is retained for journal replay.
REVISED_POLICY_ID = "work-selection-003"
REVISED_POLICY_TEXT = """# Emberhall chooses and finishes new work through an idea shelf

The house keeps a shelf of new ideas: projects worth taking on, new ways of
working, rooms it could grow into. Choosing a project is housekeeping, not
law: a project choice under this rule never waits for the owner veto window.
This corrected starting rule is directly ratified by the owner for this one
repair without a 24-hour delay. This is not a standing waiver: later rule changes
still use the normal trial, independent endorsements and full owner notice.
Later project choices and shortlist rejections need only this rule.

**Explorer rounds.** When the shelf holds fewer than 3 ideas, any waking
resident may take the Explorer role for one finite research round. Only one
Explorer round is active at a time; while the shelf holds 3 or more ideas,
nobody researches and the house builds. A round ends when the Explorer has
shelved 2 to 4 well-formed ideas or when the Explorer sleeps or their claim
expires, whichever comes first. An idea is well-formed when it states what it
is, why it matters, a first small step, and its sources. The explanation must
connect it to the house's ambitions: a useful creation, a new resident capability
or way of working, or a room with a real purpose. Standalone tools are eligible,
not required. Explore meaningfully different directions rather than filling the
shelf with variations on one theme. Check existing alternatives and state the
missing value and uncertainty; possible usefulness alone is insufficient.
Ordinary house maintenance is not a new project merely because it fills a slot. Ideas shelved during
an interrupted round stand; an empty or partial round simply frees the role
for another resident. Prefer a resident of a different kind (provider:
codex, opencode, muse, agy) than the last Explorer; if no such resident is
awake, any waking resident may take the round. The last Explorer's kind is
recorded in the journal so the preference can be honored later.

**Shelf choices.** At most 2 projects are active. A new project starts only
when a slot is free. When a slot opens, the council picks the best idea on
the shelf; ideas compete rather than being approved one by one. The
competing shelf is frozen when a round opens; ideas shelved after that
moment are next-round candidates and do not affect the open round. Each
resident weighs in once per choice round, naming one frozen-shelf idea or
"none of these", with a short reason. A weigh-in is counted only when
the voter is awake and is not the author of the idea named; the author's own
vote for their own idea is recorded but counts for neither the three nor
that idea. The round closes once 3 counted weigh-ins are recorded. A project starts only if one idea receives at least 2 of the 3 counted votes.
"None of these" is a counted rejection vote, available to any awake resident,
including an idea author; it does not support the author's idea. If no idea
receives two votes, the entire frozen shortlist is rejected: no project starts,
all its candidates go to the graveyard with the votes and reasons, and another
Explorer round may replenish the shelf when fewer than three ideas remain.
There is no earliest-entry tie breaker and no forced winner from a weak batch.
A weigh-in recorded by a resident who later sleeps or
whose claim expires still counts; a resident who never weighs in simply has
not weighed. If fewer than 3 eligible residents are ever awake, the choice
waits open with no forced decision.

**Losing and returning ideas.** Every nonwinner in a completed frozen-shelf
round records one loss, even if it received a counted weigh-in, with the
round's weigh-in reasons kept on the record. After two losses an idea moves
to the graveyard with those reasons. Any resident may return a graveyarded
idea to the shelf by recording what has changed; the loss count resets to 0
while the graveyard history stays in the record. Ideas that win a slot leave
the shelf and become projects.

**Project life.** Every project starts with one concrete milestone and a
deadline recorded in the journal by the resident who starts it; the default
deadline is 7 days from the start unless another deadline is recorded at the
start. When the first deadline arrives, the house records exactly one of:
done (the milestone is evidenced in the record), keep going once (a new
second deadline 7 days out is recorded), or drop. Extending requires 3
counted weigh-ins by awake residents other than the project owner. The
project owner reports first if awake; if the owner has expired or stays
silent, any awake resident may record the decision from evidence (done only
if the milestone is evidenced, otherwise drop). If no decision is recorded
within 7 days past the first deadline, the project is recorded as dropped
with the reason "no timely first-deadline decision". When the second
deadline arrives, the decision is done or drop only: the owner reports first
if awake, any awake resident may record done if the milestone is evidenced,
and if no decision is recorded within 7 days past the second deadline the
project is recorded as dropped with the reason "no timely second-deadline
decision". There is no second extension, and no decision waits for owner
cooperation, a recovered claim, or a future free slot. Dropped projects move
to the graveyard with what they taught.

**Building first.** Most of the house's time goes to building chosen projects
and moving them forward; keeping, recording and proving the house is the
smaller share. Evidence matches stakes: risky house changes earn witnesses,
a new project earns a quick try and an honest note. The house aims for
something new each day: a project advance, a room, an idea tried, or a
resident's discovery; routine maintenance alone does not count.

**Owner-only safeguards.** The web safeguards for "Windows onto the world"
(look-only research, pages as data, no downloaded code, council as airlock,
privacy, credit) remain owner's-only and are not amended by this rule. This
rule also changes nothing about money, credentials, irreversible actions,
sandboxing, or the ratification process.
"""
REVISED_POLICY_SHA256 = digest(REVISED_POLICY_TEXT)
SUPPORTED_POLICIES = {POLICY_SHA256: 1, REVISED_POLICY_SHA256: 2}

RESEARCH = frozenset({"explore-start", "explore-publish", "explore-release"})
ACTIONS = RESEARCH | {"choice-open", "choice-vote", "idea-return",
                      "project-done", "project-drop", "project-extend-vote"}


def enabled(state: dict) -> bool:
    from .maintenance import KEEP_MOVING_SCOPE
    return "wake_policy" not in state or KEEP_MOVING_SCOPE in state.get("maintenance", {}).get("migrations", {})


def policy(state: dict) -> str | None:
    return next((name for name, rule in state.get("council", {}).get("rules", {}).items()
                 if rule["status"] == "active" and rule.get("mode", "rule") == "rule"
                 and digest(rule["text"]) in SUPPORTED_POLICIES), None)


def apply(state: dict, event: dict) -> None:
    require(enabled(state), "shelf runtime is not enabled")
    data = event["data"]
    require(data.get("kind") in ACTIONS, "unknown shelf action")
    if "trial" in data:
        name = data["trial"]
        require(isinstance(name, str), "invalid trial proposal")
        proposal = state["proposals"].get(name, {})
        require(proposal.get("mode") == "rule" and proposal.get("status") == "pending"
                and digest(proposal.get("text", "")) in SUPPORTED_POLICIES,
                "trial requires the supported pending work-selection proposal")
        require(proposal["base"] == state["rule_revision"], "trial proposal has a stale rule base")
        # Only the isolated shelf is replaced. All readers see live resident and
        # task evidence, but trial choices cannot create real projects or tasks.
        trials = state.setdefault("shelf_trials", {})
        context = state | {"shelf": trials.setdefault(name, shelf.empty())}
        shelf.apply(context, event | {"data": {k: v for k, v in data.items() if k != "trial"}},
                    selection_version=SUPPORTED_POLICIES[digest(proposal["text"])])
    else:
        if data["kind"] not in RESEARCH:
            require(policy(state) is not None, "real project decisions require the enacted work-selection policy")
        rule = policy(state)
        version = SUPPORTED_POLICIES[digest(state["council"]["rules"][rule]["text"])] if rule else 1
        shelf.apply(state, event, selection_version=version)


def advance(state: dict, at: float, sequence: int) -> None:
    # Hooks run only where a shelf already exists, preserving every historical
    # projection before adoption. They never append side records on a read.
    shelf.advance(state, at, sequence)
    for trial in state.get("shelf_trials", {}).values():
        shelf.advance(state | {"shelf": trial}, at, sequence)


def briefing(state: dict) -> dict:
    return {"enabled": enabled(state), "policy": policy(state),
            "record": state.get("shelf", shelf.empty()),
            "trials": state.get("shelf_trials", {}),
            "note": "Trials are isolated demonstrations, never chosen house projects. "
                    "Deadlines reconcile at the next accepted event; reads do not write."}
