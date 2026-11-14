import pathlib
import subprocess
import unittest


ROOT = pathlib.Path(__file__).resolve().parent.parent


class SnapshotFreshnessTests(unittest.TestCase):
    def test_index_has_snapshot_cue_element(self) -> None:
        html = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
        self.assertIn('id="house-clock"', html)
        self.assertIn('id="snapshot-cue"', html)

    def test_snapshot_cue_formatting_and_edge_cases(self) -> None:
        js = (ROOT / "site" / "house.js").read_text(encoding="utf-8")
        script = f"""
const data = {{ timezone: "Europe/London" }};
function $(id) {{ return null; }}
function snapshotCue({js.split("function snapshotCue(")[1].split("function lighting(")[0]}
function clock(at, opts={{}}) {{
  return new Intl.DateTimeFormat("en-GB", {{
    timeZone: data.timezone || "Europe/London",
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
    ...opts,
  }}).format(new Date(at * 1000));
}}
const now = 1794643200; // 2026-11-14T08:00:00Z
console.log(JSON.stringify({{
  justNow: snapshotCue(now, now - 15, now - 15, true, "Europe/London"),
  mins: snapshotCue(now, now - 600, now - 600, true, "Europe/London"),
  hours: snapshotCue(now, now - 7200, now - 7200, true, "Europe/London"),
  days: snapshotCue(now, now - 172800, now - 172800, true, "Europe/London"),
  future: snapshotCue(now, now + 300, now + 300, true, "Europe/London"),
  invalidObs: snapshotCue(now, NaN, now, true, "Europe/London"),
  history: snapshotCue(now, now - 600, now - 3600, false, "Europe/London"),
  invalidHist: snapshotCue(now, now - 600, -1, false, "Europe/London"),
}}));
"""
        proc = subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        import json

        out = json.loads(proc.stdout)
        self.assertIn("just now", out["justNow"])
        self.assertIn("10m ago", out["mins"])
        self.assertIn("2h ago", out["hours"])
        self.assertIn("2d ago", out["days"])
        self.assertNotIn("-", out["future"])
        self.assertIn("unknown", out["invalidObs"].lower())
        self.assertIn("Event ", out["history"])
        self.assertIn("unknown", out["invalidHist"].lower())


if __name__ == "__main__":
    unittest.main()
