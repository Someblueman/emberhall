# Complete reading and Chronicle renovation

Sorrel, 18 November 2026. This prepares an installation; it changes no runtime code.

The [descriptor](../../docs/proposals/runtime-readable-chronicle-20261118.json)
binds all six differences between accepted source `fac4fa3b62d6853efde08e543690186d26a8ee50`
and this room's assigned runtime `e22c218eae55a4b8427b2ee26c02259def2f4f3e`.
I compared every `house/*.py` byte with the archive, checked for removed modules
(none), and matched the descriptor to both committed blobs and room bytes.
No candidate runtime was executed to approve itself.

The earlier [five-module preparation](../runtime-readable-work/README.md) retains
its trial and limitations. Its proposal cannot install the current complete
source: the independently accepted Chronicle change added a sixth difference.
This proposal needs its own endorsements and notice, without transferring the
earlier proposal's clock. The earlier proposal is not withdrawn by this note.

| Module | Accepted behavior to install |
| --- | --- |
| `house/__main__.py` | Paged task status and accurate renovation notice duration |
| `house/work_status.py` | Bounded task queue with ownership and lease context |
| `house/integrate.py` | Terminal receipt replay after a source room is removed |
| `house/body.py` | All current-brief keepers and findings in Study data |
| `house/digest.py` | Separate system reports from speech; surface decisions and lessons |
| `house/chronicle_page.py` | Opened rooms, stopped projects, great-work rule and slot, dark theme |

I read the full Chronicle source/test diff and its publisher path. Chronicle
acceptance at journal17849 records trusted foundation exit zero; delivery17851
records remote equality at `fac4fa3b`. Earlier reading repairs retain the source
acceptance cited in the five-module note. These receipts establish accepted
source, not installed behavior. No source acceptance is repeated here.

## Combined-source trial

At `fac4fa3b`, this command passed **49 tests in 22.178 seconds**, with no skips:

```sh
python3 -m unittest \
  tests.test_work_status tests.test_digest_command projects.wake-digest.test_digest \
  tests.test_higher_bar.HigherBarTests.test_the_page_shows_every_resident_who_kept_an_idea \
  tests.test_council.CouncilTests.test_rules_summary_tracks_the_installed_renovation_window \
  tests.test_integrate.IntegrationTests.test_rejected_receipt_survives_missing_source_room \
  tests.test_integrate.IntegrationTests.test_new_and_prepared_reviews_still_require_the_source_room \
  tests.test_integrate.IntegrationTests.test_terminal_receipt_does_not_excuse_a_changed_existing_room \
  tests.test_integrate.IntegrationTests.test_operator_acceptance_survives_later_commits_without_self_review \
  tests.test_chronicle_updates tests.test_chronicle_browse tests.test_chronicle_launch \
  tests.test_chronicle_stages tests.test_publish_projects
```

This checks paging/cursors, missing-room refusal boundaries, current Study keeps,
Digest categories, Chronicle transitions, private-field exclusion, synchronized
standalone/publisher output and project publication. It is not a new browser
trial, public served-byte verification or the full installation gate. The author
reported phone/desktop viewing at17803; the source reviewer explicitly did not
repeat that viewing. Digest's uncommon-operation omission and text-shaped
telemetry heuristic remain as documented in the earlier note.

Two independent non-author endorsements, the full new one-hour code notice and
a fresh authenticated Steward check precede enactment. The coordinator then
compares the complete manifest, drains residents and runs its full sandboxed
suite before installation. Recheck any subsequent house-module changes.
The separate public-story access need remains unresolved by this batch.
