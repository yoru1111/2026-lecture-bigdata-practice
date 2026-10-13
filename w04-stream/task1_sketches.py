#!/usr/bin/env python3
"""Week 4 · Task 1 — Bloom filter, Flajolet-Martin, reservoir sampling.

Run:
    python3 task1_sketches.py --verify
"""

import argparse
import hashlib
import math
import random
import statistics


def _hash64(item, seed, index):
    """Return a deterministic 64-bit hash."""
    key = hashlib.sha256(
        f"{seed}:{index}".encode("utf-8")
    ).digest()

    digest = hashlib.blake2b(
        str(item).encode("utf-8"),
        digest_size=8,
        key=key,
    ).digest()

    return int.from_bytes(digest, "big")


class BloomFilter:
    """Membership filter using m bits and k hash functions."""

    def __init__(self, m, k, seed=246):
        if m <= 0 or k <= 0:
            raise ValueError("m and k must be positive")

        self.m = m
        self.k = k
        self.seed = seed
        self.bits = bytearray((m + 7) // 8)

    def _positions(self, item):
        for index in range(self.k):
            yield _hash64(item, self.seed, index) % self.m

    def add(self, item):
        for position in self._positions(item):
            self.bits[position // 8] |= 1 << (position % 8)

    def __contains__(self, item):
        return all(
            self.bits[position // 8] & (1 << (position % 8))
            for position in self._positions(item)
        )

    def expected_fp_rate(self, n_inserted):
        """Textbook approximation: (1 - exp(-k*n/m))**k."""
        if n_inserted < 0:
            raise ValueError("n_inserted must be nonnegative")

        return (
            1.0 - math.exp(-self.k * n_inserted / self.m)
        ) ** self.k


def flajolet_martin(stream, n_hashes=64, seed=246):
    """Estimate distinct count in one pass using bounded state."""
    if n_hashes <= 0:
        raise ValueError("n_hashes must be positive")

    maxima = [0] * n_hashes
    seen_any = False

    for item in stream:
        seen_any = True

        for index in range(n_hashes):
            value = _hash64(item, seed, index)

            if value == 0:
                zeros = 64
            else:
                zeros = (value & -value).bit_length() - 1

            maxima[index] = max(maxima[index], zeros)

    if not seen_any:
        return 0.0

    # Average the exponents within groups, then take the median
    # of the resulting group estimates.
    group_size = max(1, math.isqrt(n_hashes))
    estimates = []

    for start in range(0, n_hashes, group_size):
        group = maxima[start:start + group_size]
        mean_r = sum(group) / len(group)
        estimates.append(2.0 ** mean_r)

    return float(statistics.median(estimates))


def reservoir_sample(stream, k, seed=246):
    """Sample at most k items uniformly from an unknown-length stream."""
    if k < 0:
        raise ValueError("k must be nonnegative")
    if k == 0:
        return []

    rng = random.Random(seed)
    sample = []

    for count, item in enumerate(stream, start=1):
        if count <= k:
            sample.append(item)
        else:
            # Select this item with probability k/count.
            slot = rng.randrange(count)
            if slot < k:
                sample[slot] = item

    return sample


# ------------------------------------------------------------------- harness
def verify():
    fails = 0
    rng = random.Random(246)

    def check(label, ok, detail=""):
        nonlocal fails
        print(f"  {'ok  ' if ok else 'FAIL'}  {label:<46} {detail}")
        fails += not ok

    # --- Bloom: no false negatives, ever
    try:
        bf = BloomFilter(m=8192, k=5)
    except NotImplementedError:
        print("  BloomFilter is still a stub")
        return 1

    inserted = [f"item-{i}" for i in range(800)]
    for x in inserted:
        bf.add(x)

    check("no false negatives", all(x in bf for x in inserted))

    absent = [f"other-{i}" for i in range(20_000)]
    fp = sum(1 for x in absent if x in bf) / len(absent)
    predicted = bf.expected_fp_rate(len(inserted))
    close = abs(fp - predicted) < max(0.02, predicted * 0.5)

    check(
        "measured false-positive rate matches theory",
        close,
        f"measured {fp:.3%}, predicted {predicted:.3%}",
    )

    # --- Flajolet-Martin: a factor of two is what this method gives you
    try:
        distinct = 20_000
        stream = [
            f"k{rng.randrange(distinct)}"
            for _ in range(120_000)
        ]
        est = flajolet_martin(stream)
    except NotImplementedError:
        print("  flajolet_martin is still a stub")
        return 1

    true_distinct = len(set(stream))
    ratio = est / true_distinct

    check(
        "distinct estimate within a factor of 2",
        0.5 <= ratio <= 2.0,
        f"estimated {est:,.0f}, true {true_distinct:,} ({ratio:.2f}x)",
    )

    # --- Reservoir: uniform over many trials
    try:
        counts = [0] * 20
        trials = 4000

        for t in range(trials):
            sample = reservoir_sample(range(20), 5, seed=t)
            for i in sample:
                counts[i] += 1
    except NotImplementedError:
        print("  reservoir_sample is still a stub")
        return 1

    expected = trials * 5 / 20
    spread = (max(counts) - min(counts)) / expected

    check(
        "reservoir is uniform across items",
        spread < 0.15,
        f"spread {spread:.1%} around {expected:.0f}",
    )

    print(f"\n  {'all ok' if not fails else str(fails) + ' failed'}")
    return 1 if fails else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    raise SystemExit(verify() if args.verify else parser.print_help())
