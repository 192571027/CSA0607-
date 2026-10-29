"""
Q7 - DAY-4 DESIGN CHALLENGE : Diagnose, Redesign and Validate
Selected solution : Q4 Brute-Force Closest Pair (drone collision-risk monitoring)

Parts
  A  Diagnose the bottleneck (evidence from the ORIGINAL implementation)
  B  Design objective (measurable)
  C  Revised strategies  R1 "sorted sweep with pruning"  (main redesign)
                          R2 "grid / spatial bucketing"   (extension, shows trade-offs)
  D  Predictions made BEFORE the redesign is run
  E  Same test conditions, original vs redesign
  F  Defence (discussed in the report; key numbers printed here)
"""
import csv
import math
import os
import random
import time
from functools import cmp_to_key

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "Output_Screenshots")
RAW = os.path.join(OUT, "raw_data")
os.makedirs(RAW, exist_ok=True)


# ============================================================ ORIGINAL (Q4)
def brute(pts):
    """Original solution. Returns (best_sq, i, j, dist_calcs, best_updates)."""
    n = len(pts)
    best = float("inf")
    bi = bj = -1
    dc = upd = 0
    for i in range(n - 1):
        xi, yi = pts[i]
        for j in range(i + 1, n):
            xj, yj = pts[j]
            dx = xi - xj
            dy = yi - yj
            d = dx * dx + dy * dy
            dc += 1
            if d < best:
                best, bi, bj = d, i, j
                upd += 1
    return best, bi, bj, dc, upd


# ============================================================ REDESIGN R1
def sweep(pts, choose_axis=True, forced_axis=0):
    """
    Sorted sweep with pruning.
      1. (preprocessing) pick the axis along which the drones are most spread out,
         sort the drones along it.
      2. For each drone i look only at the drones that FOLLOW it in sorted order
         and stop as soon as the gap along the sort axis alone is already >= the
         best distance found so far: every later drone is even further away, so
         none of them can improve the answer.
    Returns (best_sq, pi, pj, sort_comps, gap_checks, dist_calcs).
    """
    n = len(pts)
    ax = forced_axis
    pre = 0
    if choose_axis:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        pre = 4 * (n - 1)                                   # min & max of both coordinates
        ax = 0 if (max(xs) - min(xs)) >= (max(ys) - min(ys)) else 1
    cnt = [0]

    def cmp(a, b):
        cnt[0] += 1
        return (a[ax] > b[ax]) - (a[ax] < b[ax])
    s = sorted(pts, key=cmp_to_key(cmp))
    sort_comps = cnt[0] + pre
    best = float("inf")
    bi = bj = None
    gaps = dc = 0
    for i in range(n - 1):
        pi = s[i]
        xi, yi = pi
        ai = pi[ax]
        for j in range(i + 1, n):
            gaps += 1
            g = s[j][ax] - ai
            if g * g >= best:
                break
            xj, yj = s[j]
            dx = xi - xj
            dy = yi - yj
            d = dx * dx + dy * dy
            dc += 1
            if d < best:
                best, bi, bj = d, pi, s[j]
    return best, bi, bj, sort_comps, gaps, dc


def sweep_timed(pts, choose_axis=True, forced_axis=0):
    """Same algorithm, ordinary sort, same per-iteration counters as brute (fair timing)."""
    n = len(pts)
    ax = forced_axis
    if choose_axis:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        ax = 0 if (max(xs) - min(xs)) >= (max(ys) - min(ys)) else 1
    s = sorted(pts, key=lambda p: p[ax])
    best = float("inf")
    gaps = dc = 0
    for i in range(n - 1):
        xi, yi = s[i]
        ai = s[i][ax]
        for j in range(i + 1, n):
            gaps += 1
            g = s[j][ax] - ai
            if g * g >= best:
                break
            xj, yj = s[j]
            dx = xi - xj
            dy = yi - yj
            d = dx * dx + dy * dy
            dc += 1
            if d < best:
                best = d
    return best


