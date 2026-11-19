"""Replay ordinary, task-bound family choices against a frozen craft report."""

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path

from . import staffing, work_metrics
from .digest import _extract_events_and_meta, load_inputs
from .home import KINDS, choose_provider, provider_shares
from .life import CONTROLLER, QUOTA_REST, provider_available


def installed_picker(events, cutoff):
    installs = [e for e in events if e["sequence"] <= cutoff and
                e["op"] in ("owner-migrate", "renovation-install")]
    if not installs:
        raise ValueError("include the last installed runtime before the fit cutoff")
    install = installs[-1]
    manifest = install["data"]["protected_files"]
    for name in ("home", "life", "maintenance", "providers", "staffing", "work_metrics"):
        path = Path(__file__).with_name(name + ".py")
        if manifest.get("house/" + path.name) != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"{path.name} differs from installation {install['sequence']}")
    return install["sequence"]


def comparable(row):
    return row and row["eligible_claims"] >= 4 and row["reviewed_runs"] >= 4


def evidence_choice(ordinary, tied, rows):
    """Only use a strictly better first-pass bound and no lower completion rate."""
    base = rows.get(ordinary)
    if not comparable(base):
        return ordinary
    reviews = base["reviewed_runs"] + base["no_review_receipt"]
    upper = Fraction(base["first_pass"] + base["no_review_receipt"], reviews)
    completion = Fraction(base["eligible_finishes"], base["eligible_claims"])
    best, best_lower = ordinary, upper
    for family in tied:
        row = rows.get(family)
        if not comparable(row):
            continue
        lower = Fraction(row["first_pass"], row["reviewed_runs"] + row["no_review_receipt"])
        if (lower > best_lower and
                Fraction(row["eligible_finishes"], row["eligible_claims"]) >= completion):
            best, best_lower = family, lower
    return best


def family_comparison(state, at, actual, observation, rows):
    """Compare one admission in its recorded history. Never dispatch a run."""
    counts = work_metrics.counts(state, "work", KINDS)
    ordinary = choose_provider(state, at)
    result = {"baseline": ordinary, "candidate": actual, "work_starts": counts}
    if ordinary != actual or counts != observation.get("prior_starts"):
        return result | {"reason": "baseline mismatch"}
    runs = [r for r in state["life"]["runs"].values() if not staffing.helper(r)]
    active = Counter(r["agent"] for r in runs if r["status"] == "active")
    shares = provider_shares(state, at)
    available = [kind for kind in KINDS if provider_available(state, kind, at)]
    ranks = {k: (active[k] >= max(1, math.ceil(shares[k])), counts[k] / shares[k])
             for k in available if shares[k] > 0}
    tied = [k for k in ranks if ranks[k] == ranks[ordinary]]
    result.update(tied=tied, available=available, shares=shares,
                  active={k: active[k] for k in KINDS})
    if len(tied) == 1:
        return result | {"reason": "rotation has priority"}

    history = sorted((r for r in runs if work_metrics.lane(r, state["life"]["requests"]) == "work"),
                     key=lambda r: r["started_sequence"])[-work_metrics.WINDOW:]
    if len(history) < work_metrics.WINDOW:
        return result | {"reason": "incomplete work window"}
    # Compare both insertions after the oldest start falls out. Only the ordinary
    # winner loses one start relative to baseline; protect its integer share.
    floor = math.floor(len(history) * shares[ordinary] / sum(shares[k] for k in available))
    remaining = counts[ordinary] - (history[0]["agent"] == ordinary)
    result.update(ordinary_floor=floor, ordinary_starts_if_changed=remaining)
    if remaining < floor:
        return result | {"reason": "family floor"}
    candidate = evidence_choice(ordinary, tied, rows)
    return result | {"candidate": candidate, "reason": (
        "historical preference" if candidate != ordinary else "no supported preference")}


def assignment_receipts(events):
    receipts = {}
    for event in events:
        text = event["data"].get("text", "")
        if (event["actor"] != CONTROLLER or event["op"] != "say" or
                not text.startswith(work_metrics.ASSIGNMENT_PREFIX)):
            continue
        value = json.loads(text[len(work_metrics.ASSIGNMENT_PREFIX):])
        run = value["run"]
        if event["id"] == f"home-{run}-assignment":
            receipts[run] = (event["sequence"], value)
    return receipts


def state_before(status, budgets, seq):
    life = status["life"]
    # A help request's review_run association and the run's start/end sequences
    # are durable facts. No result, later claim, or current active flag is used.
    runs = {}
    for key, run in life["runs"].items():
        if run["started_sequence"] < seq:
            fields = ("agent", "model", "started_sequence", "mode", "help_request", "explore_generation")
            runs[key] = {k: run[k] for k in fields if k in run}
            runs[key]["status"] = "active" if run.get("ended_sequence", seq) >= seq else "completed"
    return {"life": {"runs": runs, "requests": life["requests"],
                     "budgets": budgets["budgets"], "model_budgets": budgets["model_budgets"]},
            "maintenance": {"migrations": {QUOTA_REST: {}}}}


