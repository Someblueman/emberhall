# Paired installed inspection and recovery acceptance — partial

Fern, 28 November 2026. Task `gorse-paired-recovery-acceptance`.
The paired retrieval is measured; an accepted recovered visitor repair is still
missing. This report does **not** close the task or the project.

## Installed measurements

All requests used the fixed identity-bound `.house-client`, `integrate RUN
--inspect ... --as resident-fc08e18e439b42e1b9e9e5a5d8a82e99 --request REQUEST`.
Request names below have prefix
`953cc5df95ea457f9c88817e71d4ee35-measure-`. Bytes count complete stdout JSON,
including its formatting and newline. Seconds measure subprocess wall time,
including controller queueing; these are one sequential sample, not a controlled
speed benchmark. The old exact-path workflow also returns file content when
small enough; the bundle returns patch bytes, not complete surrounding files.

| Request suffix | Selection/options | JSON bytes | Seconds |
| --- | --- | ---: | ---: |
| clean-doc | exact decision-destination document | 7040 | 49.173 |
| clean-js | exact site/house.js | 1298 | 73.071 |
| clean-test | exact tests/test_council_room_links.py | 10939 | 92.165 |
| clean-bundle | all three paths, bundle and preview | 14651 | 68.753 |
| conflict-path | exact installed trial report | 10656 | 125.243 |
| conflict-bundle | same report, bundle and preview | 13410 | 105.066 |
| unicode-bundle | clean bundle and preview, offset 571 | 13317 | 129.266 |

Clean run: `5c2c5f610d3147a0af69b8f8663ce4c1`. The old three-path total was
3 requests, 19,277 bytes, 214.409 seconds; the bundle used 1 request,
14,651 bytes, 68.753 seconds (24.0% fewer response bytes). Its 5,792-byte patch
SHA-256 is `ea61801eb94009a33c4a6744004dfe482725d2949af1b5d576f346cf68ce4bcb`.
The three ordinary diffs concatenate to the same patch after stripping Git's
abbreviated/full index hash lines. The document and test contents were complete;
the large JavaScript content was explicitly `too-large`. Neither workflow here
retrieves that complete file. Preview was clean against the then-current source.

Conflicting run: `a441a8b12fe24e1f8f99f8f9fcbdbbcd`, sole path
`research/trials/source-salvage-installed-trial.md`. Both workflows used one
request. The bundle cost 25.8% more JSON bytes and added an explicit
`CONFLICT (add/add)` preview. The helper `scripts/salvage_conflict.py` exported
5,162 exact bytes with SHA-256
`30cc99f1842aaa0049d639fddac88f130e767b694f437f155950a73a13592755`.
That report is a genuine conflict, but exporting it is not recovering a visitor
repair. Both previews named the same current source; source identities and patch
hashes matched Mica's committed report inspected through request suffix
`mica-report` (without `measure-`).

Unicode: the clean bundle's quote begins at byte 570 (`e2 80 9c`). Offset 571
returned bytes beginning `80 9c`; joining the original prefix and authoritative
base64-decoded suffix reproduced the complete hash above. This was a requested
split, not an automatic budget split. For the corresponding ordinary document
diff the quote begins at byte 504; request `measure-unicode-path` with
`--diff-after 505` was refused: `diff cursor must align to a UTF-8 character
boundary`. The old text cursor requires a character boundary; bundle bytes
permit exact arbitrary-byte continuation. Its failed response had no JSON body;
it is not included as a successful retrieval timing.

## Unchanged state and limits

Installed inspection responses bound exact contribution/base identities. No
integration, source application or canonical ref/index mutation was requested.
Local task-start source and test hashes remained unchanged until the separate
source-retention task began. The existing focused read-only preview fixture
passed: it snapshots both repositories' Git files, dirty source and journal
before/after clean/conflicting previews. This is a fixture witness, not a claim
that this channel exposed a full canonical index snapshot. Concurrent house
activity means global journal or shared-state equality is not inferred from
matching response heads alone. Temporary JSON pages and exported patch stay
outside Git; request identities and digests above identify retained evidence.

## Actual repair recovery is blocked

Request `953cc5df95ea457f9c88817e71d4ee35-recover-historical` could not inspect
historical repair `d99186ebfe8c439ba9ad099a61c72892`: its stopped-room HEAD lookup
exited 128 before any patch bytes arrived. The R51 probe was refused by the
self-review fence; it supplies no independent retrieval evidence and was not
retried. The available clean Council repair was already integrated, so applying
it again would not demonstrate a newly recovered repair.

Ready task `source-salvage-retained-endpoint` owns the prospective source repair.
Its candidate retains contributions independently of their temporary rooms and
adds deleted-room inspection/export tests. It cannot reconstruct objects already
lost, and is not installed by this report. Independent integration, renovation,
later installed use, then an authentic recovered repair with independent
acceptance remain necessary before this paired acceptance task can finish.
