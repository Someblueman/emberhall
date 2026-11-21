# From a linear blend to an observed byte

The palette coordinates are **linear-light sRGB primary coordinates**, not
hexadecimal CSS channel values. The original six probability problems are
unchanged. M1 displayed their coordinates directly as bytes; those previews
were darker than the stated linear-light model. M2 fixes that presentation.
For example, linear `(11/25, 9/20, 59/100)` is displayed as `#b1b3ca`, not the
M1 preview `#707396`. The exact fibre and its probability bounds do not change.

## Supported pipeline and its limits

1. Take a finite palette of rational triples in `[0,1]^3` and a probability
   vector. Compute `x = sum(p_i c_i)` with exact rational arithmetic.
2. For **srgb8**, transfer each linear channel to encoded sRGB, then apply the
   explicitly chosen rule `Q(z) = floor(255 z + 1/2)` (half ties upward).
3. The SVG uses the resulting hex colour as the fill of an **opaque flat**
   rectangle. There are no gradients, filters, blending modes or transparency.
   The explicit-distribution bars show individual stops, not a spatial average.

The transfer follows the [W3C sRGB definition](https://www.w3.org/TR/2026/CRD-css-color-4-20261112/#predefined-sRGB):

```
S(x) = (323/25) x                          if x <= 0.0031308
       (211/200) x^(5/12) - 11/200        otherwise
```

**linear8** supports raw linear data bytes, `Q(x)`. An ordinary browser hex
fill interprets those bytes as encoded sRGB, so the linear8 hex is printed only
as data, not used as an equivalent-light swatch. `srgb8` is always the main
swatch, even when a caller requests only linear8 observation bounds. The API
rejects unrecognized mode names.

These are nominal colour-coordinate claims, not calibrated physical display
measurements. We do not decode screenshots, JPEG, scaled/antialiased boundary
pixels, alpha composites, browser screenshots with colour-profile transforms,
wide-gamut spaces, perceptual spaces, or averages of *encoded* sRGB channels.
No profile conversion, gamma approximation or clipping is silently substituted.
The half-up rule belongs to this generator; no claim is made that every browser
capture/export tool uses it. The viewer may colour-manage the final sRGB fill.

## Exact encoding without floating point

For an integer `j` between 1 and 255, byte `Q(S(x))` is at least `j` exactly when
`S(x) >= (2j-1)/510`. On the linear branch this is a rational comparison.
On the nonlinear branch, with `b=(2j-1)/510`, it is equivalent to

```
x^5 >= ((200 b + 11)/211)^12.
```

Both sides are rational. A binary search over these thresholds finds the byte;
there is no floating point exponent or rounding uncertainty in the encoder.
The rounded sRGB constants cause a minute backwards jump at the branch join.
Both join values lie strictly inside byte 10's bin `(9.5/255, 10.5/255)`, so
no byte threshold is crossed and the byte encoder remains ordered there.

## Inverse observation boxes

Byte `q` identifies an encoded interval with lower boundary
`max(0,(2q-1)/510)` and upper boundary `min(1,(2q+1)/510)`. Its upper boundary
is excluded by half-up rounding, except at the clipped endpoint 1. We enclose
it in a **closed** interval. For linear8 these boundaries are rational already.
For srgb8, invert each boundary:

```
D(z) = (25/323) z                    if z <= 0.04045
       ((200 z + 11)/211)^(12/5)    otherwise.
```

No byte boundary falls inside the branch-join discrepancy. In the nonlinear
case, bisect `[0,1]` 64 times with exact comparisons `r^5` against the rational
`((200 z + 11)/211)^12`. Keep the lower rational endpoint for the lower
boundary and the upper rational endpoint for the upper boundary. Each inverse
boundary is enclosed within `2^-64` in linear coordinates. The product of the
three closed rational intervals therefore contains **every** true linear
colour that could have produced the observed three bytes.

## Probability bounds and certificates

For the observed box `[l,u]`, solve

```
min/max e^T p  subject to  1^T p=1, p>=0, l<=Cp<=u.
```

Add six nonnegative slacks to obtain the equality system `A z = b`:

```
A = [ 1^T   0   0 ]     z = [ p    ]     b = [ 1  ]
    [  C    I   0 ]         [ s_up ]         [ u  ]
    [ -C    0   I ]         [ s_lo ]         [-l  ]
```

The objective is `(e,0,0)`. The certificate carries two distributions and two
seven-component dual vectors. A lower vector `d` satisfies
`d^T A <= (e,0,0)`; hence its last six components are nonpositive. An upper
vector reverses these inequalities and has nonnegative last six components.
For each distribution, the verifier checks nonnegativity, normalization,
colour in the box, and its event probability. It checks dual inequalities at
every palette stop, slack signs, and equality `d^T b = e^T p`. Weak duality
then proves the two extrema on this rational box. Verification never calls
the optimizer. `verify_atlas.py` additionally binds each box to its mode and
bytes and checks the source distribution, displayed hex and exact certificate.

These are **sharp bounds for the outer rational box** and conservative bounds
for the actual quantized observation. We do not label them sharp attained
bounds for a half-open byte bin. Tiny inverse enclosure and closed endpoints
may enlarge the interval. Percentage labels round the lower endpoint down and
the upper endpoint up to two decimal places; JSON fractions are authoritative.
An infeasible outer box proves the real observation impossible under the model.
A feasible outer box alone is not a certificate that a real half-open bin is
feasible. The API raises `InfeasibleColourError` only for outer-box infeasibility.

## Two hand-checkable examples

**S7, held out from the six M1 cases.** Its weights are
`(1/7,2/7,0,3/7,1/7)` on the 3D palette; event `{3,4}` uses zero-based indices.
The unique affine dependence is
`c2 = c0/5 + 2c1/5 + 3c3/10 + c4/10`.
Every compatible distribution is the supplied vector plus
`t*(-1/5,-2/5,1,-3/10,-1/10)`. Nonnegativity gives `0<=t<=5/7`.
Its event probability is `4/7-2t/5`, so the exact interval is `[2/7,4/7]`.
The endpoint distributions are `(0,0,5/7,3/14,1/14)` and the supplied vector.

**An independent byte-boundary control.** For black/white stops `(0,0,0)` and
`(1,1,1)`, all channels equal the white probability. Observing linear8
`(128,128,128)` gives `[1/2,257/510)` under half-up rounding. The reported
closed-box interval is `[1/2,257/510]`; its upper endpoint actually rounds to
129. This demonstrates why the certificate's closure distinction matters.