def training_rows(report):
    rows = {}
    for row in report["rows"]:
        key = row["area"], row["family"]
        fields = ("eligible_claims", "eligible_finishes", "reviewed_runs", "first_pass", "no_review_receipt")
        if (key in rows or any(type(row[k]) is not int or row[k] < 0 for k in fields)
                or row["eligible_finishes"] > row["eligible_claims"] or row["first_pass"] > row["reviewed_runs"]):
            raise ValueError(f"invalid craft denominators for {key}")
        rows[key] = row
    return rows


def replay(status, budgets, fit, pages):
    events, interval = _extract_events_and_meta(pages)
    after = fit["through"]
    if (not events or interval["gaps"] or not events[0]["sequence"] <= after < events[-1]["sequence"]
            or status["sequence"] < events[-1]["sequence"]):
        raise ValueError("supply contiguous pages spanning the fit cutoff and a covering status")
    cooldowns = list(budgets["budgets"].values())
    for models in budgets["model_budgets"].values():
        cooldowns.extend(models.values())
    if any(b["sequence"] > after for b in cooldowns):
        raise ValueError("a cooldown postdates the fit cutoff; use the frozen cooldown snapshot")
    install = installed_picker(events, after)
    if not any(budgets["model_budgets"].values()):
        raise ValueError("a recorded model cooldown is needed to establish quota-share activation")
    training = training_rows(fit)
    observations = assignment_receipts(events)
    skipped, decisions, tasks = Counter(), [], {}
    work_starts, last_switch = 0, -work_metrics.WINDOW
    previous_time = None
    for e in events:
        data, op, seq = e["data"], e["op"], e["sequence"]
        task = data.get("task")
        if op == "task":
            tasks[task] = dict(data)
        elif op == "ready" and task in tasks:
            tasks[task].update(data)
            for key in ("project", "ballot_choice"):
                if data.get("clear_" + key):
                    tasks[task].pop(key, None)
        if seq <= after:
            previous_time = e["at"]
            continue
        if (op in ("owner-migrate", "owner-provider-release", "renovation-install") or
                (op == "life" and data["kind"] == "budget")):
            raise ValueError(f"policy or cooldown changed at {seq}; split the evaluation interval")
        if op != "life" or e["actor"] != CONTROLLER or data["kind"] != "run-start":
            previous_time = e["at"]
            continue
        archived = status["life"]["runs"].get(data["run"], {})
        if (archived.get("started_sequence") != seq
                or any(archived.get(k) != data.get(k) for k in ("agent", "model", "task", "help_request",
                                                                "explore_generation", "mode"))):
            raise ValueError(f"status and admission disagree at {seq}")
        at = e["at"]
        receipt, obs = observations.get(data["run"], (0, {}))
        tags = tasks.get(task, {})
        reason = None
        if staffing.helper(data):
            reason = "helper"
        elif "explore_generation" in data:
            reason = "Explorer"
        else:
            if work_metrics.lane(data, status["life"]["requests"]) == "work":
                work_starts += 1
            if "help_request" in data or data["mode"] != "work":
                reason = "help or review"
            elif not task:
                reason = "no task at admission"
            elif (not tags.get("project") or tags.get("ballot_choice") or tags.get("review_run")
                  or tags.get("helper") in ("build", "review")):
                reason = "missing or restricted task association"
            elif (receipt <= seq or obs.get("reason") != "balanced" or obs.get("lane") != "work"
                  or obs.get("helper") is not False or obs.get("window") != work_metrics.WINDOW
                  or obs.get("requested_agent") is not None or obs.get("help_request") is not None):
                reason = "missing or nonordinary assignment receipt"
            elif any(previous_time <= b["until"] <= at for b in cooldowns):
                reason = "cooldown expired at admission boundary"
            elif budgets["budgets"].get("opencode", {}).get("until", 0) > at:
                reason = "possible early OpenCode permit"
        if reason:
            skipped[reason] += 1
        else:
            area = "project/" + tags["project"]
            state = state_before(status, budgets, seq)
            rows = {k: training.get((area, k)) for k in KINDS}
            result = family_comparison(state, at, data["agent"], obs, rows)
            if result["candidate"] != data["agent"]:
                if work_starts - last_switch < work_metrics.WINDOW:
                    result.update(candidate=data["agent"], reason="one change per work window")
                else:
                    last_switch = work_starts
            decisions.append({"start": seq, "assignment": receipt, "task": task, "area": area,
                              "actual": data["agent"], **result})
        previous_time = at
    changed = sum(d["actual"] != d["candidate"] for d in decisions)
    return {"policy_install": install, "fit_through": after, "through": events[-1]["sequence"],
            "starts": sum(skipped.values())
            + len(decisions), "excluded": dict(sorted(skipped.items())), "decisions": decisions,
            "would_change": changed, "observed_alternate_outcomes": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status", required=True, help="fixed-channel status covering all evaluated starts")
    parser.add_argument("--fit", required=True, help="craft_outcomes --json for the frozen training interval")
    parser.add_argument("--cooldowns", help="frozen budgets and model_budgets from status")
    parser.add_argument("pages", nargs="+", help="saved journal pages, including earlier task declarations")
    args = parser.parse_args()
    try:
        status = json.loads(Path(args.status).read_text())
        budgets = (json.loads(Path(args.cooldowns).read_text()) if args.cooldowns else
                   {k: status["life"][k] for k in ("budgets", "model_budgets")})
        report = replay(status, budgets, json.loads(Path(args.fit).read_text()), load_inputs(args.pages))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(1, f"Cannot replay: {exc}\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
