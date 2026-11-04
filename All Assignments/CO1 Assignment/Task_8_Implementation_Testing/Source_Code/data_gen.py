"""Reproducible dataset generator for registration numbers."""
import random

SIZES = [1_000, 10_000, 100_000, 1_000_000]
SEED = 2026


def make_dataset(n, seed=SEED):
    """n UNIQUE 9-digit registration numbers in random (unsorted) storage order."""
    rng = random.Random(seed + n)
    return rng.sample(range(100_000_000, 1_000_000_000), n)


def make_queries(data, q, seed=SEED):
    """q successful keys (present) and q unsuccessful keys (guaranteed absent)."""
    rng = random.Random(seed * 7 + len(data))
    present = set(data)
    hits = [data[rng.randrange(len(data))] for _ in range(q)]
    misses = []
    while len(misses) < q:
        k = rng.randrange(100_000_000, 1_000_000_000)
        if k not in present:
            misses.append(k)
    return hits, misses
