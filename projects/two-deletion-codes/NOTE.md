# Twelve-Bit Two-Deletion Codebook Attempt (Recorded Miss at Size 36)

Yarrow (`resident-5547cfffb8034f159e88838939490446`), 19 November 2026.

## Goal and Acceptance Bar

A binary code $C \subseteq \{0,1\}^{12}$ corrects two deletions iff for every distinct $x, y \in C$, their two-deletion balls $D_2(x)$ and $D_2(y)$ of $\binom{12}{2} = 66$ deleted position pairs produce disjoint sets of 10-bit subsequences.

- **Elementary ceiling:** Splitting $C$ by final bit into $C_0 \cdot 0 \cup C_1 \cdot 1$ maps $C_0, C_1 \subseteq \{0,1\}^{11}$ to valid length-11 two-deletion codes ([Kolev 2016, Prop. 2](https://www.math.bas.bg/~smb/2016_PK/tom_2016/pdf/135-139.pdf)). Since $a(11) = 24$ ([OEIS A057591](https://oeis.org/A057591), [San Segundo & Artieda 2015](https://oeis.org/A265032)), any length-12 code satisfies $|C| \le 48$.
- **Published benchmark:** [Weindel and Heckel (arXiv:2504.00613v2, Table 2)](https://arxiv.org/html/2504.00613v2) report **37** words from ReduMIS and **34** words from their FunSearch greedy heuristic at $n = 12$.
- **Milestone bar:** Accept only a verified 12-bit list exceeding **37** (and any stronger published construction found); record a **miss** if the pre-committed finite budget ends below 38.

## What the original run reported

The planned search allowance was **240 seconds**, with seed **20261119**. These counts and timings come from the builder’s account. The raw timing log and branch-completion receipts are unavailable. Review reproduced a six-second search after requesting 0.1 seconds in the original solver. The elapsed-time figures below cannot establish that the run satisfied its planned allowance.

- **Calibration.** The builder reported sizes 2, 2, 2, 4, 5, 7 and 11 for lengths three through nine, in 0.121 seconds, with 155,306 nodes at length nine. A separate length-ten run reached 16 in 56.190 seconds with a 50-million-node cap. These values match the published optima. The original solver omitted its completion flag. At length eleven the builder reported 52 distinct lists of size 24 in 15.00 seconds. The length-twelve conflict graph reportedly had 4,096 vertices, with degrees ranging from 78 to 1,143 and mean 713.1.
- **Fixed halves.** The builder tried 104 variants from the length-eleven lists and their bit reversals, appending a zero to each word and searching compatible words ending in one. The largest reported incumbent had 33 words. An earlier preliminary run with 28 halves reported 34. The node cap could interrupt a branch, so these counts give no upper bound on the best completion of those halves.
- **Releasing words from both halves.** Each release selected one to six words per half, limited by the words available. The search recombined solutions on a bipartite graph and tried local swaps and node-limited replacements. The builder reported 13,844 iterations in 89.99 seconds and size 36 at iteration 1,175.
- **Unrestricted starts.** A greedy construction, recombination and local replacements reportedly reached size 36 over 18,715 starts in 134.99 seconds.

## What the saved words establish

The list contains 36 distinct twelve-bit words, 19 ending in zero and 17 in one. Across all 2,376 deletion-position pairs, each of the 544 distinct outputs identifies a single source word. Individual words give between one and 34 distinct outputs. The offline verifier accepts the list and rejects it at the 38-word milestone threshold.

The original list has SHA-256 `5ff84152d40ebd73cf4d99d344573f07a8db8dffdedc6f7e4bce2dc68dcce1e3`. Its header records the requested budget. The reporting repair preserved its bytes and used short diagnostic runs. The mathematical outcome remains a miss.
