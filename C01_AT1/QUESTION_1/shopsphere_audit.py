import math
import os
import random

OPS_PER_SEC = 10 ** 8
WINDOW_SEC = 10 * 60            # nightly processing window = 10 minutes
WINDOW_OPS = OPS_PER_SEC * WINDOW_SEC


# --------------------------------------------------------------------------
# Module implementations (instrumented: each returns the basic-operation count)
# --------------------------------------------------------------------------
def m1_duplicate_detector(products):
    """M1: compare every product with every later product.
    Basic operation = one pair comparison (title test)."""
    n, comparisons, dups = len(products), 0, []
    for i in range(0, n - 1):
        for j in range(i + 1, n):
            comparisons += 1
            if products[i][0] == products[j][0] and products[i][1] == products[j][1]:
                dups.append(j)
    return comparisons, dups


def m2_rate_limiter(n):
    """M2: audit windows of doubling size.  Basic operation = Audit(Request[j])."""
    audits, i = 0, 1
    while i < n:
        for _ in range(0, i):
            audits += 1
        i *= 2
    return audits


def s1_sequential_search(arr, key):
    """S1: sequential scan.  Returns (index or -1, comparisons)."""
    comps = 0
    for idx, v in enumerate(arr):
        comps += 1
        if v == key:
            return idx, comps
    return -1, comps


def s2_binary_search_iter(arr, key):
    """S2 (iterative): O(1) extra space."""
    lo, hi, comps = 0, len(arr) - 1, 0
    while lo <= hi:
        mid = (lo + hi) // 2
        comps += 1
        if arr[mid] == key:
            return mid, comps
        if key < arr[mid]:
            hi = mid - 1
        else:
            lo = mid + 1
    return -1, comps


def s2_binary_search_rec(arr, key, lo=0, hi=None, depth=1):
    """S2 (recursive): O(log n) stack frames.  Returns (idx, comps, max_depth)."""
    if hi is None:
        hi = len(arr) - 1
    if lo > hi:
        return -1, 0, depth - 1
    mid = (lo + hi) // 2
    if arr[mid] == key:
        return mid, 1, depth
    if key < arr[mid]:
        r = s2_binary_search_rec(arr, key, lo, mid - 1, depth + 1)
    else:
        r = s2_binary_search_rec(arr, key, mid + 1, hi, depth + 1)
    return r[0], r[1] + 1, r[2]


