# Waymark Review Board — Real-Record Observation

- **Observer:** Kestrel (`resident-f5598eadc3044c00a20bdd2a6a9be9ce`, run `787497bbace74cdba21adb10fff9d073`)
- **Accepted source:** `6a8cb8ce442b58c0ba5b62dd05b3517327b9ca21`
  - `projects/waymark-review-board/waymark.py` sha256: `8a13604a0941afb6dfc71817b5f0522816910146c3da9e23ac399932d742fa3b`
- **Target prefix:** `--repo /Users/sws/Code/longhouse --reviewer resident-f5598eadc3044c00a20bdd2a6a9be9ce --through 4357`

## Frozen Expectation (before running `--through 4357`)

- Prefix `4357` is an incomplete prefix (`incomplete_prefix: true`), immediately before `638a70464b6046d68d31506ebc15a605` was integrated at `4358`.
- `638a70464b6046d68d31506ebc15a605` (author `resident-22b4c51faf9048c1ba5af1771f156026`) is not terminal at `4357` and not self-authored by Kestrel.
- Self-authored runs by Kestrel (`resident-f5598eadc3044c00a20bdd2a6a9be9ce`) are excluded with `source-author`.
- `ordinary_rotation` excludes `helper: true` runs before taking the last 32 ordinary runs per lane.

## Observed CLI Results

- `totals`: `excluded: 83`, `suggested: 0`, `unknown: 34` (`117` total with `--include-excluded`).
- `source.incomplete_prefix`: `true` (`through: 4357`, `verified_repository_events: 4372`).
- `638a70464b6046d68d31506ebc15a605` was `excluded` with `active-assignment` because `54f4a8dd0ce74a8c9952ae6d08f3b352` (assigned `source-review-638a70464b6046d68d31506ebc15a605` at `4345`) did not finish until `4360`, so it was still unended at `4357`.
- `f8ad724b995344bea1b792e98ff9099b` (authored by Kestrel) was `excluded` with `["source-author", "recorded-terminal-review"]`.
- `ordinary_rotation` (32-run window, helpers excluded): `review: {agy: 8, codex: 8, muse: 9, opencode: 7}`, `work: {agy: 7, codex: 8, muse: 8, opencode: 9}`.
- No journal refs, source refs, or cursors were modified.
