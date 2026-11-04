"""
KartIQ - Module 4: Recommendation scores C = A x B using Strassen's method.

  * strassen_2x2_trace  - the seven products on the sample matrices
  * conventional / strassen (recursive, with a cut-off -> hybrid)
  * exact operation counts for n = 1024 and for different cut-offs
  * wall-clock timing (pure-Python leaves, and numpy/BLAS leaves)

Run:  python3 strassen.py
"""
import os
import random
import time

import numpy as np

A_SAMPLE = [[1, 7], [3, 5]]
B_SAMPLE = [[1, 3], [7, 5]]


# --------------------------------------------------------------------------
# 1. 2 x 2 Strassen with full trace
# --------------------------------------------------------------------------
def strassen_2x2_trace(A, B):
    a11, a12, a21, a22 = A[0][0], A[0][1], A[1][0], A[1][1]
    b11, b12, b21, b22 = B[0][0], B[0][1], B[1][0], B[1][1]
    print(f"A11={a11} A12={a12} A21={a21} A22={a22}")
    print(f"B11={b11} B12={b12} B21={b21} B22={b22}\n")

    M1 = (a11 + a22) * (b11 + b22)
    print(f"M1 = (A11 + A22)(B11 + B22) = ({a11}+{a22})({b11}+{b22}) = {a11+a22} x {b11+b22} = {M1}")
    M2 = (a21 + a22) * b11
    print(f"M2 = (A21 + A22) B11        = ({a21}+{a22}) x {b11} = {a21+a22} x {b11} = {M2}")
    M3 = a11 * (b12 - b22)
    print(f"M3 = A11 (B12 - B22)        = {a11} x ({b12}-{b22}) = {a11} x {b12-b22} = {M3}")
    M4 = a22 * (b21 - b11)
    print(f"M4 = A22 (B21 - B11)        = {a22} x ({b21}-{b11}) = {a22} x {b21-b11} = {M4}")
    M5 = (a11 + a12) * b22
    print(f"M5 = (A11 + A12) B22        = ({a11}+{a12}) x {b22} = {a11+a12} x {b22} = {M5}")
    M6 = (a21 - a11) * (b11 + b12)
    print(f"M6 = (A21 - A11)(B11 + B12) = ({a21}-{a11})({b11}+{b12}) = {a21-a11} x {b11+b12} = {M6}")
    M7 = (a12 - a22) * (b21 + b22)
    print(f"M7 = (A12 - A22)(B21 + B22) = ({a12}-{a22})({b21}+{b22}) = {a12-a22} x {b21+b22} = {M7}")

    C11 = M1 + M4 - M5 + M7
    C12 = M3 + M5
    C21 = M2 + M4
    C22 = M1 - M2 + M3 + M6
    print(f"\nC11 = M1 + M4 - M5 + M7 = {M1}+{M4}-{M5}+{M7} = {C11}")
    print(f"C12 = M3 + M5           = {M3}+{M5} = {C12}")
    print(f"C21 = M2 + M4           = {M2}+{M4} = {C21}")
    print(f"C22 = M1 - M2 + M3 + M6 = {M1}-{M2}+({M3})+{M6} = {C22}")
    return [[C11, C12], [C21, C22]]


def conventional_2x2(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(2)) for j in range(2)] for i in range(2)]


# --------------------------------------------------------------------------
# 2. Recursive Strassen with cut-off (hybrid) - numpy arrays
# --------------------------------------------------------------------------
class Ops:
    def __init__(self):
        self.mults = 0
        self.adds = 0


def next_pow2(n):
    p = 1
    while p < n:
        p *= 2
    return p


def strassen(A, B, cutoff, ops, leaf=None):
    """A, B are n x n numpy arrays, n a power of two."""
    n = A.shape[0]
    if n <= cutoff:
        ops.mults += n ** 3
        ops.adds += n * n * (n - 1)
        return leaf(A, B) if leaf else A @ B
    h = n // 2
    A11, A12, A21, A22 = A[:h, :h], A[:h, h:], A[h:, :h], A[h:, h:]
    B11, B12, B21, B22 = B[:h, :h], B[:h, h:], B[h:, :h], B[h:, h:]
    ops.adds += 18 * h * h                       # 10 operand + 8 combine additions
    M1 = strassen(A11 + A22, B11 + B22, cutoff, ops, leaf)
    M2 = strassen(A21 + A22, B11, cutoff, ops, leaf)
    M3 = strassen(A11, B12 - B22, cutoff, ops, leaf)
    M4 = strassen(A22, B21 - B11, cutoff, ops, leaf)
    M5 = strassen(A11 + A12, B22, cutoff, ops, leaf)
    M6 = strassen(A21 - A11, B11 + B12, cutoff, ops, leaf)
    M7 = strassen(A12 - A22, B21 + B22, cutoff, ops, leaf)
    C = np.empty_like(M1, shape=(n, n))
    C[:h, :h] = M1 + M4 - M5 + M7
    C[:h, h:] = M3 + M5
    C[h:, :h] = M2 + M4
    C[h:, h:] = M1 - M2 + M3 + M6
    return C


