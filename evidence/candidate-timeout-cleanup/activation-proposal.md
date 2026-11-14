# Proposed one-use activation scope: approval pending

This is a reviewable proposal, not active authority.

Purpose: install the exact independently reviewed timeout cleanup repair after
the prepared runtime passes its isolated acceptance suite. The existing native
sandbox profile, web safeguards, credentials, provider routes, charter, wake
policy and ratification process must stay unchanged.

Add scope candidate-timeout-cleanup-20261114 to house/maintenance.py, bound to
the existing full owner objective SHA256
ecc055f87751fe3dbab42c5b143736de025c57b88e9b741d94b18146fbef5eb8.

Its allowed protected-source changes would be exactly:
- house/test_sandbox.py: the reviewed process cleanup repair.
- house/maintenance.py: this one-use scope metadata.

Do not include house/owner_upgrade.py in the allowed set. It needs no change.
Add a refusal regression in tests/test_owner_maintenance.py: reject provider,
mailbox worker, wake policy and owner-upgrader changes; preserve all governance
state; reject reusing the scope after its first migration.

Use the existing authenticated owner-upgrade prepare/apply path, with the
approved objective bytes, reviewed source commit and actual passing isolated
tests. Drain native residents naturally, stop the sole coordinator, apply the
single migration, replace only the installed archive arguments, resume admission
and verify an actual later native action. No native runtime self-approval.

Blast radius: this adds a new permitted protected-file migration. It changes
the worker cleanup implementation; a defect could interrupt integration or leave
processes behind. It is one-use under the existing journal gate and does not
permit changes to other protected source. This is why approval review required
explicit owner approval despite the broader maintenance goal.
