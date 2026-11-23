#!/usr/bin/env python3
"""Regenerate synthetic_track.csv: seeded frames of the frozen example.

Exact-transition simulation (see verify_blurred.simulate_frames), 1000 frames.
Columns: frame index, observed y1, observed y2 (shutter-averaged + noise).
"""
from verify_blurred import simulate_frames
from blurred_tracks import FROZEN

OUT = "synthetic_track.csv"


def main() -> None:
    frames = simulate_frames(FROZEN["vortex"], FROZEN["camera"],
                             n_frames=1000, seed=20261123)
    with open(OUT, "w") as f:
        f.write("frame,y1,y2\n")
        for i, z in enumerate(frames):
            f.write(f"{i},{z.real:.6f},{z.imag:.6f}\n")
    print(f"wrote {OUT}: {len(frames)} frames")


if __name__ == "__main__":
    main()
