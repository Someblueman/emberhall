#!/usr/bin/env python3
"""One-command runner for both covreduce importing programs.

Runs the monitor/background fit (run_demo -> covreduce.cli) and the
weighted-fit program back to back and exits nonzero if either fails.
Standard library only.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from covreduce.cli import main as cli_main
import weighted_fit_demo


def main(argv=None):
    print("=== program 1: monitor/background fit (run_demo) ===")
    rc = cli_main()
    if rc != 0:
        print("FAIL program 1", file=sys.stderr)
        return 1
    print("=== program 2: weighted-fit (weighted_fit_demo) ===")
    rc = weighted_fit_demo.main()
    if rc != 0:
        print("FAIL program 2", file=sys.stderr)
        return 1
    print("both covreduce importing programs passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
