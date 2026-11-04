"""
KartIQ - Module 1: Nightly Order Consolidation using a STABLE Merge Sort.

Run:  python3 merge_sort.py
Produces: console trace + ../Report/merge_sort_comparisons.png
"""
import heapq
import math
import os
import random
import tempfile

SAMPLE_ORDERS = [(105, "O1"), (102, "O2"), (105, "O3"),
                 (101, "O4"), (102, "O5"), (103, "O6")]


class Stats:
    def __init__(self):
        self.comparisons = 0


def fmt(seq):
    return "[" + ", ".join(f"({t},{o})" for t, o in seq) + "]"


# --------------------------------------------------------------------------
# Merge sort (top-down, stable). Sorts a[lo:hi] using the auxiliary list aux.
# --------------------------------------------------------------------------
def merge_sort(a, lo, hi, aux, stats, trace=None, depth=0):
    if hi - lo <= 1:                       # BASE CASE: 0 or 1 element is sorted
        return
    mid = (lo + hi) // 2                   # DIVIDE
    if trace is not None:
        trace.append("  " * depth + f"DIVIDE   {fmt(a[lo:hi])} -> "
                     f"{fmt(a[lo:mid])} | {fmt(a[mid:hi])}")
    merge_sort(a, lo, mid, aux, stats, trace, depth + 1)   # CONQUER left
    merge_sort(a, mid, hi, aux, stats, trace, depth + 1)   # CONQUER right
    merge(a, lo, mid, hi, aux, stats, trace, depth)        # COMBINE


def merge(a, lo, mid, hi, aux, stats, trace=None, depth=0):
    aux[lo:hi] = a[lo:hi]
    i, j, k = lo, mid, lo
    left_copy, right_copy = fmt(aux[lo:mid]), fmt(aux[mid:hi])
    steps = []
    while i < mid and j < hi:
        stats.comparisons += 1
        # STABILITY: on a tie (<=) the LEFT element is taken first.
        if aux[i][0] <= aux[j][0]:
            steps.append(f"{aux[i][0]}({aux[i][1]}) <= {aux[j][0]}({aux[j][1]}) -> take left {aux[i][1]}")
            a[k] = aux[i]; i += 1
        else:
            steps.append(f"{aux[i][0]}({aux[i][1]}) >  {aux[j][0]}({aux[j][1]}) -> take right {aux[j][1]}")
            a[k] = aux[j]; j += 1
        k += 1
    while i < mid:
        a[k] = aux[i]; i += 1; k += 1
    while j < hi:
        a[k] = aux[j]; j += 1; k += 1
    if trace is not None:
        ind = "  " * depth
        trace.append(ind + f"MERGE    {left_copy} + {right_copy}")
        for s in steps:
            trace.append(ind + "           " + s)
        trace.append(ind + f"         = {fmt(a[lo:hi])}")


def sort_orders(orders, trace=None):
    a = list(orders)
    stats = Stats()
    merge_sort(a, 0, len(a), [None] * len(a), stats, trace)
    return a, stats.comparisons


# --------------------------------------------------------------------------
# Verification helpers
# --------------------------------------------------------------------------
def is_stable_and_sorted(original, result):
    """Sorted by timestamp, and equal timestamps keep arrival order."""
    arrival = {oid: idx for idx, (_, oid) in enumerate(original)}
    for x, y in zip(result, result[1:]):
        if x[0] > y[0]:
            return False
        if x[0] == y[0] and arrival[x[1]] > arrival[y[1]]:
            return False
    return True


def worst_case_comparisons(n):
    """Exact worst case of top-down merge sort: n*ceil(lg n) - 2^ceil(lg n) + 1."""
    if n <= 1:
        return 0
    c = math.ceil(math.log2(n))
    return n * c - 2 ** c + 1


# --------------------------------------------------------------------------
# External merge sort demonstration (data larger than RAM)
# --------------------------------------------------------------------------
def external_merge_sort(orders_iter, run_size, tmpdir):
    """Phase 1: sort runs of `run_size` in RAM and spill to disk.
       Phase 2: k-way merge of all runs (heapq.merge is stable: ties are
       resolved in the order the runs are supplied == arrival order)."""
    run_files, buf = [], []

    def spill():
        buf_sorted, _ = sort_orders(buf)
        path = os.path.join(tmpdir, f"run_{len(run_files)}.txt")
        with open(path, "w") as f:
            for t, o in buf_sorted:
                f.write(f"{t},{o}\n")
        run_files.append(path)

    for rec in orders_iter:
        buf.append(rec)
        if len(buf) == run_size:
            spill(); buf = []
    if buf:
        spill()

    def reader(path):
        with open(path) as f:
            for line in f:
                t, o = line.strip().split(",")
                yield (int(t), o)

    merged = list(heapq.merge(*[reader(p) for p in run_files], key=lambda r: r[0]))
    return merged, len(run_files)


