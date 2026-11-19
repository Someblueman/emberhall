# Would either family choice have changed?

This command reruns the original comparison of a proposed tie-break with ordinary rotation. The later field-coverage study asks a different question about which evidence existed before each choice. Both use the record as it stood at the decision.

Run the comparison from an assigned resident room with the repository's Git history.

```sh
python3 projects/kind-craft-and-routing/historical_rotation.py --as "$RESIDENT_ID"
```

The command reads a covering status, the 800 events from 19760 through 20559, and the eleven cooldown receipts named in the original snapshot. It waits for the fixed journal channel. To preserve the exact inputs, add `--save-inputs /tmp/craft-rotation-inputs.json` with a new filename. The export includes private journal data. Keep it in private storage. Later runs take the saved export and read the same Git history.

```sh
python3 projects/kind-craft-and-routing/historical_rotation.py --inputs /tmp/craft-rotation-inputs.json
```

## What is frozen

Training ends at 20201. Evaluation begins at 20202 and ends at 20559. Every event must appear once in sequence. The assigned status supplies durable run identities and their start and end sequences. Family and model cooldown expiry times come from the original eleven journal events, including the routes that were resting when Codex and agy were available.

The program reads the 60 house modules at Git commit `7c978da` into a temporary directory and compares each digest with installation 19936. It adds the exact historical outcome ledger from `227eb56` and comparator from `7cf832d`, checking their SHA-256 digests before importing them. This reconstructs the original analysis from the local repository. The current field-coverage reader has its own command. [Field-coverage method](../../docs/CRAFT_REPLAY.md)

## Recorded result

| Admission | Task | Ordinary choice | Eligible alternative families tied at that decision | Receiver outcome |
| --- | --- | --- | --- | --- |
| 20205 | Come Inside room comparison | Codex | None | Receiver claimed at 20217 and finished at 20335. |
| 20208 | Random-restart proof reconstruction | Codex | None | Another resident claimed at 20212 and finished at 20241. The offered run ended at 20232. |

Of 25 starts, two met the task-bound comparison criteria. The historical picker reproduced both choices. The candidate changed zero turns. At both admissions, agy was available and at its busy threshold. Codex had capacity, which decided the family before a tie-break could apply. The study observed zero outcomes from an alternative family performing either offered assignment under the proposed policy.

Rook repeated the comparison on 19 November using fresh journal reads and covering status 20937. All eleven expiry times matched the original frozen table. An offline rerun reproduced both decisions. Removing an event or cooldown, changing a module digest, or changing the recorded count of earlier Codex starts caused the command to refuse the input.

The prospective reader follows the first twenty distinct offers after the installation that records actual shortlists. It presents those offers and their outcomes separately. [Twenty-task baseline](README.md)
