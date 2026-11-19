"""Compare receiving families on offers whose field was recorded before admission."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

from cohort import read_pages
from trial import PROPOSED_AT, assess
from house.craft_offers import audit, summarize
from house.craft_outcomes import measure_events
from house.craft_replay import earlier_evidence, field_at


def compare(status, events, through, historical=False):
    if not events or status["sequence"] < through:
        raise ValueError("supply a nonempty interval and a verified status covering its final event")
    if historical:
        if (events[0]["sequence"], through) != (15560, 20559):
            raise ValueError("the historical comparison requires the fixed interval 15560–20559")
        basis = "historical ordinary offers after 15759"
        offers = audit([events], measure_events(events), 15759)["offers"]
        quota = sum(row["outcome"] == "quota" for row in offers)
    else:
        baseline = assess(events, through)
        basis = baseline["state"]
        offers = baseline["enrolled"]
        quota = baseline.get("quota_exits", 0)

    # A source review belongs to the whole run. The historical reader already
    # checks the fields of all its observed claims, including unfinished claims.
    evidence = earlier_evidence(status, events, through + 1)[0] if offers else {}
    credited = {(field, family, r["run_start"], r["sequence"])
                for (field, family), group in evidence.items() for r in group["first_reviews"]}
    details, grouped = [], []
    reviewed, passed = Counter(), Counter()
    for row in offers:
        project = row["area"].removeprefix("project/") if row["area"].startswith("project/") else None
        source = (field_at(status, events, project, row["offer"]) if project else
                  {"field": None, "reason": "no project association observed at offer"})
        field = source["field"] or "unclassified"
        family = row["family"]
        grouped.append(row | {"area": field})
        review = row["receiver_first_review"]
        eligible = row["launch"] is not None and row["outcome"] not in (None, "quota")
        attributable = bool(eligible and review and
                            (field, family, row["offer"], review["sequence"]) in credited)
        if attributable:
            reviewed[field, family] += 1
            passed[field, family] += review["status"] in {"reviewed", "integrated"}
        references = ("offer", "task", "generation", "assignment", "family", "launch", "exit", "outcome",
                      "disposition", "claim", "claimant_start", "claimant_family", "claim_finish",
                      "receiver_first_review")
        details.append({key: row[key] for key in references} | {
            "project": project, "field_at_offer": source, "eligible": eligible,
            "review_attributable_to_field": attributable})

    totals, overlap = [], defaultdict(list)
    for row in summarize(grouped):
        field, family = row["area"], row["family"]
        count = reviewed[field, family]
        totals.append({"field": field, "family": family, "eligible_offers": row["eligible_offers"],
                       "distinct_eligible_tasks": row["unique_eligible_tasks"], "finished": row["receiver_finished"],
                       "quota": row["quota"], "open": row["open"],
                       "closed_without_launch": row["closed_without_launch"],
                       "field_reviews": count, "first_pass": passed[field, family],
                       "review_without_field_attribution": row["reviewed_receiver_runs"] - count,
                       "finished_without_review": row["finished_without_review"]})
        if field != "unclassified" and row["eligible_offers"]:
            overlap[field].append((family, count))
    shared = [{"field": field, "received": [family for family, _ in groups],
               "with_attributable_review": [family for family, n in groups if n]}
              for field, groups in sorted(overlap.items()) if len(groups) >= 2]
    return {"basis": basis, "first": events[0]["sequence"], "through": through,
            "status_sequence": status["sequence"], "quota_exits": quota,
            "totals": sorted(totals, key=lambda r: (r["field"], r["family"])),
            "shared_fields": shared, "offers": details}


def display(report):
    print(f"Journal {report['first']}–{report['through']} | {report['basis']}")
    if report["basis"] == "installation not observed":
        print("The post-installation field comparison has no observations yet.")
        return
    print(f"Eligible receiving offers {sum(row['eligible_offers'] for row in report['totals'])}"
          f" | quota exits in the observed offer interval {report['quota_exits']}")
    for row in report["totals"]:
        excluded = [f"{label} {row[key]}" for key, label in
                    (("quota", "quota"), ("open", "still open"), ("closed_without_launch", "without launch"))
                    if row[key]]
        print(f"{row['field']} / {row['family']} | finished {row['finished']}/{row['eligible_offers']}"
              f" | first passes {row['first_pass']}/{row['field_reviews']} attributable reviews"
              f" | {row['finished_without_review']} awaiting or missing a review"
              f" | {row['review_without_field_attribution']} reviews without field attribution"
              + (f" | excluded {', '.join(excluded)}" if excluded else ""))
    if not report["shared_fields"]:
        print("No recorded field received eligible offers in two families.")
    for row in report["shared_fields"]:
        print(f"{row['field']} | received by {', '.join(row['received'])}"
              f" | attributable reviews for {', '.join(row['with_attributable_review']) or 'none'}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status", required=True, type=Path, help="covering verified house status")
    parser.add_argument("--historical", action="store_true", help="use the frozen earlier ordinary-offer sample")
    parser.add_argument("--json", action="store_true", help="include the event references for each offer")
    parser.add_argument("pages", nargs="+", type=Path, help="consecutive verified journal read pages")
    args = parser.parse_args()
    try:
        cursor = 15759 if args.historical else min(PROPOSED_AT, json.loads(args.pages[0].read_text())["through"])
        events, through = read_pages(args.pages, cursor)
        report = compare(json.loads(args.status.read_text()), events, through, args.historical)
    except (KeyError, TypeError, ValueError, OSError) as exc:
        parser.exit(2, f"Cannot compare fields: {exc}\n")
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        display(report)


if __name__ == "__main__":
    main()
