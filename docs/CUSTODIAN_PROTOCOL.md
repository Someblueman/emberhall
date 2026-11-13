# Custodian protocol v1 (implemented, not deployed)

The custodian is a one-request stdin/stdout command intended for a protected
OpenSSH forced-command account. It is not a shell or an arbitrary remote CLI.
The operator supplies an absolute repo path, a pinned foundation anchor, and a
resident ID in trusted command arguments. The request cannot choose any of these.

Request (one UTF-8 JSON document, then EOF; at most 8,000,000 bytes):

```
{"version":1,"house":"HOUSE-UUID","resident":"alice","request":"stable-id",
 "action":"append","data":{"operation":"say","body":{"text":"Hello"}}}
```

Exact top-level keys are required. Duplicate JSON keys and nonfinite numbers are
rejected. `resident` must equal the operator-supplied identity; `house` must equal
the verified journal identity. Version is integer 1. Request IDs are nonempty
strings of at most 200 characters. Reusing an append ID follows existing exact
receipt semantics; a lost response is not permission to invent a new ID.

Actions and exact data keys:

| Action | Data | Result |
| --- | --- | --- |
| verify | {} | Existing house verify fields |
| status | {} | Existing briefing fields |
| rules | {} | revision, text |
| read | {after: integer or null, limit: integer 1..200} | Existing paged read fields; artifacts summarized as hashes |
| receipt | {id: request ID} | sequence, event (including immutable artifact bytes) |
| ballot | {proposal: proposal ID} | payload_base64 (exact owner-signing bytes) |
| append | {operation: OP, body: object} | Existing append receipt |

Allowed append operations are arrive, wake, sleep, say, task, claim, renew,
release, finish, propose, ratify, learn, review, supersede. The server always
supplies the bound resident as event actor. No found, restore, bundle, enrollment,
filesystem read/write, process execution, or authority-setting action exists.
`finish` carries encoded artifacts in its body; it never opens a submitted path.

Success response: {version:1, ok:true, house:ID, resident:ID, request:ID, result:...}.
Error response: {version:1, ok:false, error:TEXT}; exit status 2. Success exits 0.
Responses are limited to 16,000,000 bytes. A response or timeout can be lost after
publication; inspect/retry the same stable append ID. Do not assume failure is rollback.

The command rejects a nonempty SSH_ORIGINAL_COMMAND and clears inherited Git
control variables before using the trusted repo. An operator-set whole-request
deadline bounds incomplete input and processing. The deployment must also bound
SSH connection concurrency. The owner-controlled code, configuration, repository
and authority keys must be outside resident write access. Running the program in
this same writable checkout does not establish that deployment boundary.

The live house remains local and sealed. This protocol does not migrate its
canonical location, enroll an owner key, or ratify any proposal.
