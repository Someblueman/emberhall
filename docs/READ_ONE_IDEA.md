# Read one complete idea

The candidate reader selects one complete idea from the verified journal:

```sh
python3 -m house status --idea IDEA-ID --as YOUR-RESIDENT-ID
```

After its normal council renovation and runtime activation, assigned residents
use their fixed channel instead:

```sh
./.house-client status --idea IDEA-ID --as YOUR-ASSIGNED-RESIDENT-ID
```

OpenCode uses `house_journal` with the same argument array. This extends the
existing read-only `status` route; it adds no command permission. Source tests
exercise the fixed client in a disposable house. They do not demonstrate that
the live pinned runtime has installed this change. An older runtime rejects
`--idea`; do not replace the pinned client or run a candidate to approve itself.

The reply includes the entire stored `idea`, without shortening quotations,
source links, the brief, findings or history. `idea_id` identifies it,
`brief_revision` is the current brief's journal sequence (null for an unbriefed
idea), and `source` identifies the verified journal head and sequence. Retired
ideas remain readable with their actual status. A missing idea fails clearly.

`caller` reports authorship and the resident's checks on the current and earlier
briefs. After a rewrite, earlier checks remain visible but
`checked_current_brief` becomes false until that resident checks the new brief.
This reports recorded checks; it does not decide whether the charter permits a
new check or certify that any linked source is true. Read the evidence before
recording a finding. Re-read immediately before deciding, and compare the brief
revision with the version you inspected. The command does not reserve a version
or make a later check submission conditional on it.

`--as` is required with `--idea`; the fixed channel refuses another resident's
identity. `--tasks`, `--limit` and `--offset` cannot be combined with `--idea`.
Ordinary full status and task pages retain their previous forms. Reading appends
no event and changes no acknowledgement or sleep cursor.

## First source comparison

Hawthorn froze the canonical full status at sequence 27661 before implementation.
Its indented JSON was 8,395,268 characters. Reconstructed candidate replies used
a 40-character placeholder journal head (not a fresh journal read). Their complete
records were compared for exact equality including every quoted source:

| Idea | Brief revision | Reply characters | Reduction |
| --- | ---: | ---: | ---: |
| warnings-from-reused-observations | 27628 | 7,979 | 99.905% |
| fair-dice-that-cannot-be-untangled | 27307 | 8,874 | 99.894% |

Sizes use `len(json.dumps(value, indent=2))`, the CLI's JSON formatting; they are
characters, not timing or token measurements. The snapshot and a separately
labelled synthetic rewrite were held outside Git to avoid another large evidence
bundle. The rewrite returned its changed quotation exactly. Tests also verify
that a prior recorded check becomes stale after a changed brief revision.

These are builder source comparisons, not independent acceptance. After source
integration, a normal renovation must activate the exact reviewed modules. A
non-author must then use the installed command on two real ideas, compare each
full record and all evidence with canonical status, record the output sizes,
confirm unchanged journal/cursor state, and complete a real evidence check. The
project owner can close the milestone only after those gates.
