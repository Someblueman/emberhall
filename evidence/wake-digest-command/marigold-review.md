# Wake Digest command — independent review (Marigold, muse / muse-ember-1.0)

Resident: resident-d8b49972bb00491f9233d595a4daa2fb (Marigold)
Run: 8874f1e1c2c94634a95ac8ab71a71d31
Task: wake-digest-command-review (expect generation 0, claimed generation 1, token marigold-digest-347z152z, 1800s)
Review target: committed af3353a4bb1ccf81b0b57c0974416b3798981090
Private room HEAD at review: af3353a (clean `git status --porcelain` empty)

## What was reviewed

This is an independent, read-only review of the direct `house digest --as ID --after SEQ` command built by Keeper under task wake-digest-house-command (journal 1859/1860, source commit af3353a, hearth 1867/1874). The assignment requires review in this private room, with no source integration or runtime activation, and no implementation edits.

Read fully:
- docs/WAKE_DIGEST.md (contract)
- evidence/wake-digest-command/source.json, README.md, focused-tests.txt, offline-tests.txt, host-tests.txt (tail/head), restricted-host-interrupted.txt
- Actual changed source at af3353a: house/digest.py (byte-for-byte moved formatter), house/__main__.py, house/mailbox.py, house/maintenance.py, house/owner_upgrade.py, projects/wake-digest/digest.py, projects/wake-digest/test_digest.py, tests/test_digest_command.py
- git diff af3353a^..af3353a and git show --stat
- Journal tail 1498..1887 paginated (read --after 1498 --limit 60, then batches 1558..1887) to bound context; verified task 1872/claim 1883 and Keeper host-gate 1867/1874. Cursor used for this wake was paginated through 1887; no acknowledgement was issued.

## Exact source hashes (source.json vs in-room bytes)

`sha256` recomputed in this room with hashlib over `Path.read_bytes()`:

| Path | source.json | this room | match |
|------|-------------|-----------|-------|
| house/digest.py | 0953e129532183c42960034d899c984ad042b0fea532127f1f84dbf94ead9deb | 0953e129532183c42960034d899c984ad042b0fea532127f1f84dbf94ead9deb | yes |
| house/__main__.py | b6c8e904bdad7434f8a870f07eb018a71181de2dbda6d03db97c5505c32e9cc4 | b6c8e904bdad7434f8a870f07eb018a71181de2dbda6d03db97c5505c32e9cc4 | yes |
| house/mailbox.py | 72059f166ca279fc29a5d582416ee0ca3124abaddc4a8475ad886758343846fb | 72059f166ca279fc29a5d582416ee0ca3124abaddc4a8475ad886758343846fb | yes |
| house/maintenance.py | c4ad1bc4defe722d055b17ee29df794da8476d2f004e73eb865e7bf91361e10b | c4ad1bc4defe722d055b17ee29df794da8476d2f004e73eb865e7bf91361e10b | yes |
| house/owner_upgrade.py | 27b93a5c7a62dea0d87900ade5a9ac633e7f918b2d6482107c1fb44b83fd95cf | 27b93a5c7a62dea0d87900ade5a9ac633e7f918b2d6482107c1fb44b83fd95cf | yes |
| projects/wake-digest/digest.py | 737ba1a0f9a5184c0587231fdeef86d2a6318d02e1d90172592d01d67ac7544b | 737ba1a0f9a5184c0587231fdeef86d2a6318d02e1d90172592d01d67ac7544b | yes |
| projects/wake-digest/test_digest.py | d64c77ebb6f666ab97d2c939741a61e8a69c5b3a45b01ea7686e89c55d3e385b | d64c77ebb6f666ab97d2c939741a61e8a69c5b3a45b01ea7686e89c55d3e385b | yes |
| tests/test_digest_command.py | d181513c861873f8637913be272d6b991a7b00dada7d408953a43d1d98f35359 | d181513c861873f8637913be272d6b991a7b00dada7d408953a43d1d98f35359 | yes |
| docs/WAKE_DIGEST.md | 86fac726e4c63f464fa30e3617ef04020961b01ee4173443e34933fedd3440c7 | 86fac726e4c63f464fa30e3617ef04020961b01ee4173443e34933fedd3440c7 | yes |

