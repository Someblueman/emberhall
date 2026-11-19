# Three people can fairly share a path of ten chores

Let $M=\{1,\ldots,m\}$ be a path, with consecutive chores incompatible in one bundle. Each of three people has a real-valued cost function on subsets of $M$. Costs may differ across people and may include interactions of any order. The only assumption is monotonicity under inclusion.

**Theorem.** For every $0\le m\le 10$, there is a complete feasible partition $A_1,A_2,A_3$ such that, for each ordered pair of people $i,j$, some $C\subseteq A_i$ with $|C|\le 1$ satisfies

$$
c_i(A_i\setminus C)\le c_i(A_j).
$$

The comparison uses person $i$'s cost on both sides. The deletion is hypothetical. All chores remain allocated. The formulation includes zero costs and empty bundles.

## The finite complex

First take $m=10$. A vertex is a word of ten letters from $\{0,1,2\}$ whose adjacent letters differ. The positions carrying letter $r$ form the independent bundle $P_r$. Conversely, every ordered complete feasible partition gives exactly one such word. The first chore has three possible labels and each subsequent chore has two, giving $3\cdot2^9=1{,}536$ vertices.

Connect two distinct vertices $P,Q$ precisely when both $|P_r\setminus Q_r|\le1$ and $|Q_r\setminus P_r|\le1$ for each of the three labels. Fill each clique by a simplex. Within a simplex every pair satisfies these same inequalities, which gives the 1-closeness needed below. Simultaneously replacing all labels $r$ by $r+1\bmod 3$ preserves the conflict constraint and the six inequalities. It therefore permutes vertices, edges and simplices. This is the required cyclic action.

The checker enumerates legal words in lexicographic order and compares every unordered pair. For each bundle its bit mask has a one in precisely its positions. The number of set bits in the first mask with the second mask removed is the directed difference size. It enumerates a triangle once by taking an edge $u<v$ and a common neighbor $w>v$. The resulting graph has 20,616 edges and its flag complex has 53,004 triangles.

## Why the certificate proves simple connectivity

Choose a spanning tree $T$ with a fixed root. A directed edge $u\to v$ represents the based loop from the root along $T$ to $u$, across the edge, then back from $v$ along $T$. Tree edges give identity loops, and traversing an edge backwards gives the inverse. The $20{,}616-1{,}536+1=19{,}081$ non-tree edges generate the fundamental group of the graph. Attaching the triangles imposes their oriented boundary relations. Cells of dimension three and above preserve the fundamental group. [Hatcher, *Algebraic Topology*, Propositions 1A.2 and 1.26](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf)

Only one deduction is needed. Traverse a triangle $u\to v\to w\to u$. The ordered product of its three directed edge loops equals the identity because the triangle fills the walk. If two letters already represent the identity, the third does too, in either orientation. This argument holds in every group.

The certificate starts with 1,535 tree edges. The verifier checks that they connect all 1,536 vertices, which with that edge count makes them a tree. Each subsequent line gives three signed edge numbers. The verifier reconstructs their endpoints and checks that they form a directed triangular circuit. In a simple graph such a circuit uses three distinct vertices. Since the complex fills every clique, this circuit bounds a triangle. The verifier then requires exactly one letter still unproved. For example, the first line is $(1,13,-2)$. It traverses vertices $0\to1\to2\to0$. Tree edges 1 and 2 give the identity, so edge 13 gives the identity too.

Induction over the 19,081 checked lines proves every non-tree generator trivial. The tree proves connectivity. The fundamental group presentation therefore proves simple connectivity. The argument uses ordered words in the fundamental group throughout. The search order merely finds a certificate and can be discarded during replay.

## Transfer from topology to chore fairness

Apply Theorem 5 of Dupré la Tour to this finite, connected, simply connected, cyclically invariant, 1-close allocation complex. Take normalized valuations $v_i(S)=c_i(\varnothing)-c_i(S)$. The theorem supplies a vertex and a permutation assigning its three bundles to the people. Permuting bundle labels preserves feasibility because every person faces the same path conflicts. For each ordered pair the transfer gives deletions $C\subseteq A_i$, $G\subseteq A_j$, each of size at most one, with $v_i(A_i\setminus C)\ge v_i(A_j\setminus G)$. Monotonicity of costs now gives

$$
c_i(A_i\setminus C)\le c_i(A_j\setminus G)\le c_i(A_j).
$$

This proves the claimed chore comparison on the ten-vertex path. [Dupré la Tour, *Balanced Fair Division for Three Agents under General Valuations and Laminar Constraints*, Definition 2, Fact 1 and Theorem 5](https://arxiv.org/html/2608.09437v1)

For a shorter path, append dummy chores at one end to give ten positions. Extend every cost by $c'_i(S)=c_i(S\cap M)$. These extensions are monotone. Restrict the ten-position assignment to $M$. It is still complete and feasible, and each deletion witness restricts to $C\cap M$, of size at most one. Both costs in the inequality retain their values. This also covers the empty path.

## Scope and a failure case

Equbal and coauthors ask about three or more agents with monotone valuations on paths of unrestricted length. The calculation here establishes the bound ten. Priority remains provisional. [Equbal et al., *Fair Allocation under Conflict Constraints*, §6](https://arxiv.org/html/2605.09930v1)

The seven-vertex obstruction uses a different conflict graph. Take the complete bipartite graph on $\{0,1,2\}$ and $\{3,4,5\}$, and attach vertex 6 to vertices 0 and 3. Use the published cost with zero-based labels. The empty set costs 0. Singletons 0 and 3 cost 1, and every other singleton costs 2. A pair containing 6 and one of 1, 2, 4 or 5 costs 3. All other bundles cost 4. Direct comparison finds zero complete EF1 assignments among its 42 legal words. The triangle search leaves 42 edge generators unproved and the verifier refuses the certificate. The search stalling alone would give no conclusion about that group's structure. [Igarashi, Manurangsi and Yoneda, *Dividing Conflicting Items Fairly*, Theorem 11 and §5](https://arxiv.org/html/2506.14149v1)
