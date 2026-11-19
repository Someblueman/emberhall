# Twelve-Bit Two-Deletion Codebooks (`projects/two-deletion-codes/`)

A zero-dependency offline verifier and a standalone Rust bitset solver attempting to find a binary two-deletion-correcting codebook of length 12 exceeding the published benchmark of 37 words ([Weindel & Heckel, Table 2](https://arxiv.org/html/2504.00613v2)).

**Recorded miss.** The saved list contains 36 valid words. The milestone needed at least 38. Deleting any two positions gives 544 distinct ten-bit outputs across the list, and each output identifies exactly one original word.

Yarrow specified 240 seconds and seed `20261119`. Independent review found that the original solver excluded calibration from its clock, could grant itself extra time, and omitted completion status for node-limited searches. The original run's elapsed time and fixed-half optimality claims therefore remain unverified. The saved codebook and its threshold can both be checked directly. [Mathematical note and historical run counts](NOTE.md).

## Verify the codebook offline

From the root of a repository clone (Python 3.10+, no third-party packages):

```sh
python3 projects/two-deletion-codes/verify.py projects/two-deletion-codes/codebook_12.txt --length 12
```

Recorded output:

```text
PASS: 36 words of length 12 (split 0:19, 1:17); 66 deletion pairs/word; 544 distinct 10-bit outputs (ball sizes 1..34).
```

To enforce the milestone >37 acceptance threshold (`--min-size 38`, exits 1 on this recorded miss):

```sh
python3 projects/two-deletion-codes/verify.py projects/two-deletion-codes/codebook_12.txt --length 12 --min-size 38
```

## Run the tests

```sh
python3 -m unittest discover -s projects/two-deletion-codes -p "test_*.py" -v
```

## Run the corrected solver

The solver uses `rustc` and the standard library. Give a new search its own output path. A seed fixes random choices, but elapsed-time stopping also depends on the machine.

```sh
rustc -O projects/two-deletion-codes/search.rs -o /tmp/two_del_search
/tmp/two_del_search --budget-secs 240 --seed 20261119 --max-exact-n 9 --out /tmp/two-deletion-search-output.txt
```

One deadline covers small-graph calibration, the length-eleven seed search and all three length-twelve phases. Cancellation is cooperative. Graph construction, individual bounded scans, result verification and file writing can finish after the deadline. A zero budget starts no search. If the solver reaches the deadline before finding any length-twelve words, it leaves the output path untouched. A calibration or fixed-half search earns an exact result only after its branch-and-bound traversal completes.
