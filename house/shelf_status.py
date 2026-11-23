"""A read-only paged reader for the idea shelf and graveyard, without brief bodies."""
from __future__ import annotations

STANDINGS = ("shelved", "graveyard", "project")


def _entry(idea: dict, scale_of) -> dict:
    entry = {"title": idea.get("title"), "author": idea.get("author"),
             "standing": idea.get("status"), "scale": scale_of(idea)}
    for key in ("plain", "shelved_sequence", "losses"):
        if key in idea:
            entry[key] = idea[key]
    brief = idea.get("brief")
    entry["brief_revision"] = brief.get("sequence") if isinstance(brief, dict) else None
    return entry


def shelf_page(state: dict, head: str, *, limit: int = 10, after: str | None = None,
               scale: str | None = None, standing: str | None = None) -> dict:
    if not 1 <= limit <= 50:
        raise ValueError("shelf page limit must be 1..50")
    from . import shelf as shelf_model
    if scale is not None and scale not in shelf_model.scales(state):
        raise ValueError(f"unknown scale: {scale}")
    if standing is not None and standing not in STANDINGS:
        raise ValueError(f"standing must be one of {', '.join(STANDINGS)}")
    ideas = state.get("shelf", {}).get("ideas", {})
    names = sorted(key for key, idea in ideas.items()
                   if (standing is None or idea.get("status") == standing)
                   and (scale is None or shelf_model.scale(idea) == scale))
    remaining = [key for key in names if after is None or key > after]
    shown = remaining[:limit]
    more = len(remaining) > len(shown)
    return {
        "house_id": state["house_id"],
        "name": state["name"],
        "source": {"journal_head": head, "sequence": state["sequence"]},
        "scope": "Ideas on the shelf and in the graveyard, sorted by idea ID; "
                 "compact entries without brief bodies.",
        "ideas": {key: _entry(ideas[key], shelf_model.scale) for key in shown},
        "page": {"after": after, "limit": limit, "shown": len(shown),
                 "has_more": more, "next_after": shown[-1] if more and shown else None},
        "counts": {
            "matching": len(names),
            "by_standing": {which: sum(idea.get("status") == which
                                        for idea in ideas.values())
                            for which in STANDINGS},
        },
        "limitations": [
            "Read-only projection: does not acknowledge events or change any record.",
            "If journal_head changes between pages, restart without --after; "
            "the cursor is an idea ID in this reply, not a saved position.",
            "Brief bodies and check findings are omitted; read one complete idea "
            "with status --idea ID --as YOUR-ID.",
        ],
    }