def strassen_any(A, B, cutoff, ops):
    """Pad to the next power of two, multiply, crop."""
    n = A.shape[0]
    m = next_pow2(n)
    if m == n:
        return strassen(A, B, cutoff, ops)
    Ap = np.zeros((m, m), dtype=A.dtype); Bp = np.zeros((m, m), dtype=B.dtype)
    Ap[:n, :n] = A; Bp[:n, :n] = B
    return strassen(Ap, Bp, cutoff, ops)[:n, :n]


# --------------------------------------------------------------------------
# 3. Exact operation counts from the recurrences
# --------------------------------------------------------------------------
def conv_mults(n):  return n ** 3
def conv_adds(n):   return n * n * (n - 1)
def conv_total(n):  return conv_mults(n) + conv_adds(n)


def strassen_counts(n, cutoff):
    """(mults, adds) of hybrid Strassen: recurse until size <= cutoff."""
    if n <= cutoff:
        return conv_mults(n), conv_adds(n)
    m, a = strassen_counts(n // 2, cutoff)
    return 7 * m, 7 * a + 18 * (n // 2) ** 2


def pure_python_strassen_vs_conv(n, cutoff, seed):
    """Timing with PURE PYTHON leaves (no BLAS) to show the arithmetic effect."""
    rnd = np.random.default_rng(seed)
    A = rnd.integers(0, 10, (n, n)); B = rnd.integers(0, 10, (n, n))

    def py_leaf(X, Y):
        xl, yl = X.tolist(), Y.tolist()
        yt = list(zip(*yl))
        return np.array([[sum(a * b for a, b in zip(row, col)) for col in yt] for row in xl])

    t = time.perf_counter(); C0 = py_leaf(A, B); t_conv = time.perf_counter() - t
    t = time.perf_counter(); C1 = strassen(A, B, cutoff, Ops(), leaf=py_leaf); t_str = time.perf_counter() - t
    assert (C0 == C1).all()
    return t_conv, t_str


def main():
    print("=" * 72)
    print("MODULE 4 - STRASSEN ON THE 2 x 2 SAMPLE MATRICES")
    print("=" * 72)
    print("A =", A_SAMPLE, " B =", B_SAMPLE, "\n")
    Cs = strassen_2x2_trace(A_SAMPLE, B_SAMPLE)
    Cc = conventional_2x2(A_SAMPLE, B_SAMPLE)
    print("\nStrassen     C =", Cs)
    print("Conventional C =", Cc)
    print("Results identical:", Cs == Cc)
    print("Scalar multiplications: Strassen 7, conventional 8")

    # ---------------- correctness for larger sizes -----------------------
    print("\n" + "=" * 72)
    print("CORRECTNESS: recursive Strassen (cut-off 1) vs numpy on random integer matrices")
    print("=" * 72)
    rng = np.random.default_rng(1)
    for n in (2, 4, 8, 16, 32, 64, 100):       # 100 is padded to 128
        A = rng.integers(-9, 10, (n, n)); B = rng.integers(-9, 10, (n, n))
        ops = Ops()
        C = strassen_any(A, B, 1, ops)
        print(f"n={n:>3}  equal to A@B: {np.array_equal(C, A @ B)}   "
              f"scalar mults used = {ops.mults:,}   (7^k = {7 ** int(np.ceil(np.log2(n))):,})")

    # ---------------- counts for n = 1024 ---------------------------------
    n = 1024
    print("\n" + "=" * 72)
    print("PRODUCTION COUNTS FOR n = 1,024 (exact, from the recurrences)")
    print("=" * 72)
    cm, ca = conv_mults(n), conv_adds(n)
    sm, sa = strassen_counts(n, 1)
    print(f"Conventional : multiplications = n^3          = {cm:,}")
    print(f"               additions       = n^2 (n-1)    = {ca:,}")
    print(f"               total arithmetic               = {cm + ca:,}")
    print(f"Strassen (full recursion, cut-off 1):")
    print(f"               multiplications = 7^10         = {sm:,}")
    print(f"               additions       = 6(7^10-4^10) = {sa:,}")
    print(f"               total arithmetic               = {sm + sa:,}")
    print(f"Multiplication ratio  Strassen / conventional = {sm / cm:.4f}  "
          f"({cm / sm:.2f}x fewer, saving {100 * (1 - sm / cm):.1f}%)")
    print(f"Total-arithmetic ratio                        = {(sm + sa) / (cm + ca):.4f}  "
          f"(saving only {100 * (1 - (sm + sa) / (cm + ca)):.1f}%)")

    print("\nEffect of the cut-off (hybrid) on arithmetic operations, n = 1,024:")
    print(f"{'cut-off':>8} {'levels':>7} {'multiplications':>17} {'additions':>17} "
          f"{'total':>17} {'vs conventional':>16}")
    best = None
    rows = []
    for k in range(0, 11):
        cut = 2 ** k
        m, a = strassen_counts(n, cut)
        levels = 10 - k
        tot = m + a
        rows.append((cut, levels, m, a, tot))
        if best is None or tot < best[1]:
            best = (cut, tot)
        print(f"{cut:>8} {levels:>7} {m:>17,} {a:>17,} {tot:>17,} {tot / (cm + ca):>15.4f}x")
    print(f"Minimum total arithmetic at cut-off {best[0]}: {best[1]:,} "
          f"({100 * (1 - best[1] / (cm + ca)):.1f}% fewer than conventional)")

    print("\nCross-over where one Strassen level starts to pay off (total arithmetic):")
    for sz in (2, 4, 8, 16, 32, 64):
        conv = conv_total(sz)
        one = 7 * conv_mults(sz // 2) + 7 * conv_adds(sz // 2) + 18 * (sz // 2) ** 2
        print(f"  n={sz:>3}: conventional {conv:>9,}   one-level Strassen {one:>9,}   "
              f"{'Strassen cheaper' if one < conv else 'conventional cheaper'}")

    print("\nMemory for n = 1,024 (8-byte doubles):")
    mat = n * n * 8
    print(f"  A, B, C                         = 3 x {mat / 2**20:.0f} MiB = {3 * mat / 2**20:.0f} MiB")
    # naive implementation: 10 operand sums + 7 products = 17 half-size temporaries per level
    tmp = sum(17 * (n // 2 ** k) ** 2 * 8 for k in range(1, 11))
    print(f"  Strassen temporaries, naive (17 half-size matrices per level, summed over levels) ~ {tmp / 2**20:.0f} MiB")

    # ---------------- timing ---------------------------------------------
    print("\n" + "=" * 72)
    print("TIMING 1: pure-Python leaves (arithmetic-dominated), n = 128, best of 3")
    print("=" * 72)
    for cut in (64, 32, 16, 8):
        tc, ts = min((pure_python_strassen_vs_conv(128, cut, s) for s in range(3)), key=lambda x: x[1])
        print(f"  cut-off {cut:>3}: conventional {tc:7.3f}s   hybrid Strassen {ts:7.3f}s   "
              f"ratio {ts / tc:5.2f}")

    print("\n" + "=" * 72)
    print("TIMING 2: numpy/BLAS leaves, float64, n = 1,024")
    print("=" * 72)
    rng = np.random.default_rng(2)
    A = rng.random((n, n)); B = rng.random((n, n))
    def best_of(f, reps=5):
        best = float("inf")
        for _ in range(reps):
            t = time.perf_counter(); out = f(); best = min(best, time.perf_counter() - t)
        return best, out
    t_blas, Cref = best_of(lambda: A @ B)
    print(f"  conventional (BLAS), best of 5 : {t_blas:7.3f} s")
    timing_rows = [("BLAS", t_blas, 0.0)]
    for cut in (512, 256, 128, 64):
        dt, C = best_of(lambda: strassen(A, B, cut, Ops()))
        err = np.max(np.abs(C - Cref))
        timing_rows.append((f"Strassen cut-off {cut}", dt, err))
        print(f"  Strassen hybrid, cut-off {cut:>3}, best of 5: {dt:7.3f} s   max |error| vs BLAS = {err:.2e}")

    # ---------------- graphs ---------------------------------------------
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        ns = [2 ** k for k in range(1, 12)]
        fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
        ax[0].plot(ns, [conv_mults(x) for x in ns], "o-", label="conventional n^3")
        ax[0].plot(ns, [strassen_counts(x, 1)[0] for x in ns], "s-", label="Strassen n^2.807")
        ax[0].set_xscale("log", base=2); ax[0].set_yscale("log")
        ax[0].set_xlabel("matrix size n"); ax[0].set_ylabel("scalar multiplications")
        ax[0].set_title("Multiplications"); ax[0].legend(); ax[0].grid(True, which="both", alpha=0.3)
        ax[1].plot([r[0] for r in rows], [r[4] / (cm + ca) for r in rows], "o-")
        ax[1].set_xscale("log", base=2)
        ax[1].axhline(1.0, color="gray", ls=":")
        ax[1].set_xlabel("cut-off size (below it: conventional)")
        ax[1].set_ylabel("total arithmetic / conventional total")
        ax[1].set_title("n = 1024: total arithmetic vs cut-off")
        ax[1].grid(True, which="both", alpha=0.3)
        plt.tight_layout()
        out = os.path.join(os.path.dirname(__file__), "..", "Report", "strassen_comparison.png")
        plt.savefig(out, dpi=150)
        print("\nGraph saved to Report/strassen_comparison.png")
    except ImportError:
        print("matplotlib not installed - graph skipped")


if __name__ == "__main__":
    main()
