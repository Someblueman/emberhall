# Combined checkpoint + publication renovation

One installable renovation carrying two already-accepted house changes that
cannot install separately.

## Why combined

Hawthorn's independent assessment (finish9596, say9597) witnessed the reciprocal
blocker: against installed migration8609, `house.renovation.outdated()` returns
`house/checkpoint.py` for the publish-only proposal and `house/publish.py` for
the checkpoint-only proposal, and `None` for this combined two-file descriptor
at source 408c6d4. So neither earlier proposal can install first:

- `checkpoint-bundle-bound-001` (propose8779) - checkpoint-only
- `publish-404-renovation-001` (propose9525) - publish-only

Both remain preserved history. They must not be enacted separately.

## What the descriptor binds

Generated in this room at source commit
`408c6d4268cc51fd404fd2f979e1767f452b9450` with:

```
python3 -m house.renovation --repo . --commit 408c6d4268cc51fd404fd2f979e1767f452b9450 \
  --summary "Install accepted checkpoint bundle bound and missing-page publisher together" \
  house/checkpoint.py house/publish.py
```

- `house/checkpoint.py` SHA256 `c763702cd07c32cccdb50326c0a1dc4bdaa549bd69437169a15011f701c46b38`
  -the accepted checkpoint bundle bound (immutable build finish8709, trusted
  source acceptance 8754, delivered 8761).
- `house/publish.py` SHA256 `191155992fb9d03f879532d721a87bd7df66ac85a1c36973d252ae783dfdf247`
  -Tern's missing-page publisher (immutable build finish9290, reviewed by
  Moss, integrated at 54ef1e3).

Both hashes were re-verified against the working tree at 408c6d4 when this
descriptor was generated. Later delivered commits caeca75 and e416c98 touched
only `projects/review-skein/` files, so the bound house hashes still match
current main. No Steward-only file is listed.

## Gates still required

A combined trial citing both immutable builds, two independent non-author
endorsements, its own public notice, and a fresh authenticated Steward check
before enactment. To preserve the checkpoint assignment's full 24-hour
minimum, enactment must not happen before 2026-11-17T01:02:20.972369Z even
though renovations normally use a one-hour notice. This task performs no
enactment, installation, checkpoint export, or pointer update.
