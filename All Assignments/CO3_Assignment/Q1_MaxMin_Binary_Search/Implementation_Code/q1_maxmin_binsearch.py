"""Q1 - Max/Min by Divide and Conquer + Binary Search (with comparison counting).
Student A: design/maths (see Pseudocode). Student B: experiments in part_a_experiments().
Binary Search: Student A experiments, Student B elimination logic (see Pseudocode)."""
import random, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
OUT = "../Output_Screenshots/"

# ---------------- Part A: Max / Min ----------------
class Counter:
    def __init__(self): self.c = 0

def max_min(a, lo, hi, cnt):
    """Returns (min, max) of a[lo..hi]; counts element comparisons in cnt.c"""
    if lo == hi:                       # base case: 1 element, 0 comparisons
        return a[lo], a[lo]
    if hi == lo + 1:                   # base case: 2 elements, 1 comparison
        cnt.c += 1
        return (a[lo], a[hi]) if a[lo] < a[hi] else (a[hi], a[lo])
    mid = (lo + hi) // 2
    mn1, mx1 = max_min(a, lo, mid, cnt)
    mn2, mx2 = max_min(a, mid + 1, hi, cnt)
    cnt.c += 2                         # combine: one compare for min, one for max
    return min_(mn1, mn2), max_(mx1, mx2)

def min_(x, y): return x if x < y else y
def max_(x, y): return x if x > y else y

def straightforward(a):
    """Independent scan for max and min: 2(n-1) comparisons."""
    c = 0
    mn = mx = a[0]
    for x in a[1:]:
        c += 1
        if x < mn: mn = x
        c += 1
        if x > mx: mx = x
    return mn, mx, c

def predicted(n):                      # ceil(3n/2) - 2 (exact for D&C splitting at mid)
    return math.ceil(3 * n / 2) - 2

def part_a_experiments():
    print("=== Q1 Part A: Max/Min ===")
    print(f"{'n':>8} {'D&C observed':>13} {'ceil(3n/2)-2':>13} {'2(n-1)':>9} {'saving %':>9}  datasets")
    ns = [2, 3, 4, 5, 7, 8, 16, 31, 64, 100, 128, 1000, 1024, 5000, 10000, 65536]
    xs, dc, st = [], [], []
    for n in ns:
        datasets = {
            "random": random.sample(range(10 * n), n),
            "sorted": list(range(n)),
            "reverse": list(range(n, 0, -1)),
            "all-equal": [7] * n,
        }
        counts = set()
        for name, d in datasets.items():
            cnt = Counter()
            mn, mx = max_min(d, 0, n - 1, cnt)
            assert (mn, mx) == (min(d), max(d)), "wrong result"
            counts.add(cnt.c)
        # comparison count of this algorithm is data independent
        obs = counts.pop(); assert not counts
        base = straightforward(datasets["random"])[2]
        pred = predicted(n)
        note = "match" if obs == pred else f"diff={obs-pred}"
        print(f"{n:>8} {obs:>13} {pred:>13} {base:>9} {100*(base-obs)/base:>8.1f}%  4 datasets, {note}")
        xs.append(n); dc.append(obs); st.append(base)
    plt.figure(figsize=(6, 4))
    plt.plot(xs, dc, "o-", label="D&C max/min")
    plt.plot(xs, st, "s--", label="Independent scans 2(n-1)")
    plt.xscale("log"); plt.yscale("log"); plt.xlabel("n"); plt.ylabel("comparisons")
    plt.title("Q1A: comparisons vs n"); plt.legend(); plt.grid(True, alpha=.3)
    plt.tight_layout(); plt.savefig(OUT + "q1a_maxmin_comparisons.png", dpi=130); plt.close()

# ---------------- Part B: Binary Search ----------------
def binary_search(a, target, cnt):
    lo, hi = 0, len(a) - 1
    while lo <= hi:                    # terminates when search space is empty
        mid = (lo + hi) // 2
        cnt.c += 1                     # count one 3-way comparison per probe
        if a[mid] == target: return mid
        elif a[mid] < target: lo = mid + 1   # eliminate left half incl. mid
        else: hi = mid - 1                   # eliminate right half incl. mid
    return -1

def part_b_experiments():
    print("\n=== Q1 Part B: Binary Search (probes = 3-way comparisons) ===")
    print(f"{'n':>9} {'floor(lg n)+1':>14} {'succ avg':>9} {'succ max':>9} {'first':>6} {'last':>6} {'unsucc avg':>11} {'unsucc max':>11}")
    xs, sa, ua, bound = [], [], [], []
    for n in [1, 2, 3, 7, 8, 100, 1000, 10**4, 10**5, 10**6]:
        a = [2 * i for i in range(n)]              # evens: odd numbers are guaranteed misses
        def run(t):
            c = Counter(); binary_search(a, t, c); return c.c
        succ = [run(x) for x in (a if n <= 10**5 else random.sample(a, 20000))]
        uns = [run(2 * i + 1) for i in (range(n) if n <= 10**5 else random.sample(range(n), 20000))]
        uns += [run(-5), run(2 * n + 3)]           # below min and above max
        lg = math.floor(math.log2(n)) + 1
        print(f"{n:>9} {lg:>14} {sum(succ)/len(succ):>9.2f} {max(succ):>9} {run(a[0]):>6} {run(a[-1]):>6} {sum(uns)/len(uns):>11.2f} {max(uns):>11}")
        assert max(succ) <= lg and max(uns) <= lg
        xs.append(n); sa.append(sum(succ)/len(succ)); ua.append(sum(uns)/len(uns)); bound.append(lg)
    plt.figure(figsize=(6, 4))
    plt.plot(xs, sa, "o-", label="successful (avg)")
    plt.plot(xs, ua, "s-", label="unsuccessful (avg)")
    plt.plot(xs, bound, "k--", label="floor(log2 n)+1")
    plt.xscale("log"); plt.xlabel("n"); plt.ylabel("probes"); plt.title("Q1B: Binary Search probes")
    plt.legend(); plt.grid(True, alpha=.3); plt.tight_layout()
    plt.savefig(OUT + "q1b_binary_search_probes.png", dpi=130); plt.close()
    # linear search comparison for 10^6
    print("\nLinear search worst case at n=1,000,000 = 1,000,000 comparisons vs binary search <= 20 probes")

if __name__ == "__main__":
    random.seed(42)
    part_a_experiments()
    part_b_experiments()
