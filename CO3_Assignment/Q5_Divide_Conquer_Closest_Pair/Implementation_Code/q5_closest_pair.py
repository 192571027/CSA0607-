"""Q5 - Closest pair of points: brute force (CO2) vs Divide & Conquer.
Student A: decomposition design (Pseudocode/). Student B: comparative evidence below.
Cost metric: number of distance computations (squared distances; sqrt only for the final answer)."""
import random, math, time, sys
sys.setrecursionlimit(10000)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
OUT = "../Output_Screenshots/"

def d2(p, q): return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2

def brute(P):
    cnt, best, pair = 0, float("inf"), None
    for i in range(len(P)):
        for j in range(i + 1, len(P)):
            cnt += 1; d = d2(P[i], P[j])
            if d < best: best, pair = d, (P[i], P[j])
    return best, pair, cnt

def closest_dc(P):
    """Pre-sort by x once; recursion also returns the points sorted by y (merge step) -> O(n log n)."""
    Px = sorted(P)
    cnt = [0]
    def rec(lo, hi):                         # works on Px[lo:hi]; returns (best_d2, pair, points sorted by y)
        n = hi - lo
        if n <= 3:                           # base case: brute force
            best, pair = float("inf"), None
            for i in range(lo, hi):
                for j in range(i + 1, hi):
                    cnt[0] += 1; d = d2(Px[i], Px[j])
                    if d < best: best, pair = d, (Px[i], Px[j])
            return best, pair, sorted(Px[lo:hi], key=lambda p: p[1])
        mid = (lo + hi) // 2; midx = Px[mid][0]
        dl, pl, yl = rec(lo, mid); dr, pr, yr = rec(mid, hi)
        best, pair = (dl, pl) if dl <= dr else (dr, pr)
        # merge by y
        ys, i, j = [], 0, 0
        while i < len(yl) and j < len(yr):
            if yl[i][1] <= yr[j][1]: ys.append(yl[i]); i += 1
            else: ys.append(yr[j]); j += 1
        ys.extend(yl[i:]); ys.extend(yr[j:])
        # strip: points within sqrt(best) of the dividing line, already in y order
        strip = [p for p in ys if (p[0] - midx) ** 2 < best]
        for a in range(len(strip)):
            for b in range(a + 1, len(strip)):
                if (strip[b][1] - strip[a][1]) ** 2 >= best: break   # at most ~7 neighbours survive this test
                cnt[0] += 1; d = d2(strip[a], strip[b])
                if d < best: best, pair = d, (strip[a], strip[b])
        return best, pair, ys
    best, pair, _ = rec(0, len(Px))
    return best, pair, cnt[0]

def gen(kind, n):
    if kind == "uniform":   return list({(random.randint(0, 10 * n), random.randint(0, 10 * n)) for _ in range(n)})
    if kind == "clustered":
        cs = [(random.randint(0, 10**6), random.randint(0, 10**6)) for _ in range(5)]
        return list({(c[0] + int(random.gauss(0, 500)), c[1] + int(random.gauss(0, 500))) for c in cs for _ in range(n // 5)})
    if kind == "collinear": return [(x, 5) for x in random.sample(range(10 * n), n)]
    if kind == "same-x":    return [(5, y) for y in random.sample(range(10 * n), n)]

def timeit(fn):
    t = time.perf_counter(); r = fn(); return r, (time.perf_counter() - t) * 1000

def main():
    random.seed(11)
    print("=== Q5 correctness: D&C vs brute force on 300 random small cases (incl. duplicates-free grids) ===")
    for _ in range(300):
        n = random.randint(2, 40); P = list({(random.randint(0, 30), random.randint(0, 30)) for _ in range(n)})
        if len(P) < 2: continue
        assert brute(P)[0] == closest_dc(P)[0]
    for kind in ("uniform", "clustered", "collinear", "same-x"):
        P = gen(kind, 500); assert brute(P)[0] == closest_dc(P)[0], kind
    print("all agree (including clustered, collinear, vertical-line inputs)")

    print("\n=== Growth of distance computations (uniform random points) ===")
    print(f"{'n':>7}{'brute dists':>13}{'n(n-1)/2':>12}{'D&C dists':>11}{'ratio':>9}{'brute ms':>10}{'D&C ms':>9}{'D&C dists/(n lg n)':>20}")
    ns = [10, 20, 50, 100, 200, 500, 1000, 2000, 4000]; B, D, tB, tD = [], [], [], []
    for n in ns:
        P = gen("uniform", n); n = len(P)
        (bd, _, bc), tb = timeit(lambda: brute(P)); (dd, _, dc), td = timeit(lambda: closest_dc(P))
        assert bd == dd
        B.append(bc); D.append(dc); tB.append(tb); tD.append(td)
        print(f"{n:>7}{bc:>13}{n*(n-1)//2:>12}{dc:>11}{bc/dc:>9.1f}{tb:>10.2f}{td:>9.2f}{dc/(n*math.log2(n)):>20.2f}")
    print("\nD&C only (brute force infeasible):")
    for n in (10_000, 50_000, 100_000):
        P = gen("uniform", n); (dd, _, dc), td = timeit(lambda: closest_dc(P))
        print(f"  n={len(P):>7}: D&C dists={dc:>9}  (brute would need {len(P)*(len(P)-1)//2:,})  time={td:.0f} ms")

    print("\n=== Different data distributions, n=2000 ===")
    print(f"{'kind':<10}{'n':>6}{'brute':>10}{'D&C':>8}{'D&C ms':>8}")
    for kind in ("uniform", "clustered", "collinear", "same-x"):
        P = gen(kind, 2000); (bd, _, bc), _ = timeit(lambda: brute(P)); (dd, _, dc), td = timeit(lambda: closest_dc(P))
        assert bd == dd
        print(f"{kind:<10}{len(P):>6}{bc:>10}{dc:>8}{td:>8.1f}")

    print("\n=== Practical crossover (time) for small n ===")
    for n in (4, 8, 16, 32, 64, 128):
        reps = 200 if n <= 32 else 50
        P = gen("uniform", n)
        tb = min(timeit(lambda: brute(P))[1] for _ in range(reps)); td = min(timeit(lambda: closest_dc(P))[1] for _ in range(reps))
        print(f"  n={len(P):>4}: brute {tb:.4f} ms | D&C {td:.4f} ms | {'D&C' if td < tb else 'brute'} faster")

    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].loglog(ns, B, "o-", label="brute force"); ax[0].loglog(ns, D, "s-", label="D&C"); ax[0].set_title("Distance computations")
    ax[1].loglog(ns, tB, "o-", label="brute force"); ax[1].loglog(ns, tD, "s-", label="D&C"); ax[1].set_title("Time (ms)")
    for a in ax: a.set_xlabel("n"); a.legend(); a.grid(True, alpha=.3, which="both")
    plt.tight_layout(); plt.savefig(OUT + "q5_closest_pair_growth.png", dpi=130); plt.close()

if __name__ == "__main__":
    main()
