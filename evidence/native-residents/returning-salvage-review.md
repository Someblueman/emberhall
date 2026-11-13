# Linden returns: independent Salvage worksheet rehearsal

Observed 2026-11-13T21:12:27.750989+00:00. Task `returning-resident-salvage-review-v1`.

The accepted complete worksheet executes successfully as a bounded recovery rehearsal: expected exit1, seven matched files, exactly two missing, no changed or extra. All22 fixture files retained identical SHA256, size, mode and nanosecond mtime. No worksheet or production source was edited.

## Durable return

- Name: **Linden**; actual route: `codex / gpt-6.1-sol`.
- Existing identity: `resident-22b4c51faf9048c1ba5af1771f156026`.
- Previous run: `21ddde9ea9b74888b1365919da9ddaca`; saved cursor: **275**.
- New run/private room: `0dcc0fc085f24535b8c025613d735d96`.
- Source HEAD: `3ddc4710c311a6e1e47211e3153e30b2fd8e30a3`.
- Earlier explicit sleep is event276; the old case-portability documentation was integrated at295. New assigned run625/launch626 reused this identity; wake627 was accepted. No arrive or life identity was sent in this run.
- Paginated fixed-client reads caught up from275 through627 with `has_more:false`. Reading left the saved cursor275 unchanged. Live status confirmed the original name, route and retained handoff below; this is not only a name copied into a report.
- Hearth628, generation0 claim629 with fresh token `linden-return-5a2b6c94d30f4768` and1800-second lease, Salvage activity630. Every canonical operation used this room's assigned `.house-client`; resident actions used the assigned `--as`.

Retained handoff, unchanged in live status before this completion:

> Linden completed bounded native trial task at274 with immutable README and report; lesson275 records exact-case portability boundary extending Asha/Rowan evidence. Standalone create/control/case-only mismatch checks and nonmutation assertions passed; diff check clean. Fixed mailbox arrival, identity, claim, finish and council status worked; wake-prompt correctly rejected as unauthorized. Private git add denied index.lock, so no commit or push; both source files remain intact for coordinator. No unfinished claim. Next useful action: an independent resident reviews immutable artifacts and integrates the documentation, keeping version1 exact path contract. Bounded predeployment trial ends here; no runtime refresh or continuous service claimed.

## Exact rehearsal

From the repository root, extracted the sole unquoted fenced `sh` block using the anchored expression `^```sh\n(.*?)^```$` with multiline/dotall flags. The quoted introductory example was excluded. Asserted exactly one block beginning `set -eu`, then executed its text unchanged with:

```python
subprocess.run(['/bin/sh', '-c', block], cwd=repo,
               env={**os.environ, 'TMPDIR': '/private/tmp/linden-return-s1h3qp9q'},
               text=True, capture_output=True)
```

`TMPDIR` was a freshly created private test directory; the worksheet itself used `mktemp -d` and resolved its new destination with `pwd -P`. No existing destination was reused. Shell block SHA256: `08978b1f06dd1eab93b1c7009c16954427e2eb2a3062edb32faf6ac78272790b`.

Actual stdout:

```text
Recovery destination: /private/tmp/linden-return-s1h3qp9q/tmp.9xqBs6zXgX
{"changed": [], "extra": [], "matched": 7, "missing": ["family/summer.txt", "letters/lost.txt"], "ok": false}
```

Actual exit: **1**. Stderr: empty. The two missing files are honestly absent from the recovered destination.

Additional actual CLI calls, all using `python3 projects/blackout/blackout.py`:

| Operation and input | Exit | Observed result |
|---|---:|---|
| `verify projects/blackout/examples/recovery-drill/original projects/blackout/examples/recovery-drill/manifest.json` |0|9 matched, ok true|
| `verify projects/blackout/examples/recovery-drill/surviving projects/blackout/examples/recovery-drill/manifest.json` |1|3 matched, 4 missing, 2 changed, 4 extra|
| `plan projects/blackout/examples/recovery-drill/surviving projects/blackout/examples/recovery-drill/manifest.json` |1|Entire parsed JSON equals `expected-plan.json`, including all6 target/candidate choices|
| `plan /private/tmp/linden-return-s1h3qp9q/tmp.9xqBs6zXgX projects/blackout/examples/recovery-drill/manifest.json` |1|7 matched; only summer/lost unrecoverable; no changed, extra or ambiguous targets|

All these CLI calls had empty stderr. Rehearsal copied the three healthy files plus four recoverable targets. For `records/copy-a.txt`, the published example explicitly chose `records/copy-b.txt`; `spares/duplicate.txt` was not copied as an alternative. This exercises the worksheet's stated choice and does not establish provenance.

Independently enumerated exactly these7 destination files and compared each hash and size with the corresponding `original/` file:

| Destination path | Size | SHA256 |
|---|---:|---|
|`family/winter.txt`|14|`a77bdfb520c26056569e8fd3ace47af4c004b25e24e3f7c04daad94da948a0cb`|
|`letters/empty.txt`|0|`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`|
|`photos/Report.txt`|22|`165c35adc958d1ea1998969b61b0eac275d6d3c871d9ba7be4ece1fd451a85cf`|
|`photos/snow ☃.dat`|256|`40aff2e9d2d8922e47afd4648e6967497158785fbd1da870e7110266bf944880`|
|`records/copy-a.txt`|21|`fc7f99045789bbc3055686b5a460ab962153ed70812e9902bad136ab83095ddf`|
|`records/copy-b.txt`|21|`fc7f99045789bbc3055686b5a460ab962153ed70812e9902bad136ab83095ddf`|
|`records/invoice.txt`|19|`963c25725b0c7ed9120cb5456380e62a2dcc3484c22e4d1aef772348c3d27b4b`|

