"""Lossless public-history transport; shared containers form a backward-only DAG."""
from __future__ import annotations

import hashlib
import json

# A list longer than this is stored as fixed-size chunks (version 4), so an appended list shares its old chunks.
CHUNK = 32


class Encoder:
    """Shared-container encoder whose node table can be kept and extended later."""

    def __init__(self, nodes: list | None = None, seen: dict | None = None, chunked: bool = False):
        self.nodes = [] if nodes is None else nodes
        self.seen = {} if seen is None else seen
        self.chunked = chunked
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
            return self.sequence([self.value(child) for child in item])
        return item

    def sequence(self, items: list):
        """Intern an encoded list. Past CHUNK items (chunked): CHUNK-sized list nodes joined by concat nodes."""
        if not self.chunked or len(items) <= CHUNK:
            return self.intern(items)
        level = [self.intern(items[start:start + CHUNK]) for start in range(0, len(items), CHUNK)]
        while len(level) > CHUNK:
            groups = [level[start:start + CHUNK] for start in range(0, len(level), CHUNK)]
            level = [group[0] if len(group) == 1 else self.concat(group) for group in groups]
        return self.concat(level)

    def appended(self, items: list):
        """Call after each append to a list later given to sequence(): a chunk that has just filled stays at once."""
        if self.chunked and len(items) % CHUNK == 0:
            self.intern(items[-CHUNK:])

    def concat(self, members: list):
        """A concat node is an array holding one inline array of node indexes; containers are never inline."""
        return self.intern([[member["ref"] for member in members]])

    def temporary(self):
        """Encode a changing tail; forget() drops it again, keeping the stable prefix."""
        self.added, self.mark = [], len(self.nodes)

    def forget(self):
        for key in self.added or ():
            del self.seen[key]
        del self.nodes[self.mark:]
        self.added = None


def encode(projection: dict, chunked: bool = False) -> dict:
    """Version 2; chunked lists need version 4, written here without parts."""
    encoder = Encoder(chunked=chunked)
    root = encoder.value(projection)
    if chunked:
        return {"version": 4, "parts": [], "root": root, "nodes": encoder.nodes}
    return {"version": 2, "root": root, "nodes": encoder.nodes}


def join_parts(wire: dict, parts) -> dict:
    """Version 3 as version 2 (4 as 4): the sealed parts' nodes, then the file's own, with global indexes."""
    listing = wire.get("parts")
    if not isinstance(listing, list) or not isinstance(wire.get("nodes"), list):
        raise ValueError("Unrecognized public history transport")
    load = parts if callable(parts) else (parts or {}).__getitem__
    nodes = []
    for entry in listing:
        try:
            data = load(entry["path"])
            if hashlib.sha256(data).hexdigest() != entry["sha256"]:
                raise ValueError("Public history part does not match its listing")
            chunk = json.loads(data)
            if not isinstance(chunk, list) or len(chunk) != entry["nodes"]:
                raise ValueError("Public history part has the wrong node count")
        except (KeyError, TypeError, OSError) as error:
            raise ValueError("Public history part is missing or malformed") from error
        nodes += chunk
    return {"version": 4 if wire["version"] == 4 else 2, "root": wire.get("root"), "nodes": nodes + wire["nodes"]}


def decode(wire: dict, parts=None) -> dict:
    """Decode a snapshot. Versions 3 and 4 need `parts`: a path -> bytes mapping or a callable returning bytes."""
    # Version 1 is the already published format, retained for old snapshots.
    if wire.get("version") == 1:
        return wire
    if wire.get("version") in (3, 4):
        wire = join_parts(wire, parts)
    if wire.get("version") not in (2, 4) or not isinstance(wire.get("nodes"), list):
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
        if isinstance(node, list) and len(node) == 1 and isinstance(node[0], list):
            # Concat (version 4 only): the earlier list nodes it names, joined into one flat list.
            if wire["version"] != 4 or not node[0] or any(
                    type(ref) is not int or not 0 <= ref < len(nodes) or not isinstance(nodes[ref], list)
                    for ref in node[0]):
                raise ValueError("Invalid public history concatenation")
            nodes.append([item for ref in node[0] for item in nodes[ref]])
        elif isinstance(node, dict):
            nodes.append({key: value(child) for key, child in node.items()})
        elif isinstance(node, list):
            nodes.append([value(child) for child in node])
        else:
            raise ValueError("Invalid public history node")
    root = value(wire.get("root"))
    if not isinstance(root, dict) or root.get("version") != 1:
        raise ValueError("Invalid public history root")
    return root
