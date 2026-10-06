#!/usr/bin/env python3
"""Minhash + LSH candidate generation, followed by counted exact verification."""
import hashlib
import math
import pickle
import random


class BruteForce:
    """Correct, and quadratic."""

    def __init__(self, threshold):
        self.threshold = threshold

    def find(self, docs, similarity):
        out = set()
        for i in range(len(docs)):
            for j in range(i + 1, len(docs)):
                if similarity(docs[i], docs[j]) >= self.threshold:
                    out.add((i, j))
        return out


class YourFinder:
    """160 hashes / 40 bands / 4 rows by default.

    Optional settings permit controlled banding experiments without editing
    the harness. Affine hash functions approximate independent minhashing;
    the ideal LSH probability formula is not a recall guarantee.
    """

    def __init__(self, threshold, num_hashes=160, bands=40, seed=42):
        if not math.isfinite(threshold) or not 0 <= threshold <= 1:
            raise ValueError('threshold must be between 0 and 1')
        if not isinstance(num_hashes, int) or num_hashes <= 0:
            raise ValueError('num_hashes must be a positive integer')
        if not isinstance(bands, int) or bands <= 0 or num_hashes % bands:
            raise ValueError('bands must be positive and divide num_hashes')
        self.threshold = threshold
        self.num_hashes = num_hashes
        self.bands = bands
        self.rows_per_band = num_hashes // bands
        self.prime = (1 << 61) - 1
        rng = random.Random(seed)
        self.coefficients = [
            (rng.randrange(1, self.prime), rng.randrange(self.prime))
            for _ in range(num_hashes)
        ]

    def find(self, docs, similarity):
        if len(docs) < 2:
            return set()
        # At threshold zero every pair qualifies; LSH filtering is invalid.
        if self.threshold == 0:
            return BruteForce(self.threshold).find(docs, similarity)

        # Construct row -> columns postings. No document-pair comparisons here.
        postings = {}
        for c, doc in enumerate(docs):
            for shingle in doc:
                postings.setdefault(shingle, []).append(c)

        signatures = [[self.prime] * self.num_hashes for _ in docs]
        for shingle, columns in postings.items():
            # Stable digest for ordinary Python string/int/tuple shingles.
            payload = pickle.dumps(shingle, protocol=4)
            x = int.from_bytes(hashlib.blake2b(payload, digest_size=16).digest(),
                               'big') % self.prime
            values = [(a * x + b) % self.prime
                      for a, b in self.coefficients]
            for c in columns:
                sig = signatures[c]
                for h, value in enumerate(values):
                    if value < sig[h]:
                        sig[h] = value
        del postings

        out = set()
        seen = set()
        for band in range(self.bands):
            buckets = {}
            start = band * self.rows_per_band
            end = start + self.rows_per_band
            for j, sig in enumerate(signatures):
                # Empty sets have Jaccard 0 under Task 1's convention.
                if not docs[j]:
                    continue
                key = tuple(sig[start:end])
                bucket = buckets.setdefault(key, [])
                for i in bucket:
                    pair = (i, j)
                    if pair not in seen:
                        seen.add(pair)
                        if similarity(docs[i], docs[j]) >= self.threshold:
                            out.add(pair)
                bucket.append(j)
        return out
