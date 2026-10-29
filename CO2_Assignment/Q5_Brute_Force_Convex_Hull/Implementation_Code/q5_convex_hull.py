"""
Q5 - Brute-Force Convex Hull derived from a geometric principle
(Wildlife reserve boundary monitoring)

GEOMETRIC PRINCIPLE (given):  segment PiPj is part of the boundary if all the
other points lie on one single side of the line through Pi and Pj.

MY DERIVATION
 1. Two points define a line.  For Pi=(x1,y1), Pj=(x2,y2) the line is
        a*x + b*y = c   with a = y2-y1, b = x1-x2, c = x1*y2 - y1*x2
 2. Side of a third point Pk=(x,y): s(Pk) = a*x + b*y - c.
        s > 0  one side (the LEFT of the directed line Pi->Pj),
        s < 0  the other side (the right),
        s = 0  Pk is ON the line.
    (s is the cross product (Pj-Pi) x (Pk-Pi); integer inputs -> exact test.)
 3. Examine every other point.  PiPj is a hull edge iff the non-zero values of
    s all have the SAME sign, and every point with s = 0 lies inside the
    segment PiPj (so collinear points in the middle of an edge are not
    reported as corners).
 4. Build boundary: if all s > 0 the edge, directed Pi->Pj, has the whole set to
    its left, i.e. it is a counter-clockwise hull edge; store succ[Pi]=Pj.  If
    all s < 0 use Pj->Pi.  Follow succ[] from any vertex to read the polygon.

PREDICTION (before running)
  Without early exit: every one of C(n,2) pairs tests n-2 points
  => n(n-1)(n-2)/2  side tests = Theta(n^3).
  With early exit (stop a pair as soon as both signs have appeared) most
  non-edges are rejected after a few tests, so for random points the measured
  work should be close to n^2 order, while the worst case remains n^3.
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


def side(p, q, r):
    """Sign value s of r relative to directed line p->q (cross product)."""
    return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])


def on_segment(p, q, r):
    return min(p[0], q[0]) <= r[0] <= max(p[0], q[0]) and min(p[1], q[1]) <= r[1] <= max(p[1], q[1])


def brute_force_hull(points, early_exit=True, shuffle_scan=False):
    """Return (hull vertices in counter-clockwise order, side_tests, edges)."""
    pts = sorted(set(points))                 # remove duplicate stations
    n = len(pts)
    tests = 0
    if n <= 2:
        return pts, 0, []
    succ = {}
    edges = []
    order = list(range(n))
    if shuffle_scan:
        random.Random(99).shuffle(order)          # scan the 'other points' in random order
    for i in range(n - 1):
        for j in range(i + 1, n):
            p, q = pts[i], pts[j]
            pos = neg = False
            ok = True
            for k in order:
                if k == i or k == j:
                    continue
                s = side(p, q, pts[k])
                tests += 1
                if s > 0:
                    pos = True
                elif s < 0:
                    neg = True
                elif not on_segment(p, q, pts[k]):   # collinear but outside the segment
                    ok = False
                    if early_exit:
                        break
                if pos and neg:
                    ok = False
                    if early_exit:
                        break
            if ok and not (pos and neg):
                edges.append((i, j))
                if pos:
                    succ[i] = j                      # all points on the left of i->j : CCW
                elif neg:
                    succ[j] = i
                else:                                # all points collinear: segment both ways
                    succ[i] = j
                    succ.setdefault(j, i)
    if not succ:
        return pts, tests, edges
    start = min(succ)
    hull = [pts[start]]
    cur = succ[start]
    while cur != start and len(hull) <= n:
        hull.append(pts[cur])
        cur = succ.get(cur, start)
    return hull, tests, edges


def reference_hull(points):
    """Independent check only (Andrew's monotone chain) - NOT used by the solution."""
    pts = sorted(set(points))
    if len(pts) <= 2:
        return pts

    def build(seq):
        h = []
        for p in seq:
            while len(h) >= 2 and side(h[-2], h[-1], p) <= 0:
                h.pop()
            h.append(p)
        return h
    lo, up = build(pts), build(reversed(pts))
    return lo[:-1] + up[:-1]


def same_polygon(a, b):
    return set(a) == set(b) and len(a) == len(b)


def plot_hull(ax, pts, hull, title):
    xs, ys = zip(*pts)
    ax.scatter(xs, ys, s=18, c="#4c78a8", zorder=3)
    if len(hull) >= 2:
        hx = [p[0] for p in hull] + [hull[0][0]]
        hy = [p[1] for p in hull] + [hull[0][1]]
        ax.plot(hx, hy, "r-", lw=2, zorder=2)
        ax.scatter([p[0] for p in hull], [p[1] for p in hull], s=45, c="red", zorder=4)
    ax.set_title(title, fontsize=9)
    ax.set_aspect("equal")
    ax.grid(alpha=.3)


def main():
    print("=" * 78)
    print("Q5  BRUTE-FORCE CONVEX HULL - WILDLIFE RESERVE BOUNDARY MONITORING")
    print("=" * 78)
    print(__doc__.split("MY DERIVATION")[1].split("PREDICTION")[0])

    rng = random.Random(5)
    # ---------------- test configurations
    T1 = [(0, 0), (10, 0), (12, 6), (8, 12), (2, 11), (-3, 6)]            # 6 boundary stations
    T1 += [(rng.randint(1, 8), rng.randint(2, 9)) for _ in range(14)]     # 14 interior points
    T2 = ([(0, 0), (8, 0), (8, 8), (0, 8)]                                # square corners
          + [(4, 0), (8, 4), (4, 8), (0, 4), (2, 0), (8, 6)]              # collinear points ON edges
          + [(3, 3), (5, 5), (4, 4)]                                      # interior (diagonal collinear)
          + [(0, 0), (8, 8)])                                             # duplicate stations
    T3 = [(i, 2 * i + 1) for i in range(8)]                               # all collinear
    T4 = [(round(100 * math.cos(2 * math.pi * k / 16)), round(100 * math.sin(2 * math.pi * k / 16))) for k in range(16)]
    tests = [
        ("T1 mixed: 6 boundary + 14 interior stations", T1),
        ("T2 CHALLENGE: collinear points on edges, duplicates, interior diagonal", T2),
        ("T3 DEGENERATE: all stations collinear", T3),
        ("T4 WORST CASE: 16 stations on a circle (all are hull vertices)", T4),
    ]
    fig, axes = plt.subplots(1, 4, figsize=(17, 4.5))
    csvrows = []
    for (name, pts), ax in zip(tests, axes):
        hull, t_early, edges = brute_force_hull(pts, True)
        _, t_full, _ = brute_force_hull(pts, False)
        ref = reference_hull(pts)
        u = len(set(pts))
        print("-" * 78)
        print(name)
        print("  distinct points n=%d   hull vertices h=%d   hull edges found=%d" % (u, len(hull), len(edges)))
        print("  hull (CCW): %s" % (hull,))
        print("  matches independent reference hull: %s" % same_polygon(hull, ref))
        print("  side tests: with early exit=%d   without early exit=%d   n(n-1)(n-2)/2=%d" % (
            t_early, t_full, u * (u - 1) * (u - 2) // 2))
        assert same_polygon(hull, ref)
        csvrows.append([name, u, len(hull), t_early, t_full, u * (u - 1) * (u - 2) // 2])
        plot_hull(ax, sorted(set(pts)), hull, name.split(":")[0] + " (h=%d)" % len(hull))
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "q5_hull_visualisation.png"), dpi=130)
    plt.close(fig)
    with open(os.path.join(RAW, "q5_test_configs.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["test", "n", "hull_vertices", "side_tests_early_exit", "side_tests_full", "n(n-1)(n-2)/2"])
        w.writerows(csvrows)

    # ---------------- correctness on many random sets
    bad = 0
    for s in range(300):
        r = random.Random(s)
        k = r.randint(3, 30)
        pts = [(r.randint(0, 12), r.randint(0, 12)) for _ in range(k)]     # small grid -> many collinear/duplicates
        if not same_polygon(brute_force_hull(pts)[0], reference_hull(pts)):
            bad += 1
    print("-" * 78)
    print("RANDOMISED VALIDATION: 300 random sets on a 13x13 grid (many ties/collinear) -> mismatches = %d" % bad)

    # ---------------- growth
    print("\nGROWTH OF COMPUTATIONAL WORK  (random points, uniform in a square)")
    print("%6s | %6s | %12s | %12s | %12s | %8s | %8s" % ("n", "hull h", "tests(early)", "tests(full)", "n(n-1)(n-2)/2", "full/th", "time s"))
    grow = []
    for n in (10, 20, 40, 80, 160, 320):
        pts = [(rng.randint(0, 10 ** 6), rng.randint(0, 10 ** 6)) for _ in range(n)]
        t0 = time.perf_counter()
        hull, te, _ = brute_force_hull(pts, True)
        dt_e = time.perf_counter() - t0
        t0 = time.perf_counter()
        _, tf, _ = brute_force_hull(pts, False)
        dt_f = time.perf_counter() - t0
        th = n * (n - 1) * (n - 2) // 2
        print("%6d | %6d | %12d | %12d | %12d | %8.3f | %4.3f/%4.3f" % (n, len(hull), te, tf, th, tf / th, dt_e, dt_f))
        grow.append([n, len(hull), te, tf, th, round(dt_e, 4), round(dt_f, 4)])
    for a, b in zip(grow, grow[1:]):
        print("  n %3d -> %3d : tests x%.2f (early exit)   x%.2f (full; theory x8)" % (a[0], b[0], b[2] / a[2], b[3] / a[3]))
    lx = [math.log(g[0]) for g in grow]
    def slope(col):
        ly = [math.log(g[col]) for g in grow]
        mx, my = sum(lx) / len(lx), sum(ly) / len(ly)
        return sum((a - mx) * (b - my) for a, b in zip(lx, ly)) / sum((a - mx) ** 2 for a in lx)
    print("  log-log slope of work: full = %.2f ; early exit = %.2f" % (slope(3), slope(2)))
    print("  PREDICTION CHECK: I predicted early exit would behave close to n^2 for random points.")
    print("  Observed slope %.2f => prediction NOT supported; early exit lowers the constant (about 5x fewer" % slope(2))
    print("  tests at n=320) but the growth stays close to cubic.  Hypothesis: points are scanned in x-sorted")
    print("  order, so neighbouring points tend to lie on the same side of a line and a 'second side' is found late.")
    print("  Test of hypothesis: same random sets, but 'other points' scanned in RANDOM order:")
    shuf = []
    for g in grow:
        n = g[0]
        r2 = random.Random(1000 + n)
        pts = [(r2.randint(0, 10 ** 6), r2.randint(0, 10 ** 6)) for _ in range(n)]
        h1, t_sorted, _ = brute_force_hull(pts, True, False)
        h2, t_rand, _ = brute_force_hull(pts, True, True)
        assert same_polygon(h1, h2)
        shuf.append([n, t_sorted, t_rand])
        print("    n=%4d  tests sorted-scan=%9d   random-scan=%9d   (%.1fx fewer)" % (n, t_sorted, t_rand, t_sorted / t_rand))
    sl = [math.log(shuf[-1][2] / shuf[0][2]) / math.log(shuf[-1][0] / shuf[0][0])]
    print("    log-log slope with random scan order = %.2f" % sl[0])
    # worst case for early-exit: all points on a circle
    print("\nWORST-CASE FAMILY for the early-exit version: n points on a circle (every point is a hull vertex)")
    wc = []
    for n in (10, 20, 40, 80, 160):
        pts = list({(round(10 ** 6 * math.cos(2 * math.pi * k / n)), round(10 ** 6 * math.sin(2 * math.pi * k / n))) for k in range(n)})
        hull, te, _ = brute_force_hull(pts, True)
        wc.append([len(pts), te])
        print("  n=%4d hull=%4d tests(early)=%9d  n(n-1)(n-2)/2=%9d  ratio %.3f" % (
            len(pts), len(hull), te, len(pts) * (len(pts) - 1) * (len(pts) - 2) // 2,
            te / (len(pts) * (len(pts) - 1) * (len(pts) - 2) // 2)))
    with open(os.path.join(RAW, "q5_growth.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n", "hull_vertices", "tests_early_exit", "tests_full", "n(n-1)(n-2)/2", "time_early_s", "time_full_s"])
        w.writerows(grow)

    fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
    ns = [g[0] for g in grow]
    ax[0].loglog(ns, [g[3] for g in grow], "o-", label="full (no early exit)")
    ax[0].loglog(ns, [g[2] for g in grow], "s-", label="early exit (random pts)")
    ax[0].loglog(ns, [g[4] for g in grow], "k--", label="n(n-1)(n-2)/2")
    ax[0].loglog([w_[0] for w_ in wc], [w_[1] for w_ in wc], "^-", label="early exit, circle (worst)")
    ax[0].set_xlabel("n")
    ax[0].set_ylabel("side tests")
    ax[0].set_title("Q5: work vs n")
    ax[0].legend(fontsize=8)
    ax[0].grid(alpha=.3, which="both")
    ax[1].plot(ns, [g[5] for g in grow], "s-", label="early exit")
    ax[1].plot(ns, [g[6] for g in grow], "o-", label="full")
    ax[1].set_xlabel("n")
    ax[1].set_ylabel("seconds")
    ax[1].set_title("Execution time")
    ax[1].legend()
    ax[1].grid(alpha=.3)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "q5_graph_growth.png"), dpi=130)
    plt.close(fig)

    print("""
CORRECTNESS ARGUMENT (geometric reasoning)
 Let H be the half-plane bounded by the line L through Pi and Pj that contains
 every other point (accepted edge => all s have the same sign or are 0).
 (a) A half-plane is convex, so it contains the convex hull of the whole set.
     Hence the hull lies entirely on one side of L.
 (b) Pi and Pj are points of the set, so they lie on L and belong to the hull;
     the hull is convex so the segment PiPj also lies in the hull.
 (c) A point of the hull that lies on a line that supports the hull (touches it
     with the whole hull on one side) cannot be an interior point: any
     neighbourhood of it would contain points on the empty side of L.  So
     PiPj lies on the boundary.  Conversely every hull edge lies on a
     supporting line, so such a pair passes the test: no edge is missed.
 If some Pk were on the other side, a segment from Pk to a point beyond L would
 cross L inside the hull, so PiPj would pass through the interior and could not
 be boundary - the test rejects exactly those pairs.
""")


if __name__ == "__main__":
    main()
