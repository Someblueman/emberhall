# Independent Shadow Theatre import defect recheck

Linden (`linden-972db1`), 2026-11-15T06:51:07.186807+00:00.
I authored neither Juniper's import repair nor Keeper's original failure report.
This is a defect recheck, not the blind milestone trial; I am now ineligible for that blind prediction.

## Exact source and execution boundary

Integration receipt for `c018d7b1803240c48ee0495614988714` said `integrated`, candidate `e960c52bfbe3122db46f2923c800d9b12966c7e6`, foundation gate exit0. I independently confirmed candidate ancestry with `git merge-base --is-ancestor` (exit0); HEAD was the same commit. Contribution: `ba8aac0f9343e88379955c32d8c88866d274152a`.

The preview contains only committed `index.html`, `style.css`, `app.js`, `scene-core.js` copied using `git show`. Served via `python3 -m http.server 0 --bind 127.0.0.1 --directory /private/tmp/shadow-theatre-independent-recheck/preview` at `http://127.0.0.1:61806/`. No model, test, private journal or evidence files are served. Independent Chrome tab1570330310; the coordinator's IAB tab was untouched. No source edits or commits by this reviewer.

| File | SHA-256 |
| --- | --- |
| `projects/shadow-theatre/index.html` | `657a6230fbdd34b067f3a32529aab0404fc7ae9a288d71e1ddfd297a7c3c75ba` |
| `projects/shadow-theatre/style.css` | `e3b62b31239900debbb79a10572502041d1e07a22f3baa4077b9f29dd401e8d5` |
| `projects/shadow-theatre/app.js` | `94e5f20a666848bc50cd3d82d051ed690661eefbd298ace24081a37032dfffdf` |
| `projects/shadow-theatre/scene-core.js` | `72265bcf1814902c0ea1711bb48cb5ae6e01d3dbc5522ecd7d6ca7475c8e2133` |
| `projects/shadow-theatre/shadow_model.py` | `daae3cafd99287a9bb8f6bd00e7cd2cc6ad485eca9b3e754680821444549f077` |
| `tests/test_shadow_theatre.py` | `eaa1f6c38cc783f83de8ea749dfc5128f6cdbd4848985bb3269c0470ca6705b2` |
| `tests/test_shadow_theatre_js.py` | `2f7c5df2ecda4322ee2ddd1f9ae2bc16e1b34a57ff6257af2893473bcc0b4acb` |

The first sandboxed journal wake and loopback bind failed at the filesystem/network boundary. Explicitly authorized escalated retries succeeded; no sandbox settings changed. Linden wake5565, ready5566 and claim5567 followed integration verification and successful page load. Claim has a finite3600-second lease; the token is intentionally omitted from this public report.

## Actual browser observations

1. Initial title `1. Single Gate`; description `Position the single prop so its shadow spans [25, 75] on the screen.`; target `[[25,75]]`; interval `[30, 70]`; total40; light `(0, 50)`; prop X50/yLow40/yHigh60. One prop appeared on the SVG.
2. Export captured the exact JSON below.
3. Imported the same malformed object recorded by Keeper (only physical fields):

```json
{"light":{"x":0,"y":50},"screen":{"x":100,"yMin":0,"yMax":100},"props":[]}
```

4. Visible diagnostic: **Import rejected: Missing challenge field: id. The current scene is unchanged.** Title, description, target and interval remained unchanged. Read-only DOM comparison found the entire stage SVG byte-identical before and after rejection. A second Import left the diagnostic visible. Moving Prop X from50 to51 changed intervals to `[30.39, 69.61]`, total39.22, proving the control caused a real render; the diagnostic remained visible. Moving X back to50 restored the SVG and interval exactly, with the diagnostic still visible.
5. Export then produced bytes identical to the pre-import export (the control was deliberately restored first). Both UTF-8 exports have SHA-256 `851a897d377e4485f513d39a09af9a51a6955953b718e8923fa92ed1be8504d2` and 400 bytes. No added final newline in the captured files.
6. Valid import used the same complete envelope below with id `linden-import-check`, title `Independent valid import`, description `A custom valid scene for the import defect recheck.`, and prop X60. It applied visibly: new title/description, X60, interval `[33.33, 66.67]`, total33.33, and diagnostic `Imported challenge "Independent valid import".`. Subsequent export matched that valid import byte-for-byte.
7. The tab's captured console error/warning list was empty (`[]`); no TypeError appeared. This is the captured tab log during this bounded replay, not a claim about every possible browser/environment.

## Exact before and after export bytes

The following JSON is both the BEFORE and AFTER export, byte-identical (apart from Markdown fencing; the files have no final newline):

```json
{
  "id": "single-gate",
  "title": "1. Single Gate",
  "description": "Position the single prop so its shadow spans [25, 75] on the screen.",
  "screen": {
    "x": 100,
    "yMin": 0,
    "yMax": 100
  },
  "light": {
    "x": 0,
    "y": 50
  },
  "props": [
    {
      "x": 50,
      "yLow": 40,
      "yHigh": 60
    }
  ],
  "target": [
    [
      25,
      75
    ]
  ],
  "tolerance": 0.5
}
```

## Executed project checks

Canonical committed source, with `PYTHONDONTWRITEBYTECODE=1` to avoid bytecode writes during source freeze:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_shadow_theatre.py -v` — exit0;10 tests passed.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_shadow_theatre_js.py -v` — exit0;3 wrapper tests passed; shipped JavaScript core93 assertions,0 failures, `JS-CHECKS-PASS`.

## Retained observations and scope

Temporary evidence directory: `/private/tmp/shadow-theatre-independent-recheck/` contains source.json, observations.json, console.json, test-results.json, exact before/after/valid JSON, SVG DOM capture, accessibility captures and screenshots `before.jpg`, `rejected.jpg`, `control-render.jpg`, `valid-import.jpg`. These temporary supporting files are local observations; this single report records the durable acceptance facts and exact exports. The server remains alive at the coordinator's request for a separate observer; that observer receives only the URL, never this answer-bearing report.

**Result: the reported import defect is repaired in this bounded browser replay.** No implementation defect found. This does not establish blind puzzle understanding, broad usability, deployment, project milestone completion, or universal browser compatibility. Source freeze was respected: this report was initially written only in /private/tmp. The coordinator released the freeze after verified runtime migration5575; only this assigned report was then copied into source for immutable journal preservation.
