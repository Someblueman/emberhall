"""Check the effects of one proposed substitution on recorded rolling work turns."""

import argparse
from collections import Counter
import json
from pathlib import Path

from cohort import CONTROLLER, FAMILIES, read_pages
from tie_replay import replay
from trial import REVIEWED, baseline_anchor, baseline_option
from house.craft_replay import assignment_receipts
from house.staffing import helper
from house.work_metrics import WINDOW, lane


def work_history(status, events, through):
    """Recover the work lane, including starts which later exhausted quota."""
    life = status["life"]
    requests = life["requests"]
    starts = {event["data"]["run"]: event for event in events
              if event["actor"] == CONTROLLER and event["op"] == "life"
              and event["data"]["kind"] == "run-start" and event["sequence"] <= through}
    turns = []
    first = events[0]["sequence"]
    for run_id, run in life["runs"].items():
        seq = run["started_sequence"]
        if seq > through:
            continue
        if seq >= first:
            event = starts.pop(run_id, None)
            if event is None or event["sequence"] != seq or any(
                    event["data"].get(key) != run.get(key)
                    for key in ("agent", "model", "mode", "help_request", "explore_generation")):
                raise ValueError(f"status and run start disagree at {seq}")
        if run.get("help_request") and run["help_request"] not in requests:
            raise ValueError(f"missing lane information for admission {seq}")
        if not helper(run) and lane(run, requests) == "work":
            if run["agent"] not in FAMILIES:
                raise ValueError(f"unknown family at {seq}")
            turns.append((seq, run_id, run["agent"]))
    if starts:
        raise ValueError(f"status lacks admission {min(e['sequence'] for e in starts.values())}")
    return sorted(turns)


def checked_windows(turns, receipts, first):
    """Only the controller's matching 32-start receipt corroborates a time window."""
    checked = {}
    for index, (seq, run, _) in enumerate(turns):
        if seq < first or run not in receipts:
            continue
        receipt, observation = receipts[run]
        if receipt <= seq or observation.get("lane") != "work" or observation.get("helper") is not False:
            raise ValueError(f"work admission and receipt disagree at {receipt}")
        counts = observation.get("prior_starts")
        if observation.get("window") != WINDOW or counts is None:
            continue
        history = Counter(item[2] for item in turns[max(0, index - WINDOW):index])
        if (not isinstance(counts, dict) or set(counts) != set(FAMILIES)
                or any(type(counts[k]) is not int or counts[k] != history[k] for k in FAMILIES)):
            raise ValueError(f"prior work starts disagree at receipt {receipt}")
        checked[seq] = receipt
    return checked


def compare(turns, index, decision, checked, stop):
    offer, _, family = turns[index]
    preferred = decision["evidence_preference"]
    result = {"offer": offer, "task": decision["task"], "ordinary": family,
              "preference": preferred, "windows_checked": 0, "first_loss": None}
    if family != decision["baseline"] or preferred not in decision["tied_families"]:
        raise ValueError(f"decision and recorded family choices disagree at {offer}")
    if family == preferred:
        return result | {"state": "ordinary choice retained"}
    for end in range(index, min(index + WINDOW, len(turns))):
        seq = turns[end][0]
        if seq not in checked:
            return result | {"state": "missing window receipt", "missing_at": seq}
        window = turns[max(0, end - WINDOW + 1):end + 1]
        result["windows_checked"] += 1
        if sum(turn[2] == family for turn in window) == 1:
            result["first_loss"] = {"window_from": window[0][0], "window_through": seq,
                                    "receipt": checked[seq], "family": family,
                                    "ordinary_turns": 1, "substituted_turns": 0}
            return result | {"state": "family loses its last turn"}
    if result["windows_checked"] == WINDOW:
        return result | {"state": "no last turn lost in all affected windows"}
    return result | {"state": "follow-up stopped at policy change" if stop else "partial follow-up"}


def report(status, events, through, baseline=REVIEWED):
    ties = replay(status, events, through, baseline)
    installed = ties["installed_at"]
    stop = ties["policy_stop"]
    horizon = stop - 1 if stop is not None else through
    turns = work_history(status, events, horizon)
    indices = {seq: index for index, (seq, _, _) in enumerate(turns)}
    receipts = assignment_receipts([e for e in events if e["sequence"] <= horizon])
    checked = checked_windows(turns, receipts, events[0]["sequence"])
    rows = []
    for decision in ties["decisions"]:
        offer = decision["offer"]
        if offer not in indices:
            raise ValueError(f"enrolled offer {offer} missing from work lane")
        rows.append(compare(turns, indices[offer], decision, checked, stop))
    return {"baseline": baseline, "through": through, "trial_state": ties["trial_state"], "installed_at": installed,
            "policy_stop": stop, "verified_work_receipts": list(checked.values()),
            "unverified_work_starts": [seq for seq, _, _ in turns
                                       if seq >= events[0]["sequence"] and seq not in checked],
            "decisions": rows, "routing_weight": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    baseline_option(parser)
    parser.add_argument("--status", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("pages", nargs="+", type=Path)
    args = parser.parse_args()
    try:
        events, through = read_pages(args.pages, baseline_anchor(args.baseline))
        result = report(json.loads(args.status.read_text()), events, through, args.baseline)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(2, f"Cannot check work turns: {exc}\n")
    if args.json:
        print(json.dumps(result, indent=2))
        return
    print(f"Through {through} | {result['baseline']} | {result['trial_state']} | routing weight 0")
    print(f"{len(result['verified_work_receipts'])} work receipts matched their prior turns | "
          f"{len(result['unverified_work_starts'])} starts without a comparable receipt")
    print(f"{len(result['decisions'])} enrolled offers")
    for row in result["decisions"]:
        print(f"{row['offer']} {row['task']} | {row['ordinary']} to {row['preference']} | "
              f"{row['state']} | {row['windows_checked']} windows checked")
        if row["first_loss"]:
            loss = row["first_loss"]
            print(f"  {loss['family']} falls from one turn to zero in the window ending at "
                  f"{loss['window_through']} (receipt {loss['receipt']})")


if __name__ == "__main__":
    main()