# --------------------------------------------------------------------------
# Recurrences (evaluated directly for n = power of two)
# --------------------------------------------------------------------------
def T_s2(n):
    return 1 if n == 1 else T_s2(n // 2) + 1


def T_m4_cur(n):
    return 1 if n == 1 else 4 * T_m4_cur(n // 2) + n


def T_m4_new(n):
    return 1 if n == 1 else 2 * T_m4_new(n // 2) + n


def T_m5(n):
    return 1 if n == 1 else 2 * T_m5(n // 2) + n * math.log2(n)


# --------------------------------------------------------------------------
# Closed forms derived in the report
# --------------------------------------------------------------------------
def m1_formula(n):
    return n * (n - 1) // 2


def m2_formula(n):
    return 2 ** math.ceil(math.log2(n)) - 1


def s2_formula(n):
    return int(math.log2(n)) + 1


def m4_cur_formula(n):
    return 2 * n * n - n


def m4_new_formula(n):
    return n * math.log2(n) + n


def m5_formula(n):
    L = math.log2(n)
    return n + n * L * (L + 1) / 2


def f_report(n):
    return 3 * n * n + 10 * n * math.log2(n) + 50


def s1_average(n, p):
    return p * (n + 1) / 2 + (1 - p) * n


def fmt_time(sec):
    if sec < 1e-3:
        return f"{sec * 1e6:.2f} us"
    if sec < 1:
        return f"{sec * 1e3:.2f} ms"
    if sec < 120:
        return f"{sec:.2f} s"
    if sec < 7200:
        return f"{sec / 60:.1f} min"
    return f"{sec / 3600:.2f} h"


def banner(t):
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


# --------------------------------------------------------------------------
def part_b():
    banner("PART (b)  Iterative modules M1 and M2 : measured vs. derived counts")
    print("M1: comparisons = n(n-1)/2")
    print(f"{'n':>8} {'measured':>14} {'formula':>14}  match")
    for n in (5, 10, 100, 500, 1000):
        prods = [(f"t{k}", f"s{k}") for k in range(n)]
        c, _ = m1_duplicate_detector(prods)
        print(f"{n:>8} {c:>14} {m1_formula(n):>14}  {c == m1_formula(n)}")
    prods = [("A", "S1"), ("B", "S1"), ("A", "S1"), ("C", "S2"), ("A", "S2")]
    _, d = m1_duplicate_detector(prods)
    print("Duplicate demo (rows 0 and 2 are the same title+seller): flagged ->", d)

    print("\nM2: Audit operations = 2^ceil(log2 n) - 1")
    print(f"{'n':>10} {'measured':>12} {'formula':>12} {'n log2 n':>14}  match")
    for n in (2, 3, 8, 100, 1000, 1024, 1025, 100000):
        a = m2_rate_limiter(n)
        print(f"{n:>10} {a:>12} {m2_formula(n):>12} {n * math.log2(n):>14.0f}  {a == m2_formula(n)}")
    a = m2_rate_limiter(1024)
    print(f"\nVerification n=1024: outer iterations = {int(math.log2(1024))} "
          f"(i = 1,2,...,512), Audit ops = {a}  (= 2^10 - 1 = 1023)")
    print("Ratio audits/n for growing n (stays between 1 and 2 -> Theta(n)):")
    for n in (10 ** 3, 10 ** 4, 10 ** 5, 10 ** 6):
        r = m2_rate_limiter(n)
        print(f"   n={n:>8}: audits={r:>8}  audits/n={r / n:.3f}")


def part_c():
    banner("PART (c)  Recurrence for S2 : T(n)=T(n/2)+1, T(1)=1")
    print(f"{'n':>10} {'T(n) recurrence':>16} {'1+log2 n':>10}  match")
    for k in (0, 1, 4, 10, 20):
        n = 2 ** k
        print(f"{n:>10} {T_s2(n):>16} {1 + k:>10}  {T_s2(n) == 1 + k}")
    arr = list(range(1, 1024))                       # n = 2^10 - 1
    worst = max(s2_binary_search_iter(arr, k)[1] for k in arr)
    _, c, depth = s2_binary_search_rec(arr, 1)
    print(f"\nn=1023: worst-case comparisons (iterative) = {worst}; "
          f"recursion depth (stack frames) = {depth}")
    print("Space: iterative O(1) (lo, hi, mid) ; recursive O(log n) call stack")


def part_d():
    banner("PART (d)  Master theorem : M4 and M5")
    print("M4 current : T(n)=4T(n/2)+n   a=4 b=2 f=n   n^log2(4)=n^2  -> Case 1 -> Theta(n^2)")
    print("M4 redesign: T(n)=2T(n/2)+n   a=2 b=2 f=n   n^log2(2)=n    -> Case 2 -> Theta(n log n)")
    print(f"\n{'n':>10} {'T_cur':>16} {'2n^2-n':>16} {'T_new':>14} {'n(log n+1)':>14}")
    for k in (4, 8, 12, 16):
        n = 2 ** k
        print(f"{n:>10} {T_m4_cur(n):>16} {m4_cur_formula(n):>16} "
              f"{T_m4_new(n):>14} {m4_new_formula(n):>14.0f}")
    print("\nEffect of doubling the data (ratio T(2n)/T(n)):")
    print(f"{'n':>10} {'current':>10} {'redesign':>10}")
    for k in (10, 14, 18, 20):
        n = 2 ** k
        print(f"{n:>10} {T_m4_cur(2 * n) / T_m4_cur(n):>10.3f} {T_m4_new(2 * n) / T_m4_new(n):>10.3f}")
    print("\nM5: T(n)=2T(n/2)+n log n   a=2 b=2  n^log_b a = n   f(n)=n log n")
    print("   Case 1 fails (f is bigger than n), Case 2 (k=0) fails (extra log),")
    print("   Case 3 fails (n log n is NOT Omega(n^(1+eps))). Extended MT, k=1 -> Theta(n log^2 n)")
    print(f"\n{'n':>10} {'T_m5':>16} {'n+n*L(L+1)/2':>16} {'T/(n log^2 n)':>14}")
    for k in (4, 8, 12, 16, 20):
        n = 2 ** k
        print(f"{n:>10} {T_m5(n):>16.1f} {m5_formula(n):>16.1f} {T_m5(n) / (n * k * k):>14.3f}")


def part_e():
    banner("PART (e)  Best / average / worst cases of S1 and S2")
    n = 1_000_000
    arr = list(range(1, n + 1))
    print(f"n = {n:,}")
    print(f"S1 best  (key at index 0)     : {s1_sequential_search(arr, 1)[1]:>9,} comparisons")
    print(f"S1 worst (key last / absent)  : {s1_sequential_search(arr, n)[1]:>9,} / "
          f"{s1_sequential_search(arr, -5)[1]:,} comparisons")
    print("S1 average, successful search : (n+1)/2 = {:,.1f}".format((n + 1) / 2))
    print("S1 average, unsuccessful      : n = {:,}".format(n))
    print("\nS1 average A(n,p) = p(n+1)/2 + (1-p)n")
    for p in (0.0, 0.25, 0.5, 0.75, 1.0):
        print(f"   p={p:<4}: A = {s1_average(n, p):>14,.2f}")
    print(f"\n>>> n=1,000,000, p=0.5  ->  A = {s1_average(n, 0.5):,.2f} comparisons")

    # empirical check of the formula at a smaller n with random queries
    random.seed(7)
    m, p, trials = 2000, 0.5, 60000
    a2 = list(range(m))
    tot = 0
    for _ in range(trials):
        key = random.randrange(m) if random.random() < p else -1
        tot += s1_sequential_search(a2, key)[1]
    print(f"Monte-Carlo check (n={m}, p={p}, {trials} trials): "
          f"measured {tot / trials:,.1f}  vs  formula {s1_average(m, p):,.1f}")

    print("\nS2 (binary search) on sorted index, n = 1,000,000")
    counts = [s2_binary_search_iter(arr, k)[1] for k in range(1, n + 1)]
    print(f"S2 best  (key = middle element): {s2_binary_search_iter(arr, arr[(n - 1) // 2])[1]} comparison")
    print(f"S2 average (successful, all keys): {sum(counts) / len(counts):.3f} comparisons")
    print(f"S2 worst : {max(counts)} comparisons   (floor(log2 n)+1 = {s2_formula(n)})")
    print(f"S2 unsuccessful search           : {s2_binary_search_iter(arr, 0)[1]} comparisons")


def part_f():
    banner("PART (f)  f(n)=3n^2+10n log2 n+50  is Theta(n^2)")
    c1, c2, n0 = 3, 63, 1
    ok = all(c1 * n * n <= f_report(n) <= c2 * n * n for n in range(n0, 20001))
    print(f"constants c1={c1}, c2={c2}, n0={n0}: c1 n^2 <= f(n) <= c2 n^2 for 1<=n<=20000 : {ok}")
    c2b, n0b = 4, 60
    ok2 = all(c1 * n * n <= f_report(n) <= c2b * n * n for n in range(n0b, 20001))
    print(f"tighter pair c1=3, c2=4, n0=60                                               : {ok2}"
          f"   (n=59 fails: f={f_report(59):.1f} > 4n^2={4 * 59 * 59})")
    print(f"\n{'n':>8} {'f(n)':>18} {'f(n)/n^2':>10} {'f(n)/n':>16}")
    for n in (10, 100, 1000, 10 ** 4, 10 ** 5, 10 ** 6):
        print(f"{n:>8} {f_report(n):>18,.1f} {f_report(n) / n ** 2:>10.4f} {f_report(n) / n:>16,.1f}")
    print("f(n)/n^2 -> 3 (bounded)  => Theta(n^2);  f(n)/n -> infinity => f(n) is not O(n)")
    print("Disproof of O(n): for any c, n > c/3 gives f(n) >= 3n^2 > c n.")
    for c in (10, 1000, 10 ** 6):
        n = c // 3 + 1
        print(f"   c={c:>8}: n={n:>8} -> f(n)={f_report(n):,.0f} > c*n={c * n:,}  : {f_report(n) > c * n}")


def part_g():
    banner("PART (g)  Scalability decision  (10^8 ops/s, window = 10 min = 6x10^10 ops)")
    n = 1_000_000
    rows = [
        ("M1 Duplicate detector", m1_formula(n), "Theta(n^2)"),
        ("M2 Rate limiter", m2_formula(n), "Theta(n)"),
        ("S2 Binary search (1 query)", s2_formula(n), "Theta(log n)"),
        ("M4 Recommender - current", m4_cur_formula(n), "Theta(n^2)"),
        ("M4 Recommender - redesign", m4_new_formula(n), "Theta(n log n)"),
        ("M5 Sales analytics", m5_formula(n), "Theta(n log^2 n)"),
        ("Report generator f(n)", f_report(n), "Theta(n^2)"),
    ]
    print(f"n = {n:,}   window budget = {WINDOW_OPS:,} operations\n")
    print(f"{'Module':<30}{'Complexity':<18}{'Operations':>20}{'Time':>12}  Verdict")
    print("-" * 92)
    for name, ops, cx in rows:
        t = ops / OPS_PER_SEC
        print(f"{name:<30}{cx:<18}{ops:>20,.0f}{fmt_time(t):>12}  "
              f"{'PASS' if ops <= WINDOW_OPS else 'FAIL'}")
    print("\nGrowth when the catalogue grows 100,000 -> 1,000,000 (10x):")
    print(f"{'Module':<30}{'ops @1e5':>18}{'ops @1e6':>18}{'ratio':>9}")
    n1 = 100_000
    gr = [("M1", m1_formula), ("M2", m2_formula), ("M4 current", m4_cur_formula),
          ("M4 redesign", m4_new_formula), ("M5", m5_formula), ("Report f(n)", f_report)]
    for name, fn in gr:
        a, b = fn(n1), fn(n)
        print(f"{name:<30}{a:>18,.0f}{b:>18,.0f}{b / a:>9.1f}")
    print("\nRedesign estimate for M1 (sort by (title,seller) key, then scan neighbours):")
    ops = n * math.log2(n) + n
    print(f"   ~ n log2 n + n = {ops:,.0f} ops = {fmt_time(ops / OPS_PER_SEC)}  "
          f"(hash-set variant: ~n ops, Theta(n) expected)")


def make_chart(path):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed - chart skipped")
        return
    ns = [2 ** k for k in range(4, 21)]
    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.plot(ns, [m1_formula(n) for n in ns], label="M1  n(n-1)/2  ~ n^2", marker="o", ms=3)
    ax.plot(ns, [m4_cur_formula(n) for n in ns], label="M4 current  2n^2-n", marker="s", ms=3)
    ax.plot(ns, [m5_formula(n) for n in ns], label="M5  ~ n log^2 n", marker="^", ms=3)
    ax.plot(ns, [m4_new_formula(n) for n in ns], label="M4 redesign  n(log n+1)", marker="d", ms=3)
    ax.plot(ns, [m2_formula(n) for n in ns], label="M2  2^ceil(log n)-1 ~ n", marker="x", ms=4)
    ax.plot(ns, [s2_formula(n) for n in ns], label="S2  1+log n", marker="v", ms=3)
    ax.axhline(WINDOW_OPS, color="red", ls="--", label="10-min window (6e10 ops)")
    ax.axvline(1_000_000, color="grey", ls=":")
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xlabel("catalogue size n")
    ax.set_ylabel("basic operations")
    ax.set_title("ShopSphere - growth of basic operations")
    ax.legend(fontsize=8)
    ax.grid(alpha=.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    print(f"chart saved -> {path}")


if __name__ == "__main__":
    print("ShopSphere Scalability Audit  -  CSA06 CO1 AT1")
    part_b()
    part_c()
    part_d()
    part_e()
    part_f()
    part_g()
    here = os.path.dirname(os.path.abspath(__file__))
    make_chart(os.path.join(here, "..", "Supporting_Files", "growth_chart.png"))
