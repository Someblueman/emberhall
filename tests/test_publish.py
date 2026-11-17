"""Public snapshots use an independent index and preserve the source checkout."""
import hashlib
import json
from unittest.mock import patch

from house import publish as publisher
from house.body import export
from house.home_work import git
from house.publish import BRANCH, publish
from house.public_history import decode, encode
from tests.support import HouseCase


class PublishTests(HouseCase):
    def test_publication_preserves_dirty_source_and_does_not_repeat_unchanged_views(self):
        (self.repo / "site").mkdir()
        for name in ("index.html", "house.js", "house.css"):
            (self.repo / "site" / name).write_text("committed " + name)
        git(self.repo, "add", ".")
        git(self.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test", "-c", "user.email=test@local",
            "commit", "-m", "Public fixture")
        (self.repo / "site/index.html").write_text("unfinished private edit")
        git(self.repo, "add", "site/index.html")
        before_index = (self.record.gitdir / "index").read_bytes()
        before_source = git(self.repo, "rev-parse", "HEAD")
        first = publish(self.record)
        second = publish(self.record)
        self.assertTrue(first["changed"])
        self.assertFalse(second["changed"])
        self.assertEqual(before_index, (self.record.gitdir / "index").read_bytes())
        self.assertEqual(before_source, git(self.repo, "rev-parse", "HEAD"))
        self.assertEqual(git(self.repo, "show", BRANCH + ":index.html"), "committed index.html")
        public = decode(json.loads(git(self.repo, "show", BRANCH + ":history.json")))
        self.assertEqual(public["journal_head"], self.record.read()[2])

    def test_rejected_local_chain_is_preserved_and_remote_history_fast_forwards(self):
        from unittest.mock import patch
        import subprocess
        from house.public_history import decode

        (self.repo / 'site').mkdir()
        for name in ('index.html', 'house.js', 'house.css'):
            (self.repo / 'site' / name).write_text('public ' + name)
        git(self.repo, 'add', '.')
        git(self.repo, '-c', 'commit.gpgsign=false', '-c', 'user.name=Test',
            '-c', 'user.email=test@local', 'commit', '-m', 'Fixture')
        remote = self.repo.parent / (self.repo.name + '-pages-remote')
        subprocess.run(['git', 'init', '--bare', str(remote)], capture_output=True, check=True)
        git(self.repo, 'remote', 'add', 'origin', str(remote))
        first = publish(self.record, push=True)['commit']
        ref = 'refs/heads/' + BRANCH
        # Existing v1 snapshot and oversized ancestor, followed by a small tip.
        # Recovery must inspect all unpublished blobs, not only the latest tree.
        projection = decode(json.loads(git(self.repo, 'show', ref + ':history.json')))
        blob = self.record.git('hash-object', '-w', '--stdin', data=json.dumps(projection).encode()).decode().strip()
        huge = self.record.git('hash-object', '-w', '--stdin', data=b'x' * 120000).decode().strip()
        tree = self.record.git('mktree', data=f'100644 blob {blob}\thistory.json\n100644 blob {huge}\toversized\n'.encode()).decode().strip()
        bad = self.record.git('commit-tree', tree, '-p', first, data=b'rejected snapshot').decode().strip()
        small_tree = self.record.git('mktree', data=f'100644 blob {blob}\thistory.json\n'.encode()).decode().strip()
        tip = self.record.git('commit-tree', small_tree, '-p', bad, data=b'later unpublished snapshot').decode().strip()
        self.record.git('update-ref', ref, tip, first)
        before_index = (self.record.gitdir / 'index').read_bytes()
        before_source = git(self.repo, 'rev-parse', 'HEAD')
        before_ledger = self.record.read()[2]
        with patch('house.publish.MAX_PUBLIC_BLOB', 100000):
            fixed = publish(self.record, push=True)
        self.assertEqual(git(self.repo, 'rev-parse', fixed['commit'] + '^'), first)
        self.assertEqual(git(self.repo, 'rev-parse', 'refs/house-publication-recovery/' + tip), tip)
        self.assertEqual(git(remote, 'rev-parse', ref), fixed['commit'])
        self.assertEqual(decode(json.loads(git(self.repo, 'show', ref + ':history.json')))['frames'], projection['frames'])
        self.assertEqual(before_index, (self.record.gitdir / 'index').read_bytes())
        self.assertEqual(before_source, git(self.repo, 'rev-parse', 'HEAD'))
        self.assertEqual(before_ledger, self.record.read()[2])
        self.assertFalse(publish(self.record, push=True)['changed'])
        # A rejected upload preserves the candidate and retries that exact commit.
        self.record.append('say', 'alice', {'text': 'A later public event'})
        hook = remote / 'hooks/pre-receive'
        hook.write_text('#!/bin/sh\nexit 1\n')
        hook.chmod(0o700)
        with self.assertRaises(subprocess.CalledProcessError):
            publish(self.record, push=True)
        retry_head = git(self.repo, 'rev-parse', ref)
        self.assertNotEqual(retry_head, fixed['commit'])
        self.assertEqual(git(remote, 'rev-parse', ref), fixed['commit'])
        hook.unlink()
        fixed = publish(self.record, push=True)
        self.assertFalse(fixed['changed'])
        self.assertEqual(fixed['commit'], retry_head)
        self.assertEqual(git(remote, 'rev-parse', ref), retry_head)
        # Oversized output fails before any publication ref can change.
        with patch('house.publish.MAX_PUBLIC_BLOB', 1), self.assertRaises(ValueError):
            publish(self.record, push=True)
        self.assertEqual(git(self.repo, 'rev-parse', ref), fixed['commit'])
        # Divergence is refused; no remote overwrite or automatic reconciliation.
        other = self.record.git('commit-tree', small_tree, data=b'unrelated').decode().strip()
        self.record.git('update-ref', ref, other, fixed['commit'])
        with self.assertRaises(ValueError):
            publish(self.record, push=True)
        self.assertEqual(git(remote, 'rev-parse', ref), fixed['commit'])


