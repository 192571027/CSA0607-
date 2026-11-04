"""
Q1 - Sorting Under Different Data Conditions (E-Commerce Order Processing)
CSA06 Design and Analysis of Algorithms - CO2

Each order is a record (priority_score, order_id).  Sorting is by priority_score
only, so that stability (order_id order among equal scores) can be observed.

Counted measures
  comparisons : key comparisons between two priority scores
  moves       : swaps (Selection, Bubble) or element shifts (Insertion)
  time        : best of 3 runs (secondary evidence only)

PREDICTIONS are computed from theory (formulas below) BEFORE any algorithm is
run, and are then compared with the observed counts.
"""
import csv
import os
import random
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "Output_Screenshots")
RAW = os.path.join(OUT, "raw_data")
os.makedirs(RAW, exist_ok=True)


# ----------------------------------------------------------------- algorithms
def selection_sort(data):
    a = list(data)
    n = len(a)
    comps = moves = 0
    for i in range(n - 1):
        m = i
        for j in range(i + 1, n):
            comps += 1
            if a[j][0] < a[m][0]:
                m = j
        if m != i:
            a[i], a[m] = a[m], a[i]
            moves += 1
    return a, comps, moves


def bubble_sort(data):
    """Bubble sort with the usual 'no swap in a pass -> stop' improvement."""
    a = list(data)
    n = len(a)
    comps = moves = passes = 0
    for p in range(n - 1):
        swapped = False
        for j in range(n - 1 - p):
            comps += 1
            if a[j][0] > a[j + 1][0]:
                a[j], a[j + 1] = a[j + 1], a[j]
                moves += 1
                swapped = True
        passes += 1
        if not swapped:
            break
    return a, comps, moves, passes


def insertion_sort(data):
    a = list(data)
    n = len(a)
    comps = moves = 0
    for i in range(1, n):
        v = a[i]
        j = i - 1
        while j >= 0:
            comps += 1
            if a[j][0] > v[0]:
                a[j + 1] = a[j]
                moves += 1
                j -= 1
            else:
                break
        a[j + 1] = v
    return a, comps, moves


# --------------------------------------------------- theoretical predictions
def count_inversions(vals):
    """Number of pairs i<j with vals[i] > vals[j] (merge-sort based, O(n log n))."""
    def rec(v):
        if len(v) <= 1:
            return v, 0
        mid = len(v) // 2
        l, a = rec(v[:mid])
        r, b = rec(v[mid:])
        merged, inv, i, j = [], a + b, 0, 0
        while i < len(l) and j < len(r):
            if l[i] <= r[j]:
                merged.append(l[i]); i += 1
            else:
                merged.append(r[j]); j += 1
                inv += len(l) - i
        merged += l[i:] + r[j:]
        return merged, inv
    return rec(list(vals))[1]


def predict(vals):
    n = len(vals)
    inv = count_inversions(vals)
    # greater-elements-to-the-left for every position (needed for bubble passes)
    max_left = 0
    from bisect import bisect_right, insort
    seen = []
    z = 0  # elements strictly smaller than everything before them (insertion stops at j=-1)
    for i, v in enumerate(vals):
        greater = len(seen) - bisect_right(seen, v)
        max_left = max(max_left, greater)
        if i >= 1 and greater == len(seen):
            z += 1
        insort(seen, v)
    passes = min(n - 1, max_left + 1)
    bub_comps = sum(n - 1 - p for p in range(passes))
    return {
        "inversions": inv,
        "sel_comps": n * (n - 1) // 2,
        "bub_comps": bub_comps, "bub_moves": inv, "bub_passes": passes,
        "ins_comps": inv + (n - 1) - z, "ins_moves": inv,
    }


# -------------------------------------------------------------------- datasets
def to_records(prios):
    return [(p, i) for i, p in enumerate(prios)]


def ds_random(n, rng):
    return to_records([rng.randint(1, 10 * n) for _ in range(n)])


def ds_sorted(n, rng):
    return to_records(sorted(rng.randint(1, 10 * n) for _ in range(n)))


def ds_nearly_sorted_appended(n, rng, frac=0.05):
    """95% already ordered; a small batch (5%) of NEW orders appended at the end."""
    k = int(n * frac)
    old = sorted(rng.randint(1, 10 * n) for _ in range(n - k))
    new = [rng.randint(1, 10 * n) for _ in range(k)]
    return to_records(old + new)


