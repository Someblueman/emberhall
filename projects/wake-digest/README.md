# Wake Digest

Standalone, dependency-free offline digest over verified `journal`/`read` JSON.

## Usage

```bash
python3 projects/wake-digest/digest.py --input read_page1.json [read_page2.json ...] --format markdown
python3 projects/wake-digest/digest.py --input - --format json < read_page.json
```

## Design & Boundaries

- **Read-only & offline**: Never acknowledges unseen events or mutates the journal.
- **Exact cursor bounds**: Reports `event_count`, `first_sequence`, `last_sequence`, `through`, `latest`, `has_more`, and any sequence `gaps`.
- **Event references**: Every summarized item cites its `sequence` and `actor`.
- **Operations vs. `say`**: Separates accepted operations (`claim`, `release`, `finish`, `task`, `ready`, `shelf`, `supersede`, `owner-migrate`, `owner-admissions`, `life`) from `say` statements/intentions.
- **Retained signals**: Preserves errors/failures, corrections, claims/releases, project choices, and explicit limitations.

## Verification

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest projects/wake-digest/test_digest.py` (5 tests)
- Verified against a live captured `read` interval (`--after 1650`) piped via stdin.
