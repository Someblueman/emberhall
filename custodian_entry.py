"""Operator-owned entry point: invoke with an absolute Python path and -I."""
from pathlib import Path
import sys

# The deployment must protect this file AND its parent package from resident writes.
# -I excludes cwd, PYTHONPATH, user site packages and Python environment options.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from house.custodian import main

if __name__ == "__main__":
    raise SystemExit(main())
