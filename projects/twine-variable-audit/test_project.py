"""Run the actual JavaScript behavior checks in the house project gate."""
import pathlib
import shutil
import subprocess
import unittest


class ProjectChecks(unittest.TestCase):
    def test_javascript_behavior(self):
        node = shutil.which("node")
        self.assertIsNotNone(node, "Node is required to verify the shipped checker")
        project = pathlib.Path(__file__).resolve().parent
        result = subprocess.run(
            [node, "--test", *map(str, sorted(project.glob("test_*.js")))],
            cwd=project,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
