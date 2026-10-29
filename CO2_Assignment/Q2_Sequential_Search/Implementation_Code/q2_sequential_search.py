"""
Q2 - When is Sequential Search an appropriate engineering choice?
(Aircraft maintenance tool tracking)

Record = (tool_id, technician_id, issue_time, work_bay)
Search key = tool_id.   Measure = number of key comparisons.

THEORETICAL PREDICTION (before running)
  successful search, key at position p (1-based) : p comparisons
  best case 1, worst case n, average over all keys (n+1)/2
  unsuccessful search                            : exactly n comparisons
"""
import csv
import os
import random
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "Output_Screenshots")
RAW = os.path.join(OUT, "raw_data")
os.makedirs(RAW, exist_ok=True)


def sequential_search(records, key):
    """Return (index or -1, number_of_comparisons)."""
    comps = 0
    for i in range(len(records)):
        comps += 1
        if records[i][0] == key:
            return i, comps
    return -1, comps


def make_records(n, rng):
    ids = list(range(1, n + 1))
    rng.shuffle(ids)                       # tool IDs are issued in arbitrary order
    return [("T-%d" % t, "TECH-%03d" % rng.randint(1, 120), "%02d:%02d" % (rng.randint(6, 21), rng.randint(0, 59)),
             "BAY-%d" % rng.randint(1, 12)) for t in ids]


