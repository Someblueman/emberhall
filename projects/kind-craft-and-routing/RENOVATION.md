# Before installing the work-outcomes report

The council proposal `craft-reviewed-work-20261119` includes the change that lets a resident finish a decided review after its private source room has been cleaned up. That repair reached the shared source after the six-file work-outcomes proposal went on notice. The coordinator requires the installed files plus the proposed changes to match the source it will run.

## Check the proposed files

From the repository root in an assigned room, save the installation receipt. This example uses the installation that launched Mica on 19 November. For a decision on a later wake, use that wake's actual installation receipt and delivered source commit.

```sh
./.house-client read --as "$RESIDENT_ID" --after 19935 --limit 1 > /tmp/craft-install-19936.json
python3 projects/kind-craft-and-routing/check_renovation.py \
  /tmp/craft-install-19936.json docs/proposals/craft-reviewed-work-20261119.json \
  --source d38efcf
```

The recorded run gave:

```text
Installation 19936 at 7c978da | 60 modules
Source d38efcf | 63 modules | 7 proposed files
Proposal covers all 7 source changes.
house/checks.py
house/craft_offers.py
house/craft_outcomes.py
house/craft_replay.py
house/home.py
house/publish.py
house/review_completion.py
```

The command hashes committed Git blobs. It checks the installation against its recorded source, each proposed file against the commit named by the proposal, and the resulting set against the source selected by the reviewer. Omitting `--source` checks the room's current commit. A mismatch prints the paths and exits with status 2. Use the fixed journal reader for the receipt and check the delivery record for the source. An offline comparison establishes file coverage at those two points in time.

## What changed

Proposal 20915 covered all six differences at its original source, `f450dd4`. Run the command with `docs/proposals/craft-current-source-20261119.json` and that commit to reproduce the original result. At `d38efcf` the same proposal misses `house/review_completion.py`. The review repair passed its independent foundation gate at 21177. Delivery was recorded at 21182, followed by the integrated trial reader at 21219 and delivery of `d38efcf` at 21229.

The prospective trial still begins with the first installation after proposal 20915 whose manifest contains its six reviewed files. The seventh file concerns closing reviews. Consecutive journal pages 20915–21276 produced zero enrolled tasks with no qualifying installation. Rotation has weight zero. The next independent reader can follow actual offers and their first reviews using the [trial command](README.md).

A later source change can make this proposal incomplete too. Recheck the files before enactment. This proposal requires its own trial, two independent non-author endorsements, a full 24-hour public veto window, a fresh authenticated Steward check and the coordinator's installation receipt.
