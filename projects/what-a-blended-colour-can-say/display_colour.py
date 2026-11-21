"""Explicit byte encodings for declared linear-light sRGB coordinates.

No floating-point arithmetic enters quantization or inverse enclosures.
See DISPLAY.md for the transfer, half-up rule, and unsupported pipelines.
"""

from fractions import Fraction as F
from functools import lru_cache
from typing import Sequence

MODES = ("srgb8", "linear8")
LINEAR_CUTOFF = F(7827, 2500000)  # 0.0031308


def _mode(mode: str) -> None:
    if mode not in MODES:
        raise ValueError(f"Unsupported encoding {mode!r}; choose one of {MODES}")


def _above_boundary(x: F, encoded: F, mode: str) -> bool:
    if mode == "linear8":
        return x >= encoded
    if x <= LINEAR_CUTOFF:
        return x * F(323, 25) >= encoded
    # 1.055*x**(5/12)-0.055 >= encoded; both sides are positive.
    return x**5 >= ((200 * encoded + 11) / 211)**12


def encode_channel(x: F, mode: str = "srgb8") -> int:
    """Return round-half-up(255 * transfer(x)) exactly, for rational x."""
    _mode(mode)
    x = F(x)
    if not 0 <= x <= 1:
        raise ValueError("Linear channel must lie in [0, 1]")
    low, high = 0, 256
    while high - low > 1:
        mid = (low + high) // 2
        if _above_boundary(x, F(2 * mid - 1, 510), mode):
            low = mid
        else:
            high = mid
    return low


def encode_rgb(rgb: Sequence[F], mode: str = "srgb8") -> tuple[int, int, int]:
    if len(rgb) != 3:
        raise ValueError("RGB must have three channels")
    return tuple(encode_channel(x, mode) for x in rgb)


def hex_rgb(rgb: Sequence[int]) -> str:
    if len(rgb) != 3 or any(type(x) is not int or not 0 <= x <= 255 for x in rgb):
        raise ValueError("RGB bytes must be three integers in [0, 255]")
    return "#" + "".join(f"{x:02x}" for x in rgb)


def _decode_enclosure(encoded: F) -> tuple[F, F]:
    if encoded <= F(809, 20000):
        x = encoded / F(323, 25)
        return x, x
    # Enclose ((encoded+.055)/1.055)**(12/5) by 64 exact bisections.
    power = ((200 * encoded + 11) / 211)**12
    low, high = F(0), F(1)
    for _ in range(64):
        mid = (low + high) / 2
        if mid**5 == power:
            return mid, mid
        if mid**5 < power:
            low = mid
        else:
            high = mid
    return low, high


@lru_cache(maxsize=512)
def channel_box(byte: int, mode: str = "srgb8") -> tuple[F, F]:
    """Closed rational outer enclosure of all linear values yielding this byte."""
    _mode(mode)
    if type(byte) is not int or not 0 <= byte <= 255:
        raise ValueError("Byte must be an integer in [0, 255]")
    low, high = max(F(0), F(2 * byte - 1, 510)), min(F(1), F(2 * byte + 1, 510))
    if mode == "linear8":
        return low, high
    return _decode_enclosure(low)[0], _decode_enclosure(high)[1]


def observation_box(rgb: Sequence[int], mode: str = "srgb8") -> tuple[tuple[F, ...], tuple[F, ...]]:
    if len(rgb) != 3:
        raise ValueError("RGB must have three channels")
    pairs = [channel_box(x, mode) for x in rgb]
    return tuple(x[0] for x in pairs), tuple(x[1] for x in pairs)
