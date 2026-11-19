"""Compare recorded ties using only earlier receiving-run outcomes; never route work."""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path

from trial import REVIEWED, assess, baseline_option, baseline_pages
from house.craft_offers import audit
from house.craft_outcomes import measure_events
from house.craft_replay import earlier_evidence, field_at

MIN_REVIEWS = 3


def prior_results(status, events, before, field, families):
    """Count offers, not arbitrary claims, and credit only same-field reviews."""
    rows = {family: {"eligible_offers": 0, "finished": 0, "reviewed": 0,
                     "passed": 0, "missing_review": 0, "unattributed_review": 0,
                     "quota": 0, "open": 0, "closed_without_launch": 0,
                     "examples": []} for family in families}
    prefix = [event for event in events if event["sequence"] < before]
    if not prefix or field is None:
        return rows
    outcomes = measure_events(prefix)
    offers = audit([prefix], outcomes, prefix[0]["sequence"] - 1)["offers"]
    evidence, _ = earlier_evidence(status, prefix, before)
    credited = {(area, family, r["run_start"], r["sequence"])
                for (area, family), group in evidence.items() for r in group["first_reviews"]}
    for offer in offers:
        family = offer["family"]
        if family not in rows or not offer["area"].startswith("project/"):
            continue
        project = offer["area"].removeprefix("project/")
        if field_at(status, prefix, project, offer["offer"])["field"] != field:
            continue
        row = rows[family]
        if offer["outcome"] == "quota":
            row["quota"] += 1
            continue
        if offer["outcome"] is None:
            row["open"] += 1
            continue
        if offer["launch"] is None:
            row["closed_without_launch"] += 1
            continue
        row["eligible_offers"] += 1
        finished = offer["disposition"] == "receiver finished"
        row["finished"] += finished
        review = offer["receiver_first_review"] if finished else None
        attributable = bool(review and (field, family, offer["offer"], review["sequence"]) in credited)
        row["reviewed"] += attributable
        row["passed"] += bool(attributable and review["status"] in {"integrated", "reviewed"})
        row["missing_review"] += finished and review is None
        row["unattributed_review"] += bool(review and not attributable)
        row["examples"].append({"offer": offer["offer"], "assignment": offer["assignment"],
                                "claim": offer["claim"], "finish": offer["claim_finish"],
                                "exit": offer["exit"], "review": review,
                                "review_attributable": attributable})
    return rows


def preference(baseline, families, rows):
    """A fixed descriptive score, with no statistical or routing claim."""
    if len(families) < 2:
        return baseline, "sole recorded choice"
    if any(rows[family]["reviewed"] < MIN_REVIEWS for family in families):
        return baseline, "insufficient earlier reviewed receiving runs"
    scores = {family: (Fraction(rows[family]["passed"], rows[family]["reviewed"]),
                       Fraction(rows[family]["finished"], rows[family]["eligible_offers"]))
              for family in families}
    best = max(scores.values())
    winners = [family for family in families if scores[family] == best]
    if baseline in winners or len(winners) != 1:
        return baseline, "ordinary choice retained on equal scores" if len(winners) > 1 else "ordinary choice scores highest"
    return winners[0], "higher descriptive score; fairness and benefit unverified"


def replay(status, events, through, baseline=REVIEWED):
    if not events or status["sequence"] < through:
        raise ValueError("supply a nonempty interval and a status covering its final event")
    trial = assess(events, through, baseline)
    decisions = []
    for offer in trial["enrolled"]:
        project = offer["area"].removeprefix("project/") if offer["area"].startswith("project/") else None
        provenance = (field_at(status, events, project, offer["offer"]) if project else
                      {"field": None, "reason": "no project association at admission"})
        families = offer["tied_families"]
        rows = prior_results(status, events, offer["offer"], provenance["field"], families)
        preferred, reason = preference(offer["family"], families, rows)
        if provenance["field"] is None:
            reason = provenance["reason"]
        decisions.append({"offer": offer["offer"], "task": offer["task"],
                          "assignment": offer["assignment"], "field_at_offer": provenance,
                          "baseline": offer["family"], "tied_families": families,
                          "earlier": rows, "evidence_preference": preferred, "reason": reason,
                          "routing_choice": offer["family"],
                          "fairness": "not established by a shortlist; no routing change"})
    return {"baseline": baseline, "first": events[0]["sequence"], "through": through,
            "policy_stop": trial.get("runtime_unverified_at") or trial.get("runtime_changed_at"),
            "installed_at": trial["installed_at"], "trial_state": trial["state"],
            "minimum_reviews_per_family": MIN_REVIEWS, "routing_weight": 0,
            "alternative_outcomes_estimated": False, "decisions": decisions,
            "different_preferences": sum(d["baseline"] != d["evidence_preference"] for d in decisions)}


def display(report):
    print(f"Journal {report['first']}–{report['through']} | {report['baseline']} | {report['trial_state']}")
    print(f"{len(report['decisions'])} enrolled comparisons | routing weight 0 | no alternative outcomes estimated")
    for decision in report["decisions"]:
        print(f"{decision['offer']} {decision['task']} | ordinary {decision['baseline']} | "
              f"evidence preference {decision['evidence_preference']} | {decision['reason']}")
        for family, row in decision["earlier"].items():
            print(f"  {family}: finishes {row['finished']}/{row['eligible_offers']} earlier offers; "
                  f"first passes {row['passed']}/{row['reviewed']} attributable reviews; "
                  f"missing {row['missing_review']}, unattributed {row['unattributed_review']}; "
                  f"excluded: quota {row['quota']}, open {row['open']}, unlaunched {row['closed_without_launch']}")
    print("Recorded ties do not establish the family floor after a changed choice. All routing choices remain ordinary.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    baseline_option(parser)
    parser.add_argument("--status", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("pages", nargs="+", type=Path)
    args = parser.parse_args()
    try:
        events, through = baseline_pages(args.pages, args.baseline)
        report = replay(json.loads(args.status.read_text()), events, through, args.baseline)
    except (KeyError, TypeError, ValueError, OSError) as exc:
        parser.exit(2, f"Cannot compare recorded ties: {exc}\n")
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        display(report)


if __name__ == "__main__":
    main()
