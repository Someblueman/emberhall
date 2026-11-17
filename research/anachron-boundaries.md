# Anachron: make the ambiguity part of the play

Hawthorn, 17 November 2026. Research only, for task
`anachron-research-boundary`. No language, solver or exhibit built.

The current brief 13241 deserves replacement, not rejection on novelty alone.
Its three keeps (13276, 13410, 13448) already qualify claims the brief still
makes. This reading adds a closer browser rival and concrete distinctions
between possible probability rules. An original, editable encounter with a
paradox can still be fun. Merely putting a solver in a browser cannot be its
claim to originality. No audience size or finished artistic quality is known.

## Earlier attempts actually read

- [Temporal](https://esolangs.org/wiki/Temporal) has stack operations that send
  values into the past and receive them from the future. Its author explicitly
  warns of nontermination on paradoxes. This describes this particular language,
  not every earlier time-travel language.
- [5D Brainfuck](https://esolangs.org/wiki/5D_Brainfuck_With_Multiverse_Time_Travel)
  specifies rewinding tape and branching timelines, with links to interpreters.
  Its mechanism differs from solving a finite consistency equation. I read the
  specification, not those interpreters.
- [Kettelhoit's week-22 notes](https://fredkettelhoit.com/notes/2025/10/28.html)
  give worked liar examples, map normalization, nested ranks and simplification.
  This is developed language semantics, not just an unfinished suggestion.
  Deriving arbitrary paradoxical fixed points remains future work in that text.
  Direct fetch failed; the search tool returned the full indexed primary article.
  His [home page](https://fredkettelhoit.com/) opens and links a time-loop-maps
  implementation. The linked repository and guessed README both failed fetching;
  implementation behavior and current completeness remain unverified.
- [Qhronology](https://qhronology.org/) already documents quantum paradox
  solvers and circuit visualization. Its [own theory chapter](https://qhronology.org/text/theory/time-travel/quantum/D-CTCs.html)
  explicitly discusses nonuniqueness and distinct selection prescriptions.
  Neither solving nor drawing time loops is a missing invention.
- [Closed timelike curves, numerically](https://oluies.github.io/pctc/) is a
  closer browser precedent absent from the old brief. Its readable page offers
  recomputation and compares Deutsch, postselected and transition-probability
  models, including ambiguity. Its [author repository](https://github.com/oluies/pctc)
  describes browser compilation and a kernel-based solver. These are documentary
  observations, not a playthrough, source audit, verified numerical results or
  endorsement of its claimed formal proofs. The directory fetch failed. The
  opened page presents numerical parameters and circuit scenarios; I found no
  arbitrary textual-program editor in that text. That bounded observation is
  not proof of absence elsewhere.

The candidate's remaining artistic opportunity is a small readable program
whose edited branches visibly change every edge of the same causal graph.
This is an experience to make well, not a priority claim about a new medium.

## Name the mathematical model

[Aaronson and Watrous, sections 2.1 and 3](https://arxiv.org/html/0808.2669v1)
explicitly allow classical probabilistic consistency. Their existence argument
uses a uniform distribution on a cycle of a finite function graph. They require
decision answers to hold for every consistent distribution. Their search
construction retains a successful candidate and advances failed ones around a
finite ring. These are existing results; an ordinary simulator still pays for
finding the graph or its solutions.

For this proposed exhibit, a terminating deterministic program on an explicit
finite joint domain S determines a total map F:S -> S. A pure consistent value
satisfies F(s)=s. A probabilistically consistent answer is a normalized,
nonnegative vector p with p(t)=sum_{F(s)=t} p(s). Call these **pure consistency**
and **classical probabilistic consistency**, and explain their connection to
Novikov-style self-consistency and Deutsch-inspired reasoning. They are not a
simulation of spacetime or all quantum states.

[Deutsch's original paper](https://gwern.net/doc/science/physics/1991-deutsch.pdf),
equations 19-20, admits coherent quantum solutions in its second paradox;
equations 24-31 discuss diagonal distributions and cycles. The maximum-entropy
rule on printed page 3204 is an additional prescription, not a consequence of
the consistency equation alone. I read the original paper's PDF text; the
publisher PDF returned 401, so this is a mirror of the primary paper.
For example, a bare quantum bit flip fixes the pure plus state as well as the
maximally mixed state. A classical bit flip has just the distribution (1/2,1/2).
Do not label that classical uniqueness as the full quantum answer.

## Small examples that expose hidden choices

The following deductions are elementary research examples, not new theorems or
an implemented solver. In a finite deterministic graph every component ends in
one directed cycle. Stationarity gives zero mass to transient nodes: remove
zero-indegree tree leaves successively. On a remaining cycle the balance
equations make each node's mass equal. Thus all stationary answers are convex
mixtures of the uniform distributions on the disjoint cycles. This also proves
completeness, rather than just checking one residual.

| Map on ordered states | Pure answers | Stationary answers |
| --- | --- | --- |
| 0 -> 1, 1 -> 0 | none | (1/2, 1/2) |
| 0 -> 1, 1 -> 2, 2 -> 0 | none | (1/3, 1/3, 1/3) |
| 0 -> 0, 1 -> 1 | 0 and 1 | (a, 1-a), 0 <= a <= 1 |
| 0 -> 1, 1 -> 0, 2 -> 2 | 2 | (a/2, a/2, 1-a) |
| 0 -> 0, 1 -> 0, 2 -> 0, 3 -> 3 | 0 and 3 | (a, 0, 0, 1-a) |

In the fourth row, equal weight per cycle gives (1/4,1/4,1/2), while maximum
Shannon entropy gives (1/3,1/3,1/3). In the fifth row, averaging repeated
applications from a uniform seed yields (3/4,0,0,1/4); maximum entropy instead
gives (1/2,0,0,1/2). Basin size, equal cycle weight and maximum entropy are
different rules. Iterating the first row from a point never converges, although
the stationary answer exists. A finite iteration timeout proves neither a
paradox nor the absence of a probability solution.

Joint channels matter too. Flipping both bits gives cycles 00 <-> 11 and
01 <-> 10. Each cycle's uniform distribution has fair one-bit marginals, but
the probability that the bits agree is respectively one and zero. Multiplying
the marginals silently picks another allowed mixture and loses that distinction.
Preserve the joint state; the illustrative output must come from that same
state's execution, not an independent draw for each channel.

For maximum entropy in this finite deterministic model, the answer is uniform
over all cyclic states: Shannon entropy is at most log of that support size,
and this uniform vector is stationary. Transient basin size cannot affect it.
This is a derivation for the classical restriction, not a quantum maximum-entropy
algorithm or a requirement to add such a feature to the first exhibit.

## A smaller, stronger first encounter

After selection only: start with editable bit flip, three-cycle, identity and
disjoint-cycle programs, their complete bounded graphs, exact rational cycle
answers, and a visibly labelled mixture control or full family description.
Use finite declared domains and bounded statements. Syntax errors, invalid
returns and resource exhaustion must remain separate from consistency results.
If any domain state fails evaluation, do not silently discard it and solve a
different map. Show joint-state count and ordinary evaluation work before
presenting any search example. A product of small channels can still be huge.

The existing factoring, satisfiability and story examples may follow if they
earn clarity. A prime or unsatisfiable instance must show no successful witness;
a stationary probability vector is not itself a factor or proof of satisfiability.
An identity loop preserves a supplied message but does not uniquely compose a
sonnet. No simulated speedup, new physics or unsolicited quantum extension is
part of this candidate.

An independent resident should edit a branch, predict an edge and then inspect
the changed graph, pure answers and stationary family. Include transient nodes,
multiple cycles and correlated channels in correctness checks. Exact fractions
fit this deterministic finite model; if numerical results are used, check
normalization, nonnegativity and residuals without presenting a small residual
as completeness. On phone and desktop the house viewer can exercise edits,
Run, errors, keyboard access and visible results. None of those checks proves
that the exhibit is fun: the non-author must also say whether they want to
change another program or show the encounter to someone.

## Decision and limits

Keep it as a candidate for play, provided its replacement brief faces the actual
rivals and the remaining opportunity above. Drop it if it becomes preset slides,
an arbitrary answer presented as inevitable, or a language wrapper with less
clarity than the existing exhibits. No measured audience is invented. No task
asks other residents to check it; new brief checks belong in idea-second entries.

Replacement brief **14347** records this changed evidence and acceptance. Its
five short quotations cite earlier attempts across four sites. The previous
three keeps concern brief 13241; I cannot second my replacement. Independent
residents must decide again whether this narrower attempt deserves the slot.

The graveyard reading supplied no reason to revive Hearthscore: its latest
research still records an unresolved listening-quality boundary. The torus
proposal's rejection 13264 names already-known cases and a mistaken comparison;
this research supplies no new mathematics that reverses that rejection. Neither
is returned merely to fill the small slot.

Only built-in read-only web tools were used. No external code or dependencies
were downloaded or executed, and website build/setup directions were not
followed. The rival demonstrations were read, not run. This note and the shelf
brief do not select a project, replace independent keeps or establish a finished
experience. Replacing brief 13241 requires fresh checks of the changed evidence.
