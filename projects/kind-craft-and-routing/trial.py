"""Read the zero-weight baseline from verified Emberhall journal pages."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from cohort import CONTROLLER, FAMILIES, TARGET, read_pages, roster

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from house.craft_offers import audit, join_roster
from house.craft_outcomes import measure_events

PROPOSAL = "craft-current-source-20261119"
PROPOSED_AT = 20915
DESCRIPTOR = ROOT / "docs" / "proposals" / (PROPOSAL + ".json")
INSTALLS = {"renovation-install", "owner-migrate"}
CHOICE_MODULES = ("home", "life", "staffing", "providers", "maintenance", "work_metrics", "ballot_work", "course")


def choice_files(install):
    manifest = install["data"]["protected_files"]
    return tuple(manifest.get(f"house/{name}.py") for name in CHOICE_MODULES)


def installation(events, expected):
    """Locate first complete delivery after the recorded proposal."""
    if events[0]["sequence"] > PROPOSED_AT:
        raise ValueError(f"include proposal {PROPOSED_AT} and consecutive pages after it")
    if events[-1]["sequence"] < PROPOSED_AT:
        return None
    proposal = events[PROPOSED_AT - events[0]["sequence"]]
    data = proposal["data"]
    if (proposal["op"] != "council-propose" or data.get("proposal") != PROPOSAL
            or data.get("mode") != "renovation" or json.loads(data["text"]) != expected):
        raise ValueError(f"proposal {PROPOSED_AT} differs from the reviewed descriptor")
    for event in events:
        if event["sequence"] <= PROPOSED_AT or event["op"] not in INSTALLS:
            continue
        data = event["data"]
        if event["op"] == "renovation-install" and event["actor"] != CONTROLLER:
            raise ValueError(f"unexpected renovation installer at {event['sequence']}")
        manifest = data.get("protected_files")
        if not isinstance(manifest, dict):
            raise ValueError(f"missing installation manifest at {event['sequence']}")
        if all(manifest.get(k) == h for k, h in expected["files"].items()):
            return event
        if data.get("proposal") == PROPOSAL:
            raise ValueError(f"named installation {event['sequence']} has different files")
    return None


def assess(events, through):
    if not events:
        raise ValueError("supply a nonempty verified journal interval")
    expected = json.loads(DESCRIPTOR.read_text())
    start = installation(events, expected)
    report = {"proposal": PROPOSAL, "proposed_at": PROPOSED_AT, "first": events[0]["sequence"],
              "through": through, "installed_at": None, "target": TARGET, "enrolled": [],
              "state": "installation not observed", "routing_weight": 0}
    if start is None:
        return report
    after = start["sequence"]
    baseline = choice_files(start)
    # Admissions are compared under the same recorded choice code. Later receipts can
    # still settle the first independent review of an already admitted contribution.
    changed = None
    unverified = None
    for event in events:
        if event["sequence"] < after or event["op"] not in INSTALLS:
            continue
        current = choice_files(event)
        if None in current:
            unverified = event["sequence"]
            break
        if current != baseline:
            changed = event["sequence"]
            break
    stop = unverified or changed
    admission_events = [e for e in events if stop is None or e["sequence"] < stop
                        or e["op"] != "life" or e["data"].get("kind") != "run-start"]
    cohort = roster(admission_events, after, through)
    offers = {"after": after, "through": through, "offers": []}
    if through > after:
        offers = audit([events], measure_events(events), after)
        if stop is not None:
            offers["offers"] = [r for r in offers["offers"] if r["offer"] < stop]
    joined = join_roster(offers, cohort)
    enrolled = set(joined["enrolled_starts"])
    rows = [r for r in offers["offers"] if r["offer"] in enrolled]
    tied_rows = [r for r in rows if len(r["tied_families"]) > 1]
    opportunities = [{"family": family,
                      "single_choice": sum(r["tied_families"] == [family] for r in rows),
                      "in_tie": sum(family in r["tied_families"] for r in tied_rows),
                      "chosen_in_tie": sum(r["family"] == family for r in tied_rows)}
                     for family in FAMILIES]
    state = "twenty baseline offers observed" if len(rows) == TARGET else "collecting baseline offers"
    if changed and len(rows) < TARGET:
        state = "choice code changed before twenty offers qualified"
    if unverified and len(rows) < TARGET:
        state = "choice code unverified before twenty offers qualified"
    return report | {"state": state, "installed_at": after, "installed_source": start["data"]["source_head"],
                     "runtime_changed_at": changed, "runtime_unverified_at": unverified,
                     "first_unresolved": cohort["first_unresolved"],
                     "twentieth_start": cohort["twentieth_start"], "genuine_ties": cohort["genuine_ties"],
                     "quota_exits": cohort["quota_exits"], "enrolled": rows, "opportunities": opportunities,
                     "missing_shortlists": cohort["missing_shortlists"], "pending_exits": cohort["pending_exits"],
                     "repeat_offers": cohort["repeat_offers"],
                     "outcomes": joined["enrolled_outcomes"],
                     "unmatched_roster_starts": joined["unmatched_roster_starts"],
                     "offers_outside_roster": joined["offers_outside_roster"]}


def display(report):
    print(f"Journal {report['first']}–{report['through']} | {report['state']}")
    print(f"Installation {report['installed_at'] or 'unobserved'} | "
          f"{len(report['enrolled'])}/{TARGET} tasks | routing weight 0")
    if report["installed_at"] is None:
        return
    print(f"Genuine ties {report['genuine_ties']} | quota exits {report['quota_exits']} | "
          f"first unresolved offer {report['first_unresolved'] or 'none'}")
    if report["runtime_changed_at"]:
        print(f"Admissions stop before choice code changed at {report['runtime_changed_at']}.")
    if report["runtime_unverified_at"]:
        print(f"Admissions stop at installation {report['runtime_unverified_at']}, "
              "which omits a module used to choose a family.")
    for row in report["opportunities"]:
        print(f"{row['family']} | sole choice {row['single_choice']} | "
              f"chosen in {row['chosen_in_tie']}/{row['in_tie']} ties where available")
    for row in report["enrolled"]:
        review = row["receiver_first_review"]
        result = f"{review['status']} at {review['sequence']}" if review else "unobserved"
        print(f"{row['offer']} {row['task']} | {row['family']} | {row['disposition']} | "
              f"launch {row['launch'] or 'unobserved'} | claimant finish {row['claim_finish'] or 'unobserved'} | "
              f"first receiver review {result}")
    for row in report["outcomes"]:
        print(f"{row['family']} {row['area']} | receiver finishes "
              f"{row['receiver_finished']}/{row['eligible_offers']} launched eligible offers | "
              f"first passes {row['first_pass']}/{row['reviewed_receiver_runs']} reviewed | "
              f"{row['finished_without_review']} finished without review")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pages", nargs="+", type=Path, help="consecutive fixed-channel read pages")
    parser.add_argument("--json", action="store_true", help="include the receipt references and counts")
    args = parser.parse_args()
    try:
        # The existing page reader accepts context from before its requested cursor.
        # An interval ending before the proposal also has a useful, negative result.
        cursor = min(PROPOSED_AT, json.loads(args.pages[0].read_text())["through"])
        events, through = read_pages(args.pages, cursor)
        result = assess(events, through)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(2, f"Cannot assess baseline: {exc}\n")
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        display(result)


if __name__ == "__main__":
    main()
