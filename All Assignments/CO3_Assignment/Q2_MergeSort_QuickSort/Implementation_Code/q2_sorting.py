"""Q2 - Merge Sort vs Quick Sort: quality of decomposition.
Quick Sort pivot strategy (stated): LAST element is the pivot, out-of-place stable partition
  (L = elements < pivot, R = elements >= pivot, original order preserved).
Student A: inputs that give balanced / unbalanced partitions, partition sizes, max depth.
Student B: Merge Sort decomposition & comparison with Quick Sort recursion tree."""
import sys, math, random, time
sys.setrecursionlimit(20000)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
OUT = "../Output_Screenshots/"

class Stats:
    def __init__(self): self.cmp = 0; self.depth = 0; self.parts = []   # parts: (size, |L|, |R|)

def quick_sort(a, st, depth=1):
    st.depth = max(st.depth, depth)
    if len(a) <= 1: return a
    p = a[-1]                                   # pivot = last element
    L, R = [], []
    for x in a[:-1]:
        st.cmp += 1
        (L if x < p else R).append(x)
    st.parts.append((len(a), len(L), len(R)))
    return quick_sort(L, st, depth + 1) + [p] + quick_sort(R, st, depth + 1)

def merge_sort(a, st, depth=1):
    st.depth = max(st.depth, depth)
    n = len(a)
    if n <= 1: return a
    mid = n // 2
    l = merge_sort(a[:mid], st, depth + 1)
    r = merge_sort(a[mid:], st, depth + 1)
    out, i, j = [], 0, 0
    while i < len(l) and j < len(r):
        st.cmp += 1
        if l[i] <= r[j]: out.append(l[i]); i += 1
        else: out.append(r[j]); j += 1
    out.extend(l[i:]); out.extend(r[j:])
    return out

def balanced_input(values):
    """Permutation of sorted 'values' such that last-element-pivot Quick Sort splits perfectly in half
    at EVERY level (median placed last, then the two halves recursively arranged)."""
    n = len(values)
    if n <= 1: return list(values)
    m = (n - 1) // 2
    return balanced_input(values[:m]) + balanced_input(values[m + 1:]) + [values[m]]

def worst_input(n):  return list(range(n))              # sorted: pivot (last) is the maximum -> n-1 : 0
def ratio_input(n, r=0.9):                               # skewed ~90:10 at every level
    vals = list(range(n)); return skewed(vals, r)
def skewed(values, r):
    n = len(values)
    if n <= 1: return list(values)
    m = min(n - 1, int(r * (n - 1)))
    return skewed(values[:m], r) + skewed(values[m + 1:], r) + [values[m]]

def run(fn, data):
    st = Stats(); t = time.perf_counter(); out = fn(list(data), st); t = time.perf_counter() - t
    assert out == sorted(data); return st, t

def main():
    random.seed(1)
    print("=== Q2: Quick Sort partition investigation (pivot = last element) ===")
    n = 1023
    cases = {"balanced (constructed)": balanced_input(list(range(n))),
             "random": random.sample(range(n), n),
             "90:10 skew (constructed)": ratio_input(n, 0.9),
             "sorted (worst)": worst_input(n),
             "reverse sorted": list(range(n, 0, -1))}
    print(f"n={n}, ideal depth ~ log2(n+1)={math.log2(n+1):.0f}, worst depth = n")
    print(f"{'input':<26}{'comparisons':>12}{'max depth':>10}{'time ms':>9}  first partitions (size: L|R)")
    for name, d in cases.items():
        st, t = run(quick_sort, d)
        first = ", ".join(f"{s}:{l}|{r}" for s, l, r in st.parts[:4])
        print(f"{name:<26}{st.cmp:>12}{st.depth:>10}{t*1000:>9.2f}  {first}")
    ms, t = run(merge_sort, cases["sorted (worst)"])
    print(f"{'Merge Sort (any input)':<26}{ms.cmp:>12}{ms.depth:>10}{t*1000:>9.2f}  halves: 1023 -> 511|512 -> ...")
    for name in ("balanced (constructed)", "sorted (worst)"):
        parts = quick_sort(cases[name], Stats()) and None
    st_b, _ = run(quick_sort, cases["balanced (constructed)"])
    print("\nBalanced input - first 7 partitions (size, |L|, |R|):", st_b.parts[:7])
    st_w, _ = run(quick_sort, list(range(12)))
    print("Sorted input n=12 partitions (size, |L|, |R|):", st_w.parts)

    print("\n=== Scaling: comparisons / max depth ===")
    ns = [64, 128, 256, 512, 1000, 1500]
    series = {k: [] for k in ("QS balanced", "QS random", "QS sorted", "Merge sort")}
    depths = {k: [] for k in series}
    print(f"{'n':>6}{'QS bal cmp':>12}{'QS rnd cmp':>12}{'QS sorted cmp':>14}{'n(n-1)/2':>10}{'MS cmp':>9}{'QS bal d':>9}{'QS srt d':>9}{'MS d':>6}")
    for n in ns:
        b, _ = run(quick_sort, balanced_input(list(range(n))))
        r, _ = run(quick_sort, random.sample(range(n), n))
        s, _ = run(quick_sort, worst_input(n))
        m, _ = run(merge_sort, random.sample(range(n), n))
        print(f"{n:>6}{b.cmp:>12}{r.cmp:>12}{s.cmp:>14}{n*(n-1)//2:>10}{m.cmp:>9}{b.depth:>9}{s.depth:>9}{m.depth:>6}")
        for k, v in zip(series, (b, r, s, m)): series[k].append(v.cmp); depths[k].append(v.depth)
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    for k in series:
        ax[0].plot(ns, series[k], "o-", label=k); ax[1].plot(ns, depths[k], "o-", label=k)
    ax[0].set_title("Comparisons"); ax[1].set_title("Max recursion depth")
    for a in ax: a.set_xlabel("n"); a.legend(); a.grid(True, alpha=.3)
    ax[1].set_yscale("log")
    plt.tight_layout(); plt.savefig(OUT + "q2_sorting_comparisons_depth.png", dpi=130); plt.close()

    print("\n=== Effect of split ratio on depth/comparisons (n=1000) ===")
    for r in (0.5, 0.7, 0.9, 0.99):
        st, _ = run(quick_sort, skewed(list(range(1000)), r))
        print(f"split {int(r*100)}:{100-int(r*100)}  depth={st.depth:>4}  comparisons={st.cmp:>7}  "
              f"theory depth ~ log(n)/log(1/{r})={math.log(1000)/math.log(1/r):.1f}" if r < 1 else "")

if __name__ == "__main__":
    main()