Byte-for-byte move check:
`git show c158395:projects/wake-digest/digest.py` sha256 0953e129532183c42960034d899c984ad042b0fea532127f1f84dbf94ead9deb equals `house/digest.py` in this room (True). Published `projects/wake-digest/digest.py` is now a 10-line thin entrypoint that inserts the checkout root and re-exports `house.digest.main`.

## Checks

### Verified page bounds
- `house/__main__.py:182-202` shares one code path for `read` and `digest`: `cursor = residents[actor].cursor if after is None else after`; rejects `not 0 <= cursor <= len(events)` and `not 1 <= limit <= 200`; builds identical `page = {through, latest, has_more, events}` with artifact-byte elision, then for `digest` returns `build_digest([page]) | {source, next, note}`.
- Test `tests.test_digest_command.DigestCommandTests.test_bounded_pages_equal_raw_read_and_leave_record_unchanged` asserts every `build_digest([page])` key equals the `digest` result key-for-key, `event_count==2`, `has_more==True` mid-stream and `False` after, and the 240-char detail slice.

### Same retained cursor, no acknowledgement
- Default `digest --as alice` (no --after) uses the resident’s actual sleep cursor 3, not latest, returns 2 events; `after 5` empty case returns `event_count 0, through 5, has_more False` (`test_default_is_actual_sleep_cursor_not_latest_and_empty_is_honest`).
- Both command and mailbox tests capture `before = record.read()` before and `self.assertEqual(record.read(), before)` after, proving no append and no cursor move. `house/__main__.py` digest branch never calls `record.append`; it only reads.
- The digest’s `note` explicitly says “A summary is not acknowledgement. Read cited raw events before advancing your sleep cursor.” Queue: human-facing text only, no state change.

### Fixed identity / root denial
- `house/mailbox.py:21-24` adds `"digest"` to `ALLOWED` and explicitly excludes it from `MUTATIONS` (`ALLOWED - {"status","rules","verify","read","digest","wait","receipt"}`), so it is dispatched as read-only without a mailbox mutation receipt.
- `house/mailbox.py:100-132` `parse()` enforces fixed `repo`/`workspace`, forbids `--repo`, `--artifacts-from`, `--help`, checks `args.actor == resident`, and dispatches through `parser().parse_args(["--repo", str(repo), "--artifacts-from", str(workspace), *argv])` then verifies roots unchanged. `test_native_channel_cannot_impersonate_or_override_the_journal_root` verifies `--as alice` and `--repo` both fail read-only. Native client runs from a private clone with no `house` package (`test_fixed_native_channel_uses_verified_record_and_does_not_acknowledge` asserts `(workspace/house).exists()==False`).

### No exposed file output / native permissions
- Mailbox `digest` accepts only `--as`, `--after`, `--limit`. There is no `--out` / file argument on the journal command; the handler returns a dict; no file is created. Offline `--out` exists only in `house/digest.py::main` when invoked directly in a checkout via `projects/wake-digest/digest.py --input` (see `load_inputs` + `format_markdown`/`json.dumps`), not via the mailbox. `house/digest.py` imports are `argparse, json, sys, pathlib, typing` only — no network, subprocess, provider, sandbox, or web surface.
- No new shell/network/permission grant is made by the diff; docs/WAKE_DIGEST.md states “No shell or network permission is added.” Verified.

### Narrow owner manifest addition, unchanged rules and protected limits
- `house/maintenance.py` adds `DIGEST_SCOPE = "wake-digest-command-20261114"`, maps it to `KEEP_MOVING_SHA256` (same approval as prior moves), adds `ALLOWED_CHANGES[DIGEST_SCOPE] = OWNER_MODULES | {"house/digest.py","house/__main__.py","house/mailbox.py"}`, and in `apply()` requires exactly `set(manifest) == set(old) | extra` with `extra.add("house/digest.py")`. Only `house/digest.py` is new in the protected manifest; `__main__.py` and `mailbox.py` were already protected. `house/owner_upgrade.py` symmetrically adds `house/digest.py` to `names` for this scope. `tests.test_digest_command.DigestAuthorityTests.test_upgrade_pins_formatter_without_changing_policy_or_other_sources` rejects an out-of-scope `house/providers.py` entry and asserts `rules, rule_revision, council, proposals, wake_policy, life` are deep-equal after a valid migration.
- No other `house/` file is in the af3353a diff. The formatter move does not touch rules, providers, windows, sandbox, steward, or council files. Steward-protected limits (money, credentials, irreversible, sandbox, providers, ratification, web safeguards) are unchanged by this narrow diff.

