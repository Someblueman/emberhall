"""Packaging contract: the project installs and imports for real.

The demos reach the package through ``sys.path``; a user outside this
tree needs ``pip install`` to work.  These tests check the PEP 621
metadata and do one real install into a temporary target, then import
from a neutral working directory in a subprocess.
"""
import os
import subprocess
import sys
import tempfile
import textwrap
import tomllib
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))

import covreduce  # noqa: E402

CHECK = textwrap.dedent("""
    import importlib.metadata

    import covreduce
    from covreduce import source

    assert importlib.metadata.version("covreduce") == covreduce.__version__
    monitor = source(1000.0, 25.0)
    counts = source([120.0, 80.0], [12.0, 9.0], dims=("bin",))
    rates = counts / monitor
    # Shared monitor: cov(0, 1) = 120*80*25 / 1000**4 > 0.
    assert rates.covariance()[0][1] > 0.0
    print(covreduce.__version__)
    """)


class TestMetadata(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(PROJECT / "pyproject.toml", "rb") as handle:
            cls.data = tomllib.load(handle)

    def test_pep621_contract(self):
        project = self.data["project"]
        self.assertEqual(project["name"], "covreduce")
        self.assertEqual(project["dependencies"], [])
        self.assertEqual(project["requires-python"], ">=3.10")
        self.assertEqual(project["readme"], "README.md")
        self.assertEqual(project["dynamic"], ["version"])
        dynamic = self.data["tool"]["setuptools"]["dynamic"]
        self.assertEqual(dynamic["version"],
                         {"attr": "covreduce.__version__"})
        self.assertEqual(self.data["tool"]["setuptools"]["packages"],
                         ["covreduce"])
        self.assertTrue(covreduce.__version__)


class TestInstallAndImport(unittest.TestCase):
    def test_pip_install_into_temp_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "site"
            install = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--quiet",
                 "--no-build-isolation", "--no-deps", "--target",
                 str(target), str(PROJECT)],
                capture_output=True, text=True, timeout=300)
            self.assertEqual(install.returncode, 0, install.stderr)
            env = dict(os.environ)
            env["PYTHONPATH"] = str(target)
            check = subprocess.run(
                [sys.executable, "-c", CHECK], capture_output=True,
                text=True, env=env, cwd=tmp, timeout=60)
            self.assertEqual(check.returncode, 0, check.stderr)
            self.assertEqual(check.stdout.strip(), covreduce.__version__)


if __name__ == "__main__":
    unittest.main()