def main():
    print("=" * 72)
    print("MODULE 1 - MERGE SORT TRACE ON THE SAMPLE ORDERS")
    print("=" * 72)
    print("Input (arrival order):", fmt(SAMPLE_ORDERS))
    trace = []
    result, comps = sort_orders(SAMPLE_ORDERS, trace)
    print("\n".join(trace))
    print("\nSorted output :", fmt(result))
    print("Comparisons   :", comps)
    print("Sorted and stable? ->", is_stable_and_sorted(SAMPLE_ORDERS, result))

    print("\nStability check on tied timestamps:")
    for ts in (102, 105):
        print(f"  timestamp {ts}: input order",
              [o for t, o in SAMPLE_ORDERS if t == ts],
              "-> output order", [o for t, o in result if t == ts])

    # ---- Experiments ------------------------------------------------------
    print("\n" + "=" * 72)
    print("EXPERIMENT - comparisons vs n (random, sorted, reverse, formula)")
    print("=" * 72)
    random.seed(7)
    sizes = [2 ** k for k in range(4, 17)]
    rows = []
    print(f"{'n':>8} {'random':>10} {'sorted':>10} {'reverse':>10} "
          f"{'worst(formula)':>15} {'n lg n - n + 1':>15}")
    for n in sizes:
        rnd = [(random.randint(0, n), f"O{i}") for i in range(n)]
        srt = sorted(rnd, key=lambda r: r[0])
        rev = srt[::-1]
        c_r = sort_orders(rnd)[1]
        c_s = sort_orders(srt)[1]
        c_v = sort_orders(rev)[1]
        w = worst_case_comparisons(n)
        f = int(n * math.log2(n) - n + 1)
        rows.append((n, c_r, c_s, c_v, w, f))
        print(f"{n:>8} {c_r:>10} {c_s:>10} {c_v:>10} {w:>15} {f:>15}")

    # ---- Production estimate ---------------------------------------------
    N = 10_000_000
    lg = math.log2(N)
    print("\n" + "=" * 72)
    print("PRODUCTION ESTIMATE  (n = 10,000,000 orders)")
    print("=" * 72)
    print(f"log2(n)                      = {lg:.4f}  (ceil = {math.ceil(lg)})")
    print(f"n*log2(n)                    = {N*lg:,.0f}")
    print(f"Worst case  n*ceil(lg n) - 2^ceil(lg n) + 1 = {worst_case_comparisons(N):,}")
    print(f"Approx.  n*lg n - n + 1      = {N*lg - N + 1:,.0f}")
    print(f"Best case (already sorted) ~ (n/2)*lg n      = {N*lg/2:,.0f}")
    rec_bytes = 16  # 8-byte timestamp + 8-byte order id
    print(f"Data size  (16 B/record)     = {N*rec_bytes/1e6:,.0f} MB")
    print(f"Extra buffer, full copy      = {N*rec_bytes/1e6:,.0f} MB")
    print(f"Extra buffer, half copy      = {N*rec_bytes/2e6:,.0f} MB")
    print(f"Recursion depth              = {math.ceil(lg)} levels")

    # ---- External merge sort demo ----------------------------------------
    print("\n" + "=" * 72)
    print("EXTERNAL MERGE SORT DEMO (20,000 orders, runs of 3,000 'fit in RAM')")
    print("=" * 72)
    random.seed(11)
    demo = [(random.randint(0, 500), f"O{i}") for i in range(20_000)]
    with tempfile.TemporaryDirectory() as td:
        merged, nruns = external_merge_sort(iter(demo), 3_000, td)
    print("runs written to disk :", nruns)
    print("matches in-memory stable sort :",
          merged == sorted(demo, key=lambda r: r[0]))
    print("sorted and stable             :", is_stable_and_sorted(demo, merged))

    # ---- Graph -----------------------------------------------------------
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        ns = [r[0] for r in rows]
        plt.figure(figsize=(7, 4.5))
        plt.plot(ns, [r[1] for r in rows], "o-", label="random input")
        plt.plot(ns, [r[2] for r in rows], "s-", label="already sorted")
        plt.plot(ns, [r[4] for r in rows], "^--", label="worst-case formula")
        plt.plot(ns, [n * math.log2(n) for n in ns], "k:", label="n log2 n")
        plt.xscale("log", base=2); plt.yscale("log")
        plt.xlabel("number of orders n"); plt.ylabel("key comparisons")
        plt.title("Merge Sort comparisons grow as n log n")
        plt.legend(); plt.grid(True, which="both", alpha=0.3); plt.tight_layout()
        out = os.path.join(os.path.dirname(__file__), "..", "Report",
                           "merge_sort_comparisons.png")
        plt.savefig(out, dpi=150)
        print("\nGraph saved to Report/merge_sort_comparisons.png")
    except ImportError:
        print("matplotlib not installed - graph skipped")


if __name__ == "__main__":
    main()
