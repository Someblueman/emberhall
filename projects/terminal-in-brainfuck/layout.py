"""Shared tape addresses for the generator and its control emitter."""

ROWS = 24
COLS = 40
SB = 64               # first screen cell
GUARD = SB - 1        # permanent zero
H = 6                 # row header size
STRIDE = H + COLS * 6  # 246: character and encoded attribute triples
TAPE_SIZE = 6000

# home cells
CUR, PROW, COL, TOP, DROW = 0, 1, 2, 3, 4
M255, M254 = 5, 6
G = list(range(7, 15))            # general temps G0..G7 = 7..14
LT_W0, LT_W1, LT_Q, LT_TG = 15, 16, 17, 18
LT_BIT = list(range(19, 27))      # 8 bit cells
LT_EQF, LT_TMP, LT_TMP2, LT_F, LT_F2 = 28, 29, 30, 31, 32
DSP_T, DSP_DONE, DSP_F, DSP_F2, DSP_TMP = 33, 34, 35, 36, 37
FG, BG, BRIGHT, ATTR = range(56, 60)
SGR_VALID, SGR_MATCH, SGR_TEMP = range(60, 63)


def rcnt(r):
    return SB + r * STRIDE


def rcol(r):
    return rcnt(r) + 1


def rval(r):
    return rcnt(r) + 3


def data(r, c):
    return SB + r * STRIDE + H + 6 * c + 2


def attribute(r, c):
    # Store attribute + 1: even black-on-black is nonzero for seek-home.
    return data(r, c) + 3

