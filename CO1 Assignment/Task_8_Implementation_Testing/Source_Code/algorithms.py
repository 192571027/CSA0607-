"""
algorithms.py - Three distinct strategies for locating a registration number.

  1. linear_search            : ITERATIVE  - brute force sequential scan (no preprocessing)
  2. binary_search_recursive  : RECURSIVE  - decrease-and-conquer on a sorted array
                                (preprocessing: merge_sort, divide-and-conquer)
  3. HashIndex                : ITERATIVE  - hashing with separate chaining (space-time trade-off)
                                (preprocessing: build the table in O(n))

Every search has two forms:
  * a plain version used for TIMING (no instrumentation overhead)
  * a *_counted version that returns (position, comparisons) used for operation counts
"""
import sys

sys.setrecursionlimit(10_000)


# --------------------------------------------------------------------------
# 1. Linear search (iterative, brute force)
# --------------------------------------------------------------------------
def linear_search(a, key):
    """Return index of key in unsorted list a, or -1."""
    for i, v in enumerate(a):
        if v == key:
            return i
    return -1


def linear_search_counted(a, key):
    comps = 0
    for i, v in enumerate(a):
        comps += 1                      # basic operation: a[i] == key
        if v == key:
            return i, comps
    return -1, comps


# --------------------------------------------------------------------------
# 2. Binary search (recursive, decrease-and-conquer) + merge sort preprocessing
# --------------------------------------------------------------------------
def binary_search_recursive(a, key, lo=0, hi=None):
    """Return index of key in SORTED list a, or -1."""
    if hi is None:
        hi = len(a) - 1
    if lo > hi:                          # base case: empty sub-array
        return -1
    mid = (lo + hi) // 2
    v = a[mid]
    if v == key:
        return mid
    if key < v:
        return binary_search_recursive(a, key, lo, mid - 1)
    return binary_search_recursive(a, key, mid + 1, hi)


def binary_search_counted(a, key, lo=0, hi=None, _c=0):
    """Counts one three-way comparison (key vs a[mid]) per recursive call."""
    if hi is None:
        hi = len(a) - 1
    if lo > hi:
        return -1, _c
    mid = (lo + hi) // 2
    _c += 1                              # basic operation: compare key with a[mid]
    v = a[mid]
    if v == key:
        return mid, _c
    if key < v:
        return binary_search_counted(a, key, lo, mid - 1, _c)
    return binary_search_counted(a, key, mid + 1, hi, _c)


def merge_sort(a):
    """Top-down merge sort. Returns (sorted_list, comparisons). T(n)=2T(n/2)+Theta(n)."""
    n = len(a)
    if n <= 1:
        return list(a), 0
    mid = n // 2
    left, cl = merge_sort(a[:mid])
    right, cr = merge_sort(a[mid:])
    out = []
    i = j = 0
    nl, nr = len(left), len(right)
    c = 0
    while i < nl and j < nr:
        c += 1                           # basic operation of sorting
        if left[i] <= right[j]:
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    if i < nl:
        out.extend(left[i:])
    if j < nr:
        out.extend(right[j:])
    return out, cl + cr + c


def merge_sorted(a, b):
    """Linear-time merge of two sorted lists (used for the daily batch update)."""
    out = []
    i = j = 0
    na, nb = len(a), len(b)
    while i < na and j < nb:
        if a[i] <= b[j]:
            out.append(a[i]); i += 1
        else:
            out.append(b[j]); j += 1
    out.extend(a[i:]); out.extend(b[j:])
    return out


# --------------------------------------------------------------------------
# 3. Hash index with separate chaining (iterative)
# --------------------------------------------------------------------------
def next_prime(x):
    def is_prime(p):
        if p < 2:
            return False
        if p % 2 == 0:
            return p == 2
        d = 3
        while d * d <= p:
            if p % d == 0:
                return False
            d += 2
        return True
    while not is_prime(x):
        x += 1
    return x


_KNUTH = 2654435761            # Knuth multiplicative constant (~2^32 / golden ratio)


class HashIndex:
    """Hash table (separate chaining). Chains store RECORD INDICES into the records list,
    exactly like a database index that points to a row; a lookup therefore compares
    records[idx] with the key. Load factor alpha = n / m is kept near 0.75."""

    def __init__(self, records, load=0.75):
        self.records = records
        self.m = next_prime(int(len(records) / load) + 1)
        self.table = [None] * self.m
        self.build()

    def _h(self, key):
        return ((key * _KNUTH) & 0xFFFFFFFF) % self.m

    def build(self):
        t, m, rec = self.table, self.m, self.records
        for i, k in enumerate(rec):
            h = ((k * _KNUTH) & 0xFFFFFFFF) % m
            b = t[h]
            if b is None:
                t[h] = [i]
            else:
                b.append(i)

    def insert(self, key):
        """Append a new record and index it: O(1) expected."""
        idx = len(self.records)
        self.records.append(key)
        h = self._h(key)
        if self.table[h] is None:
            self.table[h] = [idx]
        else:
            self.table[h].append(idx)

    def search(self, key):
        b = self.table[((key * _KNUTH) & 0xFFFFFFFF) % self.m]
        if b is None:
            return -1
        rec = self.records
        for idx in b:
            if rec[idx] == key:
                return idx
        return -1

    def search_counted(self, key):
        """Returns (index, key comparisons inside the chain)."""
        b = self.table[self._h(key)]
        if b is None:
            return -1, 0
        c = 0
        for idx in b:
            c += 1                       # basic operation: records[idx] == key
            if self.records[idx] == key:
                return idx, c
        return -1, c

    def chain_stats(self):
        lens = [len(b) for b in self.table if b is not None]
        return {"m": self.m, "n": len(self.records), "alpha": len(self.records) / self.m,
                "used_buckets": len(lens), "max_chain": max(lens) if lens else 0}
