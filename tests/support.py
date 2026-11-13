"""Disposable real Git repositories for the house boundary tests."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from house.record import Record

SOURCE = Path(__file__).resolve().parents[1]


class HouseCase(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="house-test-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.repo = self.new_repo("house")
        self.record = Record(self.repo)
        self.foundation = self.record.found("Test house", "Initial rules")
        self.record.append("arrive", "alice", {"name": "Alice"})
        self.record.append("arrive", "bob", {"name": "Bob"})

    def new_repo(self, name):
        path = self.root / name
        path.mkdir()
        subprocess.run(["git", "init", "-q", str(path)], check=True, capture_output=True)
        return path

    def process(self, *args, repo=None):
        return subprocess.Popen(
            [sys.executable, "-m", "house", "--repo", str(repo or self.repo), *args],
            cwd=SOURCE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )

    def cli(self, *args, repo=None, success=True):
        process = self.process(*args, repo=repo)
        out, err = process.communicate(timeout=20)
        self.assertEqual(process.returncode, 0 if success else 2, (out, err))
        return json.loads(out) if success else err

    def script(self, source):
        return subprocess.Popen(
            [sys.executable, "-u", "-c", source, str(self.repo)], cwd=SOURCE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            env=dict(os.environ, PYTHONPATH=str(SOURCE)),
        )

    def task(self):
        self.record.append("task", "alice", {
            "task": "work", "title": "Work", "description": "A bounded test"})

    def rejected(self, op, actor, data, message):
        head = self.record.read()[2]
        with self.assertRaisesRegex(ValueError, message):
            self.record.append(op, actor, data)
        self.assertEqual(self.record.read()[2], head)
