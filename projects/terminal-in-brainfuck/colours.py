"""Emit the frozen, atomic two-parameter SGR subset on the tape."""
from layout import ATTR, BG, BRIGHT, FG, G, SGR_MATCH, SGR_TEMP, SGR_VALID

SUPPORTED = (0, 1, 22, *range(30, 38), 39, *range(40, 48), 49)


def sgr(b, first, second, separator):
    # Validate both parameters before touching any persistent colour state.
    def validate(parameter):
        b.clear(SGR_MATCH)
        for value in SUPPORTED:
            b.if_eq(parameter, value, lambda: b.setv(SGR_MATCH, 1),
                    G[2], G[0], G[1])
        b.is_zero(SGR_MATCH, SGR_TEMP, G[0])
        b.if_flag(SGR_TEMP, lambda: b.clear(SGR_VALID))

    def apply(parameter):
        def reset():
            b.setv(FG, 7)
            b.clear(BG)
            b.clear(BRIGHT)
        actions = {0: reset, 1: lambda: b.setv(BRIGHT, 1),
                   22: lambda: b.clear(BRIGHT), 39: lambda: b.setv(FG, 7),
                   49: lambda: b.clear(BG)}
        actions.update({30 + n: lambda n=n: b.setv(FG, n) for n in range(8)})
        actions.update({40 + n: lambda n=n: b.setv(BG, n) for n in range(8)})
        for value, action in actions.items():
            b.if_eq(parameter, value, action, G[2], G[0], G[1])

    b.setv(SGR_VALID, 1)
    validate(first)
    b.copy(separator, SGR_TEMP, G[0])
    b.if_flag(SGR_TEMP, lambda: validate(second))

    def accepted():
        apply(first)
        b.copy(separator, SGR_TEMP, G[0])
        b.if_flag(SGR_TEMP, lambda: apply(second))
        b.setv(ATTR, 1)
        for source, weight in ((FG, 1), (BG, 8), (BRIGHT, 64)):
            b.copy(source, G[0], G[1])
            b.go(G[0])
            b.emit('[')
            b.add(ATTR, weight)
            b.add(G[0], -1)
            b.emit(']')
    b.if_flag(SGR_VALID, accepted)