class PublishInPartsTests(HouseCase):
    def setUp(self):
        super().setUp()
        (self.repo / "site").mkdir()
        for name in ("index.html", "house.js", "house.css"):
            (self.repo / "site" / name).write_text("committed " + name)
        git(self.repo, "add", ".")
        git(self.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test", "-c", "user.email=test@local",
            "commit", "-m", "Public fixture")
        self.private = self.record.common / "house-home"

    def tree(self):
        return {path: blob for _, _, blob, path in (line.replace("\t", " ").split(" ", 3)
                for line in git(self.repo, "ls-tree", "-r", BRANCH).splitlines())}

    def shown(self, path):
        return self.record.git("show", BRANCH + ":" + path)

    def speak(self, count, start=0):
        for number in range(start, start + count):
            self.record.append("say", "alice", {"text": f"A distinct public remark number {number}"})

    def test_parts_are_sealed_stable_and_decode_to_the_full_projection(self):
        self.speak(12)
        with patch("house.publish.PART_TARGET", 800), patch("house.public_history.CHUNK", 4):
            self.assertTrue(publish(self.record)["changed"])
            first_tree, wire = self.tree(), json.loads(self.shown("history.json"))
            self.assertEqual(wire["version"], 4)
            self.assertEqual(json.loads(self.shown("head.json"))["history_version"], 4)
            everything = wire["nodes"] + [node for part in wire["parts"] for node in json.loads(self.shown(part["path"]))]
            self.assertTrue(any(len(node) == 1 and isinstance(node[0], list) for node in everything if isinstance(node, list)))
            self.assertGreaterEqual(len(wire["parts"]), 3)
            self.assertEqual(sorted(path for path in first_tree if path.startswith("history/")),
                             sorted(part["path"] for part in wire["parts"]))
            for number, part in enumerate(wire["parts"]):
                data = self.shown(part["path"])
                self.assertEqual(part["sha256"], hashlib.sha256(data).hexdigest())
                self.assertEqual(part["path"], f"history/part-{number:04d}-{part['sha256'][:16]}.json")
                self.assertEqual(part["nodes"], len(json.loads(data)))
                self.assertGreaterEqual(len(data), 800)
                self.assertEqual(data, json.dumps(json.loads(data), separators=(",", ":")).encode())
            head = json.loads(self.shown("head.json"))
            public = decode(wire, lambda path: self.shown(path))
            self.assertEqual(public, export(self.record, public["observed_at"]))
            self.assertEqual(head["journal_head"], public["journal_head"])
            # A later publication keeps every earlier part, byte for byte, and only appends.
            self.speak(12, 12)
            self.assertTrue(publish(self.record)["changed"])
            second_tree, later = self.tree(), json.loads(self.shown("history.json"))
            self.assertGreater(len(later["parts"]), len(wire["parts"]))
            self.assertEqual(later["parts"][:len(wire["parts"])], wire["parts"])
            for part in wire["parts"]:
                self.assertEqual(second_tree[part["path"]], first_tree[part["path"]])
            self.assertEqual(decode(later, lambda path: self.shown(path)),
                             export(self.record, decode(later, lambda path: self.shown(path))["observed_at"]))
            # Lost private part files are rebuilt from the cache with the same bytes.
            for file in (self.private / publisher.PARTS_DIR).iterdir():
                file.unlink()
            self.speak(1, 24)
            publish(self.record)
            for part in later["parts"]:
                self.assertEqual(self.tree()[part["path"]], second_tree[part["path"]])
            files = list((self.private / publisher.PARTS_DIR).iterdir())
            self.assertEqual(len(files), len(json.loads(self.shown("history.json"))["parts"]))
            self.assertTrue(all(file.stat().st_mode & 0o777 == 0o600 for file in files))
            # An unchanged record is not published again.
            self.assertFalse(publish(self.record)["changed"])

    def test_a_cache_without_parts_gets_boundaries_once_and_an_oversized_part_is_refused(self):
        import marshal
        self.speak(12)
        with patch("house.publish.PART_TARGET", 800):
            publish(self.record)
            cache_path = self.private / publisher.HISTORY_CACHE
            cache = marshal.loads(cache_path.read_bytes())
            names = [part["path"] for part in cache["parts"]]
            del cache["parts"]
            cache_path.write_bytes(marshal.dumps(cache))
            with patch("house.publish.replay_context", side_effect=AssertionError("full replay")):
                publisher.history(self.record, self.private)
            self.assertEqual([part["path"] for part in marshal.loads(cache_path.read_bytes())["parts"]], names)
            self.speak(1, 99)
            with patch("house.publish.MAX_PUBLIC_BLOB", 700), self.assertRaises(ValueError):
                publish(self.record)

    def test_a_previous_version_two_or_three_publication_is_replaced_and_decodes_without_parts(self):
        self.speak(3)
        publish(self.record)
        public = decode(json.loads(self.shown("history.json")), lambda path: self.shown(path))
        head = json.loads(self.shown("head.json"))
        entries = {name: self.shown(name) for name in self.tree() if "/" not in name}
        ref = "refs/heads/" + BRANCH
        for version, with_head in ((2, True), (2, False), (3, True), (3, False)):
            old = encode(public) | ({"version": 3, "parts": []} if version == 3 else {})
            entries["history.json"] = json.dumps(old, separators=(",", ":")).encode()
            entries["head.json"] = json.dumps({**head, "history_version": version} if version == 3 else
                                              {key: head[key] for key in head if key != "history_version"}).encode()
            if not with_head:
                del entries["head.json"]
            listing = "".join("100644 blob " + self.record.git("hash-object", "-w", "--stdin", data=body).decode().strip()
                              + "\t" + name + "\n" for name, body in entries.items())
            tree = self.record.git("mktree", data=listing.encode()).decode().strip()
            old = self.record.git("commit-tree", tree, data=b"version two").decode().strip()
            self.record.git("update-ref", ref, old)
            self.assertEqual(decode(json.loads(self.shown("history.json"))), public)
            result = publish(self.record)
            self.assertTrue(result["changed"])
            self.assertEqual(json.loads(self.shown("history.json"))["version"], 4)
            again = decode(json.loads(self.shown("history.json")), lambda path: self.shown(path))
            self.assertEqual(again["frames"], public["frames"])
            self.assertFalse(publish(self.record)["changed"])
