"""
Q3 - Engineering the behaviour of Brute-Force String Matching
(Cybersecurity log screening)

Counted measure: character comparisons  text[i+j] == pattern[j]

PREDICTIONS (made before running, from the algorithm's structure)
  There are n-m+1 alignments.  At each alignment the inner loop stops at the
  first mismatch, so work per alignment = (length of the matching prefix)+1.

  T1 "little work"  : pattern's first character never occurs in the text ->
                      every alignment costs exactly 1  => n-m+1 comparisons.
  T2 "engineered"   : text = A^n, pattern = A^(m-1)B -> every alignment matches
                      m-1 characters before the final mismatch => m per alignment
                      => (n-m+1)*m comparisons (no match found).
  T3 "realistic log": random-looking English-like log text.  If f(c) is the
                      relative frequency of character c in the text, then the
                      expected cost per alignment is
                          E = 1 + f(p0) + f(p0)f(p1) + ... (m-1 product terms)
                      => predicted comparisons ~ (n-m+1) * E.
  T4 "match at start": pattern = text[:m] -> exactly m comparisons, stops.
  Scaling prediction: worst case grows like n*m, best case like n.
"""
import csv
import os
import random
import string
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "Output_Screenshots")
RAW = os.path.join(OUT, "raw_data")
os.makedirs(RAW, exist_ok=True)


def brute_force_match(text, pattern):
    """Return (list of match positions, character_comparisons). Finds ALL matches."""
    n, m = len(text), len(pattern)
    comps = 0
    hits = []
    for i in range(n - m + 1):
        j = 0
        while j < m:
            comps += 1
            if text[i + j] != pattern[j]:
                break
            j += 1
        if j == m:
            hits.append(i)
    return hits, comps


def first_match(text, pattern):
    """Stops at the first match (used for the 'match at start' test)."""
    n, m = len(text), len(pattern)
    comps = 0
    for i in range(n - m + 1):
        j = 0
        while j < m:
            comps += 1
            if text[i + j] != pattern[j]:
                break
            j += 1
        if j == m:
            return i, comps
    return -1, comps


def expected_cost(text, pattern):
    freq = Counter(text)
    N = len(text)
    e, prod = 0.0, 1.0
    for ch in pattern:
        e += prod            # this comparison is executed with prob. prod
        prod *= freq[ch] / N
    return e


def realistic_log(n_target, rng):
    words = ["user", "login", "session", "opened", "closed", "for", "from", "port", "accepted", "connection", "kernel",
             "service", "started", "stopped", "request", "GET", "POST", "status", "error", "warning", "info", "root",
             "admin", "ssh", "password", "failed", "invalid", "timeout", "retry", "disk", "memory", "cpu"]
    out = []
    size = 0
    while size < n_target:
        line = "2026-10-%02d %02d:%02d:%02d host%d %s %s %s %s\n" % (
            rng.randint(1, 26), rng.randint(0, 23), rng.randint(0, 59), rng.randint(0, 59), rng.randint(1, 9),
            rng.choice(words), rng.choice(words), rng.choice(words), rng.choice(words))
        out.append(line)
        size += len(line)
    return "".join(out)[:n_target]


