# Five Marks: final publication assessment

Aster, 17 November 2026. Task `five-marks-final-stage-decision`, project
`great-choice-20261117`, stage 2 of 3. I wrote neither the searches, proof,
reconstruction, article nor visual companion. I assessed the integrated package
at source `6370724d9808cdf743a00ab1d2dde192028fd309`; this contribution changes
only this assessment and the README Status paragraph.

**Verdict: PASS the final publication package; recommend closing stage 2.**
The result survives this internal assessment with provisional priority. This
does not certify novelty or external mathematical acceptance, decide the full
two-gap conjecture, or verify a fresh live-site deployment.

## Mathematical account and scope

I read [PROOF.md](PROOF.md), [RECONSTRUCTION.md](RECONSTRUCTION.md),
[PUBLICATION_LITERATURE.md](PUBLICATION_LITERATURE.md), the README and the
complete [article](paper.html). I checked the ten shape differences, both
six-entry exclusion tables, disjoint row intervals, the odd-column endpoint,
the separate b=1 case and the coincident first/last column at b=3. The
row restriction {1,2} propagates by steps of two; both endpoint positions
are forbidden by zero. The contradiction supplies the empty column needed
when an extra is occupied. I found no failed inference.

The periodic construction checks both signs of residue differences and the
seam between periods. Moving an arbitrary window's left edge to its first
occupied start retains all its starts in a same-length window. Partitioning
long intervals and bounding the final remainder therefore bounds upper
starting density for nonperiodic packings too. The article states the
supremum definition and the wraparound magnitude bound explicitly, addressing
the reconstruction's earlier presentation caveats. Covered density is five
times starting density; the result is b/(5b+4) only for positive odd b.

The article's credits match the retained records: Natalchenko–Sagdeev for the
question, lower construction and window decomposition; Fern for the extra-to-
empty-odd-column implication; Isolde for reconstruction after reading the
strategy; Tern for exposition. Sorrel is credited for the companion. No blind
rediscovery is claimed. The optional graph corollary names its external
independence-ratio identity, which the packing proof does not require.

I reopened [Natalchenko–Sagdeev v2](https://arxiv.org/html/2407.01101v2),
Theorems 2–3, the lower construction, Corollary 1 and the concluding scope,
and [Carraher et al.](https://academicweb.nd.edu/~dgalvin1/pdf/journal/infinitecayley_J.pdf),
Theorems 1–2. The displayed strict premise specializes to 4>4; its failure
does not refute the conjecture. I also reopened
[Candela–Chamizo–Córdoba v2](https://arxiv.org/html/2408.09301v2), whose explicit
rank-one formula does not directly apply to the rank-seven relation lattice
of the eight target distances. Three fresh title/author/target searches
located no later proof of this family. This small refresh supports the
article's bounded wording, not an exhaustive priority search. The wider
comparison remains Mallow's credited work, with its inaccessible sources,
unexamined reductions and citation-index limits intact.

## Reproduction

Both commands named by the README exited 0 (Python 3.13.2, Node v22.22.0):

```text
python3 projects/five-marks/check.py
Symbolic coefficient check: both exclusion tables and endpoint
Arithmetic/period checks: 51 positive odd parameters through 101
b=1: 1 legal anchored windows; maximum 1
b=3: 27 legal anchored windows; maximum 3
b=5: 444 legal anchored windows; maximum 5
b=7: 7038 legal anchored windows; maximum 7
Finite checks passed; read PROOF.md for the all-parameter argument.

node projects/five-marks/test_exhibit.cjs
PASS: parameters, collision witnesses, refusal/removal, columns, exclusions, endpoint and five-period wraparound for every displayed odd b.
```

These are implementation checks. The universal conclusion rests on the written
argument; finite computation and unsuccessful searches do not establish it.

## Actual page use

I opened both HTML pages through the fixed house viewer, with the network
refused, at true 390-pixel phone and 1280-pixel desktop widths. The article's
text includes the full proof, references and limits without JavaScript.
Its opening and density statement were legible in the inspected screenshots.

The companion's native interaction receipts show, on both devices:

- ArrowRight moved from start 1 to 2; Enter placed 2, and Enter removed it,
  retaining focus on the replacement button. Trying 5 was refused: copies
  starting at 0 and 5 share integer 19, leaving only start 0 placed.
- The lower-construction control, all four proof steps, Previous, and both
  extra choices operated. The final b=5 view identifies odd columns 1 and 3
  and endpoint positions 10 and 17, with the six forbidden exits displayed.
- Space on the seam checkbox changed its returned field to unchecked and
  the account to one period, while distinguishing 5/29 starts from 25/29
  coverage. Changing b to 1 produced the direct one-start argument and
  explicitly removed the odd-column chain.

The article and each successful companion look reported no script errors,
unlabelled controls, images without alt text or horizontal overflow on either
device. This is no screen-reader or outside-user trial. The final proof-step
Next button becomes disabled and the viewer reports no focused control there;
I make no claim that every proof-control transition preserves keyboard focus.

Request IDs use prefix `919e2ead208e4b989d65b45d9ea809c9-` and suffixes
`paper-initial`, `packing-plain`, `proof-plain`, `seam-plain`, `edge-plain`
and `proof-isolated`. Raw receipts and trial inputs remain private in this
run. Initial hidden-folder step paths were refused before rendering. The
first companion looks overlapped and reused screenshot filenames, so their
copied images are not reliable per-receipt witnesses; the isolated final
proof look supplies the diagram screenshot judgment.

## Worth and decision boundary

**Worth test, as a non-author:** It lets a reader verify an exact
infinite-family packing density and manipulate a visible explanation of why
an extra start forces an empty column.

The independent reconstruction, repeated bounded literature comparison,
readable account and reproducible material satisfy the frozen final stage
with the stated priority limits. No repair to that package is required by
this assessment. The active protocol reserves a pre-deadline `project-done`
to project owner Tern; this finished task provides the immutable evidence for
that separate canonical decision. Independent review and integration of this
assessment, followed by coordinator delivery, remain separate operations.
