"""
experiments.py
--------------
Part (d): experimental comparison of the corrected (brute-force) and optimised
SentinelOps functions.  Counts BASIC OPERATIONS with instrumented copies of the
algorithms (identical logic to the real functions; their outputs are asserted
equal to the real functions) and also measures wall-clock time on the real,
un-instrumented functions.

Writes:  ../Supporting_Files/experiment_results.json / *.csv
         ../Report/graphs/*.png
Usage:   python experiments.py
"""
import csv
import json
import math
import os
import random
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import corrected_sentinelops as corr
import optimised_sentinelops as opt

HERE = os.path.dirname(os.path.abspath(__file__))
SUPPORT = os.path.join(HERE, "..", "Supporting_Files")
GRAPHS = os.path.join(HERE, "..", "Report", "graphs")
os.makedirs(SUPPORT, exist_ok=True)
os.makedirs(GRAPHS, exist_ok=True)
SEED = 2026
RESULTS = {}


def timed(fn, *args, repeat=1):
    best = math.inf
    out = None
    for _ in range(repeat):
        t0 = time.perf_counter()
        out = fn(*args)
        best = min(best, time.perf_counter() - t0)
    return out, best


# ======================================================================
# 1. SORTING - insertion sort comparisons, nearly sorted vs random
# ======================================================================
def insertion_counts(alerts):
    """Corrected insertion sort; returns (sorted list, comparisons, shifts)."""
    comps = shifts = 0
    for i in range(1, len(alerts)):
        key = alerts[i]
        j = i - 1
        while j >= 0:
            comps += 1                       # one evaluation of alerts[j][1] < key[1]
            if alerts[j][1] < key[1]:
                alerts[j + 1] = alerts[j]
                shifts += 1
                j -= 1
            else:
                break
        alerts[j + 1] = key
    return alerts, comps, shifts


class Counted:
    """Wraps a severity so list.sort's comparisons can be counted."""
    n = 0
    __slots__ = ("v",)

    def __init__(self, v):
        self.v = v

    def __lt__(self, other):
        Counted.n += 1
        return self.v < other.v


def timsort_comparisons(alerts):
    Counted.n = 0
    alerts.sort(key=lambda a: Counted(a[1]), reverse=True)
    return Counted.n