def ds_nearly_sorted_local(n, rng, frac=0.05, spread=5):
    """95% in place; 5% of orders displaced by at most `spread` positions."""
    p = sorted(rng.randint(1, 10 * n) for _ in range(n))
    for _ in range(int(n * frac)):
        i = rng.randrange(n)
        j = min(n - 1, max(0, i + rng.randint(-spread, spread)))
        p[i], p[j] = p[j], p[i]
    return to_records(p)


def ds_reverse(n, rng):
    return to_records(sorted((rng.randint(1, 10 * n) for _ in range(n)), reverse=True))


def ds_all_equal(n, rng):
    return to_records([500] * n)


def ds_few_levels(n, rng):
    return to_records([rng.choice([1, 2, 3, 4, 5]) for _ in range(n)])


def is_sorted(a):
    return all(a[i][0] <= a[i + 1][0] for i in range(len(a) - 1))


def is_stable(a):
    return all(not (a[i][0] == a[i + 1][0] and a[i][1] > a[i + 1][1]) for i in range(len(a) - 1))


def best_time(fn, data, reps=3):
    best = 1e9
    for _ in range(reps):
        t = time.perf_counter()
        fn(data)
        best = min(best, time.perf_counter() - t)
    return best * 1000.0  # ms


def run_all(data):
    res = {}
    a, c, m = selection_sort(data)
    assert is_sorted(a)
    res["Selection"] = dict(comps=c, moves=m, ms=best_time(selection_sort, data), stable=is_stable(a))
    a, c, m, p = bubble_sort(data)
    assert is_sorted(a)
    res["Bubble"] = dict(comps=c, moves=m, passes=p, ms=best_time(bubble_sort, data), stable=is_stable(a))
    a, c, m = insertion_sort(data)
    assert is_sorted(a)
    res["Insertion"] = dict(comps=c, moves=m, ms=best_time(insertion_sort, data), stable=is_stable(a))
    return res


