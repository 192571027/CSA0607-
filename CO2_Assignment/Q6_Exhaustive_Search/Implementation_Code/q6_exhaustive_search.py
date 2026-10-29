"""
Q6 - Exhaustive Search and Combinatorial Growth (Humanitarian airlift planning)

DESIGN
  Representation : a candidate = subset of packages = n-bit integer mask,
                   bit k = 1  <=>  package k is loaded.  There are 2^n masks
                   (0 .. 2^n - 1) and each subset corresponds to exactly one.
  Generation     : for mask in range(2**n)  (every subset exactly once).
  Feasibility    : total weight of selected packages <= payload limit W.
  Evaluation     : total humanitarian value of the selected packages.
  Best retained  : keep (best_value, best_mask); replace only on a strictly
                   higher value (ties keep the first found).

PREDICTION (before running)
  Each package is independently in or out: 2*2*...*2 = 2^n candidates.
  Adding ONE package doubles the candidates; adding 10 multiplies them by 1024.
  Examining every candidate costs ~n item checks (to add up weight/value), so
  work ~ n * 2^n ; running time should roughly double (slightly more) per +1 package.
"""
import csv
import math
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


def exhaustive_search(weights, values, limit):
    """Return (best_value, best_mask, candidates_examined, feasible_count, item_checks)."""
    n = len(weights)
    best_v, best_mask = 0, 0
    examined = feasible = checks = 0
    for mask in range(1 << n):
        examined += 1
        w = v = 0
        for k in range(n):
            checks += 1
            if mask >> k & 1:
                w += weights[k]
                v += values[k]
        if w <= limit:
            feasible += 1
            if v > best_v:
                best_v, best_mask = v, mask
    return best_v, best_mask, examined, feasible, checks


def dp_reference(weights, values, limit):
    """Independent check only (dynamic programming) - not used by the solution."""
    best = [0] * (limit + 1)
    for w, v in zip(weights, values):
        for c in range(limit, w - 1, -1):
            best[c] = max(best[c], best[c - w] + v)
    return best[limit]


def mask_to_ids(mask, n):
    return [k + 1 for k in range(n) if mask >> k & 1]


def make_instance(n, seed):
    r = random.Random(seed)
    w = [r.randint(5, 40) for _ in range(n)]
    v = [r.randint(10, 100) for _ in range(n)]
    return w, v, sum(w) // 2          # payload limit = half of the total weight


