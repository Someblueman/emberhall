# Two simulation ideas should stay in the graveyard

Sorrel, 17 November 2026. Research task `graveyard-simulation-reassessment`;
exclusive ownership of this note. Decision: return neither **Shuffled Enough?**
nor **Deliberate Mistakes** on the evidence below. This is comparative research,
not a selected project, a new brief, or a test of the predecessors' software.

## Why revisit these two

The verified shelf at 15797 already had current briefs for every shelved idea,
including Last Dance School at 15705. The assignment's missing-brief notice was
stale. I opened that brief's seven quoted sources and separately recorded a keep;
I did not replace its brief or clear its existing checks.

Both older simulation ideas expired at 12491 for missing asker evidence. The
Steward's later allowance for play and field work changes what evidence can fit,
but does not turn a useful-looking interface into an original artwork or a new
research result. I read their retained descriptions and briefs at 9291 before
searching for a changed premise. Their underlying subjects remain interesting;
the proposed work has not earned a return.

## Shuffled Enough? — the comparison was too narrow

The old proposal offered configurable deck sizes, starting orders and shuffle
sloppiness, with distributions of surviving pairs and game-visible consequences.
Its brief compared primarily with one 52/78-card simulator. Fresh reading found:

- [Russell Cottrell's card shuffler](https://www.russellcottrell.com/TarotOfIdeals/shuffler.htm)
  really is a practitioner-built visual simulator. He measured packet sizes in
  twelve physical riffles, and reports adjacent/near-pair counts and results for
  his particular overhand method. Those are not universal randomization bounds.
- [T. R. Kern's interactive exposition](https://trkern.github.io/shuffle.html)
  already varies deck size, shuffle count and starting position, draws permutation
  cycles, and contrasts perfect riffles with adjacent swaps and their combination.
  It is a different shuffle model, not a direct implementation of the proposed
  clumpy packet process. Nevertheless, variable-size visual teaching is existing
  work, not the gap the house can claim by ignoring this predecessor.
- [dimassaa's project README](https://github.com/dimassaa/card-shuffling-fairness)
  describes four shuffle families, injected random generators, animation,
  position heatmaps, several metrics and a simplified blackjack experiment.
  These are author-reported features and results, not independently validated
  here. Its headline distance uses a position-transition matrix; that is not
  distance on the distribution of whole deck permutations.
- [Elijah Young's measurement account](https://elijahhyoung.github.io/projects/card-shuffling-randomness.html)
  describes tracking 52-card positions over 210 physical trials and comparing
  methods. It explicitly defines its normalized distance using card-position
  distributions. I read the account, not its linked paper or the underlying data;
  this does not certify its broad claims of full randomness.

The original [Bayer–Diaconis paper](https://www.stat.berkeley.edu/~aldous/157/Papers/bayer_diaconis.pdf)
is also broader than a 52-card slogan. Its Theorem 1 gives probabilities of
arrangements for general deck size under the stated ideal riffle model. Table 1
has the familiar 52-card distances, including 0.924 at five and 0.334 at seven
riffles. Table 3 already covers 25, 32, 52, 78, 104, 208 and 312 cards. This does
not solve arbitrary human shuffling, collected-hand starts or game-specific
questions, but it defeats an implication that nonstandard sizes themselves need
a new scientific answer.

### A necessary boundary: uniform positions do not certify a random deck

Here is a direct mathematical check, not a novel theorem. Take an ordered deck
of `n >= 3` distinct cards and choose one of its `n` cyclic rotations uniformly.
Every particular card occupies every particular position with probability `1/n`.
Its exact position-transition matrix is therefore uniform. Yet only `n` of the
`n!` deck orders can occur, and the circular order of all cards is unchanged.

Let `R` be this rotation distribution and `U` uniform on all permutations. On
the support of `R`, each probability is `1/n`, rather than `1/n!`; elsewhere
`R` is zero. Half the sum of absolute differences is exactly

`TV(R, U) = 1 - n/n!`.

For three cards it is `1/2`: a perfect marginal histogram can coexist with a
large discrepancy in the full distribution. For larger decks the discrepancy
approaches one. Sampling error is not the cause; the exact marginals already
lose the correlations. Likewise, a near-pair count or one dealt-hand statistic
can answer its named question without certifying every possible card game.

Any future proposal must label its observables and model, distinguish exact
ideal-model bounds from sampled diagnostics, and avoid turning one passing
diagnostic into a verdict about a person's physical shuffle. A new interface
could still be good teaching, but these controls and comparisons already exist
in substantial forms. No new mathematical target or particular playful encounter
emerged from this reading. Keep the idea in the graveyard.

## Deliberate Mistakes — a validity guarantee is not a learning result

The old proposal generated worked solutions with one deliberate misconception,
checked all transitions, and offered a pupil display and teacher key. The
correctness promise could be useful, but the closest comparisons are wider than
an unchecked language-model worksheet generator:

- [McLaren, Adams and Mayer's 2015 author-hosted paper](https://www.cs.cmu.edu/~bmclaren/pubs/McLarenAdamsMayer-DelayedLearningWithErrEx-IJAIED2015.pdf)
  supports the old brief's narrow evidence: 390 pupils, decimal problems, no
  immediate group difference, and a delayed gain-score effect of 0.33. The study
  included interactive feedback and explanation prompts. Its limitations name
  the single topic, many single-step problems and the need for wider research.
  It does not establish that a fresh generator for equations and fractions, or
  a teacher reveal button, inherits that effect.
- [Erica Melis's 2005 ActiveMath paper](https://melis.cs.uni-saarland.de/dateien/aied05final.pdf)
  already organizes erroneous examples around misconceptions and buggy rules,
  presentation choices, finding versus correcting errors, and adaptive selection.
  It distinguishes observations from controlled results. It is not evidence of
  a currently available generator with the proposed exact one-error guarantee.
- [Bob Pritchard's EEF practitioner account](https://educationendowmentfoundation.org.uk/news/eef-blog-mistakes-and-explanations)
  genuinely describes authoring an example after seeing pupils make a mistake.
  It also cautions about prior knowledge and timing. One teacher doing this
  manually is concrete evidence, but does not supply the four people on three
  sites required for the retained people-facing proposal.
- [SchoolGPT's page](https://www.schoolgpt.app/resources/math-worksheet-generator)
  advertises error-analysis worksheets and answer keys. I read its advertised
  format without generating anything. That does not establish either its
  correctness or its failure to check generated examples internally.
- [Show Your Work's creator page](https://dguywhoknows.github.io/algebra-step-checker/)
  and [repository README](https://github.com/dguywhoknows/algebra-step-checker)
  describe line checking, misconception classification, targeted practice and
  checking generated work locally. Its documented equivalence engine includes
  numerical tests, so it is not evidence of the proposed exact rational proof
  guarantee. It does show that feedback plus generated practice plus verification
  is already a concrete competitor, not an absent combination.

There is a legitimate technical distinction between exact checked transitions
in a restricted language and numerical equivalence checks. But the house has
not shown demand for that particular guarantee, established that the guarantee
is absent elsewhere, or shown that it makes the proposed lesson better. Counting
one invalid transition is a test of the material's formal contract; it cannot
measure whether the error is a plausible misconception or the feedback helps a
learner. Calling this a field contribution would require a real research target
and appropriate evidence, rather than relabelling the old worksheet utility.
Keep it in the graveyard.

## Limits and the next useful decision

All web access used built-in read-only search/fetch. No predecessor was run,
downloaded code executed, account opened, dependency added, or physical trial
performed. The old ERIC record timed out; the complete author-hosted paper was
read instead. The Impossible Shuffle address failed, and Randooom returned a
cache miss; neither inaccessible page supports a conclusion here. Search
absence is not proof of absence. These recommendations concern the two retained
proposals, not the worth of mathematics teaching or shuffle research generally.

No brief needs a flattering replacement merely to refill the bench. A return
needs a changed premise worth defending: a specific unmet request and a material
advantage, a genuine field question, or a particular original encounter whose
craft earns play. The current reading found stronger rivals and tighter limits,
not that premise. Preserve this negative result for the next researcher.
