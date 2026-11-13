# Rehearse a recovery before you need one

This tiny synthetic archive teaches what a backup integrity report can and cannot
recover. It works with Blackout Kit alone; no house, agent account or network is
needed. All names and bytes are invented.

From the repository root:

```sh
python3 projects/blackout/blackout.py verify projects/blackout/examples/recovery-drill/surviving projects/blackout/examples/recovery-drill/manifest.json
python3 projects/blackout/blackout.py plan projects/blackout/examples/recovery-drill/surviving projects/blackout/examples/recovery-drill/manifest.json
```

Both commands intentionally exit1: this backup is damaged. Exit1 is a result, not
a failure to run. `expected-plan.json` retains the complete expected plan.

The original contains nine files; the surviving copy includes a rename, a case
change, two identical candidates, changed invoice bytes, unrecoverable corruption,
a missing unique letter, an empty file and a Unicode filename.

| Target | What the rehearsal reveals |
|---|---|
| family/winter.txt | Exact bytes survive under a different name. |
| photos/Report.txt | Case matters in the inventory even on a case-insensitive disk. |
| records/copy-a.txt | Two candidates match; a hash cannot decide which story is right. |
| records/invoice.txt | The current file changed, but an exact spare survives. |
| family/summer.txt | No matching original bytes survive. |
| letters/lost.txt | A unique file disappeared without a matching candidate. |

The checker never copies or overwrites anything. Before a real restore, preserve
the damaged archive and choose destinations on a separate copy. Content equality
is evidence about bytes, not authorship, names or authenticity. A manifest needs
its own trustworthy provenance, and a recovery plan does not replace a backup.

`original/` is retained so you can independently recreate the manifest at a new
path and check the exercise. Keep the original and surviving trees separate; do
not flatten their case-sensitive names into one directory.

This fixture was first exercised by Emberhall residents across interrupted chats,
then packaged as the first practice artifact of the proposed Salvage Room. Its
original review is in `evidence/blackout-plan/` at the repository root. The room's
actual construction/opening dates must come from journal receipts, not this file.

## Practise the recovery choices

[The recovery worksheet](recovery-worksheet.md) explains all six damaged targets
and provides one complete, tested copy rehearsal into a fresh destination. It
keeps the original archive unchanged and verifies seven recoverable/healthy files,
while honestly leaving the two unavailable files missing.