def make_alerts(n, rng, kind):
    sev = [rng.randint(1, 10) for _ in range(n)]
    alerts = [(f"A{i}", s) for i, s in enumerate(sev)]
    if kind == "nearly_sorted":
        alerts = sorted(alerts, key=lambda a: -a[1])
        # ~1 % of alerts arrive out of place: swap a random alert with one up to n/20
        # positions later, retrying until their severities differ (a swap of equal
        # severities would not create any inversion).
        for _ in range(max(1, n // 100)):
            while True:
                p = rng.randrange(n - 1)
                q = min(n - 1, p + rng.randint(1, max(2, n // 20)))
                if alerts[p][1] != alerts[q][1]:
                    break
            alerts[p], alerts[q] = alerts[q], alerts[p]
    return alerts


def experiment_sort():
    print("\n[1] sort_alerts: comparisons (severity 1..10)")
    rng = random.Random(SEED)
    rows = []
    for n in (1000, 2000, 5000, 10000):
        for kind in ("random", "nearly_sorted"):
            data = make_alerts(n, rng, kind)
            expected = sorted(data, key=lambda a: -a[1])
            res, comps, shifts = insertion_counts(list(data))
            assert res == expected == opt.sort_alerts(list(data))
            tcomps = timsort_comparisons(list(data))
            _, t_ins = timed(corr.sort_alerts, list(data))
            _, t_opt = timed(opt.sort_alerts, list(data))
            # predicted comparisons: shifts + (n-1) - r, r = insertions that reached the front
            inv_pred = n * n * (1 - 1 / 10) / 4          # expected inversions, random, k=10 levels
            row = dict(n=n, input=kind, insertion_comparisons=comps, insertion_shifts=shifts,
                       timsort_comparisons=tcomps, n_log2_n=round(n * math.log2(n)),
                       predicted_random_inversions=round(inv_pred),
                       insertion_seconds=round(t_ins, 5), timsort_seconds=round(t_opt, 6))
            rows.append(row)
            print("   ", row)
    RESULTS["sort"] = rows
    return rows


# ======================================================================
# 2. BLOCKLIST - sequential search vs hash index
# ======================================================================
def linear_comparisons(blocklist, ip):
    c = 0
    for x in blocklist:
        c += 1
        if x == ip:
            return True, c
    return False, c


def experiment_blocklist():
    print("\n[2] is_blocked: sequential search vs hash set (2,000 queries, 50 % hits)")
    rng = random.Random(SEED)
    rows = []
    q = 2000
    for b in (1000, 5000, 20000):
        blocklist = [f"10.{i // 65536 % 256}.{i // 256 % 256}.{i % 256}" for i in range(b)]
        rng.shuffle(blocklist)
        hits = rng.sample(blocklist, q // 2)
        misses = [f"192.168.{rng.randint(0, 255)}.{rng.randint(0, 255)}" for _ in range(q // 2)]
        queries = hits + misses
        rng.shuffle(queries)
        total = 0
        member = set(blocklist)
        for ip in queries:
            res, c = linear_comparisons(blocklist, ip)
            assert res == corr.is_blocked(blocklist, ip) == (ip in member)
            total += c
        _, t_lin = timed(lambda: [corr.is_blocked(blocklist, ip) for ip in queries])
        t0 = time.perf_counter()
        index = opt.build_blocklist_index(blocklist)
        t_build = time.perf_counter() - t0
        out, t_set = timed(lambda: [opt.is_blocked(index, ip) for ip in queries], repeat=3)
        assert out == [ip in member for ip in queries]
        row = dict(blocklist_size=b, queries=q, linear_comparisons=total,
                   hash_probes=q, hash_build_inserts=b,
                   linear_seconds=round(t_lin, 5), build_seconds=round(t_build, 6),
                   hash_lookup_seconds=round(t_set, 6))
        rows.append(row)
        print("   ", row)
    RESULTS["blocklist"] = rows
    return rows


# ======================================================================
# 3. SIGNATURE SCAN - character comparisons
# ======================================================================
def count_original_windows(n, m):
    return max(0, n - m)             # original range(n - m)


def brute_comparisons(log, pattern):
    """Corrected brute force, counting character comparisons."""
    n, m = len(log), len(pattern)
    c, hits = 0, []
    for i in range(n - m + 1):
        for j in range(m):
            c += 1
            if log[i + j] != pattern[j]:
                break
        else:
            hits.append(i)
    return hits, c


def optimised_comparisons(log, pattern):
    """Optimised scan (first-char skip), counting character comparisons."""
    n, m = len(log), len(pattern)
    if m == 0 or m > n:
        return [], 0
    c, hits = 0, []
    first = pattern[0]
    for i in range(n - m + 1):
        c += 1
        if log[i] != first:
            continue
        j = 1
        while j < m:
            c += 1
            if log[i + j] != pattern[j]:
                break
            j += 1
        if j == m:
            hits.append(i)
    return hits, c


def horspool_comparisons(log, pattern):
    n, m = len(log), len(pattern)
    if m == 0 or m > n:
        return [], 0
    shift = {pattern[k]: m - 1 - k for k in range(m - 1)}
    c, hits, i = 0, [], 0
    while i <= n - m:
        j = m - 1
        while j >= 0:
            c += 1
            if log[i + j] != pattern[j]:
                break
            j -= 1
        if j < 0:
            hits.append(i)
        i += shift.get(log[i + m - 1], m)
    return hits, c


def experiment_signature():
    print("\n[3] find_signature: character comparisons")
    rng = random.Random(SEED)
    rows = []
    cases = []
    for n in (10_000, 100_000, 200_000):
        text = "".join(rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ _:-0123456789") for _ in range(n))
        # plant a few signatures, including one at the very end
        chars = list(text)
        for pos in (0, n // 3, 2 * n // 3, n - 4):
            chars[pos:pos + 4] = "FAIL"
        cases.append((f"random log n={n}", "".join(chars), "FAIL"))
    n = 20_000
    cases.append(("worst case 'AAAA..A' / 'A..AB' (m=8)", "A" * n, "A" * 7 + "B"))
    for name, log, pat in cases:
        h1, c1 = brute_comparisons(log, pat)
        h2, c2 = optimised_comparisons(log, pat)
        h3, c3 = horspool_comparisons(log, pat)
        assert h1 == h2 == h3 == opt.find_signature(log, pat) == corr.find_signature(log, pat)
        _, t1 = timed(corr.find_signature, log, pat, repeat=3)
        _, t2 = timed(opt.find_signature, log, pat, repeat=3)
        _, t3 = timed(opt.find_signature_horspool, log, pat, repeat=3)
        row = dict(case=name, n=len(log), m=len(pat), hits=len(h1),
                   original_windows=count_original_windows(len(log), len(pat)),
                   correct_windows=len(log) - len(pat) + 1,
                   brute_char_comparisons=c1, optimised_char_comparisons=c2,
                   horspool_char_comparisons=c3,
                   brute_seconds=round(t1, 5), optimised_seconds=round(t2, 5),
                   horspool_seconds=round(t3, 5))
        rows.append(row)
        print("   ", row)
    RESULTS["signature"] = rows
    return rows


# ======================================================================
# 4. CLOSEST PAIR - distance computations
# ======================================================================
def brute_counts(events):
    """Corrected brute force with sqrt per pair; counts distance computations."""
    n = len(events)
    dist = sqrt_calls = 0
    min_dist, pair = math.inf, None
    for i in range(n):
        for j in range(i + 1, n):
            dist += 1
            sqrt_calls += 1
            d = math.sqrt((events[i][0] - events[j][0]) ** 2 + (events[i][1] - events[j][1]) ** 2)
            if d < min_dist:
                min_dist, pair = d, (i, j)
    return pair, min_dist, dist, sqrt_calls


def optimised_counts(events):
    """Pruned sweep; counts squared-distance evaluations (sqrt is called once)."""
    n = len(events)
    if n < 2:
        return None, math.inf, 0
    order = sorted(range(n), key=lambda k: events[k][0])
    xs = [events[k][0] for k in order]
    ys = [events[k][1] for k in order]
    best, best_pair, dist = math.inf, None, 0
    for a in range(n - 1):
        xa, ya, ia = xs[a], ys[a], order[a]
        for b in range(a + 1, n):
            dx = xs[b] - xa
            dx2 = dx * dx
            if dx2 > best:
                break
            dist += 1
            dy = ys[b] - ya
            d2 = dx2 + dy * dy
            if d2 <= best:
                ib = order[b]
                cand = (ia, ib) if ia < ib else (ib, ia)
                if d2 < best or (best_pair is not None and cand < best_pair):
                    best, best_pair = d2, cand
    return best_pair, math.sqrt(best), dist


def experiment_closest():
    print("\n[4] closest_logins: distance computations")
    rng = random.Random(SEED)
    rows = []
    for n in (1000, 2000, 4000, 8000):
        events = [(round(rng.uniform(0, 1000), 2), round(rng.uniform(0, 1000), 2)) for _ in range(n)]
        p1, d1, c1, s1 = brute_counts(events)
        p2, d2, c2 = optimised_counts(events)
        assert p1 == p2 and math.isclose(d1, d2)
        r_b, t_b = timed(corr.closest_logins, events)
        r_o, t_o = timed(opt.closest_logins, events, repeat=3)
        assert r_b[0] == r_o[0] == p1 and math.isclose(r_b[1], r_o[1])
        row = dict(n=n, original_pairs_n_squared=n * n, brute_distance_computations=c1,
                   brute_sqrt_calls=s1, optimised_distance_computations=c2,
                   optimised_sqrt_calls=1, reduction_factor=round(c1 / c2, 1),
                   brute_seconds=round(t_b, 4), optimised_seconds=round(t_o, 4),
                   speedup=round(t_b / t_o, 1), closest_pair=list(p1), closest_km=round(d1, 4))
        rows.append(row)
        print("   ", row)
    # degenerate input: every event on one meridian (same x) -> no x-pruning possible
    n = 2000
    events = [(500.0, round(rng.uniform(0, 1000), 2)) for _ in range(n)]
    p1, d1, c1, _ = brute_counts(events)
    p2, d2, c2 = optimised_counts(events)
    assert p1 == p2 and math.isclose(d1, d2)
    row = dict(case="degenerate: all events share one x", n=n,
               brute_distance_computations=c1, optimised_distance_computations=c2)
    print("   ", row)
    RESULTS["closest"] = rows
    RESULTS["closest_degenerate"] = row
    return rows


# ======================================================================
# graphs + files
# ======================================================================
def make_graphs():
    plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.alpha": 0.3})

    # --- closest pair
    rows = RESULTS["closest"]
    ns = [r["n"] for r in rows]
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ax[0].plot(ns, [r["brute_distance_computations"] for r in rows], "o-", label="brute force  n(n-1)/2")
    ax[0].plot(ns, [r["optimised_distance_computations"] for r in rows], "s-", label="optimised (sort + prune)")
    ax[0].set_yscale("log"); ax[0].set_xlabel("login events per batch (n)")
    ax[0].set_ylabel("distance computations (log scale)")
    ax[0].set_title("closest_logins: distance computations"); ax[0].legend()
    ax[1].plot(ns, [r["brute_seconds"] for r in rows], "o-", label="brute force")
    ax[1].plot(ns, [r["optimised_seconds"] for r in rows], "s-", label="optimised")
    ax[1].set_xlabel("login events per batch (n)"); ax[1].set_ylabel("seconds")
    ax[1].set_title("closest_logins: running time"); ax[1].legend()
    fig.tight_layout(); fig.savefig(os.path.join(GRAPHS, "closest_logins_comparison.png"), dpi=150); plt.close(fig)

    # --- sort
    rows = RESULTS["sort"]
    sizes = sorted({r["n"] for r in rows})
    get = lambda kind, key: [next(r[key] for r in rows if r["n"] == n and r["input"] == kind) for n in sizes]
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ax[0].plot(sizes, get("random", "insertion_comparisons"), "o-", label="insertion sort, random")
    ax[0].plot(sizes, get("nearly_sorted", "insertion_comparisons"), "s-", label="insertion sort, nearly sorted")
    ax[0].plot(sizes, get("random", "timsort_comparisons"), "^--", label="Timsort, random")
    ax[0].plot(sizes, get("nearly_sorted", "timsort_comparisons"), "v--", label="Timsort, nearly sorted")
    ax[0].set_yscale("log"); ax[0].set_xlabel("alerts (n)"); ax[0].set_ylabel("comparisons (log scale)")
    ax[0].set_title("sort_alerts: comparisons"); ax[0].legend(fontsize=8)
    ax[1].plot(sizes, get("random", "insertion_seconds"), "o-", label="insertion sort, random")
    ax[1].plot(sizes, get("nearly_sorted", "insertion_seconds"), "s-", label="insertion sort, nearly sorted")
    ax[1].plot(sizes, get("random", "timsort_seconds"), "^--", label="Timsort, random")
    ax[1].set_yscale("log"); ax[1].set_xlabel("alerts (n)"); ax[1].set_ylabel("seconds (log scale)")
    ax[1].set_title("sort_alerts: running time"); ax[1].legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(GRAPHS, "sort_alerts_comparison.png"), dpi=150); plt.close(fig)

    # --- blocklist
    rows = RESULTS["blocklist"]
    bs = [r["blocklist_size"] for r in rows]
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ax[0].plot(bs, [r["linear_comparisons"] for r in rows], "o-", label="sequential search (2,000 queries)")
    ax[0].plot(bs, [r["hash_probes"] + r["hash_build_inserts"] for r in rows], "s-", label="hash set: build + 2,000 probes")
    ax[0].set_yscale("log"); ax[0].set_xlabel("blocklist size (b)"); ax[0].set_ylabel("basic operations (log scale)")
    ax[0].set_title("is_blocked: operations"); ax[0].legend(fontsize=8)
    ax[1].plot(bs, [r["linear_seconds"] for r in rows], "o-", label="sequential search")
    ax[1].plot(bs, [r["build_seconds"] + r["hash_lookup_seconds"] for r in rows], "s-", label="hash set (build + lookups)")
    ax[1].set_yscale("log"); ax[1].set_xlabel("blocklist size (b)"); ax[1].set_ylabel("seconds (log scale)")
    ax[1].set_title("is_blocked: running time"); ax[1].legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(GRAPHS, "is_blocked_comparison.png"), dpi=150); plt.close(fig)

    # --- signature
    rows = RESULTS["signature"][:3]
    ns_ = [r["n"] for r in rows]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(ns_, [r["brute_char_comparisons"] for r in rows], "o-", label="brute force (early exit)")
    ax.plot(ns_, [r["horspool_char_comparisons"] for r in rows], "s-", label="Horspool (optional)")
    ax.set_xlabel("log length (n)"); ax.set_ylabel("character comparisons")
    ax.set_title("find_signature on random logs (m = 4)"); ax.legend()
    fig.tight_layout(); fig.savefig(os.path.join(GRAPHS, "find_signature_comparison.png"), dpi=150); plt.close(fig)


def save_files():
    with open(os.path.join(SUPPORT, "experiment_results.json"), "w") as f:
        json.dump(RESULTS, f, indent=2)
    for name, rows in RESULTS.items():
        if isinstance(rows, list) and rows:
            with open(os.path.join(SUPPORT, f"experiment_{name}.csv"), "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                w.writeheader()
                w.writerows(rows)


if __name__ == "__main__":
    experiment_sort()
    experiment_blocklist()
    experiment_signature()
    experiment_closest()
    make_graphs()
    save_files()
    print("\nSaved results to Supporting_Files/ and graphs to Report/graphs/")
