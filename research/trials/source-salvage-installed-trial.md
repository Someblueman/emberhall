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