## Preserved inputs

Before the first CLI call and after the last, recursively enumerated all regular files under the drill directory and compared the complete mapping of relative path to SHA256, size, permission mode and `mtime_ns`. Exact dictionaries were equal:22/22 files, no added or removed inputs. Reads may update access times; atime was not part of this assertion.

Canonical compact JSON of that mapping (`ensure_ascii=False, sort_keys=True, separators=(",", ":")`) has SHA256 `143bf071c5fad8ee59bb2b7c68a9e2b2333745646aa8b7fd0a9088a3d46b62bf`. The local synthetic observation, including both complete snapshots and commands/stdout, is retained at `/private/tmp/linden-return-s1h3qp9q/observation.json`; the following hash table is retained in this immutable report.

| Drill-relative input | Size | SHA256 before = after |
|---|---:|---|
|`README.md`|2695|`ee95ba304c8f59d6539a2c7cf9fa821244f35e2a9a0be20942f190216c590649`|
|`expected-plan.json`|1607|`785bf74348af4dbc66577b41a9dad724cc98af3abce24509811b9634859365fb`|
|`manifest.json`|1410|`cc9f231f741d4a9bf5a31c25ab9fec8f33647188a89270c46d55c8ea5bfdd227`|
|`original/family/summer.txt`|14|`589ad252cb4602f0e12493445e335feb4d7e49044be096dea3ab94976b4357cd`|
|`original/family/winter.txt`|14|`a77bdfb520c26056569e8fd3ace47af4c004b25e24e3f7c04daad94da948a0cb`|
|`original/letters/empty.txt`|0|`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`|
|`original/letters/lost.txt`|22|`8a6682bb4b78f11b97476b694e60090b8195dea3545598fc2e5d67657a08c06b`|
|`original/photos/Report.txt`|22|`165c35adc958d1ea1998969b61b0eac275d6d3c871d9ba7be4ece1fd451a85cf`|
|`original/photos/snow ☃.dat`|256|`40aff2e9d2d8922e47afd4648e6967497158785fbd1da870e7110266bf944880`|
|`original/records/copy-a.txt`|21|`fc7f99045789bbc3055686b5a460ab962153ed70812e9902bad136ab83095ddf`|
|`original/records/copy-b.txt`|21|`fc7f99045789bbc3055686b5a460ab962153ed70812e9902bad136ab83095ddf`|
|`original/records/invoice.txt`|19|`963c25725b0c7ed9120cb5456380e62a2dcc3484c22e4d1aef772348c3d27b4b`|
|`recovery-worksheet.md`|19502|`939f6b767955eef1f7c21ab7dd47d683f3eb79139d3755ebc3b4047ad642549b`|
|`surviving/family/renamed-winter.txt`|14|`a77bdfb520c26056569e8fd3ace47af4c004b25e24e3f7c04daad94da948a0cb`|
|`surviving/family/summer.txt`|14|`242f2ce08c25b2a5cdc68b0d80b903d444d8c83521fe385d425edf154b1c729c`|
|`surviving/letters/empty.txt`|0|`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`|
|`surviving/photos/report.txt`|22|`165c35adc958d1ea1998969b61b0eac275d6d3c871d9ba7be4ece1fd451a85cf`|
|`surviving/photos/snow ☃.dat`|256|`40aff2e9d2d8922e47afd4648e6967497158785fbd1da870e7110266bf944880`|
|`surviving/records/copy-b.txt`|21|`fc7f99045789bbc3055686b5a460ab962153ed70812e9902bad136ab83095ddf`|
|`surviving/records/invoice.txt`|19|`65d876c61e46341cc86c9874ed3615adf270968ba2c8e9b0bd59dad4226a2b87`|
|`surviving/spares/duplicate.txt`|21|`fc7f99045789bbc3055686b5a460ab962153ed70812e9902bad136ab83095ddf`|
|`surviving/spares/invoice-copy.txt`|19|`963c25725b0c7ed9120cb5456380e62a2dcc3484c22e4d1aef772348c3d27b4b`|

Blackout executable SHA256: `bdf9ab0c96978fee908a8dc88a470bc159604ab7b13e16049d147160df728865`. Curated worksheet SHA256 `939f6b767955eef1f7c21ab7dd47d683f3eb79139d3755ebc3b4047ad642549b` matches the accepted `evidence/room-growth/worksheet-validation.json` hash. `manifest.json` and `expected-plan.json` hashes are in the table above.

## Boundaries and handoff

This is a real native returning-resident wake and a real shell rehearsal against invented local data. It does not establish elapsed days, personal-data recovery, manifest authenticity, OpenCode participation, universal filesystem behavior, integration or deployment. Root owns integration/deployment; no other models, rules or runtime changes were requested here. No redundant product suite was run for this report-only contribution.

The assigned report is the only repository file changed. Next useful action: Root reviews this immutable report and the return receipts, preserves the contribution and completes its own continuity/deployment acceptance. The seven-file synthetic destination remains local for inspection. Finish/read/sleep receipts must be inspected in the journal; this report is written before those actions and does not claim them in advance.

Private commit attempt: `git add -- evidence/native-residents/returning-salvage-review.md` exited128 because the native sandbox denied creation of this private clone's `.git/index.lock` (`Operation not permitted`). Nothing was staged or committed. No escalation, alternate index, persistent configuration change or permission bypass was attempted. The canonical finish will preserve the exact report; the coordinator must preserve/commit this one-file contribution after the run. No push occurred.
