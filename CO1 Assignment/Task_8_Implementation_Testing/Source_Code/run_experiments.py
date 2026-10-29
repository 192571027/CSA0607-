"""
run_experiments.py - Tasks 8 & 9: benchmark the three strategies on 1K / 10K / 100K / 1M records.
Writes results to ../../Task_9_Experimental_Performance/results.json and results.csv.
Usage:  python run_experiments.py            (full run, ~2-3 minutes)
        python run_experiments.py --quick    (sizes up to 100,000 only)
"""
import csv, json, math, os, statistics, sys, time, tracemalloc, platform
from algorithms import (linear_search, linear_search_counted, binary_search_recursive,
                        binary_search_counted, merge_sort, HashIndex)
from data_gen import SIZES, make_dataset, make_queries

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "Task_9_Experimental_Performance")
os.makedirs(OUT, exist_ok=True)


def time_per_search(fn, keys, repeats):
    """Median over `repeats` of (total time / number of keys), in microseconds."""
    runs = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        for k in keys:
            fn(k)
        runs.append((time.perf_counter() - t0) / len(keys) * 1e6)
    return statistics.median(runs)


def print_summary(results):
    line = "-" * 96
    print("\n" + line)
    print("MEAN TIME PER SUCCESSFUL SEARCH (microseconds)  /  MEAN COMPARISONS (successful)")
    print(line)
    print(f"{'n':>10} | {'Linear us':>12} {'Binary us':>10} {'Hash us':>9} | {'Linear cmp':>11} {'Binary cmp':>11} {'Hash cmp':>9}")
    for r in results:
        print(f"{r['n']:>10,} | {r['linear_us_hit']:>12.2f} {r['binary_us_hit']:>10.3f} {r['hash_us_hit']:>9.3f} | "
              f"{r['linear_cmp_avg_hit']:>11.1f} {r['binary_cmp_avg_hit']:>11.2f} {r['hash_cmp_avg_hit']:>9.3f}")
    print(line)
    print("PREPROCESSING (seconds)  /  WORST-CASE COMPARISONS OBSERVED")
    print(line)
    print(f"{'n':>10} | {'MergeSort s':>12} {'HashBuild s':>12} | {'Linear worst':>12} {'Binary worst':>12} {'Hash worst':>10}")
    for r in results:
        print(f"{r['n']:>10,} | {r['sort_time_s']:>12.4f} {r['hash_build_s']:>12.4f} | "
              f"{r['linear_cmp_worst']:>12,} {r['binary_cmp_worst']:>12} {r['hash_cmp_worst']:>10}")
    print(line)


def main(sizes):
    results = []
    for n in sizes:
        print(f"\n=== n = {n:,} ===", flush=True)
        data = make_dataset(n)
        q_fast = 2000                       # queries for binary / hash
        q_slow = 100 if n >= 100_000 else 300   # queries for linear
        hits_f, miss_f = make_queries(data, q_fast)
        hits_s, miss_s = hits_f[:q_slow], miss_f[:q_slow]
        r = {"n": n, "machine": platform.processor() or platform.machine(),
             "python": platform.python_version()}

        # ---------------- preprocessing ----------------
        reps = 3 if n < 1_000_000 else 1
        ts = []
        for _ in range(reps):
            t0 = time.perf_counter(); sdata, sort_comps = merge_sort(data); ts.append(time.perf_counter() - t0)
        r["sort_time_s"] = statistics.median(ts)
        r["sort_comparisons"] = sort_comps
        r["sort_nlogn_bound"] = n * math.log2(n)
        t0 = time.perf_counter(); _ = sorted(data); r["timsort_builtin_s"] = time.perf_counter() - t0
        assert sdata == _

        ts = []
        for _ in range(reps):
            t0 = time.perf_counter(); H = HashIndex(data); ts.append(time.perf_counter() - t0)
        r["hash_build_s"] = statistics.median(ts)
        r["hash_stats"] = H.chain_stats()
        tracemalloc.start(); _H = HashIndex(data); cur, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
        r["hash_extra_mem_MB"] = cur / 1e6
        r["sorted_extra_mem_MB"] = (8 * n) / 1e6      # one pointer per record in the sorted copy
        del _H

        # ---------------- timing ----------------
        rep_slow = 3
        r["linear_us_hit"] = time_per_search(lambda k: linear_search(data, k), hits_s, rep_slow)
        r["linear_us_miss"] = time_per_search(lambda k: linear_search(data, k), miss_s, rep_slow)
        r["binary_us_hit"] = time_per_search(lambda k: binary_search_recursive(sdata, k), hits_f, 5)
        r["binary_us_miss"] = time_per_search(lambda k: binary_search_recursive(sdata, k), miss_f, 5)
        r["hash_us_hit"] = time_per_search(H.search, hits_f, 5)
        r["hash_us_miss"] = time_per_search(H.search, miss_f, 5)

        # ---------------- comparison counts ----------------
        lc_h = [linear_search_counted(data, k)[1] for k in hits_f[:1000]]   # 1000 successful queries for a stable mean
        lc_m = [linear_search_counted(data, k)[1] for k in miss_s]
        r["linear_cmp_best"] = linear_search_counted(data, data[0])[1]
        r["linear_cmp_avg_hit"] = statistics.mean(lc_h)
        r["linear_cmp_worst"] = max(lc_m + [linear_search_counted(data, data[-1])[1]])
        bc_h = [binary_search_counted(sdata, k)[1] for k in hits_f]
        bc_m = [binary_search_counted(sdata, k)[1] for k in miss_f]
        r["binary_cmp_best"] = binary_search_counted(sdata, sdata[(n - 1) // 2])[1]
        r["binary_cmp_avg_hit"] = statistics.mean(bc_h)
        r["binary_cmp_avg_miss"] = statistics.mean(bc_m)
        r["binary_cmp_worst"] = max(bc_h + bc_m)
        hc_h = [H.search_counted(k)[1] for k in hits_f]
        hc_m = [H.search_counted(k)[1] for k in miss_f]
        r["hash_cmp_avg_hit"] = statistics.mean(hc_h)
        r["hash_cmp_avg_miss"] = statistics.mean(hc_m)
        r["hash_cmp_worst"] = max(hc_h + hc_m)

        # theory for the same n
        a = n / H.m
        r["theory"] = {
            "linear_avg_hit": (n + 1) / 2, "linear_worst": n,
            "binary_worst": math.floor(math.log2(n)) + 1,
            "binary_avg_hit": ((n + 1) / n) * math.log2(n + 1) - 1,
            "hash_avg_hit": 1 + a / 2, "hash_avg_miss": a,
        }
        results.append(r)
        print(f"  done: linear {r['linear_us_hit']:.1f} us | binary {r['binary_us_hit']:.2f} us | hash {r['hash_us_hit']:.3f} us (successful search, mean)", flush=True)

    with open(os.path.join(OUT, "results.json"), "w") as f:
        json.dump(results, f, indent=2)
    flat = [{k: v for k, v in r.items() if not isinstance(v, dict)} for r in results]
    with open(os.path.join(OUT, "results.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(flat[0].keys())); w.writeheader(); w.writerows(flat)
    print_summary(results)
    print("\nSaved results.json / results.csv")


if __name__ == "__main__":
    main([s for s in SIZES if s <= 100_000] if "--quick" in sys.argv else SIZES)
