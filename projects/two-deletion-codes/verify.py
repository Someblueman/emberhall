"""Zero-dependency offline verifier for two-deletion-correcting binary codebooks."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

DEFAULT_CODEBOOK = Path(__file__).resolve().parent / "codebook_12.txt"


def parse_words(text: str) -> list[str]:
    """Extract binary words from text, ignoring blank lines and # comments."""
    words: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if line:
            words.append(line)
    return words


def two_deletion_subsequences(word: str) -> dict[str, tuple[int, int]]:
    """Map each distinct (n-2)-bit subsequence of word to one witness pair (i, j)."""
    n = len(word)
    outputs: dict[str, tuple[int, int]] = {}
    for i in range(n):
        for j in range(i + 1, n):
            sub = word[:i] + word[i + 1 : j] + word[j + 1 :]
            if sub not in outputs:
                outputs[sub] = (i, j)
    return outputs


def verify_words(words: list[str], *, expected_length: int = 12) -> dict:
    """Verify distinctness, bit length, and disjoint two-deletion balls."""
    if expected_length < 3:
        raise ValueError(f"expected_length must be at least 3, got {expected_length}")
    if not words:
        raise ValueError("empty codebook: expected at least one word")

    seen_words: dict[str, int] = {}
    for idx, word in enumerate(words):
        if any(ch not in ("0", "1") for ch in word):
            raise ValueError(f"non-binary word at index {idx}: {word!r}")
        if len(word) != expected_length:
            raise ValueError(
                f"wrong length at index {idx}: got {len(word)}, expected {expected_length} ({word!r})"
            )
        if word in seen_words:
            raise ValueError(
                f"duplicate word {word!r} at indices {seen_words[word]} and {idx}"
            )
        seen_words[word] = idx

    owner: dict[str, tuple[str, tuple[int, int]]] = {}
    per_word_sizes: list[int] = []
    for word in words:
        subs = two_deletion_subsequences(word)
        per_word_sizes.append(len(subs))
        for sub, pair in subs.items():
            if sub in owner:
                other_word, other_pair = owner[sub]
                raise ValueError(
                    f"collision on {sub}: {other_word} (delete {other_pair}) "
                    f"and {word} (delete {pair})"
                )
            owner[sub] = (word, pair)

    pairs_per_word = expected_length * (expected_length - 1) // 2
    half_0 = sum(1 for w in words if w.endswith("0"))
    half_1 = len(words) - half_0
    return {
        "count": len(words),
        "length": expected_length,
        "pairs_per_word": pairs_per_word,
        "total_subsequences": len(owner),
        "min_ball_size": min(per_word_sizes),
        "max_ball_size": max(per_word_sizes),
        "half_0": half_0,
        "half_1": half_1,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "path",
        nargs="?",
        default=str(DEFAULT_CODEBOOK),
        help="Path to plain-text binary codebook (one word per line).",
    )
    parser.add_argument(
        "--length",
        type=int,
        default=12,
        help="Required bit length of each word (default: 12).",
    )
    parser.add_argument(
        "--min-size",
        type=int,
        default=None,
        help="Optional minimum required codebook size.",
    )
    args = parser.parse_args(argv)

    path = Path(args.path)
    try:
        words = parse_words(path.read_text(encoding="utf-8"))
        report = verify_words(words, expected_length=args.length)
        if args.min_size is not None and report["count"] < args.min_size:
            raise ValueError(
                f"codebook size {report['count']} is below required minimum {args.min_size}"
            )
    except (OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    print(
        f"PASS: {report['count']} words of length {report['length']} "
        f"(split 0:{report['half_0']}, 1:{report['half_1']}); "
        f"{report['pairs_per_word']} deletion pairs/word; "
        f"{report['total_subsequences']} distinct {report['length'] - 2}-bit outputs "
        f"(ball sizes {report['min_ball_size']}..{report['max_ball_size']})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
