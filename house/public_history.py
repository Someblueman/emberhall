"""Lossless public-history transport; shared containers form a backward-only DAG."""
from __future__ import annotations

import json


class Encoder:
    """Shared-container encoder whose node table can be kept and extended later."""

    def __init__(self, nodes: list | None = None, seen: dict | None = None):
        self.nodes = [] if nodes is None else nodes
        self.seen = {} if seen is None else seen
        self.added: list[str] | None = None

    def intern(self, node):
        key = json.dumps(node, sort_keys=True, separators=(",", ":"), allow_nan=False)
        index = self.seen.get(key)
        if index is None:
            index = self.seen[key] = len(self.nodes)
            self.nodes.append(node)
            if self.added is not None:
                self.added.append(key)
        return {"ref": index}

    def value(self, item):
        if isinstance(item, dict):
            return self.intern({key: self.value(child) for key, child in item.items()})
        if isinstance(item, list):
            return self.intern([self.value(child) for child in item])
        return item

    def temporary(self):
        """Encode a changing tail; forget() drops it again, keeping the stable prefix."""
        self.added, self.mark = [], len(self.nodes)

    def forget(self):
        for key in self.added or ():
            del self.seen[key]
        del self.nodes[self.mark:]
        self.added = None


def encode(projection: dict) -> dict:
    encoder = Encoder()
    root = encoder.value(projection)
    return {"version": 2, "root": root, "nodes": encoder.nodes}


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
