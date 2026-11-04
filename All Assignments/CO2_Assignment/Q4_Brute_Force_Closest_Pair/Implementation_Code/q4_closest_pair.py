"""
Q4 - Brute-Force Closest Pair (Drone collision-risk monitoring)

Design
  Candidate pairs : every unordered pair {Di, Dj}, i < j.
  Duplicates avoided : (Di,Dj) and (Dj,Di) have the same distance, so only
                       pairs with j > i are examined  (and i != j).
  Number of pairs : sum_{i=0}^{n-2} (n-1-i) = (n-1)+(n-2)+...+1 = n(n-1)/2 = C(n,2)
  Distance used   : squared Euclidean distance (monotone in the true distance,
                    so the minimiser is identical; the square root is avoided).

PREDICTION (before running)
  pairs examined = distance calculations = n(n-1)/2 exactly, for every input;
  time ~ c * n^2, so doubling n should multiply the time by about 4.
"""
import csv
import math
import os
import random
import time
from itertools import combinations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "Output_Screenshots")
RAW = os.path.join(OUT, "raw_data")
os.makedirs(RAW, exist_ok=True)


def brute_force_closest_pair(pts):
    """Return (best_sq_distance, i, j, pairs_examined, distance_calculations)."""
    n = len(pts)
    best = float("inf")
    bi = bj = -1
    pairs = dist_calcs = 0
    for i in range(n - 1):
        xi, yi = pts[i]
        for j in range(i + 1, n):
            pairs += 1
            xj, yj = pts[j]
            dx = xi - xj
            dy = yi - yj
            d = dx * dx + dy * dy
            dist_calcs += 1
            if d < best:
                best, bi, bj = d, i, j
    return best, bi, bj, pairs, dist_calcs


def make_points(n, seed=None):
    rng = random.Random(n if seed is None else seed)
    return [(rng.uniform(0, 10000), rng.uniform(0, 10000)) for _ in range(n)]