# ============================================================ REDESIGN R2
def grid(pts):
    """
    Spatial bucketing.  Cell side s ~ sqrt(area/n) (about one drone per cell).
    An upper bound on the answer is found first from the n-1 consecutive pairs;
    then each drone is compared only with drones in the cells within
    r = ceil(sqrt(best)/s) cells of its own cell (anything farther is farther than best).
    Returns (best_sq, cell_lookups, dist_calcs, max_cell_occupancy).
    """
    n = len(pts)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    w = max(xs) - min(xs)
    h = max(ys) - min(ys)
    mnx, mny = min(xs), min(ys)          # computed ONCE (a first prototype recomputed min() per drone: O(n^2) hidden work)
    side = max(math.sqrt(w * h / n), max(w, h) / n, 1e-9)
    cells = {}
    for idx, (x, y) in enumerate(pts):
        cells.setdefault((int((x - mnx) // side), int((y - mny) // side)), []).append(idx)
    best = float("inf")
    dc = 0
    for i in range(n - 1):
        dx = pts[i][0] - pts[i + 1][0]
        dy = pts[i][1] - pts[i + 1][1]
        dc += 1
        best = min(best, dx * dx + dy * dy)
    lookups = 0
    for i in range(n):
        x, y = pts[i]
        cx, cy = int((x - mnx) // side), int((y - mny) // side)
        r = int(math.ceil(math.sqrt(best) / side)) if best > 0 else 0
        for a in range(cx - r, cx + r + 1):
            for b in range(cy - r, cy + r + 1):
                lookups += 1
                lst = cells.get((a, b))
                if lst:
                    for j in lst:
                        if j > i:
                            dx = x - pts[j][0]
                            dy = y - pts[j][1]
                            dc += 1
                            d = dx * dx + dy * dy
                            if d < best:
                                best = d
    return best, lookups, dc, max(len(v) for v in cells.values())


# ============================================================ data sets
def uniform(n):                       # identical to the Q4 generator -> same test conditions
    rng = random.Random(n)
    return [(rng.uniform(0, 10000), rng.uniform(0, 10000)) for _ in range(n)]


def clustered(n):
    rng = random.Random(7000 + n)
    centres = [(rng.uniform(1000, 9000), rng.uniform(1000, 9000)) for _ in range(5)]
    pts = []
    for k in range(n):
        cx, cy = centres[k % 5]
        pts.append((cx + rng.gauss(0, 150), cy + rng.gauss(0, 150)))
    return pts


def column(n):                        # all drones in a narrow vertical corridor (x-spread 1 m)
    rng = random.Random(9000 + n)
    return [(rng.uniform(0, 1), rng.uniform(0, 10000)) for _ in range(n)]


def two_lines(n):                     # adversarial for a single-axis sweep: two far-apart vertical lines
    rng = random.Random(11000 + n)
    return [((0.0 if k % 2 == 0 else 10000.0), rng.uniform(0, 5000)) for k in range(n)]


def timeit(fn, reps):
    t = time.perf_counter()
    for _ in range(reps):
        r = fn()
    return (time.perf_counter() - t) / reps, r


def main():
    print("=" * 78)
    print("Q7  DAY-4 DESIGN CHALLENGE  -  closest-pair redesign")
    print("=" * 78)

    # ============================================================== A
    print("\n" + "#" * 78 + "\nA. DIAGNOSE THE COMPUTATIONAL BOTTLENECK (original brute force)\n" + "#" * 78)
    print("%6s | %12s | %10s | %12s | %22s | %s" % (
        "n", "dist calcs", "best upd.", "useful %", "pairs with gap>=d_min", "time spent in pair loop"))
    diag = []
    for n in (500, 1000, 2000, 4000):
        pts = uniform(n)
        t = time.perf_counter()
        best, i, j, dc, upd = brute(pts)
        dt = time.perf_counter() - t
        dmin = math.sqrt(best)
        far = sum(1 for a in range(n - 1) for b in range(a + 1, n) if abs(pts[a][0] - pts[b][0]) >= dmin)
        print("%6d | %12d | %10d | %11.4f%% | %10d (%6.2f%%) | 100%% of %.3f s (no other phase)" % (
            n, dc, upd, 100.0 * upd / dc, far, 100.0 * far / dc, dt))
        diag.append([n, dc, upd, far, round(dt, 4)])
    print("""
DIAGNOSIS
  * Where is the effort?  100% in the double loop: one squared-distance evaluation per pair.
  * Which operation grows?  Distance evaluations: n(n-1)/2 (quadratic, Q4: slope ~2.0).
  * Unnecessary / repeated work?  Yes.  The best distance was improved only 'best upd.' times
    out of millions of evaluations, and more than 99% of the pairs differ by at least d_min in the
    x-coordinate ALONE, so they could be rejected without ever computing a distance.
  * Which characteristic causes it?  The algorithm is oblivious to position: it treats every pair as
    equally likely to be the answer and never uses what is already known (the current best) to
    discard candidates.  Candidate set size is fixed by n, independent of the data.
""")

    # ============================================================== B
    print("#" * 78 + "\nB. DESIGN OBJECTIVE\n" + "#" * 78)
    print("""  O1  Exactness: return the same minimum distance as brute force on every input.
  O2  Distance calculations at n=2000 (uniform) reduced by >= 99% versus 1,999,000.
  O3  Growth of distance calculations with n lower than quadratic (log-log slope < 1.5).
  O4  Wall-clock time (including sorting) >= 10x faster at n=4000 uniform.
  O5  Degenerate inputs must not silently fall back to n^2 behaviour without being detected.
""")

    # ============================================================== C / D
    print("#" * 78 + "\nC. REVISED STRATEGY (see Pseudocode folder)  /  D. PREDICTIONS (before running)\n" + "#" * 78)
    print("""  R1 sorted sweep: preprocessing = sort along the widest axis (n log2 n comparisons, O(n) memory).
     A drone only needs to be compared with drones whose coordinate gap along that axis is < d_best.
  R2 grid: preprocessing = O(n) hashing into cells (O(n) memory); compare only nearby cells.

  PREDICTIONS
   P1 Uniform data: distance calcs for R1 grow roughly like n (a small constant number of near
      neighbours per drone) -> ~ 10-30 per drone, i.e. about 20,000-60,000 at n=2000 (>= 97% fewer).
   P2 Total key operations of R1 are dominated by the sort, ~ n*log2(n).
   P3 Time at n=4000 improves by about 20-50x; the advantage GROWS with n.
   P4 Clustered data: R1 still helps but less (clusters put many drones inside the pruning window).
   P5 Column data: sorting on x alone (fixed axis) will NOT prune (every gap is ~0), staying ~ n^2;
      choosing the widest axis restores the benefit.
   P6 R2 (grid) is excellent on uniform data but degrades on clustered data because the cell size is
      tuned to average density (many drones per cell).
   P7 For very small n (< ~30) the original may be as fast or faster (sort overhead).
""")

    # ============================================================== E
    print("#" * 78 + "\nE. IMPLEMENT AND VALIDATE  (same test conditions: Q4 generator, same seeds)\n" + "#" * 78)
    results = []

    def run_dataset(name, gen, sizes):
        print("\nDATASET: %s" % name)
        print("%6s | %12s | %10s %10s %10s %9s | %10s %10s | %9s %9s %9s | %s" % (
            "n", "BRUTE calcs", "R1 sort", "R1 gaps", "R1 calcs", "R1 reduc", "R2 lookups", "R2 calcs",
            "t brute", "t R1", "t R2", "same answer"))
        for n in sizes:
            pts = gen(n)
            reps = 1 if n >= 1000 else 5
            tb, (bb, _, _, dcb, _) = timeit(lambda: brute(pts), reps)
            bs, _, _, sc, gp, dcs = sweep(pts)
            ts, _ = timeit(lambda: sweep_timed(pts), reps)
            tg, (bg, lk, dcg, occ) = timeit(lambda: grid(pts), reps)
            ok = math.isclose(bb, bs, rel_tol=1e-12, abs_tol=1e-12) and math.isclose(bb, bg, rel_tol=1e-12, abs_tol=1e-12)
            assert ok, (name, n, bb, bs, bg)
            red = 100.0 * (1 - dcs / dcb)
            print("%6d | %12d | %10d %10d %10d %8.2f%% | %10d %10d | %8.4fs %8.4fs %8.4fs | %s" % (
                n, dcb, sc, gp, dcs, red, lk, dcg, tb, ts, tg, ok))
            results.append([name, n, dcb, sc, gp, dcs, round(red, 3), lk, dcg, occ, round(tb, 5), round(ts, 5), round(tg, 5)])

    run_dataset("U  uniform random in 10 km x 10 km (same data as Q4)", uniform, [100, 250, 500, 1000, 2000, 4000, 8000])
    run_dataset("C  clustered (5 Gaussian clusters, sigma=150 m)", clustered, [500, 1000, 2000, 4000])

    print("\nDATASET: V  vertical corridor (x-spread 1 m, y-spread 10 km) - tests axis choice")
    print("%6s | %12s | %22s | %22s | %s" % ("n", "BRUTE calcs", "R1 fixed x-axis calcs", "R1 widest-axis calcs", "same answer"))
    for n in (500, 1000, 2000, 4000):
        pts = column(n)
        bb, _, _, dcb, _ = brute(pts)
        fx = sweep(pts, choose_axis=False, forced_axis=0)
        au = sweep(pts, choose_axis=True)
        ok = math.isclose(bb, fx[0], rel_tol=1e-12) and math.isclose(bb, au[0], rel_tol=1e-12)
        assert ok
        print("%6d | %12d | %14d (%5.1f%%) | %14d (%5.1f%%) | %s" % (
            n, dcb, fx[5], 100.0 * fx[5] / dcb, au[5], 100.0 * au[5] / dcb, ok))
        results.append(["V corridor fixed-x", n, dcb, fx[3], fx[4], fx[5], round(100 * (1 - fx[5] / dcb), 3), "", "", "", "", "", ""])
        results.append(["V corridor widest-axis", n, dcb, au[3], au[4], au[5], round(100 * (1 - au[5] / dcb), 3), "", "", "", "", "", ""])

    print("\nDATASET: W  two parallel vertical lines x=0 and x=10 km (x-spread 10 km > y-spread 5 km) - ADVERSARIAL for R1")
    print("%6s | %12s | %20s | %20s | %s" % ("n", "BRUTE calcs", "R1 calcs (% of brute)", "R2 grid calcs", "same answer"))
    for n in (500, 1000, 2000, 4000):
        pts = two_lines(n)
        bb, _, _, dcb, _ = brute(pts)
        r1 = sweep(pts)
        r2 = grid(pts)
        ok = math.isclose(bb, r1[0], rel_tol=1e-12) and math.isclose(bb, r2[0], rel_tol=1e-12)
        assert ok
        print("%6d | %12d | %12d (%5.1f%%) | %12d (%5.1f%%) | %s" % (n, dcb, r1[5], 100.0 * r1[5] / dcb, r2[2], 100.0 * r2[2] / dcb, ok))
        results.append(["W two parallel lines", n, dcb, r1[3], r1[4], r1[5], round(100 * (1 - r1[5] / dcb), 3), r2[1], r2[2], r2[3], "", "", ""])

    print("\nEDGE CASES (correctness): duplicates, two points, identical x")
    for name, pts in (("two drones", [(0.0, 0.0), (3.0, 4.0)]),
                      ("duplicate position", [(1.0, 1.0), (5.0, 5.0), (1.0, 1.0), (9.0, 2.0)]),
                      ("all same x", [(2.0, float(y)) for y in (0, 10, 25, 26, 80)])):
        b = brute(pts)[0]
        s1 = sweep(pts)[0]
        g1 = grid(pts)[0]
        print("  %-20s brute=%.3f  sweep=%.3f  grid=%.3f  agree=%s" % (name, math.sqrt(b), math.sqrt(s1), math.sqrt(g1), b == s1 == g1))
        assert b == s1 == g1

    print("\nCROSSOVER FOR SMALL n (uniform data, time per call, 300 repetitions)")
    print("%6s | %12s | %12s | %s" % ("n", "brute (us)", "sweep (us)", "faster"))
    small = []
    for n in (5, 10, 20, 30, 50, 100):
        pts = uniform(n)
        tb, _ = timeit(lambda: brute(pts), 300)
        ts, _ = timeit(lambda: sweep_timed(pts), 300)
        print("%6d | %12.1f | %12.1f | %s" % (n, tb * 1e6, ts * 1e6, "brute" if tb < ts else "sweep"))
        small.append([n, round(tb * 1e6, 2), round(ts * 1e6, 2)])

    # prediction checks
    U = [r for r in results if r[0].startswith("U")]
    u2000 = [r for r in U if r[1] == 2000][0]
    lx = [math.log(r[1]) for r in U]

    def slope(col):
        ly = [math.log(r[col]) for r in U]
        mx, my = sum(lx) / len(lx), sum(ly) / len(ly)
        return sum((a - mx) * (b - my) for a, b in zip(lx, ly)) / sum((a - mx) ** 2 for a in lx)
    s_dc, s_all = slope(5), None
    tot = [[r[1], r[3] + r[4] + r[5]] for r in U]
    ly = [math.log(t[1]) for t in tot]
    mx, my = sum(lx) / len(lx), sum(ly) / len(ly)
    s_all = sum((a - mx) * (b - my) for a, b in zip(lx, ly)) / sum((a - mx) ** 2 for a in lx)
    u4000 = [r for r in U if r[1] == 4000][0]
    print("\nOBJECTIVE / PREDICTION CHECK")
    print("  O1 exactness            : all runs agree with brute force -> met")
    print("  O2 reduction at n=2000  : %.3f%% fewer distance calcs (%d -> %d)  target >= 99%%" % (u2000[6], u2000[2], u2000[5]))
    print("  O3 growth exponent      : distance calcs slope = %.2f ; total key ops (sort+gaps+calcs) slope = %.2f (brute 2.00)" % (s_dc, s_all))
    print("  O4 speed-up at n=4000   : R1 %.1fx faster ; R2 %.1fx faster" % (u4000[10] / u4000[11], u4000[10] / u4000[12]))
    print("  P2 sort dominates?      : at n=2000 sort comps=%d, gap checks=%d, distance calcs=%d" % (u2000[3], u2000[4], u2000[5]))

    with open(os.path.join(RAW, "q7_original_vs_redesign.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dataset", "n", "brute_dist_calcs", "R1_sort_comparisons", "R1_gap_checks", "R1_dist_calcs", "R1_reduction_pct",
                    "R2_cell_lookups", "R2_dist_calcs", "R2_max_cell_occupancy", "t_brute_s", "t_R1_s", "t_R2_s"])
        w.writerows(results)
    with open(os.path.join(RAW, "q7_small_n_crossover.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n", "brute_us", "sweep_us"])
        w.writerows(small)
    with open(os.path.join(RAW, "q7_diagnosis.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n", "dist_calcs", "best_updates", "pairs_with_x_gap>=dmin", "time_s"])
        w.writerows(diag)

    # ------------------------------------------------ graphs
    ns = [r[1] for r in U]
    fig, ax = plt.subplots(1, 3, figsize=(15.5, 4.4))
    ax[0].loglog(ns, [r[2] for r in U], "o-", label="original (n(n-1)/2)")
    ax[0].loglog(ns, [r[5] for r in U], "s-", label="R1 distance calcs")
    ax[0].loglog(ns, [r[3] + r[4] + r[5] for r in U], "^-", label="R1 total key ops")
    ax[0].loglog(ns, [r[8] for r in U], "d-", label="R2 grid calcs")
    ax[0].set_xlabel("n")
    ax[0].set_ylabel("operations")
    ax[0].set_title("Uniform data: operations")
    ax[0].legend(fontsize=8)
    ax[0].grid(alpha=.3, which="both")
    ax[1].loglog(ns, [r[10] for r in U], "o-", label="original")
    ax[1].loglog(ns, [r[11] for r in U], "s-", label="R1 sweep")
    ax[1].loglog(ns, [r[12] for r in U], "d-", label="R2 grid")
    ax[1].axhline(1.0, color="r", ls=":", label="1 s limit")
    ax[1].set_xlabel("n")
    ax[1].set_ylabel("seconds")
    ax[1].set_title("Uniform data: time")
    ax[1].legend(fontsize=8)
    ax[1].grid(alpha=.3, which="both")
    C = [r for r in results if r[0].startswith("C")]
    idx = [r[1] for r in C]
    xs = range(len(C))
    ax[2].bar([x - 0.27 for x in xs], [r[2] for r in C], 0.27, label="original")
    ax[2].bar(list(xs), [r[5] for r in C], 0.27, label="R1 sweep")
    ax[2].bar([x + 0.27 for x in xs], [r[8] for r in C], 0.27, label="R2 grid")
    ax[2].set_xticks(list(xs))
    ax[2].set_xticklabels(idx)
    ax[2].set_yscale("log")
    ax[2].set_xlabel("n")
    ax[2].set_ylabel("distance calculations")
    ax[2].set_title("Clustered data")
    ax[2].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "q7_graph_original_vs_redesign.png"), dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    main()