def main():
    rng = random.Random(184)
    print("=" * 78)
    print("Q2  SEQUENTIAL SEARCH - AIRCRAFT MAINTENANCE TOOL TRACKING")
    print("=" * 78)

    # ---------------------------------------------------------- Experiment 1
    sizes = [100, 1000, 10000, 100000]
    print("\nEXPERIMENT 1: comparisons for successful searches at different positions")
    print("              and for an unsuccessful search (tool not currently issued)")
    print("%8s | %7s %7s %7s %7s %7s | %12s | %12s | %s" % (
        "n", "first", "25%", "middle", "75%", "last", "unsuccessful", "avg(all keys)", "(n+1)/2"))
    rows = []
    for n in sizes:
        recs = make_records(n, rng)
        pos = {"first": 0, "q1": n // 4, "mid": n // 2, "q3": (3 * n) // 4, "last": n - 1}
        c = {}
        for k, p in pos.items():
            idx, comps = sequential_search(recs, recs[p][0])
            assert idx == p
            c[k] = comps
        idx, cu = sequential_search(recs, "T-NOT-ISSUED")
        assert idx == -1
        # average over every key (exact for n<=10000, 2000 random keys for 100000)
        keys = [r[0] for r in recs] if n <= 10000 else rng.sample([r[0] for r in recs], 2000)
        avg = sum(sequential_search(recs, k)[1] for k in keys) / len(keys)
        print("%8d | %7d %7d %7d %7d %7d | %12d | %12.1f | %.1f" % (
            n, c["first"], c["q1"], c["mid"], c["q3"], c["last"], cu, avg, (n + 1) / 2))
        rows.append([n, c["first"], c["q1"], c["mid"], c["q3"], c["last"], cu, round(avg, 2), (n + 1) / 2])
    with open(os.path.join(RAW, "q2_comparisons_by_position.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n", "first", "pos_25pct", "middle", "pos_75pct", "last", "unsuccessful", "avg_all_keys_measured", "(n+1)/2"])
        w.writerows(rows)

    # ---------------------------------------------------------- Experiment 2
    print("\nEXPERIMENT 2: successful vs unsuccessful - expected comparisons")
    print("  (tool is currently issued with probability s; otherwise the search fails)")
    print("%8s | %10s %10s %10s %10s" % ("n", "s=100%", "s=90%", "s=50%", "s=10%"))
    for n in sizes:
        print("%8d | %10.1f %10.1f %10.1f %10.1f" % (
            n, *(s * (n + 1) / 2 + (1 - s) * n for s in (1.0, 0.9, 0.5, 0.1))))

    # ---------------------------------------------------------- Experiment 3
    print("\nEXPERIMENT 3: measured speed of this machine (worst case, full scan)")
    speeds = []
    for n in sizes:
        recs = make_records(n, rng)
        reps = max(3, 200000 // n)
        t = time.perf_counter()
        for _ in range(reps):
            sequential_search(recs, "T-NOT-ISSUED")
        dt = (time.perf_counter() - t) / reps
        speeds.append(n / dt)
        print("  n=%7d  one unsuccessful search = %9.4f ms  -> %.2f million comparisons/s" % (n, dt * 1000, n / dt / 1e6))
    rate = sum(speeds) / len(speeds)
    print("  Mean measured rate r = %.2f million comparisons / second (interpreted Python)" % (rate / 1e6))

    # ---------------------------------------------------------- Acceptability criteria
    LAT = 0.050   # 50 ms per query
    UTIL = 0.10   # lookup traffic may use at most 10% of one core
    print("\nACCEPTABILITY CRITERIA (defined by me)")
    print("  C1 latency    : one worst-case lookup <= 50 ms (feels instantaneous on a technician's screen)")
    print("  C2 utilisation: lookups (avg n/2 comparisons each) use <= 10% of one core, leaving headroom")
    print("  => C1 limit: n <= r*0.05 = %d records" % int(rate * LAT))
    print("  => C2 limit: q * n / 2 <= 0.10 * r  ->  q * n <= %.2e  (q = lookups per second)" % (0.2 * rate))

    print("\nOPERATING-BOUNDARY TABLE - core utilisation (%) caused by lookups")
    qs = [0.01, 0.1, 1, 10, 100, 1000]
    print("%10s | " % "n \\ q/s" + " ".join("%9s" % q for q in qs))
    btable = []
    for n in [100, 1000, 10000, 100000, 1000000]:
        line = []
        for q in qs:
            u = 100.0 * q * (n / 2) / rate
            line.append(u)
        btable.append([n] + [round(x, 4) for x in line])
        print("%10d | " % n + " ".join(("%8.3f%s" % (x, "*" if x > 100 * UTIL else " ")) for x in line))
    print("  ( * = exceeds the 10% budget -> stop recommending sequential search )")
    with open(os.path.join(RAW, "q2_boundary_table.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n"] + ["q=%s/s" % q for q in qs])
        w.writerows(btable)

    # ---------------------------------------------------------- Changed condition
    print("\n" + "=" * 78)
    print("CHANGED CONDITION: 1 hangar -> 20 facilities")
    print("=" * 78)
    print("""Assumptions (stated explicitly; adjust to real data):
  one hangar : ~500 tools issued at a time, ~5,000 operations/day
  20 sites   : ~10,000 tools issued, ~100,000 operations/day (20x records, 20x requests)
  operation mix: 40% lookup (who has T-x?), 30% issue (add), 30% return (find + remove)""")

    def simulate(n_steady, n_ops, seed):
        r = random.Random(seed)
        ids = list(range(1, n_steady + 1))
        r.shuffle(ids)
        lst = [("T-%d" % t,) for t in ids]        # sequential structure (1-field records)
        dct = {t[0]: True for t in lst}           # indexed structure (hash table on tool id)
        next_id = n_steady + 1
        seq_comps = hash_probes = 0
        check = 0
        for _ in range(n_ops):
            u = r.random()
            if u < 0.40:                                   # lookup of an issued tool
                key = lst[r.randrange(len(lst))][0]
                idx = lst.index((key,))                    # C-speed scan; scan stops at idx
                seq_comps += idx + 1                       # == comparisons of sequential_search
                hash_probes += 1
                if check < 300:                            # verify equivalence with explicit function
                    assert sequential_search(lst, key)[1] == idx + 1
                    check += 1
            elif u < 0.70:                                 # issue a new tool: append
                key = "T-%d" % next_id
                next_id += 1
                lst.append((key,))
                dct[key] = True
            else:                                          # return: must find the record first
                key = lst[r.randrange(len(lst))][0]
                idx = lst.index((key,))
                seq_comps += idx + 1
                lst.pop(idx)
                hash_probes += 1
                del dct[key]
        return seq_comps, hash_probes

    t0 = time.perf_counter()
    base_c, base_h = simulate(500, 5000, 1)
    t_base = time.perf_counter() - t0
    t0 = time.perf_counter()
    big_c, big_h = simulate(10000, 100000, 2)
    t_big = time.perf_counter() - t0
    print("\n%-34s %16s %16s" % ("", "Sequential list", "Hash index"))
    print("%-34s %16d %16d   (key comparisons / hash probes)" % ("Original hangar (n~500, 5k ops)", base_c, base_h))
    print("%-34s %16d %16d" % ("20 facilities (n~10k, 100k ops)", big_c, big_h))
    print("Growth factor of sequential cost : %.0fx   (records x20, requests x20 => ~400x)" % (big_c / base_c))
    print("Growth factor of hash-index cost : %.0fx   (only the number of requests: x20)" % (big_h / base_h))
    print("Sequential comparisons per day at 20 sites = %d ; at the measured rate that is %.1f s of CPU/day"
          % (big_c, big_c / rate))
    peak_q = 100000 / (10 * 3600) * 10        # operations over a 10-hour day, x10 peak factor
    print("Peak request rate (10x average over a 10 h shift) ~ %.1f operations/s" % peak_q)
    u = 100 * (peak_q * 0.7) * (10000 / 2) / rate
    print("Peak utilisation of one core by sequential searching (n=10,000): %.2f%%  (budget 10%%)" % u)
    print("(wall-clock of the two simulations, C-speed list.index: %.2fs and %.2fs - additional evidence only)" % (t_base, t_big))
    with open(os.path.join(RAW, "q2_changed_condition.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["scenario", "n_steady", "operations", "sequential_comparisons", "hash_probes"])
        w.writerow(["one hangar", 500, 5000, base_c, base_h])
        w.writerow(["20 facilities (centralised)", 10000, 100000, big_c, big_h])

    # ---------------------------------------------------------- Graphs
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
    for label, col in (("first", 1), ("middle", 3), ("last", 5), ("unsuccessful", 6)):
        ax[0].plot(sizes, [r[col] for r in rows], "o-", label=label)
    ax[0].plot(sizes, [(n + 1) / 2 for n in sizes], "k--", label="(n+1)/2 average")
    ax[0].set_xscale("log")
    ax[0].set_yscale("log")
    ax[0].set_xlabel("list size n")
    ax[0].set_ylabel("comparisons")
    ax[0].set_title("Q2: comparisons vs list size")
    ax[0].legend()
    ax[0].grid(alpha=.3, which="both")
    ax[1].bar(["Original\nhangar", "20 facilities"], [base_c, big_c], color=["#4c78a8", "#e45756"], label="Sequential")
    ax[1].bar(["Original\nhangar", "20 facilities"], [base_h, big_h], color=["#72b7b2", "#54a24b"], label="Hash index")
    ax[1].set_yscale("log")
    ax[1].set_ylabel("comparisons / probes (log)")
    ax[1].set_title("Total search work, same operation mix")
    ax[1].legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "q2_graph_comparisons.png"), dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    main()