def main():
    rng = random.Random(33)
    n, m = 10000, 8
    print("=" * 78)
    print("Q3  BRUTE-FORCE STRING MATCHING - CYBERSECURITY LOG SCREENING")
    print("=" * 78)

    t1_text = "a" * n
    t1_pat = "Xerror!!"[:m]
    t2_text = "A" * n
    t2_pat = "A" * (m - 1) + "B"
    t3_text = realistic_log(n, rng)
    t3_pat = "password"
    t4_text = t3_text
    t4_pat = t3_text[:m]

    tests = [
        ("T1 BEST-LIKE  : text a^n, pattern 'Xerror!!' (first char never in text)", t1_text, t1_pat, "all"),
        ("T2 ENGINEERED : text A^n, pattern A^(m-1)B  (repeated partial matches)", t2_text, t2_pat, "all"),
        ("T3 OWN CHOICE : realistic synthetic log, signature 'password'", t3_text, t3_pat, "all"),
        ("T4 EXTRA      : pattern equals first m chars of the text (match at start)", t4_text, t4_pat, "first"),
    ]

    # ------------------------------------------------- predictions first
    pred = {}
    pred[0] = n - m + 1
    pred[1] = (n - m + 1) * m
    e3 = expected_cost(t3_text, t3_pat)
    pred[2] = (n - m + 1) * e3
    pred[3] = m

    print("\nPREDICTIONS (computed from theory before executing any test), n=%d, m=%d" % (n, m))
    print("  T1: n-m+1                 = %d" % pred[0])
    print("  T2: (n-m+1)*m             = %d" % pred[1])
    print("  T3: (n-m+1)*E, E=%.4f     = %.0f   (E from character frequencies of the log text)" % (e3, pred[2]))
    print("  T4: m                     = %d" % pred[3])

    print("\nRESULTS")
    print("%-72s %10s %10s %7s %7s" % ("test", "predicted", "observed", "ratio", "matches"))
    rows = []
    for idx, (name, text, pat, mode) in enumerate(tests):
        if mode == "all":
            hits, comps = brute_force_match(text, pat)
            assert hits == [i for i in range(len(text) - len(pat) + 1) if text.startswith(pat, i)]
            nm = len(hits)
        else:
            h, comps = first_match(text, pat)
            nm = 1 if h >= 0 else 0
        print("%-72s %10.0f %10d %7.3f %7d" % (name[:72], pred[idx], comps, comps / pred[idx], nm))
        rows.append([name, n, len(pat), round(pred[idx], 1), comps, nm])
    print("  (comparisons per alignment: T1 %.2f   T2 %.2f   T3 %.2f)" % tuple(r[4] / (n - m + 1) for r in rows[:3]))

    with open(os.path.join(RAW, "q3_tests.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["test", "n", "m", "predicted_comparisons", "observed_comparisons", "matches_found"])
        w.writerows(rows)

    # ------------------------------------------------- effect of alphabet size
    print("\nEXTRA EXPERIMENT A: effect of alphabet size (random text, n=10000, pattern length 8, mean of 5 texts)")
    print("%10s %14s %14s %12s" % ("alphabet", "observed", "predicted", "per align."))
    arows = []
    for k in (2, 4, 8, 26, 62):
        alpha = (string.ascii_letters + string.digits)[:k]
        tot = ptot = 0
        for _ in range(5):
            text = "".join(rng.choice(alpha) for _ in range(n))
            pat = "".join(rng.choice(alpha) for _ in range(m))
            tot += brute_force_match(text, pat)[1]
            ptot += (n - m + 1) * expected_cost(text, pat)
        print("%10d %14.0f %14.0f %12.3f" % (k, tot / 5, ptot / 5, tot / 5 / (n - m + 1)))
        arows.append([k, tot / 5, ptot / 5])

    # ------------------------------------------------- scaling in n and m
    print("\nEXTRA EXPERIMENT B: growth of the ENGINEERED case with n and m  (comparisons = (n-m+1)*m)")
    print("%8s %6s %14s %14s %s" % ("n", "m", "observed", "(n-m+1)*m", "random-text (26 letters) comparisons"))
    srows = []
    for nn in (1000, 2000, 4000, 8000, 16000):
        for mm in (4, 8, 16):
            comps = brute_force_match("A" * nn, "A" * (mm - 1) + "B")[1]
            rt = "".join(rng.choice(string.ascii_lowercase) for _ in range(nn))
            rp = "".join(rng.choice(string.ascii_lowercase) for _ in range(mm))
            rc = brute_force_match(rt, rp)[1]
            assert comps == (nn - mm + 1) * mm
            print("%8d %6d %14d %14d %14d" % (nn, mm, comps, (nn - mm + 1) * mm, rc))
            srows.append([nn, mm, comps, rc])
    with open(os.path.join(RAW, "q3_scaling.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n", "m", "engineered_comparisons", "random_text_comparisons"])
        w.writerows(srows)

    print("\nSAME INPUT SIZE, VERY DIFFERENT WORK:")
    print("  T1 and T2 both have n=%d, m=%d: observed %d vs %d comparisons -> %.1fx difference" % (
        n, m, rows[0][4], rows[1][4], rows[1][4] / rows[0][4]))

    # ------------------------------------------------- graphs
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
    labels = ["T1\nfirst char\nabsent", "T2\nengineered", "T3\nrealistic log", "T4\nmatch at start"]
    ax[0].bar(labels, [r[4] for r in rows], color=["#54a24b", "#e45756", "#4c78a8", "#b279a2"])
    ax[0].set_yscale("log")
    ax[0].set_ylabel("character comparisons (log)")
    ax[0].set_title("Q3: same n=%d, m=%d, different work" % (n, m))
    for mm in (4, 8, 16):
        ax[1].plot([r[0] for r in srows if r[1] == mm], [r[2] for r in srows if r[1] == mm], "o-", label="engineered m=%d" % mm)
    ax[1].plot([r[0] for r in srows if r[1] == 8], [r[3] for r in srows if r[1] == 8], "k--", label="random text m=8")
    ax[1].set_xlabel("text length n")
    ax[1].set_ylabel("comparisons")
    ax[1].set_title("Growth with n and m")
    ax[1].legend()
    ax[1].grid(alpha=.3)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "q3_graph_comparisons.png"), dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    main()
