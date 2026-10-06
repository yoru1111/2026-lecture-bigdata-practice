#!/usr/bin/env python3
"""One-pass minhash and banded LSH. Uneven band division raises ValueError."""
import argparse
from itertools import combinations


def jaccard(a, b):
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def minhash_signatures(columns, hashes, n_rows):
    signatures = [[float('inf')] * len(hashes) for _ in columns]
    for r in range(n_rows):
        row_hashes = [h(r) for h in hashes]
        for c, rows in enumerate(columns):
            if r in rows:
                for h, value in enumerate(row_hashes):
                    signatures[c][h] = min(signatures[c][h], value)
    return signatures


def lsh_candidates(signatures, bands):
    if not isinstance(bands, int) or bands <= 0:
        raise ValueError('bands must be a positive integer')
    if not signatures:
        return set()
    length = len(signatures[0])
    if any(len(sig) != length for sig in signatures):
        raise ValueError('all signatures must have the same length')
    if length == 0 or length % bands:
        raise ValueError('signature length must be positive and divisible by bands')
    rows_per_band = length // bands
    candidates = set()
    for band in range(bands):
        buckets = {}
        start = band * rows_per_band
        for c, sig in enumerate(signatures):
            key = tuple(sig[start:start + rows_per_band])
            buckets.setdefault(key, []).append(c)
        for bucket in buckets.values():
            candidates.update(combinations(bucket, 2))
    return candidates


BOOK = [[1, 0, 0, 1],
        [0, 0, 1, 0],
        [0, 1, 0, 1],
        [1, 0, 1, 1],
        [0, 0, 1, 0]]
BOOK_HASHES = [lambda r: (r + 1) % 5, lambda r: (3 * r + 1) % 5]


def columns_from_matrix(matrix):
    n_rows, n_cols = len(matrix), len(matrix[0])
    return [{r for r in range(n_rows) if matrix[r][c]} for c in range(n_cols)]


def verify():
    fails = 0

    def check(label, got, want):
        nonlocal fails
        ok = got == want
        print(f"  {'ok  ' if ok else 'FAIL'}  {label:<44} {got}"
              + ("" if ok else f"\n{'':>54}want {want}"))
        fails += not ok

    cols = columns_from_matrix(BOOK)
    check("jaccard(S1, S4)", round(jaccard(cols[0], cols[3]), 4), round(2 / 3, 4))
    check("jaccard(S1, S2)", jaccard(cols[0], cols[1]), 0.0)
    check("jaccard on empty sets", jaccard(set(), set()), 0)
    sig = minhash_signatures(cols, BOOK_HASHES, len(BOOK))
    check("signature of S1", sig[0], [1, 0])
    check("signature of S2", sig[1], [3, 2])
    check("signature of S3", sig[2], [0, 0])
    check("signature of S4", sig[3], [1, 0])
    cands = lsh_candidates([[1, 0], [3, 2], [0, 0], [1, 0]], bands=2)
    check("S1 and S4 are candidates", (0, 3) in cands, True)
    check("S1 and S2 are not", (0, 1) in cands, False)
    print(f"\n  {'all ok' if not fails else str(fails) + ' failed'}")
    if not fails:
        print("  Note that S1 and S4 agree in both signature positions, which "
              "estimates\n  their similarity as 1.0 when it is actually 2/3. "
              "Two hashes is not many.")
    return 1 if fails else 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--verify", action="store_true")
    a = p.parse_args()
    raise SystemExit(verify() if a.verify else p.print_help())
