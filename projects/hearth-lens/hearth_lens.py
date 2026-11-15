#!/usr/bin/env python3
"""Standalone entry point for the house's Hearth Lens."""
from pathlib import Path
import sys

# Allow invocation from any working directory while using this checkout's core.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from house.hearth_lens import main


if __name__ == "__main__":
    raise SystemExit(main())
