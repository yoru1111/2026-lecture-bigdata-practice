#!/usr/bin/env python3
"""Week 4 · Task 3 — Same memory, fewer mistakes.

Textbook §4.4 (Bloom filters), §4.5 (counting distinct).

`NaiveFilter` is a membership filter in a fixed number of bits. It works. It
also makes far more mistakes than it has to with the memory it was given, and
it does so for a reason you can find by reading §4.4.2 and doing one derivative.

You get **exactly the same number of bits**. Make fewer mistakes.

    python3 bench.py
    python3 bench.py --yours

The rule that makes this interesting: a false negative is not allowed. Ever.
The whole point of this structure is that "no" means no. A filter that gets a
better score by occasionally forgetting something it was given has not improved
anything, it has broken the contract.
"""
import hashlib


class NaiveFilter:
    """One hash function, and the bits it was given."""

    def __init__(self, n_bits, seed=246):
        self.n_bits = n_bits
        self.seed = seed
        self.bits = bytearray(n_bits)

    def _index(self, item):
        d = hashlib.blake2b(str(item).encode(), digest_size=8,
                            key=str(self.seed).encode()).digest()
        return int.from_bytes(d, "big") % self.n_bits

    def add(self, item):
        self.bits[self._index(item)] = 1

    def __contains__(self, item):
        return bool(self.bits[self._index(item)])

    def memory_bits(self):
        return self.n_bits


class YourFilter:
    """Packed Bloom filter with seven hashes and accounted storage."""

    __slots__ = ("n_bits", "seed", "bits")

    def __init__(self, n_bits, seed=246):
        if n_bits <= 2048:
            raise ValueError("The budget is too small for this implementation")

        # Reserve 2048 bits for the object and its configuration.
        # Use whole bytes for the remaining packed bit array.
        n_bytes = (n_bits - 2048) // 8

        self.n_bits = n_bytes * 8
        self.seed = seed
        self.bits = bytearray(n_bytes)

        if self.memory_bits() > n_bits:
            raise RuntimeError("Filter storage exceeds the supplied budget")

    def _positions(self, item):
        data = str(item).encode("utf-8")

        for index in range(7):
            key = f"{self.seed}:{index}".encode("utf-8")
            digest = hashlib.blake2b(
                data,
                digest_size=8,
                key=key,
            ).digest()

            yield int.from_bytes(digest, "big") % self.n_bits

    def add(self, item):
        for position in self._positions(item):
            self.bits[position // 8] |= 1 << (position % 8)

    def __contains__(self, item):
        for position in self._positions(item):
            if not (
                self.bits[position // 8] & (1 << (position % 8))
            ):
                return False

        return True

    def memory_bits(self):
        import sys

        # Count retained instance storage:
        # object, packed array including overhead, and configuration.
        total_bytes = (
            sys.getsizeof(self)
            + sys.getsizeof(self.bits)
            + sys.getsizeof(self.n_bits)
            + sys.getsizeof(self.seed)
        )
        return total_bytes * 8
