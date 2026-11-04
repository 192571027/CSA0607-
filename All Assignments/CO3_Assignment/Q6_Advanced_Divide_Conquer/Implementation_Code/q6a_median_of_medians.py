"""Q6 (Student A) - k-th smallest: Median of Medians (deterministic worst-case O(n)) vs QuickSelect.
Counts element comparisons. Strategies compared:
  MoM            : groups of 5 -> median of medians pivot
  QS-first       : QuickSelect, deterministic pivot = first element (poor on sorted data)
  QS-random      : QuickSelect, random pivot
  (sorted input + first-element pivot is the adversarial case for QS-first)"""
import random, sys, math
sys.setrecursionlimit(20000)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
OUT = "../Output_Screenshots/"

class St:
    def __init__(self): self.cmp = 0; self.depth = 0; self.sizes = []

def partition3(a, p, st):
    lo, eq, hi = [], [], []
    for x in a:
        st.cmp += 1
        if x < p: lo.append(x)
        elif x == p: eq.append(x)
        else: hi.append(x)
    return lo, eq, hi

def select(a, k, pivot_fn, st, depth=1):
    """k is 0-based rank. pivot_fn(a, st) chooses the pivot value."""
    st.depth = max(st.depth, depth); st.sizes.append(len(a))
    if len(a) == 1: return a[0]
    p = pivot_fn(a, st)
    lo, eq, hi = partition3(a, p, st)
    if k < len(lo): return select(lo, k, pivot_fn, st, depth + 1)
    if k < len(lo) + len(eq): return p
    return select(hi, k - len(lo) - len(eq), pivot_fn, st, depth + 1)

def pivot_first(a, st): return a[0]
def pivot_last(a, st): return a[-1]
def pivot_random(a, st): return random.choice(a)

def small_median(g, st):
    # insertion sort on <=5 elements, counting comparisons
    g = list(g)
    for i in range(1, len(g)):
        j = i
        while j > 0:
            st.cmp += 1
            if g[j - 1] > g[j]: g[j - 1], g[j] = g[j], g[j - 1]; j -= 1
            else: break
    return g[(len(g) - 1) // 2]

def pivot_mom(a, st):
    if len(a) <= 5: return small_median(a, st)
    meds = [small_median(a[i:i + 5], st) for i in range(0, len(a), 5)]      # step 1-2: groups of 5, medians
    return select(meds, (len(meds) - 1) // 2, pivot_mom, st, 1)             # step 3: recursive median of medians

def mom_select(a, k, st): return select(a, k, pivot_mom, st)

def adversarial_for_last_pivot(n):
    """Input for which pivot=last element is always the current maximum => partitions of size m-1."""
    return list(range(n))                                  # sorted ascending: last = max

def main():
    random.seed(5)
    print("=== Correctness (k-th smallest vs sorted) ===")
    for _ in range(300):
        n = random.randint(1, 200); a = [random.randint(0, 60) for _ in range(n)]; k = random.randrange(n)
        assert mom_select(a, k, St()) == sorted(a)[k]
        assert select(a, k, pivot_random, St()) == sorted(a)[k]
        assert select(a, k, pivot_first, St()) == sorted(a)[k]
    print("MoM, QS-random, QS-first match sorted()[k] on 300 random cases (with duplicates)")

    print("\n=== Comparisons to find the median (k=n/2) ===")
    print(f"{'n':>7}{'input':>13}{'MoM cmp':>10}{'MoM cmp/n':>10}{'QS-rand':>9}{'QS-first':>10}{'QS-first depth':>15}")
    ns = [100, 500, 1000, 2000, 4000]; res = {"MoM random": [], "QS random pivot": [], "QS first pivot (sorted)": []}
    for n in ns:
        for label, a in (("random", random.sample(range(n * 3), n)), ("sorted", list(range(n)))):
            k = n // 2
            m, r = St(), St()
            mom_select(a, k, m); select(a, k, pivot_random, r)
            fk = St(); select(a, k, pivot_first, fk)
            print(f"{n:>7}{label:>13}{m.cmp:>10}{m.cmp/n:>10.2f}{r.cmp:>9}{fk.cmp:>10}{fk.depth:>15}")
            if label == "random": res["MoM random"].append(m.cmp); res["QS random pivot"].append(r.cmp)
            else: res["QS first pivot (sorted)"].append(fk.cmp)
    print("(QS-first = deterministic first-element pivot; on sorted input every pivot is the current minimum -> partitions 0 : n-1)")

    print("\n=== Effect of a deterministic poor-pivot strategy (n=2000, median, sorted input) ===")
    a = list(range(2000))
    for name, fn in (("pivot=first (deterministic)", pivot_first), ("pivot=random", pivot_random), ("median of medians", pivot_mom)):
        st = St(); select(a, 1000, fn, st)
        print(f"{name:<28} comparisons={st.cmp:>8}  max depth={st.depth:>5}  first subproblem sizes={st.sizes[:5]}")

    print("\n=== Randomised QuickSelect is not immune (n=2000, 300 runs, random input) ===")
    a = random.sample(range(6000), 2000); cs = []
    for _ in range(300):
        st = St(); select(a, 1000, pivot_random, st); cs.append(st.cmp)
    cs.sort(); mst = St(); mom_select(a, 1000, mst)
    print(f"QS-random comparisons: min={cs[0]} median={cs[150]} 95th pct={cs[285]} max={cs[-1]}  |  MoM (deterministic): {mst.cmp}")
    print("  => random pivots give expected O(n) but a bad run (max) can cost several times more; MoM has a hard bound.")

    print("\n=== MoM recurrence check: T(n) <= T(n/5) + T(7n/10 + 6) + c*n  =>  comparisons/n stays bounded ===")
    for n in (1000, 10_000, 100_000):
        a = random.sample(range(n * 3), n); st = St(); mom_select(a, n // 2, st)
        print(f"  n={n:>7}: cmp={st.cmp:>9}  cmp/n={st.cmp/n:.2f}  max depth={st.depth}")

    plt.figure(figsize=(6, 4))
    for k, v in res.items(): plt.plot(ns, v, "o-", label=k)
    plt.xlabel("n"); plt.ylabel("comparisons"); plt.title("Q6A: selection comparisons"); plt.legend(); plt.grid(True, alpha=.3)
    plt.tight_layout(); plt.savefig(OUT + "q6a_selection_comparisons.png", dpi=130); plt.close()

if __name__ == "__main__":
    main()