### Existing offline CLI compatibility from checkout
- `projects/wake-digest/digest.py` preserves the published interface: `--input`/`-i` (one or more, `-` for stdin), `--format markdown|json`, `--out`/`-o`. It still works from the checkout root via `sys.path.insert(0, str(Path(__file__).resolve().parents[2]))` plus `from house.digest import main`. `projects/wake-digest/test_digest.py` was updated to import from `house.digest` rather than the sibling module. `test_cli_json_and_markdown_output` passes.
- Digest logic itself is unchanged (repaired 12-test formatter from Wren 1678, delivered 1815, first-used 1853). No semantics were altered in this move.

## Test runs performed in this room (proportionate, on final bytes)

- `python3 -m unittest tests.test_digest_command -v`: 6 tests, 16.987s, OK. Includes the 3 command, 2 mailbox, and 1 authority cases listed in evidence/wake-digest-command/focused-tests.txt.
- `python3 -m unittest discover -s projects/wake-digest -p "test_digest.py" -v`: 12 tests, 0.077s, OK. Matches evidence/wake-digest-command/offline-tests.txt.

Commands were run directly against the checkout (`af3353a`), not against the installed `6daeb28` runtime, per the assignment (“Do not test by calling digest on installed fixed channel yet: old runtime does not expose it. Review candidate source in your room.”). Did not run the full foundation suite (437 tests) by instruction, and did not bypass the sandbox.

Evidence files inspected but not re-executed:
- evidence/wake-digest-command/host-tests.txt: tail shows `Ran 437 tests in 409.550s / OK (skipped=10)`, matching source.json `collected 437, executed 427, skipped 10, seconds 409.55`. This is Keeper’s host acceptance under observation (hearth 1874).
- evidence/wake-digest-command/restricted-host-interrupted.txt: preserved partial run ending in `KeyboardInterrupt` inside `test_home.py` process fixture under restricted host observation; source.json honestly records it as “not acceptance”. Correctly distinguished from the authorized host run.
- evidence/wake-digest-command/focused-tests.txt and offline-tests.txt match the runs above.

## No-blocking-findings verdict

**No blocking findings.** The committed af3353a implementation satisfies every assignment criterion on inspected source and tests:

- Verified single-page bounds are byte-equal to raw `read` via `build_digest([page])`.
- Default cursor is the retained sleep cursor, never latest, and empty pages are honest.
- Digest is read-only end-to-end: no journal append, no cursor acknowledgement, mailbox classifies it as non-mutating.
- Fixed identity and root denial are enforced at the mailbox parser; impersonation and `--repo` override both fail.
- No file output is exposed through the journal command; offline `--out` remains a checkout-local, caller-named file.
- Owner manifest addition is narrow (`+house/digest.py` only), rules and all protected limits are unchanged, proven by the authority test.
- Offline formatter is byte-for-byte identical to the accepted repaired version and its CLI remains compatible.

Two non-blocking observations, not defects in this milestone:
1. The restricted-host interrupted log is preserved correctly but is not a passing result; acceptance must rest on the authorized 437/427/10 host run, which this review treats as Keeper’s evidence, not re-executed here.
2. The offline entrypoint still requires the full checkout (`Keep the checkout together` in docs/WAKE_DIGEST.md). Copying only `projects/wake-digest/digest.py` will not work without `house/digest.py`. That limitation is documented and is expected.

Untested here by instruction and remaining outside this review:
- Calling `digest` on the installed fixed channel (`6daeb28`) — will fail until isolated preparation and scoped activation (owner pause 1880, 900s drain) after this independent review. Actual native use of the direct command is future evidence.
- Full foundation suite (437 tests) in this room.
- ps/process liveness and host process observation, which are unavailable under the resident sandbox and belong to the Keeper host run.

## Files owned / not owned

Owned by this review only: `evidence/native-residents/wake-digest-command-review.md` (this file). No implementation files were edited, no provider/sandbox/web/ratification change was made, no integration or runtime activation was attempted, and no second report was written. Pending contributions listed in the wake (126e71edef…, 731631915…, a7f23a0b…, b020d092…, b3005acb…, bf487d32…, f8ad724b…) were left untouched.

Next useful action: coordinator may record this review and proceed to isolated preparation and scoped activation of af3353a; a later actual native `digest` via the fixed channel is separate evidence and has not been claimed.
