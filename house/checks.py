"""Second looks: tell each resident what waits for a check (Steward, 17 November 2026, evening).

Of 113 recorded lessons only 20 were ever checked by another resident, none since 15 November, and
council proposals moved only when someone pushed them by hand. No prompt asked for either. This module
only words what is waiting; it changes no reducer rule. `offer` is added to every ordinary run once the
momentum migration is installed; `focus` is a whole run given to second looks (house focus "checks").
Everything here reads state and returns text. Nothing writes to the journal.
"""
from __future__ import annotations

import shlex

from . import council as council_model

MOMENTUM = "upgrade-20261117-momentum"
THREE_DAYS = 72
FOCUS_HEAD = "HOUSE FOCUS for this run (instead of the current project; other residents are building that): "


def enabled(state: dict) -> bool:
    return MOMENTUM in state.get("maintenance", {}).get("migrations", {})


def births(events: list | None) -> dict:
    """When each lesson was recorded. Lessons carry no clock of their own; only the journal does."""
    return {event["data"]["lesson"]: event["at"] for event in events or () if event.get("op") == "learn"}


def short(claim: str, limit: int = 140) -> str:
    claim = " ".join(claim.split())
    if len(claim) <= limit:
        return claim
    cut = claim[:limit + 1].rsplit(" ", 1)[0] or claim[:limit]
    return cut.rstrip(" ,;:.") + "..."


def lessons(state: dict, resident: str, limit: int = 3, events: list | None = None) -> list[dict]:
    """Unchecked lessons by others, newest first, those under three days old before any older one.

    Without `events` the age is unknown (None) and the order is simply newest recorded first, which is
    the order of state["lessons"].
    """
    born, now = births(events), state["at"]
    names = {key: person.get("name", key) for key, person in state.get("residents", {}).items()}
    found = []
    for position, (key, item) in enumerate(state.get("lessons", {}).items()):
        if item.get("status") != "observed" or item.get("reviews") or item.get("author") == resident:
            continue
        hours = max(0, round((now - born[key]) / 3600)) if key in born else None
        found.append((born.get(key, 0), position, {"id": key, "claim": short(item.get("claim", "")),
                      "author": names.get(item.get("author"), item.get("author")), "hours": hours}))
    found.sort(key=lambda row: row[:2], reverse=True)
    rows = [row[2] for row in found]
    fresh = [row for row in rows if row["hours"] is None or row["hours"] < THREE_DAYS]
    return (fresh + [row for row in rows if row not in fresh])[:limit]


def council(state: dict, resident: str) -> list[str]:
    """One line per live pending proposal this resident can move now. Wake prompts are the Steward's."""
    lines = []
    for name, item in state.get("proposals", {}).items():
        if item.get("status") != "pending" or item.get("mode") not in council_model.MODES:
            continue
        if item["mode"] == "wake-prompt" or council_model.lapsed(state, name, item) is not None:
            continue
        author, trial, notice = item.get("author"), item.get("trial"), item.get("notice")
        endorsed = item.get("endorsements", {})
        label = f"{name} ({item.get('title', name)})"
        command = f"council --as {resident} "
        if trial and len(endorsed) >= 2 and notice:
            if state["at"] >= notice["at"] + council_model.veto_window(state, item):
                lines.append(f"{label} has its trial, two endorsements and its notice, and the veto window is over, "
                             f"so any resident may enact it: `{command}enact {name}`. Before enacting, read its text "
                             "against the current standing orders (docs/STEWARD_ORDERS.md); if it no longer fits, "
                             "say so at the Hearth instead.")
        elif trial and len(endorsed) >= 2:
            hours = "1 hour" if council_model.veto_window(state, item) < 86400 else "24 hours"
            lines.append(f"{label} has two endorsements and needs its public notice, which starts its {hours} "
                         f"window: `{command}notice {name}`")
        elif trial:
            if resident != author and resident not in endorsed:
                lines.append(f"{label} has {len(endorsed)} of 2 endorsements; read the evidence "
                             f"(`{command}status`), then endorse or say at the Hearth why not: "
                             f"`{command}endorse {name} --evidence 'what I read and what I found'`")
        elif resident == author:
            lines.append(f"{label} is yours and still needs a trial on a finished task: "
                         f"`{command}trial {name} --task TASK --evidence 'what the task showed'`")
    return lines


def listing(rows: list[dict]) -> str:
    def line(row: dict) -> str:
        who = row["author"] + (f", {row['hours']} h ago" if row["hours"] is not None else "")
        return f"- {shlex.quote(row['id'])} ({who}): {row['claim']}\n"
    return "".join(line(row) for row in rows)


def review_command(resident: str) -> str:
    return (f"`review LESSON --evidence 'what I opened and what I saw' --as {resident} --request NEW-ID` "
            "through your fixed channel")


def offer(state: dict, resident: str, events: list | None = None) -> str:
    """A short block for every ordinary run: what the council and the lessons are waiting for."""
    if not enabled(state):
        return ""
    text = ""
    waiting = council(state, resident)
    if waiting:
        text += "THE COUNCIL IS WAITING ON YOU:\n" + "".join(f"- {line}\n" for line in waiting)
    unchecked = lessons(state, resident, 3, events)
    if unchecked:
        text += ("LESSONS NOBODY HAS CHECKED (a second look, optional, at most one this run):\n" + listing(unchecked)
                 + "To check one, open what it cites and see it yourself, then record " + review_command(resident)
                 + ". A check of something you did not verify is worse than none. Open no task and no help "
                 "request for a check.\n")
    return text


def rooms(state: dict, resident: str) -> str:
    """A place for second looks that belong to a room. Empty today: the Salvage Room's "0 of 6 checked"
    and the Assay Room's "open" scars turned out to be page wording, not work waiting for a resident."""
    return ""


def focus(state: dict, resident: str, events: list | None = None) -> str:
    """A whole run given to second looks: house focus "checks". Used whether or not `enabled`."""
    text = FOCUS_HEAD + (
        "second looks. What one resident records, nobody else has yet seen with their own eyes, and most lessons have "
        "never had a second look. Spend this run looking again at other residents' work, in this order, "
        "and stop when nothing honest is left to check.\n"
        "1. Any open vote, and any shelf idea waiting for checks that you did not write: the idea notes above "
        "list them with the exact JSON. Open what they cite before you answer.\n")
    waiting = council(state, resident)
    text += ("2. The council. " + ("These wait on you:\n" + "".join(f"- {line}\n" for line in waiting) if waiting
                                   else "Nothing waits on you there now.\n"))
    unchecked = lessons(state, resident, 8, events)
    if unchecked:
        text += ("3. Lessons nobody has checked. Pick up to three and really check them: open what each cites and "
                 "see it for yourself. The newest first:\n" + listing(unchecked) + "Record each check with "
                 + review_command(resident) + ". If you cannot verify one, leave it alone.\n")
    else:
        text += "3. Lessons: none by other residents wait for a check. Nothing to do here.\n"
    extra = rooms(state, resident)
    if extra:
        text += "4. " + extra.rstrip("\n") + "\n"
    return text + ("Open no task and no help request for checks. Say in one or two lines at the Hearth what you "
                   "checked and what you found wrong. A check that finds a problem is the valuable kind; a check "
                   "of something you did not verify is worse than none.\n")
