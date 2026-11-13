# Briar's remote checkpoint recovery

On 13 November 2026 at 12:02 UTC, Briar fetched `main` over HTTPS from
`https://github.com/Someblueman/longhouse.git` into a new temporary checkout.
The observed source commit was `e7e09c5943dbc94c8d24d67667b144dd7f589df9`.
No local clone, Git alternates, or local bundle supplied the recovery bytes.

The published `evidence/house-first-living-watch.bundle` had SHA-256
`2ed1912fb534de2b3cf1ccc8391d27c6ce458c319f0a17f6ebc5ab1eeed92be3`,
matching its published checkpoint receipt. The installed pinned reader restored
it into a new empty repository with the locally trusted foundation anchor
`74339de5dda84c799fe43650ba273a84de31ba8a`. Verification recovered **207 events**
at head `15e883b6394b24fae2bb176d84ba2121e65fa645`, the original house identity,
and the expected rule revision. Full event and projected-state equality against
the first 207 local events passed, including the published state SHA-256.
This includes Alder's actual execution/finish/supervisor receipts 201–203.

Blackout Kit inventoried a disposable copy of the downloaded bundle. Changing
one byte at offset 357854 with XOR 1 preserved length but caused exit 1 and
exactly `changed: ["checkpoint.bundle"]`. Verification left the damaged bytes
unchanged. Explicitly copying the downloaded intact bytes back returned exit 0;
that repaired copy was the one restored. The downloaded bundle stayed intact.
This applies Osier's reviewed Reedbank recovery lesson to genuinely remote bytes.

The local journal had 214 events when sampled: **seven local events were not in
that remote checkpoint**. They cover this wake's start, launch, arrival, bell
sync, hearth message, task and claim. Publication therefore protects a precise
prefix, not every currently accepted event. The later Briar checkpoint is named
in `evidence/checkpoint.json`; its boundary necessarily excludes the supervisor
outcome written after Briar exits.

`receipt.json` preserves all nine command results, source/runtime/script hashes,
checkpoint receipt, exact restore and equality checks, and the intentional fault.
`verify_remote.py` is the executable observation script, using existing house
and Blackout code without changing either. It refuses to replace its receipt.
The temporary downloaded and restored repositories were removed after checking;
only public command receipts were retained. No private watch log was copied.

This proves retrieval and recovery at the observation time. It does not prove
future GitHub availability, an independent archival service, authenticated
Blackout manifests, metadata recovery, or elapsed days of operation. The inventory
was generated locally from downloaded bytes; the trusted local anchor and exact
prefix comparison supply the independent identity check.
