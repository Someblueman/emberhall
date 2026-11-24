# Shorter-word forcing compiler: partial follow-on

Aster, 24 November 2026. **This task is unfinished.** No new all-scale
constraint beyond APERIODIC_COMPLETION.md has yet been proved, and the
universal tripod milestone remains open. Priority remains provisional.

The standard-library module compiles equation (12) of that document from
only the centre and shorter-arm strings. It constructs the known signed
shell derivative in linear time, integrates it exactly to F_0, and builds
R=-z^N(F_0+F_0*+2S_0). It never supplies any long-arm signs. The existing
all-hole recovery theorem supplies the geometry bounds checked on input.

For a caller-supplied constant-first polynomial Q, the module verifies
that Q divides both radial P and its padded reversal modulo 1,000,003.
Only then does it reduce R. A nonzero residue excludes every integer
long-arm completion for those fixed shorter words: equation (12) would
imply Q divides R in the same field. A zero residue is only a necessary
condition. No rational-to-sign, support, or existence conclusion follows.
Laurent remainders are supported because Q's constant coefficient is
required nonzero. The primary equation's proof and uniqueness theorem
remain in APERIODIC_COMPLETION.md rather than being claimed anew here.

Input uses the same `lengths`, `holes`, `centre`, `arm2`, `arm3` parameter
format as the completed recovery module. For T(99,79,23), holes (1,19)
and (1,99), take Q=1+z^3:

    python3 projects/almost-halving-three-branches/shorter_arm_elimination.py PARAMETERS.json --modulus '[1,0,0,1]'
    python3 -m unittest discover -s projects/almost-halving-three-branches -p test_shorter_arm_elimination.py -v

Recorded run from the actual t=1 homometric witness's retained words:
retained_signs=103, radial_degree=177, forcing_residue={}, and both
existence_decided and all_scale_family_proved false. Flipping just the
third-arm depth-one sign produces residue 4+2z-2z^2 modulo the field and
is rejected for every long-arm word. Independent BFS checks validate F_0
on t=1 and t=3; the altered-word and invalid-factor controls discriminate
the implication. Three tests pass. This is a working compiler and a
finite control, **not the new all-scale result required to finish the task**.

Next: find and prove common radial factors or equivalent coupled shorter
constraints across t=2660k+1, show they add restrictions beyond the
independent ternary clauses, or find an actual full construction or
universal obstruction. Do not infer a common factor at another scale
from the t=1 control; factor verification is mandatory at every use.
The earlier full polynomial gcd diagnostic is intentionally capped and
was not practical at the first open scale in a naive sparse Euclidean
probe. Use structural algebra rather than declaring that probe decisive.
