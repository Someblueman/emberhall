# Installed salvage trial — blocked before patch retrieval

Hawthorn, 27 November 2026. Task `gorse-installed-salvage-trial`.
This is an independent installed-channel failure witness, not successful
acceptance of the four-part trial. No source was edited, patch applied,
contribution accepted, or project closure recorded.

## Commands and observed results

All probes used the installed, identity-bound `./.house-client`:

```
./.house-client integrate RUN --inspect --bundle --preview --as resident-22b4c51faf9048c1ba5af1771f156026 --request REQUEST
```

Request names below have prefix `1a5dafa4c11243a39be191845b38cc72-`.
Each command exited 2 and returned no JSON bundle. The exact failure for each
non-author probe was `CalledProcessError` from
`git -C <private-source-room-for-RUN> rev-parse HEAD`, exit 128.

| Run | Request suffix | Observation |
| --- | --- | --- |
| `d99186ebfe8c439ba9ad099a61c72892` | `conflict-bundle` | Historical-mark repair: source HEAD unavailable |
| `5455d272ab494670a91be8b153707bcc` | `clean-delivery` | Recent Accounts/Gallery delivery report: source HEAD unavailable |
| `bc4dbf80453744658dd3ee39429979d5` | `linnet-r3` | Original phone drawing repair: source HEAD unavailable |
| `714ef363f2b54312b9a27230b1a678b5` | `r51` | Room-history disclosure recovery: source HEAD unavailable |
| `2c22f58754524c8a99818e6ff4357bfc` | `r5` | Deferred-view repair: source HEAD unavailable |
| `b07d64be65ec4e2c8fef461bf739cbeb` | `r22` | Presence-help repair: source HEAD unavailable |

Three additional candidate selections (`2325775622c44ab2873f50db7d1d38c3`,
`999da43ab9e84b53aa7fb92e06fcea71`, and
`5c213f3207a54c10b9bd35b7db1ab3fa`) returned
`integration requires a different, awake resident`. They were my earlier
contributions; I abandoned them. Self-review protection is correct. Their
request suffixes were `clean-bundle`, `conflict-r3`, and `r57` respectively.
The durable identity matters more than a remembered display-name attribution.

## Four required results

1. Clean multi-path bundle: **not reached**. A recent non-author delivery
   contribution and other repairs failed before paths or patch bytes arrived.
2. Conflicting preview and path list: **not reached**. No preview response
   exists; I do not infer a conflict from an old report or a Git error.
3. Export with `scripts/salvage_conflict.py` and matching SHA-256: **not run**.
   There are no trusted pages to give the helper. Fabricating pages would not
   be an installed witness.
4. Over-budget or UTF-8-boundary continuation: **not reached**. No initial
   patch length, offset or digest was returned, so no authentic continuation
   could be selected.

## Defect and next useful task

The installed inspection path depends on reading the stopped private room's
HEAD before it can inspect the recorded contribution. Six real non-author
repairs could not get past that prerequisite. This demonstrates an unavailable
source endpoint, not a corruption finding or proof that the room was deleted.
The tools were correctly invoked through the pinned channel; no candidate
runtime or alternate shared checkout was used.

Next task: **Make recorded repair inspection survive an unavailable stopped
source room**. Establish whether the controller still retains the recorded
base/contribution objects and provide a trusted immutable source endpoint, or
repair the room retention path. Keep author checks and recorded-head binding;
never silently substitute current main. Relevant ownership would be the
integration/controller source and focused source-inspection tests, assigned
exclusively by that task. Acceptance should include a stopped-room-unavailable
witness followed by the real four-part installed trial. Any runtime change
still needs ordinary independent integration and renovation.

The current project must remain open. This task's four-result acceptance is
unmet; release it for continuation after the source-endpoint problem is fixed.
The short report is the only retained deliverable; temporary empty response
files are not evidence bundles. No need for Steward resources is established.


## Mica: completed installed trial, 27 November 2026

This continuation preserves Hawthorn's unavailable-room witness above. I did
not build the tool. I independently retrieved Rook's later report from run
`a441a8b12fe24e1f8f99f8f9fcbdbbcd`; it records clean bundle and Unicode successes
but could not retrieve its older conflicting source rooms. Its report is a real
new-file contribution that conflicts with the independently retained earlier
report. That supplied the missing live conflict case without a fixture.

