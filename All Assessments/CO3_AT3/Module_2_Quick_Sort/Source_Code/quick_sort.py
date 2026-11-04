"""
KartIQ - Module 2: Live Seller Leaderboard using Quick Sort.

Compares three pivot strategies on nearly sorted data:
    first   - current implementation (pivot = first element)
    median3 - median of first, middle and last element (proposed)
    random  - uniformly random pivot

Quick sort is implemented iteratively with an explicit stack (smaller side
processed first for the proposed variants) so that the O(n) recursion depth
of the first-element pivot cannot crash the interpreter.

Run:  python3 quick_sort.py
"""
import math
import os
import random

SAMPLE_SCORES = [42, 17, 63, 8, 55, 29]


class Stats:
    def __init__(self):
        self.comparisons = 0
        self.max_depth = 0


# --------------------------------------------------------------------------
# Partition (Lomuto style, pivot is moved to a[lo] first)
# --------------------------------------------------------------------------
def partition(a, lo, hi, stats, verbose=False):
    pivot = a[lo]
    i = lo
    if verbose:
        print(f"  pivot = {pivot}   array = {a[lo:hi+1]}")
    for j in range(lo + 1, hi + 1):
        stats.comparisons += 1
        if a[j] < pivot:
            i += 1
            a[i], a[j] = a[j], a[i]
            if verbose:
                print(f"  j={j}: {a[i]:>2} < {pivot} -> i={i}, swap  -> {a[lo:hi+1]}")
        elif verbose:
            print(f"  j={j}: {a[j]:>2} >= {pivot} -> no swap            -> {a[lo:hi+1]}")
    a[lo], a[i] = a[i], a[lo]
    if verbose:
        print(f"  place pivot: swap a[{lo}] and a[{i}]  -> {a[lo:hi+1]}  (pivot index {i})")
    return i


def choose_pivot(a, lo, hi, strategy, stats):
    """Move the chosen pivot to a[lo]."""
    if strategy == "first":
        return
    if strategy == "random":
        p = random.randint(lo, hi)
    elif strategy == "median3":
        mid = (lo + hi) // 2
        x, y, z = a[lo], a[mid], a[hi]
        stats.comparisons += 3            # three comparisons to find the median
        if (x <= y <= z) or (z <= y <= x):
            p = mid
        elif (y <= x <= z) or (z <= x <= y):
            p = lo
        else:
            p = hi
    else:
        raise ValueError(strategy)
    a[lo], a[p] = a[p], a[lo]


def quick_sort(a, strategy="first", stats=None, cutoff=1):
    """Iterative quick sort. Returns Stats."""
    stats = stats or Stats()
    stack = [(0, len(a) - 1, 1)]
    while stack:
        lo, hi, depth = stack.pop()
        stats.max_depth = max(stats.max_depth, depth)
        if hi - lo + 1 <= cutoff:
            continue
        choose_pivot(a, lo, hi, strategy, stats)
        p = partition(a, lo, hi, stats)
        left, right = (lo, p - 1), (p + 1, hi)
        # push the LARGER side first so the smaller side is handled next
        if (left[1] - left[0]) > (right[1] - right[0]):
            stack.append((*left, depth + 1)); stack.append((*right, depth + 1))
        else:
            stack.append((*right, depth + 1)); stack.append((*left, depth + 1))
    return stats


def nearly_sorted(n, swaps, seed):
    rnd = random.Random(seed)
    a = list(range(1, n + 1))
    for _ in range(swaps):
        i = rnd.randrange(n - 1)
        a[i], a[i + 1] = a[i + 1], a[i]          # small local disturbance
    return a


