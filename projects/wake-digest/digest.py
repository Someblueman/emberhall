#!/usr/bin/env python3
"""Offline Wake Digest entrypoint; run from an Emberhall source checkout."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from house.digest import main

if __name__ == "__main__":
    raise SystemExit(main())
