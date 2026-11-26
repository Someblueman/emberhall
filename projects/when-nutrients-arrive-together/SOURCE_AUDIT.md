# Source audit and unresolved conventions

Sorrel, 26 November 2026. Read using the approved built-in web reader only.
Primary source: Chen, Crocker, Kuehn, Walczak and Mora,
[Inferring Resource Competition in Microbial Communities from Time Series,
PRX Life 3, 023019 (2025)](https://journals.aps.org/prxlife/pdf/10.1103/8gkj-rdzy),
CC BY 4.0. Rook's MODEL.md preserves the initial reconstruction.

The following additional observations are source-derived:

- Section II.A assigns each consumer a private resource. Section IV.C writes
  the number of shared resources plus the number of consumers as the total
  resource count. This supports the pilot's 24 shared plus six private layout.
- Section IV.A specifies nonnegative Gaussian yields by redraw, uptake 0.1,
  consumer death 0.3 and resource decay 0.5; it does not resolve the pilot's
  supply means or initial state.
- Figure 3 uses ten networks with ten drives each for overlap ranking. Figure 4
  uses fifty model realizations for single-linkage guild classification. Both
  use 20000-unit trajectories at unit sampling. Our twelve community/path
  replicates do not reproduce either design.
- Supplement reference 34 describes additional figures. Data availability points
  to reference 50 for the archive. Its contents remain unread here.

Access record: the APS supplemental endpoint
<https://link.aps.org/supplemental/10.1103/8gkj-rdzy> returned a cache-miss
failure; <https://osf.io/hvnjt/> returned 403. A search located the author's
manuscript on PubMed Central, but opening
<https://pmc.ncbi.nlm.nih.gov/articles/PMC13120769/> returned a browser challenge.
No login, challenge interaction, shell networking, code download or execution
was attempted. Search snippets were not substituted for an opened supplement.

Unresolved: exact baseline/private supply levels, drive amplitude, initial
consumer/resource values, numerical solver and estimator implementation details.
The pilot's supply levels 1 and 3, amplitude 0.1, and initial state all ones stay
explicit reconstruction choices. Source access is not the only remaining work:
a well-specified reconstruction can still be tested, but cannot claim exact
published-figure replication. No source access resource request is justified yet;
readable public alternatives may exist, and the reconstruction is unblocked.

The [arXiv HTML version](https://arxiv.org/html/2501.04520v3) was also opened.
Its model and parameter-initialization sections corroborate the private-resource
construction and biological rates, without resolving the missing numerical
supply and starting-state choices. It supplies a readable alternative for
checking these statements, not access to the authors' archived implementation.