def main():
    print("=" * 78)
    print("Q6  EXHAUSTIVE SEARCH - HUMANITARIAN AIRLIFT PLANNING")
    print("=" * 78)

    # ------------------------------------------------ correctness instance
    names = ["Medical kit", "Water", "Food", "Blankets", "Radio"]
    W = [4, 6, 5, 3, 2]
    V = [10, 7, 8, 4, 6]
    LIM = 10
    n = len(W)
    print("\nCORRECTNESS INSTANCE: 5 packages, payload limit %d kg" % LIM)
    print("  %-3s %-12s %6s %6s" % ("ID", "Package", "Weight", "Value"))
    for k in range(n):
        print("  %-3d %-12s %6d %6d" % (k + 1, names[k], W[k], V[k]))
    print("\n  All 2^5 = 32 subsets (listed independently of the search code):")
    print("  %-6s %-14s %6s %6s  %s" % ("mask", "packages", "weight", "value", "status"))
    table_best = 0
    for mask in range(32):
        ids = mask_to_ids(mask, n)
        w = sum(W[i - 1] for i in ids)
        v = sum(V[i - 1] for i in ids)
        feas = w <= LIM
        table_best = max(table_best, v if feas else 0)
        print("  %-6s %-14s %6d %6d  %s" % (format(mask, "05b"), str(ids), w, v, "feasible" if feas else "over limit"))
    bv, bm, ex, fe, ck = exhaustive_search(W, V, LIM)
    print("\n  Hand-checkable optimum from the table above = %d" % table_best)
    print("  Algorithm result: value=%d, packages=%s (%s), weight=%d" % (
        bv, mask_to_ids(bm, n), ", ".join(names[i - 1] for i in mask_to_ids(bm, n)), sum(W[i - 1] for i in mask_to_ids(bm, n))))
    print("  candidates examined=%d (=2^5)   feasible=%d   -> correct: %s" % (ex, fe, bv == table_best == dp_reference(W, V, LIM)))
    assert bv == table_best

    # randomised cross-check against dynamic programming
    bad = 0
    for s in range(200):
        r = random.Random(s)
        k = r.randint(1, 12)
        w = [r.randint(1, 15) for _ in range(k)]
        v = [r.randint(1, 50) for _ in range(k)]
        lim = r.randint(1, sum(w))
        if exhaustive_search(w, v, lim)[0] != dp_reference(w, v, lim):
            bad += 1
    print("  Randomised cross-check on 200 instances (n<=12) against dynamic programming: mismatches = %d" % bad)

    # ------------------------------------------------ growth
    print("\nPREDICTED GROWTH: candidates = 2^n ; +1 package doubles the search space")
    sizes = [8, 10, 12, 14, 16, 18, 20, 22]
    print("\nEXPERIMENT (random instances, payload = half of total weight)")
    print("%4s | %10s %10s | %10s %12s | %9s | %8s | %s" % (
        "n", "examined", "2^n", "feasible", "item checks", "time (s)", "t/t_prev", "best value"))
    rows = []
    prev = None
    for n in sizes:
        w, v, lim = make_instance(n, 600 + n)
        t = time.perf_counter()
        bv, bm, ex, fe, ck = exhaustive_search(w, v, lim)
        dt = time.perf_counter() - t
        assert bv == dp_reference(w, v, lim) and ex == 2 ** n and ck == n * 2 ** n
        print("%4d | %10d %10d | %10d %12d | %9.3f | %8s | %d" % (
            n, ex, 2 ** n, fe, ck, dt, "" if prev is None else "%.2f" % (dt / prev), bv))
        rows.append([n, ex, 2 ** n, fe, ck, round(dt, 4), bv])
        prev = dt
    with open(os.path.join(RAW, "q6_growth.csv"), "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["n", "candidates_examined", "2^n", "feasible", "item_checks", "time_s", "best_value"])
        wr.writerows(rows)

    print("\nTHEORY vs EXPERIMENT for +2 packages (candidates x4 predicted):")
    for a, b in zip(rows, rows[1:]):
        print("  n %2d -> %2d : candidates x%.1f   item checks x%.2f   time x%.2f" % (a[0], b[0], b[1] / a[1], b[4] / a[4], b[5] / a[5]))

    # fit time = c * n * 2^n
    c = sum(r[5] * r[0] * 2 ** r[0] for r in rows[2:]) / sum((r[0] * 2 ** r[0]) ** 2 for r in rows[2:])
    per_sub = rows[-1][5] / rows[-1][1]
    print("\n  fitted model t(n) = c * n * 2^n with c = %.3e s ;   at n=22 cost per subset = %.2f microseconds" % (c, per_sub * 1e6))

    # ------------------------------------------------ deployment decision
    LIMIT = 10.0
    print("\nDEPLOYMENT DECISION")
    print("  Fixed response time chosen: %.0f s.  Reason: a loading plan is made before departure, the planner" % LIMIT)
    print("  can wait a few seconds, but must be able to re-run it several times as packages / limit change;")
    print("  >10 s breaks that interactive 'what-if' loop during an emergency.")
    nmax = max(n for n in range(1, 60) if c * n * 2 ** n <= LIMIT)
    print("  Largest n with predicted t(n) <= %.0f s  ->  n = %d packages (this machine, interpreted Python)" % (LIMIT, nmax))
    print("  Safety margin (inputs vary, machine may be slower; pick 1 step lower): deploy for n <= %d" % (nmax - 1))
    print("\n  %4s | %18s | %16s | %s" % ("n", "candidates 2^n", "predicted time", "verdict"))
    for n in (20, 22, 24, 25, 26, 30, 40, 50, 60):
        t = c * n * 2 ** n
        if t < 120:
            ts = "%.1f s" % t
        elif t < 86400:
            ts = "%.1f min" % (t / 60) if t < 7200 else "%.1f h" % (t / 3600)
        elif t < 86400 * 365:
            ts = "%.1f days" % (t / 86400)
        else:
            ts = "%.2e years" % (t / 86400 / 365)
        print("  %4d | %18d | %16s | %s" % (n, 2 ** n, ts, "OK" if t <= LIMIT else "too slow"))
    print("  A 100x faster compiled implementation adds only log2(100) ~ 6-7 packages to the limit.")

    # ------------------------------------------------ graphs
    ns = [r[0] for r in rows]
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.3))
    ax[0].semilogy(ns, [r[1] for r in rows], "o", label="measured candidates")
    ax[0].semilogy(ns, [2 ** n for n in ns], "k--", label="2^n")
    ax[0].set_xlabel("n packages")
    ax[0].set_ylabel("candidates (log)")
    ax[0].set_title("Solution space")
    ax[0].legend()
    ax[0].grid(alpha=.3, which="both")
    ax[1].semilogy(ns, [r[5] for r in rows], "o-", label="measured")
    xs = list(range(8, 27))
    ax[1].semilogy(xs, [c * x * 2 ** x for x in xs], "k--", label="c*n*2^n (fit)")
    ax[1].axhline(LIMIT, color="r", ls=":", label="10 s limit")
    ax[1].set_xlabel("n packages")
    ax[1].set_ylabel("seconds (log)")
    ax[1].set_title("Execution time")
    ax[1].legend()
    ax[1].grid(alpha=.3, which="both")
    ax[2].plot(ns, [r[3] / r[2] * 100 for r in rows], "o-")
    ax[2].set_xlabel("n packages")
    ax[2].set_ylabel("% of candidates feasible")
    ax[2].set_title("Feasible fraction (limit = 50% of total weight)")
    ax[2].grid(alpha=.3)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "q6_graph_growth.png"), dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    main()
