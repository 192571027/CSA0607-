"""Q6 (Student B) - Subset Sum: brute force 2^n vs Meet-in-the-Middle (2 * 2^(n/2) enumeration + sort/two-pointer).
Counts: subset sums generated, search steps, and stored entries (memory)."""
import random, time, itertools, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
OUT = "../Output_Screenshots/"

def subset_sums(items):
    """All 2^m subset sums by iterative doubling."""
    sums = [0]
    for x in items: sums += [s + x for s in sums]
    return sums

def brute_force(a, T):
    """Enumerate all 2^n subsets (via doubling) and count how many hit T. Returns (found, #sums, #stored)."""
    sums = subset_sums(a)
    return T in set(sums), len(sums), len(sums)

def mitm(a, T, want_subset=False):
    n = len(a); h = n // 2
    L = subset_sums(a[:h]); R = subset_sums(a[h:])         # 2^(n/2) each
    R_sorted = sorted(R); L_sorted = sorted(L)
    steps = 0
    i, j = 0, len(R_sorted) - 1                            # two pointers: L ascending, R descending
    found = False
    while i < len(L_sorted) and j >= 0:
        steps += 1
        s = L_sorted[i] + R_sorted[j]
        if s == T: found = True; break
        elif s < T: i += 1
        else: j -= 1
    return found, len(L) + len(R), len(L) + len(R) + steps, steps

def reconstruct(a, T):
    """Return an actual subset using MITM with a dict (for correctness demo, small n)."""
    h = len(a) // 2
    def table(items):
        d = {}
        for mask in range(1 << len(items)):
            s = sum(items[i] for i in range(len(items)) if mask >> i & 1); d.setdefault(s, mask)
        return d
    L, R = table(a[:h]), table(a[h:])
    for s, m in L.items():
        if T - s in R:
            mr = R[T - s]
            return [a[i] for i in range(h) if m >> i & 1] + [a[h + i] for i in range(len(a) - h) if mr >> i & 1]
    return None

def timeit(fn):
    t = time.perf_counter(); r = fn(); return r, (time.perf_counter() - t) * 1000

def main():
    random.seed(21)
    print("=== Correctness: MITM vs brute force (random small instances) ===")
    for _ in range(400):
        n = random.randint(1, 14); a = [random.randint(1, 50) for _ in range(n)]; T = random.randint(0, 5 * n * 10)
        assert brute_force(a, T)[0] == mitm(a, T)[0]
        sub = reconstruct(a, T)
        assert (sub is not None) == brute_force(a, T)[0] and (sub is None or sum(sub) == T)
    print("400 instances agree; reconstructed subsets sum to the target")
    a = [3, 34, 4, 12, 5, 2]; print(f"example: a={a}, T=9 -> subset {reconstruct(a, 9)}; T=30 -> {reconstruct(a, 30)}")

    print("\n=== Work and memory (target is unreachable so both do their FULL work; all values random 1..10^9) ===")
    print(f"{'n':>4}{'2^n (brute sums)':>18}{'MITM sums 2*2^(n/2)':>21}{'MITM search steps':>19}{'MITM stored':>13}{'brute ms':>10}{'MITM ms':>9}")
    ns = [10, 14, 18, 20, 22, 24]; tb, tm, wb, wm = [], [], [], []
    for n in ns:
        a = [random.randint(1, 10**9) for _ in range(n)]; T = -1       # unreachable: forces full enumeration
        (fb, sb, stb), t1 = timeit(lambda: brute_force(a, T)); (fm, sm, stm, steps), t2 = timeit(lambda: mitm(a, T))
        assert not fb and not fm
        tb.append(t1); tm.append(t2); wb.append(sb); wm.append(sm)
        print(f"{n:>4}{sb:>18}{sm:>21}{steps:>19}{sm:>13}{t1:>10.1f}{t2:>9.1f}")
    print("\nMITM only (brute force infeasible):")
    for n in (30, 36, 40):
        a = [random.randint(1, 10**9) for _ in range(n)]
        (fm, sm, stm, steps), t2 = timeit(lambda: mitm(a, -1))
        print(f"  n={n}: brute would enumerate 2^{n} = {2**n:,} subsets; MITM generated {sm:,} sums, {steps:,} search steps, {t2/1000:.1f} s, "
              f"~{sm*8/1e6:.0f} MB of integers if stored as 8-byte values (Python lists use ~3x more)")

    print("\n=== Time-memory trade-off (theory) ===")
    print(f"{"n":>4}{"brute time 2^n":>26}{'MITM time 2^(n/2)*n/2':>24}{'MITM memory 2^(n/2)':>22}{'brute memory (streaming)':>26}")
    for n in (20, 30, 40, 50, 60):
        print(f"{n:>4}{2**n:>26,}{(2**(n//2))*(n//2):>24,}{2**(n//2):>22,}{'O(n) / O(1) extra':>26}")

    plt.figure(figsize=(6, 4))
    plt.semilogy(ns, wb, "o-", label="brute force: 2^n sums"); plt.semilogy(ns, wm, "s-", label="MITM: 2*2^(n/2) sums")
    plt.xlabel("n"); plt.ylabel("subset sums generated"); plt.title("Q6B: work, brute vs MITM"); plt.legend(); plt.grid(True, alpha=.3, which="both")
    plt.tight_layout(); plt.savefig(OUT + "q6b_mitm_work.png", dpi=130); plt.close()

if __name__ == "__main__":
    main()
