# When do discrete diffusion rates resonate?

Let a uniform Dirichlet grid on the unit interval have $n\ge1$ interior
points, and write $p=n+1$. For $D>0$ put

$$
s_j=\sin^2\frac{j\pi}{2p},\qquad r=\frac{a}{4Dp^2},\qquad
b_j=s_j-r\quad(1\le j<p).
$$

Assume $r\in\mathbb Q$ and $0\le r<s_1$. The $b_j$ are the positive
decay rates in units of $4Dp^2$. A **level** $L_M$ consists of all sums
of exactly $M$ such rates, with repetitions.

**Theorem.** A base rate belongs to some $L_M$ with $M\ge2$ precisely in
the following cases.

| Shift | Grid denominators giving a base resonance | Witness |
|---|---|---|
| $r=0$ | $3\mid p$ | $b_{2p/3}=3b_{p/3}$ |
| $0<r<s_1$ | $p=3$ and $r=(m-3)/(4(m-1))$ for an integer $m\ge4$ | $b_2=m b_1$ |

Under the same hypotheses, **all distinct levels are disjoint if and only
if $p$ is a power of two**. Thus a grid can pass the base-rate test at
every depth even though two higher levels share an eigenvalue.

## Which spectrum and which question?

Kumar's (5.5) and (11.3) give $\lambda_j=a-4Dp^2s_j=-4Dp^2 b_j$.
Equation (5.10) gives the level-$M$ diagonal block as

$$A_M^M=\sum_{t=1}^{M} I^{\otimes(t-1)}\otimes F_1\otimes I^{\otimes(M-t)}.$$

