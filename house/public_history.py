"""Lossless public-history transport; shared containers form a backward-only DAG."""
from __future__ import annotations

import json


def encode(projection: dict) -> dict:
    nodes: list[dict | list] = []
    seen: dict[str, int] = {}

    def value(item):
        if isinstance(item, dict):
            node = {key: value(child) for key, child in item.items()}
        elif isinstance(item, list):
            node = [value(child) for child in item]
        else:
            return item
        key = json.dumps(node, sort_keys=True, separators=(",", ":"), allow_nan=False)
        if key not in seen:
            seen[key] = len(nodes)
            nodes.append(node)
        return {"ref": seen[key]}

    root = value(projection)
    return {"version": 2, "root": root, "nodes": nodes}


def decode(wire: dict) -> dict:
    # Version 1 is the already published format, retained for old snapshots.
    if wire.get("version") == 1:
        return wire
    if wire.get("version") != 2 or not isinstance(wire.get("nodes"), list):
        raise ValueError("Unrecognized public history transport")
    nodes = []

    def value(item):
        if isinstance(item, dict):
            ref = item.get("ref")
            if set(item) != {"ref"} or type(ref) is not int or not 0 <= ref < len(nodes):
                raise ValueError("Invalid public history reference")
            return nodes[ref]
        if isinstance(item, list):
            raise ValueError("Inline public history container")
        return item

    for node in wire["nodes"]:
        if isinstance(node, dict):
            nodes.append({key: value(child) for key, child in node.items()})
        elif isinstance(node, list):
            nodes.append([value(child) for child in node])
        else:
            raise ValueError("Invalid public history node")
    root = value(wire.get("root"))
    if not isinstance(root, dict) or root.get("version") != 1:
        raise ValueError("Invalid public history root")
    return root
