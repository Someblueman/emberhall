"""The publisher replays only new events, yet publishes exactly the full history."""
import json
import marshal
from unittest.mock import patch

from house import publish
from house.body import export
from house.public_history import decode
from tests.support import HouseCase


class HistoryCacheTests(HouseCase):
    def setUp(self):
        super().setUp()
        self.private = self.record.common / "house-home"
        self.private.mkdir(exist_ok=True)

    def history(self, at=1e10):
        body, summary, parts = publish.history(self.record, self.private, observed_at=at)
        return decode(json.loads(body), parts), summary

    def grow(self):
        if "garden" not in self.record.read()[0].get("life", {}).get("rooms", {}):
            self.record.append("life", "alice", {"kind": "room", "room": "garden", "name": "Glass garden"})
        else:
            self.record.append("say", "alice", {"text": "In the garden"})
        self.record.append("say", "alice", {"text": "I am by the hearth"})

    def test_resumed_history_equals_a_full_rebuild(self):
        first, summary = self.history()
        self.assertEqual(first, export(self.record, 1e10))
        self.grow()
        with patch("house.publish.replay", wraps=publish.replay) as replay:
            resumed, later = self.history()
        context = replay.call_args.args[1]
        self.assertEqual(summary["seq"], len(first["frames"]))
        self.assertEqual(later["seq"], summary["seq"] + 2)
        self.assertEqual(resumed, export(self.record, 1e10))
        self.assertEqual(later["seq"], context["replayed"])

    def test_changed_code_or_rewritten_journal_rebuilds_from_the_start(self):
        self.history()
        path = self.private / publish.HISTORY_CACHE
        for change in ({"code": "0" * 64}, {"head": "0" * 40}, {"format": 0}):
            cache = marshal.loads(path.read_bytes())
            cache.update(change)
            path.write_bytes(marshal.dumps(cache))
            self.grow()
            with patch("house.publish.replay_context", wraps=publish.replay_context) as fresh:
                rebuilt, _ = self.history()
            fresh.assert_called_once()
            self.assertEqual(rebuilt, export(self.record, 1e10))
        path.write_bytes(b"not marshal")
        self.assertEqual(self.history()[0], export(self.record, 1e10))

    def test_chunked_history_resumes_to_the_bytes_of_a_full_rebuild_and_old_caches_are_dropped(self):
        with patch("house.public_history.CHUNK", 4):
            for _ in range(3):
                self.grow()
            first, _, _ = publish.history(self.record, self.private, observed_at=1e10)
            self.assertEqual(json.loads(first)["version"], 4)
            self.assertTrue(any(len(node) == 1 and isinstance(node[0], list)
                                for node in json.loads(first)["nodes"] if isinstance(node, list)))
            for _ in range(3):
                self.grow()
            resumed, summary, parts = publish.history(self.record, self.private, observed_at=1e10)
            self.assertEqual(summary["history_version"], 4)
            self.assertEqual(decode(json.loads(resumed), parts), export(self.record, 1e10))
            (self.private / publish.HISTORY_CACHE).unlink()
            self.assertEqual(publish.history(self.record, self.private, observed_at=1e10)[0], resumed)
            # A cache written before chunking (format 1) holds unchunked nodes and is rebuilt.
            path = self.private / publish.HISTORY_CACHE
            cache = marshal.loads(path.read_bytes())
            path.write_bytes(marshal.dumps({**cache, "format": 1}))
            with patch("house.publish.replay_context", wraps=publish.replay_context) as fresh:
                self.assertEqual(publish.history(self.record, self.private, observed_at=1e10)[0], resumed)
            fresh.assert_called_once()