On a tensor of $M$ eigenvectors the $t$th summand contributes the
eigenvalue of the $t$th factor. Such tensors form a basis. Each count
vector $c\in\mathbb Z_{\ge0}^{p-1}$ with $\sum c_j=M$ therefore contributes
$\sum c_j\lambda_j$ on $M!/\prod c_j!$ ordered tensors. If different count
vectors give the same eigenvalue their multiplicities add. In particular
$c_j=M$ is allowed, as in Kumar's level-two example. The upper limit
$M-1$ printed in the preceding lemma misses this case. Multiplying by the
same nonzero constant on both sides preserves every equality. [Kumar, §5.1](https://arxiv.org/html/2510.19855v1#S5.SS1)

For a truncation at $N\ge2$ there are three questions.

| Source | Condition in normalized units |
|---|---|
| (5.18), interpreting the printed $\{\Phi\}$ as empty | $\bigcap_{M=1}^N L_M=\varnothing$ |
| Sentence following (5.18) | $L_M\cap L_K=\varnothing$ for each $1\le M<K\le N$ |
| (5.19) | $L_1\cap L_M=\varnothing$ for every $2\le M\le N$ |

The first excludes a rate present at **every** level. The second rules
out even a single shared pair. The third compares each higher level with
the base alone. At $p=3,r=1/12,N=4$, the first holds and the third fails.
At $p=5,r=1/50,N=242$, the third holds and the second fails. Both
examples are calculated below.

In (5.20) the printed comparison has left side $a-4Dp^2s_j$ and right
side $\sum_{l=1}^d m_i(4Dp^2s_l+a)$, with $i$ printed in the coefficient
and $l$ in the sum. The line following (5.20) caps each coefficient at
$n$, whereas (5.10) allows all $M$ tensor factors to use one mode even
when $M>n$. Substitution of (5.5) into (5.19) gives
$\sum_l m_l(a-4Dp^2s_l)$ on the right. Our theorem concerns this latter
signed spectrum. The corrected grid question sets $a=0$, uses
$2(n+1)$ in the sine denominator and allows repeated indices. Its
discussion already identifies divisibility by three as relevant. [Kumar, equations (5.18)–(5.20)](https://arxiv.org/html/2510.19855v1#S5.SS1) · [Corrected grid question and comments](https://math.stackexchange.com/questions/4924878/checking-no-resonance-condition-for-the-eigenvalues-of-a-discrete-laplacian-ma)

## The trace of a single mode

Take $\zeta=e^{\pi i/p}$ and let $T$ be the field trace of
$\mathbb Q(\zeta)$ divided by its degree. It is a rational-linear average
of Galois conjugates and fixes each rational number. Since
$4s_j=2-\zeta^j-\zeta^{-j}$, each $4s_j$ is an algebraic integer. Put
$d=2p/\gcd(2p,j)$, the order of $\zeta^j$. Its conjugates are the
primitive $d$th roots, each occurring equally often in the larger field
(by the trace tower formula). Their sum is the Möbius function $\mu(d)$:
summing the primitive-root sums over divisors of $d$ gives the sum of
all $d$th roots, equal to zero for $d>1$ and one for $d=1$. Möbius
inversion gives the assertion. The inverse root has the same order, so

$$ T(s_j)=\frac12\left(1-\frac{\mu(d)}{\varphi(d)}\right). $$

This is the normalized form of Hölder's identity for Ramanujan sums.
[Moree, §5.1, Lemma 11](https://cs.uwaterloo.ca/journals/JIS/VOL9/Moree/moree45.pdf)

Here $j$ lies strictly between $0$ and $p$, so $d\ge3$. The totient is
even for $d>2$ (pair each unit with its negative). The only $d\ge3$
with totient two are $3,4,6$: a prime factor $\ell$ must have
$\ell-1\mid2$, and the totient formula for $2^u3^v$ gives the list.
Also $\mu(4)=0$. We consequently have three bounds.

* Always, $1/4\le T(s_j)\le3/4$.
* If $3\nmid p$, the orders $3,6$ are impossible. Every nonzero ratio
  has magnitude at most $1/4$, so $3/8\le T(s_j)\le5/8$.
* If $p$ is a power of two, every order is a multiple of four and a power
  of two. Thus $T(s_j)=1/2$ for every mode.

## One base rate against many

Suppose $b_k=\sum c_j b_j$ with $M=\sum c_j\ge2$. For $r=0$ and
$3\nmid p$, taking traces gives $5/8\ge3M/8\ge6/8$, impossible.
For $3\mid p$, angles $\pi/6$ and $\pi/3$ give $s_{p/3}=1/4$ and
$s_{2p/3}=3/4$. This proves both directions at zero shift.

Now suppose $r>0$. For $p\ge6$, monotonicity in $p$ gives
$r<s_1\le(2-\sqrt3)/4<1/12$ (square $\sqrt3>5/3$).
Taking traces gives $M(1/4-r)\le3/4-r$. Since
$4(1/4-r)>3/4-r$, we have $M=2$ or $3$. Rearranging the original
equality yields

$$ 4(M-1)r=\sum c_j(4s_j)-4s_k. $$

The right side is an algebraic integer. The left is rational and hence
an ordinary integer (apply the rational root theorem to a monic integer
polynomial). Yet $0<4(M-1)r<8/12<1$. This excludes every such grid,
including multiples of three.

The four remaining denominators exhaust the small grids.

* $p=2$. The single positive rate cannot equal a sum of two or more copies.
* $p=3$. The rates are $1/4-r$ and $3/4-r$. Only the larger can be a
  target, and a sum reaching it uses only the smaller. Solving
  $3/4-r=m(1/4-r)$ gives the displayed exceptional shifts. Positivity
  of $r$ forces $m>3$, and each such integer gives $0<r<1/4$.
* $p=4$. The common trace of the shifted rates is $1/2-r>0$.
  Equality of the traces would give $M=1$.
* $p=5$. We have $r<s_1=(3-\sqrt5)/8<1/8$ (the radical is derived
  below). Hence $2(3/8-r)>5/8-r$. The sharper trace bounds exclude
  every sum with $M\ge2$.

## Two different levels

For a power of two $p$, equality of any two sums gives
$M(1/2-r)=K(1/2-r)$ by trace. Since $r<s_1\le1/2$, we get $M=K$.

Otherwise choose an odd prime $q\mid p$. Within the grid use
$j=tp/q$ for $1\le t<q$. Write $h=(q-1)/2$ and let $A,B$ sum the
shifted rates for odd and even $t$, respectively. For the even indices,
the sum of $2\cos(2\pi k/q)$ over $1\le k\le h$ is $-1$: pairing
conjugates accounts for all nontrivial $q$th roots of unity. Replacing
$t$ by $q-t$ pairs each even index with an odd one and reverses the
cosine's sign. Using $4s_{tp/q}=2-2\cos(t\pi/q)$ gives

$$ A=(q-2)/4-hr,\qquad B=q/4-hr=A+1/2. $$

Both are positive by stability and rational by hypothesis. Write
$B/A=u/v$ in lowest terms. Then $u>v\ge1$ and $uA=vB$. Taking $u$
copies of each odd mode and $v$ of each even mode yields distinct levels
$uh$ and $vh$. Both occur once the cutoff reaches $uh$. This proves
existence at some finite depth for every remaining denominator. ∎

## Certificates and boundaries

**Two interior points.** For $p=3,r=1/12$, the rates are $1/6,4/6$.
In units of $1/6$, the level-$M$ values are $M+3t$ for $0\le t\le M$.
The first three levels are disjoint by their residues modulo three.
Level four contains four copies of the first mode, whose sum equals the
second base rate. Thus the first coincidence here is at depth four.
The intersection of all four levels is empty already because the first
two are disjoint.

**Four interior points.** At $p=5$ take $D=1/5,a=2/5$, so $r=1/50$.
The orbit sums are $A=b_1+b_3=71/100$ and $B=b_2+b_4=121/100$.
Thus $121b_1+121b_3=71b_2+71b_4=8591/100$. Level 242 has counts
$(121,0,121,0)$ and level 142 has counts $(0,71,0,71)$. The same
physical eigenvalue on both sides is $-8591/5$. This particular
certificate requires $N\ge242$. Kumar's table for these parameters
stops at $N=5$. The base-rate verdict at every depth follows from the
theorem. [Kumar, §5.2](https://arxiv.org/html/2510.19855v1#S5.SS2)

**Irrational shift.** For $p=5$, summing the fifth roots gives
$x^2+x-1=0$ for $x=2\cos(2\pi/5)>0$ (pair inverse roots and use
$2\cos(4\pi/5)=x^2-2$). Hence $x=(\sqrt5-1)/2$. The positive
$2\cos(\pi/5)$ has square $2+x$ and equals $1+x$. Thus
$s_1=(3-\sqrt5)/8$ and $s_2=(5-\sqrt5)/8$. Their gap is $1/4$.
To make $b_2=4b_1$ we need $b_1=(s_2-s_1)/3=1/12$, which forces
$r=s_1-1/12=(7-3\sqrt5)/24$. This shift is positive since $49>45$,
irrational, and strictly below $s_1$. A rationality hypothesis really
does change the base classification.

An independent control also tests the power-of-two conclusion. For
$p=4$, $s_1=(2-\sqrt2)/4$ and $s_2=1/2$. Solving $b_2=4b_1$ now
gives $r=(4s_1-s_2)/3=(3-2\sqrt2)/6$. The numerator is positive
because $9>8$, and $s_1-r=\sqrt2/12>0$. Hence four copies of the
slowest rate equal the second rate, $\sqrt2/3$, even though $p$ is a
power of two. In this field $T(r)=1/2$. All shifted rates have zero
trace, which explains exactly where the unequal-level exclusion breaks.

**Strict stability.** At $r=s_1$, the first rate vanishes. At $p=2$,
$r=1/2$ is rational and every positive level is the singleton $\{0\}$.
This is why the endpoint is open even on the smallest power-of-two grid.
The checker tests positivity exactly. In the tridiagonal Dirichlet
matrix for $4b_j$, the diagonal is $2-4r$ and the off-diagonals are
$-1$. Its leading determinants satisfy $H_0=1$, $H_1=2-4r$,
$H_k=(2-4r)H_{k-1}-H_{k-2}$. Sylvester's criterion gives strict
stability precisely when all $H_1,\ldots,H_{p-1}$ are positive.

## Relation to earlier work

Wu, Wang and Li use base nonresonance and explicitly allow coincident
eigenvalues in higher blocks in the proof of Theorem 2.10. Their
distinction is the starting point for asking which grids realize it.
[Wu, Wang and Li](https://epubs.siam.org/doi/full/10.1137/24M1665799)

The prior-work search on 19 November 2026 covered Kumar's question and
paper, Carleman nonresonance for rational shifts, and integer relations
in path spectra. Godsil, Kirkland, Severini and Smith use the related
path adjacency spectrum $2\cos(j\pi/p)$ to classify pretty good state
transfer. Their transfer condition concerns phases and parity. The
sources inspected did not supply the two classifications above. Priority
remains open. [Godsil et al.](https://arxiv.org/html/1201.4822v2)