# ------------------------------------------------------------------------ main
def main():
    N = 1000
    rng = random.Random(2024)
    datasets = [
        ("D0 Random (baseline)", ds_random(N, rng)),
        ("D0b Already sorted (baseline)", ds_sorted(N, rng)),
        ("D1 Nearly sorted: 95% ordered + 5% new batch appended", ds_nearly_sorted_appended(N, rng)),
        ("D1b Nearly sorted: 5% locally displaced", ds_nearly_sorted_local(N, rng)),
        ("D2 Reverse sorted (significantly disordered)", ds_reverse(N, rng)),
        ("D3 EDGE CASE: all priorities identical", ds_all_equal(N, rng)),
    ]

    print("=" * 78)
    print("Q1  SORTING UNDER DIFFERENT DATA CONDITIONS   (n = %d orders)" % N)
    print("=" * 78)
    print("""
PREDICTIONS (derived from the algorithms' structure, BEFORE running them)
 Selection : comparisons = n(n-1)/2 for EVERY input (scan of unsorted part
             never stops early); moves <= n-1 (one swap per pass at most).
 Bubble    : moves = #inversions; passes = 1 + max(#larger elements to the left
             of any element) because an element moves left only ONE place per
             pass.  Sorted input -> n-1 comparisons (early-exit flag).
 Insertion : shifts = #inversions; comparisons = inversions + (n-1) - z where z
             = elements smaller than every earlier element.  Sorted -> n-1.
 D1 (5% new orders appended): few inversions overall but each appended order
             may have to travel far LEFT.  Insertion should be cheap (about
             k*n/2 shifts); Bubble suffers (one pass per position travelled);
             Selection unchanged at n(n-1)/2.
 D2 (reverse): worst case for Bubble and Insertion (n(n-1)/2 moves).
 D3 (all equal): no inversions -> Bubble & Insertion n-1 comparisons, 0 moves;
             Selection still n(n-1)/2 comparisons, 0 swaps.
""")

    rows = []
    for name, data in datasets:
        pred = predict([r[0] for r in data])
        obs = run_all(data)
        print("-" * 78)
        print(name)
        print("  inversions (independent count) = %d, predicted bubble passes = %d"
              % (pred["inversions"], pred["bub_passes"]))
        hdr = "  %-10s %12s %12s %12s %9s %7s" % ("Algorithm", "Comparisons", "Moves", "Predicted C", "Time ms", "Stable")
        print(hdr)
        pc = {"Selection": pred["sel_comps"], "Bubble": pred["bub_comps"], "Insertion": pred["ins_comps"]}
        pm = {"Bubble": pred["bub_moves"], "Insertion": pred["ins_moves"]}
        for alg in ("Selection", "Bubble", "Insertion"):
            o = obs[alg]
            ok = "OK" if o["comps"] == pc[alg] and (alg == "Selection" or o["moves"] == pm[alg]) else "MISMATCH"
            print("  %-10s %12d %12d %12d %9.2f %7s  %s" % (alg, o["comps"], o["moves"], pc[alg], o["ms"], o["stable"], ok))
            rows.append([name, N, alg, o["comps"], o["moves"], pc[alg], o.get("passes", ""), round(o["ms"], 3), o["stable"], ok])
        print("  Bubble passes observed = %d (predicted %d)" % (obs["Bubble"]["passes"], pred["bub_passes"]))

    with open(os.path.join(RAW, "q1_dataset_results.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dataset", "n", "algorithm", "comparisons", "moves", "predicted_comparisons", "bubble_passes", "time_ms", "stable", "prediction_check"])
        w.writerows(rows)

    # ---------------- stability test (extra edge case: duplicates)
    print("-" * 78)
    print("STABILITY TEST: 1000 orders with only 5 distinct priority levels")
    d = ds_few_levels(N, random.Random(7))
    for alg, fn in (("Selection", selection_sort), ("Bubble", bubble_sort), ("Insertion", insertion_sort)):
        out = fn(d)[0]
        print("  %-10s sorted=%s stable=%s" % (alg, is_sorted(out), is_stable(out)))

    # ---------------- scaling for the 95%-ordered scenario
    print("=" * 78)
    print("SCALING  - fulfilment-centre scenario: 95% ordered + 5% new batch appended")
    print("=" * 78)
    print("%6s | %-26s | %-26s | %-26s" % ("n", "Selection comps / moves", "Bubble comps / moves", "Insertion comps / moves"))
    srows = []
    sizes = [250, 500, 1000, 2000, 3000]
    for n in sizes:
        data = ds_nearly_sorted_appended(n, random.Random(n))
        r = run_all(data)
        print("%6d | %12d / %-11d | %12d / %-11d | %12d / %-11d" % (
            n, r["Selection"]["comps"], r["Selection"]["moves"], r["Bubble"]["comps"], r["Bubble"]["moves"],
            r["Insertion"]["comps"], r["Insertion"]["moves"]))
        for alg in r:
            srows.append([n, alg, r[alg]["comps"], r[alg]["moves"], round(r[alg]["ms"], 3)])
    with open(os.path.join(RAW, "q1_scaling_95pct_sorted.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n", "algorithm", "comparisons", "moves", "time_ms"])
        w.writerows(srows)

    print("\nTiming (ms, best of 3) for the same runs:")
    for n in sizes:
        t = {alg: [r[4] for r in srows if r[0] == n and r[1] == alg][0] for alg in ("Selection", "Bubble", "Insertion")}
        print("  n=%5d  Selection %9.2f  Bubble %9.2f  Insertion %9.2f" % (n, t["Selection"], t["Bubble"], t["Insertion"]))

    # ---------------- graph 1: operation counts per dataset
    fig, ax = plt.subplots(figsize=(10, 5))
    names = [r[0].split(":")[0].split(" (")[0] for r in rows[::3]]
    width = 0.27
    for k, alg in enumerate(("Selection", "Bubble", "Insertion")):
        vals = [r[3] + r[4] for r in rows if r[2] == alg]
        ax.bar([i + (k - 1) * width for i in range(len(names))], vals, width, label=alg)
    ax.set_yscale("log")
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, fontsize=8, rotation=15)
    ax.set_ylabel("comparisons + moves (log scale)")
    ax.set_title("Q1: total key operations by input condition (n=1000)")
    ax.legend()
    ax.grid(axis="y", alpha=.3)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "q1_graph_operations_by_dataset.png"), dpi=130)
    plt.close(fig)

    # ---------------- graph 2: scaling
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
    for alg in ("Selection", "Bubble", "Insertion"):
        ax[0].plot(sizes, [r[2] + r[3] for r in srows if r[1] == alg], "o-", label=alg)
        ax[1].plot(sizes, [r[4] for r in srows if r[1] == alg], "o-", label=alg)
    ax[0].set_title("Operations (comparisons+moves), 95% ordered input")
    ax[1].set_title("Execution time (ms), 95% ordered input")
    for a_ in ax:
        a_.set_xlabel("n (orders)")
        a_.legend()
        a_.grid(alpha=.3)
    ax[0].set_yscale("log")
    ax[1].set_yscale("log")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "q1_graph_scaling_95pct.png"), dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    main()
