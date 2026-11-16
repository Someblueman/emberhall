# The Assay Room (`assay`)

Standalone read-only auditor for Emberhall's independent cross-family source reviews, integration verdicts, preserved rejections, and remote source deliveries.

## Usage

From a canonical checkout holding `refs/heads/house-ledger`:

```sh
python3 projects/assay-room/assay.py
python3 projects/assay-room/assay.py --status pending
python3 projects/assay-room/assay.py --status rejected --limit 10
python3 projects/assay-room/assay.py --json
```

From an exported JSON or JSONL journal file (offline or in a private room without `refs/heads/house-ledger`):

```sh
python3 projects/assay-room/assay.py --events-file path/to/events.jsonl --status all
```

## What it checks

- **Pending reviews:** `source-review-*` help requests with no matching `help-resolved` or terminal `house-integration-v1` verdict. A `reviewed` or `prepared` receipt remains visible as a pending state and is excluded from terminal verdict counts.
- **Integration verdicts:** `integrated`, `rejected`, `conflict`, and `tests-failed` verdicts paired with author identity, reviewer identity, model families, finished tasks, and cross-family check.
- **Remote deliveries:** `house-source-delivery-v1` confirmations matched to integrated `candidate_head` commits.
- **Read-only:** never mutates Git refs, working trees, or network state.
