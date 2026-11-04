"""
KartIQ - Module 3: Order Lookup by timestamp using Binary Search.

  * standard_search  - returns ANY matching position
  * first_occurrence - returns the FIRST (leftmost) matching position
  * linear_search    - baseline

Run:  python3 binary_search.py
"""
import math
import os
import random

# Output of Module 1 (sorted, stable)
SORTED_ORDERS = [(101, "O4"), (102, "O2"), (102, "O5"),
                 (103, "O6"), (105, "O1"), (105, "O3")]


class Counter:
    def __init__(self):
        self.comparisons = 0


def standard_search(arr, key, cnt, trace=False):
    """Classic binary search; one three-way comparison per iteration."""
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        cnt.comparisons += 1
        t = arr[mid][0]
        if trace:
            print(f"  lo={lo} hi={hi} mid={mid} arr[mid]={t}  key={key}", end="")
        if t == key:
            if trace: print("  -> found")
            return mid
        if t < key:
            if trace: print("  -> go right")
            lo = mid + 1
        else:
            if trace: print("  -> go left")
            hi = mid - 1
    return -1


def first_occurrence(arr, key, cnt, trace=False):
    """Leftmost match. Invariant: every index < lo has timestamp < key and
    every index >= hi has timestamp >= key.  Never stops early on equality."""
    lo, hi = 0, len(arr)                 # search window [lo, hi)
    while lo < hi:
        mid = (lo + hi) // 2
        cnt.comparisons += 1
        t = arr[mid][0]
        if trace:
            print(f"  lo={lo} hi={hi} mid={mid} arr[mid]={t}  key={key}", end="")
        if t < key:
            if trace: print("  -> < key : lo = mid+1")
            lo = mid + 1
        else:
            if trace: print("  -> >= key: hi = mid")
            hi = mid
    cnt.comparisons += 1                 # final equality check
    if lo < len(arr) and arr[lo][0] == key:
        return lo
    return -1


def linear_search(arr, key, cnt):
    for i, (t, _) in enumerate(arr):
        cnt.comparisons += 1
        if t == key:
            return i
    return -1


class VirtualOrders:
    """Sorted list of n orders created on the fly (no memory): timestamp of
    position i is i // 3, so every timestamp appears three times."""
    def __init__(self, n):
        self.n = n
    def __len__(self):
        return self.n
    def __getitem__(self, i):
        return (i // 3, f"O{i}")


def main():
    print("=" * 72)
    print("MODULE 3 - BINARY SEARCH ON THE SORTED OUTPUT OF MODULE 1")
    print("=" * 72)
    print("Sorted list:", SORTED_ORDERS)

    for key in (102, 105, 104):
        print(f"\n--- standard binary search for timestamp {key} ---")
        c = Counter()
        idx = standard_search(SORTED_ORDERS, key, c, trace=True)
        print(f"  result index={idx}, order={SORTED_ORDERS[idx] if idx >= 0 else None}, "
              f"comparisons={c.comparisons}")

    print("\nStandard search returns an ARBITRARY match among duplicates.")
    print("Now the modified search that returns the FIRST order:")
    for key in (102, 105, 101, 103, 104, 99, 200):
        print(f"\n--- first_occurrence for timestamp {key} ---")
        c = Counter()
        idx = first_occurrence(SORTED_ORDERS, key, c, trace=True)
        print(f"  result index={idx}, order={SORTED_ORDERS[idx] if idx >= 0 else 'NOT FOUND'}, "
              f"comparisons={c.comparisons}")

    # --------------------------------------------------------------------
    print("\n" + "=" * 72)
    print("VERIFICATION against a brute-force scan on random sorted data")
    print("=" * 72)
    random.seed(3)
    ok = True
    for trial in range(2000):
        n = random.randint(0, 60)
        arr = sorted(((random.randint(0, 20), f"O{i}") for i in range(n)),
                     key=lambda r: r[0])
        key = random.randint(-1, 21)
        expect = next((i for i, r in enumerate(arr) if r[0] == key), -1)
        got = first_occurrence(arr, key, Counter())
        if got != expect:
            ok = False
            print("MISMATCH", arr, key, got, expect)
            break
    print("2000 random tests passed:", ok)

    # --------------------------------------------------------------------
    print("\n" + "=" * 72)
    print("WHY SORTING IS ESSENTIAL: binary search on UNSORTED data")
    print("=" * 72)
    unsorted = [(105, "O1"), (102, "O2"), (105, "O3"), (101, "O4"), (102, "O5"), (103, "O6")]
    c = Counter()
    print("search 101 in the unsorted arrival-order list ->",
          standard_search(unsorted, 101, c), "(101 IS present at index 3 -> wrongly missed)")
    c = Counter()
    print("search 101 in the sorted list                ->",
          standard_search(SORTED_ORDERS, 101, c))

    # --------------------------------------------------------------------
    print("\n" + "=" * 72)
    print("PRODUCTION SCALE: n = 10,000,000 orders (virtual sorted array)")
    print("=" * 72)
    N = 10_000_000
    arr = VirtualOrders(N)
    worst_std, worst_first = 0, 0
    random.seed(9)
    keys = [random.randint(-5, N // 3 + 5) for _ in range(20000)]
    keys += [-1, 0, 1, N // 3, N // 3 + 1, (N - 1) // 3]
    for k in keys:
        c1, c2 = Counter(), Counter()
        standard_search(arr, k, c1)
        first_occurrence(arr, k, c2)
        worst_std = max(worst_std, c1.comparisons)
        worst_first = max(worst_first, c2.comparisons)
    print(f"floor(lg n) + 1                     = {math.floor(math.log2(N)) + 1}")
    print(f"ceil(lg n) + 1                      = {math.ceil(math.log2(N)) + 1}")
    print(f"max comparisons observed (standard) = {worst_std}")
    print(f"max comparisons observed (first)    = {worst_first}")
    c = Counter(); idx = first_occurrence(arr, 1_234_567, c)
    print(f"first_occurrence(1,234,567) -> index {idx} (expected {1_234_567*3}), "
          f"comparisons {c.comparisons}")
    print(f"linear search worst case             = {N:,} comparisons "
          f"(average if present ~ {N//2:,})")
    print(f"speed-up in comparisons (worst)      = {N / worst_std:,.0f} x")

    # --------------------------------------------------------------------
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        ns = [2 ** k for k in range(4, 25)]
        plt.figure(figsize=(7, 4.5))
        plt.plot(ns, [math.floor(math.log2(n)) + 1 for n in ns], "o-", label="binary search (worst)")
        plt.plot(ns, ns, "s--", label="linear search (worst)")
        plt.xscale("log", base=2); plt.yscale("log")
        plt.axvline(10_000_000, color="gray", ls=":")
        plt.text(10_000_000, 3, " n = 10M\n 24 vs 10,000,000", fontsize=8)
        plt.xlabel("number of orders n"); plt.ylabel("worst-case comparisons")
        plt.title("Order lookup: binary vs linear search")
        plt.legend(); plt.grid(True, which="both", alpha=0.3); plt.tight_layout()
        out = os.path.join(os.path.dirname(__file__), "..", "Report",
                           "binary_search_comparisons.png")
        plt.savefig(out, dpi=150)
        print("\nGraph saved to Report/binary_search_comparisons.png")
    except ImportError:
        print("matplotlib not installed - graph skipped")


if __name__ == "__main__":
    main()
