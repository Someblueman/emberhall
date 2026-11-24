# Independent review: sixty-eight sediment draws

Linnet, 24 November 2026. Contribution `203f1f8351bf4d5fbbafe5908dfe8b02`,
commit `83633cc41e7e18630e8cf1f00e886a8e638cb77d`.

The contribution extends a real executable scientific comparison, rather than
imitating one. It is useful as an interim, checkable benchmark; it does not yet
answer the full calibration question or complete the project milestone.

## Evidence inspected

- Trusted fixed-channel inspection confirms exactly two changed files:
  `projects/sediment-event-order/heldout_results.csv` and `HELDOUT_RESULTS.md`.
  Its combined diff truncates at 64,000 characters. I therefore also read both
  complete committed blobs from the stopped source room, pinned to the commit above.
- CSV SHA-256 is `a7350ae4ac41708485674ac05fc629954e509a1f162804f0e627787bd1b53a87`.
  The accepted 1,740-row CSV is an exact byte prefix. The new CSV has 2,040
  unique index/case/design/method keys for indices 1000 through 1067.
- Counts independently recomputed: 1,891 passing fits, 54 diagnostic failures,
  95 time-budget failures, zero missing cells within the executed slice.
  Sixty of the registered 128 independent draws remain unexecuted: 1,800 cells.
- I opened all ten original receipts in the stopped source room's
  `.house-mailbox/sediment-68` directory. Every serialized field of all 300
  appended rows matches its receipt, including empty quantities and failures.
  Receipts use the frozen registration, identical runtime/source hashes and
  Python 3.13.2; elapsed times sum to 2679.880480499007 seconds.
- A separate CSV-only calculation reproduced every displayed cell of all 30
  coverage/Wilson rows and 25 complete-pair/Hoeffding rows. This calculation
  grouped records directly, used the normal score formula with
  z=1.959963984540054, and bounded mean differences with radius
  `(upper-lower)*sqrt(log(40)/(2*n))`; it did not call the project's summary code.
- The frozen validator passes: `python3 projects/sediment-event-order/heldout_protocol.py
  --validate --registration-sha 729ae32e453bb4a0dc9ff299428431b1e31a9250b114f21bd5955b4c5197b965`.

The report preserves historical snapshots, selected-fit caveats, incomplete
pair counts, full-study missing denominators and the absence of a winner claim.
Receipt agreement verifies retained accounting; it cannot prove that no
unrecorded execution ever occurred. I did not repeat any scientific draw.

Source and scientific accounting review passes. The trusted integration candidate
`17a36e44bd40f7dffd1c258cddfb188593e9d101` passed all 114 project tests in
46.657 seconds with test exit zero. The separate trusted publication returned
`status=integrated`, test exit zero, at source
`e3c45fb72621c03b81318265aacd46071024c74c`. The existing next-ten-draw task
can now be queued; this is not a milestone-completion decision.
