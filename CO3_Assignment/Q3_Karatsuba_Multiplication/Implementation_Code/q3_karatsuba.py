"""Q3 - Karatsuba vs standard (schoolbook) multiplication on decimal digit strings.
Student A: derivation (Pseudocode/). Student B: crossover experiment below.
Cost model: number of single-digit multiplications ("mults") + wall-clock time."""
import time, random, math, sys
sys.setrecursionlimit(10000)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
OUT = "../Output_Screenshots/"

def digits(x): return [int(c) for c in reversed(str(x))]          # little-endian digit list

def schoolbook(x, y):
    """Standard O(n^2) multiplication on digit lists; returns (product, digit mults)."""
    a, b = digits(x), digits(y)
    res = [0] * (len(a) + len(b)); mults = 0
    for i, da in enumerate(a):
        carry = 0
        for j, db in enumerate(b):
            cur = res[i + j] + da * db + carry; mults += 1
            carry, res[i + j] = divmod(cur, 10)
        res[i + len(b)] += carry
    return int("".join(map(str, reversed(res)))), mults

def karatsuba(x, y, cutoff=1, cnt=None):
    """Karatsuba. Below `cutoff` digits it switches to schoolbook (cutoff=1 -> pure Karatsuba).
    cnt is a one-element list accumulating digit multiplications."""
    if cnt is None: cnt = [0]
    n = max(len(str(x)), len(str(y)))
    if n <= cutoff:
        if n == 1: cnt[0] += 1; return x * y, cnt[0]
        p, m = schoolbook(x, y); cnt[0] += m; return p, cnt[0]
    m = n // 2; base = 10 ** m
    a, b = divmod(x, base); c, d = divmod(y, base)                 # x = a*B + b, y = c*B + d
    z2, _ = karatsuba(a, c, cutoff, cnt)                           # a*c
    z0, _ = karatsuba(b, d, cutoff, cnt)                           # b*d
    z1, _ = karatsuba(a + b, c + d, cutoff, cnt)                   # (a+b)(c+d)
    z1 -= z2 + z0                                                  # = ad + bc
    return z2 * base * base + z1 * base + z0, cnt[0]

def rand_n(n): return random.randint(10 ** (n - 1), 10 ** n - 1)

def timeit(fn, reps):
    best = 1e9
    for _ in range(reps):
        t = time.perf_counter(); fn(); best = min(best, time.perf_counter() - t)
    return best

def main():
    random.seed(7)
    print("=== Q3 correctness ===")
    for n in (1, 2, 3, 5, 8, 17, 64, 100, 257):
        for _ in range(20):
            x, y = rand_n(n), rand_n(n)
            assert schoolbook(x, y)[0] == x * y and karatsuba(x, y)[0] == x * y
    print("schoolbook & Karatsuba agree with Python's built-in * on 180 random pairs")

    print("\n=== Crossover experiment: digit multiplications and best-of-5 time ===")
    print(f"{'n digits':>9}{'school mults':>13}{'kara mults':>12}{'n^1.585':>11}{'mult ratio':>11}{'school ms':>11}{'kara ms':>10}{'faster':>9}")
    ns = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]
    S, K, tS, tK = [], [], [], []
    for n in ns:
        x, y = rand_n(n), rand_n(n)
        s_prod, sm = schoolbook(x, y); k_prod, km = karatsuba(x, y)
        assert s_prod == k_prod == x * y
        reps = 5 if n <= 512 else 3
        ts = timeit(lambda: schoolbook(x, y), reps) * 1000
        tk = timeit(lambda: karatsuba(x, y), reps) * 1000
        S.append(sm); K.append(km); tS.append(ts); tK.append(tk)
        print(f"{n:>9}{sm:>13}{km:>12}{n**math.log2(3):>11.0f}{sm/km:>11.2f}{ts:>11.3f}{tk:>10.3f}{'Karatsuba' if tk < ts else 'school':>9}")

    print("\n=== Hybrid: Karatsuba with schoolbook below a cutoff (n=1024, best of 3) ===")
    x, y = rand_n(1024), rand_n(1024)
    print(f"{'cutoff':>7}{'mults':>10}{'time ms':>10}")
    best = None
    for cutoff in (1, 2, 4, 8, 16, 32, 64, 128):
        t = timeit(lambda: karatsuba(x, y, cutoff), 3) * 1000
        _, m = karatsuba(x, y, cutoff)
        print(f"{cutoff:>7}{m:>10}{t:>10.3f}")
        if best is None or t < best[1]: best = (cutoff, t)
    print(f"best cutoff in this run: {best[0]} digits")

    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].loglog(ns, S, "o-", label="schoolbook n^2"); ax[0].loglog(ns, K, "s-", label="Karatsuba ~n^1.585")
    ax[0].set_title("Digit multiplications"); ax[1].loglog(ns, tS, "o-", label="schoolbook"); ax[1].loglog(ns, tK, "s-", label="Karatsuba")
    ax[1].set_title("Time (ms)")
    for a in ax: a.set_xlabel("digits"); a.legend(); a.grid(True, alpha=.3, which="both")
    plt.tight_layout(); plt.savefig(OUT + "q3_karatsuba_crossover.png", dpi=130); plt.close()

if __name__ == "__main__":
    main()