def main():
    print("=" * 72)
    print("MODULE 2 - ONE PARTITION STEP ON THE SAMPLE SCORES (first-element pivot)")
    print("=" * 72)
    a = list(SAMPLE_SCORES)
    print("Input:", a)
    st = Stats()
    p = partition(a, 0, len(a) - 1, st, verbose=True)
    print(f"Result: left part {a[:p]} | pivot {a[p]} | right part {a[p+1:]}")
    print(f"Comparisons in this partition: {st.comparisons}  (= n - 1)")

    b = list(SAMPLE_SCORES)
    s = quick_sort(b, "first")
    print("\nFull sort of the sample:", b, "comparisons:", s.comparisons)

    print("\n" + "=" * 72)
    print("EXPERIMENT - nearly sorted data (1% of positions disturbed by adjacent swaps)")
    print("=" * 72)
    random.seed(5)
    sizes = [250, 500, 1000, 2000, 4000, 8000]
    table = []
    print(f"{'n':>6} {'first':>12} {'median3':>10} {'random':>10} {'n(n-1)/2':>12} "
          f"{'n lg n':>10} {'depth first':>12} {'depth med3':>11}")
    for n in sizes:
        data = nearly_sorted(n, max(1, n // 100), seed=n)
        r = {}
        for strat in ("first", "median3", "random"):
            d = list(data)
            s = quick_sort(d, strat)
            assert d == sorted(data), strat
            r[strat] = s
        table.append((n, r["first"].comparisons, r["median3"].comparisons,
                      r["random"].comparisons))
        print(f"{n:>6} {r['first'].comparisons:>12,} {r['median3'].comparisons:>10,} "
              f"{r['random'].comparisons:>10,} {n*(n-1)//2:>12,} {n*math.log2(n):>10,.0f} "
              f"{r['first'].max_depth:>12} {r['median3'].max_depth:>11}")

    print("\nFully sorted and reverse-sorted input (n = 2000):")
    for name, data in (("sorted", list(range(2000))), ("reverse", list(range(2000, 0, -1)))):
        out = []
        for strat in ("first", "median3", "random"):
            d = list(data)
            out.append(f"{strat}={quick_sort(d, strat).comparisons:,}")
        print(f"  {name:8}", "  ".join(out))

    print("\n" + "=" * 72)
    print("PRODUCTION ESTIMATE (n = 100,000 sellers, nearly sorted)")
    print("=" * 72)
    n = 100_000
    worst = n * (n - 1) // 2
    best = n * math.log2(n) - n + 1
    H = math.log(n) + 0.5772156649
    rnd_exp = 2 * (n + 1) * H - 4 * n
    print(f"First-element pivot (worst case) n(n-1)/2    = {worst:,}")
    print(f"Median-of-3 on nearly sorted ~ n lg n - n + 1 = {best:,.0f}")
    print(f"Random pivot, expected 2(n+1)H_n - 4n         = {rnd_exp:,.0f}")
    print(f"Reduction first -> median-of-3                 = {worst / best:,.0f} x fewer comparisons")
    print(f"Recursion depth: first = n-1 = {n-1:,};  median-of-3 ~ lg n = {math.log2(n):.1f}")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        ns = [t[0] for t in table]
        plt.figure(figsize=(7, 4.5))
        plt.plot(ns, [t[1] for t in table], "o-", label="first-element pivot")
        plt.plot(ns, [t[2] for t in table], "s-", label="median-of-three")
        plt.plot(ns, [t[3] for t in table], "^-", label="random pivot")
        plt.xscale("log"); plt.yscale("log")
        plt.xlabel("number of sellers n"); plt.ylabel("key comparisons")
        plt.title("Quick Sort on nearly sorted scores")
        plt.legend(); plt.grid(True, which="both", alpha=0.3); plt.tight_layout()
        out = os.path.join(os.path.dirname(__file__), "..", "Report",
                           "quick_sort_comparisons.png")
        plt.savefig(out, dpi=150)
        print("\nGraph saved to Report/quick_sort_comparisons.png")
    except ImportError:
        print("matplotlib not installed - graph skipped")


if __name__ == "__main__":
    main()