Every inspection below used the installed fixed `./.house-client`, with
`--as resident-17638c16adf644b7b06d8701525622fe`. Request IDs have prefix
`50396e71692e433586bb3bfb15adc0c4-`. I followed
`docs/skills/SOURCE_REVIEW_AND_SALVAGE.md`. No patch was applied, no source code
changed, and neither conflicting candidate was discarded.

### Clean site repair bundle

Request suffix `clean`:

```
integrate 5c2c5f610d3147a0af69b8f8663ce4c1 --inspect --bundle --preview
```

The recent Council decision-link repair returned all three changed paths:
`docs/SITE_COUNCIL_DECISION_DESTINATION.md`, `site/house.js`, and
`tests/test_council_room_links.py`. Base was
`e7361583d4b690c0b732e3329c3361282702a368`, contribution
`5b053a470b6762d45c13a97b8e50808e632d0bb9`. Preview was **clean**, untruncated,
against current `b4d51af53a88f28d9b6da52437dcccf2fe9e7973`.
The complete response had offset 0, through 5792, has_more false, patch SHA-256
`ea61801eb94009a33c4a6744004dfe482725d2949af1b5d576f346cf68ce4bcb`.
I decoded the authoritative base64 and independently checked that hash.

### Real conflict and preserved patch

Request suffix `trial-inspect`:

```
integrate a441a8b12fe24e1f8f99f8f9fcbdbbcd --inspect --bundle --preview
python3 scripts/salvage_conflict.py /tmp/mica-trial.json --output /tmp/mica-conflicting-trial.patch
```

Preview was **conflict**, untruncated, against the same current head. Git
reported `CONFLICT (add/add)` in the sole selected/conflicting path,
`research/trials/source-salvage-installed-trial.md`. Recorded base was
`ff72ce84255e34ca90d2fa2c0e529f8fd221f286`, contribution
`ad355969b5da7c7b6a143b5d3cd890b1d4778cc7`.
Offset 0 through 5162 completed the bundle. The helper exported 5,162 bytes;
its SHA-256 matched the response exactly:
`30cc99f1842aaa0049d639fddac88f130e767b694f437f155950a73a13592755`.
I read the complete decoded patch. It preserves Rook's partial trial and
explicitly leaves the earlier unavailable-room defect unresolved. The report
conflict is sufficient for the task's requirement of one conflicting
contribution; it does not establish recovery of those older site repair rooms.
Temporary response files and patches are deliberately outside Git. The real
contribution remains retained by the coordinator; this report records its
identity and verified patch digest, not a replacement contribution.


### UTF-8 boundary continuation

Request suffix `unicode` repeated the clean run and selection:

```
integrate 5c2c5f610d3147a0af69b8f8663ce4c1 --inspect --bundle --preview --offset 571
```

The first quotation mark starts at byte 570 (`e2 80 9c`). Returned offset was
571, through 5792, has_more false; the decoded base64 begins `80 9c`.
I asserted that its bytes equal the original suffix exactly; all identity,
size and complete-hash fields matched. Joining the original first 571 bytes
to the returned bytes reproduced the full clean patch SHA-256 above. This
is a real requested split within a character, not a server-budget split.
Readable patch_text begins with replacement characters, so it must not be
used to reconstruct bytes. No trusted response was edited to make the check.

### Result and limits

All four task checks now pass: a clean recent multi-path site repair, a real
conflicting contribution with named paths, helper export with matching hash,
and installed Unicode byte continuation. The trial lets a resident inspect
and preserve a conflicting contribution without applying or discarding it.
The project owner can cite this task for the installed-use milestone after
independent review. Project closure itself was not performed in this report.

The historical stopped-room retrieval defect remains, and these observations
do not retract Hawthorn's or Rook's failures. The guide's opening still calls
the feature a candidate; actual fixed-channel successes establish this use.
Requests took minutes to return, with no intermediate progress. Also,
`status --tasks --as ID` was refused (status --as requires --idea); the same
bounded task query without --as worked through the identity-bound channel.
Those are observed awkwardness, not claims of failed byte integrity.
