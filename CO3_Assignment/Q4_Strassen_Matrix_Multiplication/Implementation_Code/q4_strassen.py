"""Q4 - Conventional vs Strassen matrix multiplication.
Student B: algebraic design & correctness (Pseudocode/). Student A: experiments below.
Part 1 (pure Python lists): scalar mults/adds + time, padding to a power of two.
Part 2 (NumPy): Strassen with a cutoff vs BLAS matmul, to show real-world engineering reality."""
import time, random, math, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
OUT = "../Output_Screenshots/"

class Ops:
    def __init__(self): self.mul = 0; self.add = 0

# ---------- pure Python ----------
def conv(A, B, ops):
    n = len(A); C = [[0] * n for _ in range(n)]
    for i in range(n):
        Ai = A[i]; Ci = C[i]
        for k in range(n):
            a = Ai[k]; Bk = B[k]
            for j in range(n):
                Ci[j] += a * Bk[j]
    ops.mul += n ** 3; ops.add += n * n * (n - 1)
    return C

def madd(A, B, ops): ops.add += len(A) ** 2; return [[x + y for x, y in zip(r, s)] for r, s in zip(A, B)]
def msub(A, B, ops): ops.add += len(A) ** 2; return [[x - y for x, y in zip(r, s)] for r, s in zip(A, B)]

def split(M):
    h = len(M) // 2
    return ([r[:h] for r in M[:h]], [r[h:] for r in M[:h]], [r[:h] for r in M[h:]], [r[h:] for r in M[h:]])

def join(C11, C12, C21, C22):
    return [a + b for a, b in zip(C11, C12)] + [a + b for a, b in zip(C21, C22)]

def strassen(A, B, ops, cutoff=1):
    n = len(A)
    if n <= cutoff: return conv(A, B, ops)
    A11, A12, A21, A22 = split(A); B11, B12, B21, B22 = split(B)
    M1 = strassen(madd(A11, A22, ops), madd(B11, B22, ops), ops, cutoff)
    M2 = strassen(madd(A21, A22, ops), B11, ops, cutoff)
    M3 = strassen(A11, msub(B12, B22, ops), ops, cutoff)
    M4 = strassen(A22, msub(B21, B11, ops), ops, cutoff)
    M5 = strassen(madd(A11, A12, ops), B22, ops, cutoff)
    M6 = strassen(msub(A21, A11, ops), madd(B11, B12, ops), ops, cutoff)
    M7 = strassen(msub(A12, A22, ops), madd(B21, B22, ops), ops, cutoff)
    C11 = madd(msub(madd(M1, M4, ops), M5, ops), M7, ops)
    C12 = madd(M3, M5, ops)
    C21 = madd(M2, M4, ops)
    C22 = madd(msub(madd(M1, M3, ops), M2, ops), M6, ops)
    return join(C11, C12, C21, C22)

def pad(M, m):
    n = len(M); return [r + [0] * (m - n) for r in M] + [[0] * m for _ in range(m - n)]

def strassen_any(A, B, ops, cutoff=1):
    """Handles any n by zero-padding up to the next power of two, then cropping."""
    n = len(A); m = 1 << (n - 1).bit_length()
    C = strassen(pad(A, m) if m != n else A, pad(B, m) if m != n else B, ops, cutoff)
    return [r[:n] for r in C[:n]]

def rnd(n): return [[random.randint(-9, 9) for _ in range(n)] for _ in range(n)]

def timeit(fn, reps):
    best = 1e9
    for _ in range(reps):
        t = time.perf_counter(); fn(); best = min(best, time.perf_counter() - t)
    return best * 1000

# ---------- NumPy ----------
def strassen_np(A, B, cutoff=128):
    n = A.shape[0]
    if n <= cutoff: return A @ B
    h = n // 2
    A11, A12, A21, A22 = A[:h, :h], A[:h, h:], A[h:, :h], A[h:, h:]
    B11, B12, B21, B22 = B[:h, :h], B[:h, h:], B[h:, :h], B[h:, h:]
    M1 = strassen_np(A11 + A22, B11 + B22, cutoff); M2 = strassen_np(A21 + A22, B11, cutoff)
    M3 = strassen_np(A11, B12 - B22, cutoff);       M4 = strassen_np(A22, B21 - B11, cutoff)
    M5 = strassen_np(A11 + A12, B22, cutoff);       M6 = strassen_np(A21 - A11, B11 + B12, cutoff)
    M7 = strassen_np(A12 - A22, B21 + B22, cutoff)
    C = np.empty_like(A)
    C[:h, :h] = M1 + M4 - M5 + M7; C[:h, h:] = M3 + M5
    C[h:, :h] = M2 + M4;           C[h:, h:] = M1 - M2 + M3 + M6
    return C