def main():
    print("=" * 78)
    print("Q4  BRUTE-FORCE CLOSEST PAIR - DRONE COLLISION-RISK MONITORING")
    print("=" * 78)
    print("""
DERIVATION  number of unique candidate pairs for n drones
  Drone 1 is paired with n-1 others; drone 2 with the n-2 NOT already paired
  with it (j>i); ... drone n-1 with 1; drone n with none:
        (n-1) + (n-2) + ... + 1 = n(n-1)/2
  Equivalently C(n,2) = n!/(2!(n-2)!).  Counting ordered pairs would give
  n(n-1), i.e. every pair twice.  Growth is Theta(n^2): the pair count
  multiplies by ~4 whenever n doubles.
""")

    # ------------------------------------------------ correctness check
    print("CORRECTNESS CHECK against an independent itertools.combinations minimum")
    for n in (2, 3, 10, 50, 200):
        pts = make_points(n, seed=1000 + n)
        b = brute_force_closest_pair(pts)
        ref = min((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 for p, q in combinations(pts, 2))
        assert abs(b[0] - ref) < 1e-9
        print("  n=%4d  closest pair (%d,%d)  distance=%.4f   matches reference: True" % (n, b[1], b[2], math.sqrt(b[0])))

    print("\nDUPLICATE-PAIR AVOIDANCE (n=1000): ordered scan i!=j examines %d pairs; unique scan examines %d"
          % (1000 * 999, 1000 * 999 // 2))

    # ------------------------------------------------ experiment
    sizes = [100, 250, 500, 1000, 2000, 4000, 8000]
    print("\nEXPERIMENT: random drone positions in a 10,000 x 10,000 m airspace")
    print("%7s | %12s %12s %12s %5s | %9s | %9s | %s" % (
        "n", "pairs exam.", "dist. calcs", "n(n-1)/2", "equal", "time (s)", "t/t_prev", "closest dist (m)"))
    rows = []
    prev_t = None
    for n in sizes:
        pts = make_points(n)
        t = time.perf_counter()
        best, i, j, pairs, dc = brute_force_closest_pair(pts)
        dt = time.perf_counter() - t
        theo = n * (n - 1) // 2
        ratio = "" if prev_t is None else "%.2f" % (dt / prev_t)
        print("%7d | %12d %12d %12d %5s | %9.4f | %9s | %.3f" % (n, pairs, dc, theo, pairs == theo == dc, dt, ratio, math.sqrt(best)))
        rows.append([n, pairs, dc, theo, round(dt, 5), round(math.sqrt(best), 4)])
        prev_t = dt
    with open(os.path.join(RAW, "q4_bruteforce_results.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n", "pairs_examined", "distance_calculations", "n(n-1)/2", "time_s", "closest_distance_m"])
        w.writerows(rows)

    # ------------------------------------------------ theory vs experiment
    print("\nTHEORY vs EXPERIMENT (growth)")
    print("%7s -> %7s | pairs multiplier (theory 4 for x2) | time multiplier" % ("n", "2n"))
    for a, b in zip(rows, rows[1:]):
        if b[0] == 2 * a[0]:
            print("%7d -> %7d | %6.3f                           | %6.3f" % (a[0], b[0], b[1] / a[1], b[4] / a[4]))
    # least-squares fit  t = c * n^2  (through the origin) and log-log slope
    c = sum(r[4] * r[0] ** 2 for r in rows) / sum(r[0] ** 4 for r in rows)
    lx = [math.log(r[0]) for r in rows]
    ly = [math.log(r[4]) for r in rows]
    mx, my = sum(lx) / len(lx), sum(ly) / len(ly)
    slope = sum((a - mx) * (b - my) for a, b in zip(lx, ly)) / sum((a - mx) ** 2 for a in lx)
    print("  fitted model  t(n) = c*n^2  with c = %.3e s/n^2     (log-log slope of measured time = %.3f)" % (c, slope))
    per_pair = sum(r[4] for r in rows) / sum(r[1] for r in rows)
    print("  average cost per candidate pair = %.3f microseconds" % (per_pair * 1e6))

    # ------------------------------------------------ scalability
    LIMIT = 1.0
    nmax = math.sqrt(LIMIT / c)
    print("\nACCEPTABLE RESPONSE TIME (my definition): the collision check must finish within ONE position-report")
    print("interval, assumed 1.0 s, otherwise results are stale before they are shown.")
    print("  Largest n with t(n) <= %.1f s  ->  n_max ~ sqrt(%.1f/c) = %d drones (this environment)" % (LIMIT, LIMIT, nmax))
    print("  %9s | %16s | %14s | %s" % ("n", "pairs", "predicted time", "verdict"))
    for n in (1000, 2000, 5000, 8000, 10000, 20000, 50000, 100000):
        t_pred = c * n * n
        print("  %9d | %16d | %12.2f s | %s" % (n, n * (n - 1) // 2, t_pred, "acceptable" if t_pred <= LIMIT else "IMPRACTICAL"))
    print("  (a compiled implementation ~50x faster would only raise n_max by ~sqrt(50) = 7x -> ~%d)" % (nmax * 7))

    print("""
WHERE DOES THE INEFFICIENCY ORIGINATE?
  Every pair is examined, although a pair can only matter if its two drones are
  CLOSE.  Almost all pairs are far apart and can never be the answer, yet each
  costs one full distance evaluation.  The algorithm uses no information about
  the geometry (nearness, ordering) of the data and never reuses what one
  comparison tells it about others (e.g. 'A and B are far apart' says nothing
  to the algorithm about C, which is also far from B).  A redesigned strategy
  must avoid comparing pairs that cannot beat the current best distance, e.g.
  by ordering/partitioning the drones spatially so that only neighbours are
  compared (this is the Q7 redesign).
""")

    # ------------------------------------------------ graphs
    ns = [r[0] for r in rows]
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.3))
    ax[0].plot(ns, [r[3] for r in rows], "k--", label="theory n(n-1)/2")
    ax[0].plot(ns, [r[1] for r in rows], "o", label="measured pairs")
    ax[0].set_xlabel("n")
    ax[0].set_ylabel("pairs examined")
    ax[0].set_title("Pairs: theory vs measured")
    ax[0].legend()
    ax[0].grid(alpha=.3)
    ax[1].plot(ns, [r[4] for r in rows], "o-", label="measured time")
    xs = list(range(100, 8200, 100))
    ax[1].plot(xs, [c * x * x for x in xs], "k--", label="fit c*n^2")
    ax[1].axhline(LIMIT, color="r", ls=":", label="1 s acceptability limit")
    ax[1].set_xlabel("n")
    ax[1].set_ylabel("seconds")
    ax[1].set_title("Execution time")
    ax[1].legend()
    ax[1].grid(alpha=.3)
    ax[2].loglog(ns, [r[4] for r in rows], "o-", label="measured (slope %.2f)" % slope)
    ax[2].loglog(ns, [c * x * x for x in ns], "k--", label="n^2")
    ax[2].set_xlabel("n")
    ax[2].set_ylabel("seconds")
    ax[2].set_title("Log-log: slope ~ 2")
    ax[2].legend()
    ax[2].grid(alpha=.3, which="both")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "q4_graph_growth.png"), dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    main()
