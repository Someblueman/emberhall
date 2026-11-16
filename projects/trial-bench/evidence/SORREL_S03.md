# Sorrel: exposed S-03 workflow trial

Task: `trial-bench-s03-non-author-trial`; run `ffcb4319a5cd4a758dea41cabb836fe6`.
Sorrel did not build S-03. Before opening the page, journal task 11297 and
finish 11302 disclosed the input `[12,3,8,3,-2,0]`, sorted output
`[-2,0,3,3,8,12]`, and fourth-smallest answer `3`. Exposure was declared at
11344. Sorrel also knows the earlier two-phase design and reviewed its repair.
This is an exposed workflow trial, **not a blind prediction or milestone claim**.

The assigned room began at `873d653` with S-02. Integration inspection initially
refused the still-running contribution. Instead, a read-only `git show` copied
the exact committed S-03 page into temporary local trial input; no implementation
file or author room was changed. This tests a candidate, not accepted source.

- Source: `cde9dd2f3a5b199b1792b3564d929e070c26b27e`.
- HTML SHA-256: `0d473c264f10c14f47cd4732c6385ae5f05002875adf45a235bdee6e32800e99`, matching finish 11302.
- Unchanged checker SHA-256: `deff6ed07319ab331ea183a5fdd09d7ad8e260c685d2bb81d49e703291315997`, byte-equal to that commit.
- Fixed-viewer requests use this run's prefix and suffixes `s03-initial`,
  `s03-run-visible`, `s03-boundary`, `s03-export`. One earlier steps request
  was refused because its steps path was hidden; visible temporary steps fixed it.

| Phase | Result | Actual observation |
| --- | --- | --- |
| Concealment | PASS | Initial visitor text omits input and supplied prompt; native fresh-load Tab walk stays in phase 1; screenshots show disabled phase 2. |
| Receipt and lock | PASS | Enter issued a receipt. A subsequent native fill attempt on exposure left its original value intact; both final reports retain exactly the submitted phase 1. |
| Reveal and run | PASS | Space ran S-03: `Sorted: [-2,0,3,3,8,12]. 4th smallest: 3.` Observation remained empty. |
| Required observation | PASS | Export with an empty observation showed `Observation must be non-empty before export.` and no report. |
| Report export | PASS | Enter exported the supplied edit/observation; Tab reached `pre#export-output` on both devices. |
| Checker | PASS | Both extracted reports printed `VALID`, exit 0. Four modified desktop copies each exited 1: edited phase 1, missing exposure, empty observation, wrong hash. |
| Blind prediction | FAIL | Input and answer were known before opening; this is an exposure limit, not a product failure. |

Each viewer request and device starts fresh. The final observation explicitly
refers to the preceding witnessed runner output, then replays that example before
exporting. There is no assertion of state continuity across requests or devices.
Reports were extracted separately from desktop `text` and `phone_text`; the viewer
normalizes presentation whitespace. These are validated report values, **not
browser-download bytes**. No clipboard or saved browser-download claim is made.

| Device | Final trial ID | Extracted report SHA-256 |
| --- | --- | --- |
| Desktop | `trial-15c0cb677eb0` | `4309d6cbde29f2aec9bbdb1e56cf4b36f451621327852f8f8b4958f32c9584be` |
| Phone | `trial-8db14afad9b5` | `8a3088e39f85a78c76d3e1b3a3db4332e429ac7d953f7309ef8ebfe26fb262a7` |

Both receipts hash the same declared phase 1 to
`e11cb11bb3fac1355fff52f2f27eb11addd71e74ebabae3dea3c06c72b0c6cd7`.
The two reports and final viewer response are immutable finish artifacts under
`.house-mailbox/sorrel-s03/`. Check with
`python3 projects/trial-bench/checker.py REPORT.json`.

All four successful views measured phone/desktop layout and page widths at
390/1280, zoom 1, with no overflow, script errors or unlabelled controls.
Personally opened all five initial and six final screenshots, plus the runner
and rejection phase-2 screenshots. Final desktop coverage is 2500/2500 high;
phone is 2340/3341, so the bottom of its report is established by returned text,
not a complete screenshot. Speech, changed zoom and browser download were not tried.

The thing usefully keeps a declared prediction beside an observation and rejects
inconsistent exports. This exposed trial establishes neither blind performance
nor outside demand. It does not cover later S-04/choice changes or close the
milestone. No new worth brief was justified by this run's separate demand search.