def main():
    random.seed(3)
    print("=== Q4 correctness (integer matrices, exact) ===")
    for n in (1, 2, 3, 5, 8, 13, 16, 31):
        A, B = rnd(n), rnd(n)
        assert strassen_any(A, B, Ops()) == conv(A, B, Ops()), n
    print("Strassen == conventional for n in 1,2,3,5,8,13,16,31 (non powers of two use padding)")

    print("\n=== Part 1: pure Python, scalar operation counts and time (pure Strassen, cutoff=1) ===")
    print(f"{'n':>5}{'conv mul':>12}{'str mul':>12}{'mul ratio':>10}{'conv add':>11}{'str add':>12}{'conv ms':>10}{'str ms':>10}")
    ns = [2, 4, 8, 16, 32, 64, 128]; cm, sm, ct, st = [], [], [], []
    for n in ns:
        A, B = rnd(n), rnd(n)
        oc, os_ = Ops(), Ops(); conv(A, B, oc); strassen(A, B, os_)
        tc = timeit(lambda: conv(A, B, Ops()), 3 if n <= 64 else 2)
        ts = timeit(lambda: strassen(A, B, Ops()), 3 if n <= 64 else 2)
        cm.append(oc.mul); sm.append(os_.mul); ct.append(tc); st.append(ts)
        print(f"{n:>5}{oc.mul:>12}{os_.mul:>12}{oc.mul/os_.mul:>10.2f}{oc.add:>11}{os_.add:>12}{tc:>10.2f}{ts:>10.2f}")

    print("\n=== Part 1b: Strassen with cutoff (n=128, pure Python) ===")
    A, B = rnd(128), rnd(128)
    print(f"{'cutoff':>7}{'mul':>10}{'add':>10}{'time ms':>10}")
    print(f"{'conv':>7}{128**3:>10}{128*128*127:>10}{timeit(lambda: conv(A, B, Ops()), 2):>10.1f}")
    for cutoff in (1, 2, 4, 8, 16, 32, 64):
        o = Ops(); strassen(A, B, o, cutoff)
        print(f"{cutoff:>7}{o.mul:>10}{o.add:>10}{timeit(lambda: strassen(A, B, Ops(), cutoff), 2):>10.1f}")

    print("\n=== Part 1c: padding overhead for non powers of two ===")
    print(f"{'n':>5}{'padded m':>9}{'extra cells %':>14}{'conv mul n^3':>13}{'strassen mul (padded)':>22}")
    for n in (33, 65, 100, 129, 200):
        m = 1 << (n - 1).bit_length(); o = Ops()
        # count-only run: padded size m with cutoff=1 -> 7^log2(m) multiplications
        print(f"{n:>5}{m:>9}{100*(m*m-n*n)/(n*n):>13.1f}%{n**3:>13}{7**int(math.log2(m)):>22}")

    print("\n=== Part 2: NumPy float64, Strassen(cutoff=128, recursion in Python) vs np.matmul (BLAS) ===")
    print(f"{'n':>6}{'BLAS ms':>10}{'Strassen ms':>13}{'ratio S/B':>10}{'max abs err':>13}")
    nn, tb, ts_ = [], [], []
    rng = np.random.default_rng(0)
    for n in (128, 256, 512, 1024, 2048):
        A = rng.standard_normal((n, n)); B = rng.standard_normal((n, n))
        t1 = timeit(lambda: A @ B, 3); t2 = timeit(lambda: strassen_np(A, B, 128), 3)
        err = np.abs(strassen_np(A, B, 128) - A @ B).max()
        nn.append(n); tb.append(t1); ts_.append(t2)
        print(f"{n:>6}{t1:>10.2f}{t2:>13.2f}{t2/t1:>10.2f}{err:>13.2e}")

    fig, ax = plt.subplots(1, 3, figsize=(15, 4))
    ax[0].loglog(ns, cm, "o-", label="conventional n^3"); ax[0].loglog(ns, sm, "s-", label="Strassen 7^k")
    ax[0].set_title("Scalar multiplications")
    ax[1].loglog(ns, ct, "o-", label="conventional"); ax[1].loglog(ns, st, "s-", label="Strassen (cutoff 1)")
    ax[1].set_title("Pure Python time (ms)")
    ax[2].loglog(nn, tb, "o-", label="BLAS matmul"); ax[2].loglog(nn, ts_, "s-", label="Strassen (cutoff 128)")
    ax[2].set_title("NumPy time (ms)")
    for a in ax: a.set_xlabel("n"); a.legend(); a.grid(True, alpha=.3, which="both")
    plt.tight_layout(); plt.savefig(OUT + "q4_strassen_experiments.png", dpi=130); plt.close()

if __name__ == "__main__":
    main()
