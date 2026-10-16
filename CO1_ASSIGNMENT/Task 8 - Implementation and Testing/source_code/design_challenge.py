"""
design_challenge.py - Task 12 evidence: 50,000 searches/hour on 1,000,000 records,
new records added once per day.
  Part A: one simulated hour of traffic (50,000 searches, 90% hits / 10% misses)
  Part B: daily-update strategies for k new registrations
  Part C: break-even number of searches between strategies
Writes ../../Task_12_Design_Challenge/design_challenge_results.json
"""
import json, os, random, statistics, time
from algorithms import (linear_search, binary_search_recursive, merge_sort, merge_sorted, HashIndex)
from data_gen import make_dataset

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "Task_12_Design_Challenge")
os.makedirs(OUT, exist_ok=True)

N = 1_000_000
REQ_PER_HOUR = 50_000
NEW_PER_DAY = 2_000
data = make_dataset(N)
rng = random.Random(99)
present = set(data)
queries = []
for _ in range(REQ_PER_HOUR):
    if rng.random() < 0.9:
        queries.append(data[rng.randrange(N)])
    else:
        while True:
            k = rng.randrange(100_000_000, 1_000_000_000)
            if k not in present:
                queries.append(k); break

res = {"n": N, "requests_per_hour": REQ_PER_HOUR, "requests_per_second": REQ_PER_HOUR / 3600,
       "requests_per_day": REQ_PER_HOUR * 24, "new_records_per_day": NEW_PER_DAY}

# ---- preprocessing ---------------------------------------------------------
t0 = time.perf_counter(); sdata, _ = merge_sort(data); res["sort_s"] = time.perf_counter() - t0
t0 = time.perf_counter(); H = HashIndex(data); res["hash_build_s"] = time.perf_counter() - t0

# ---- Part A: one hour of traffic -------------------------------------------
def run(fn, qs):
    lat = []
    t_all = time.perf_counter()
    for k in qs:
        t0 = time.perf_counter_ns(); fn(k); lat.append(time.perf_counter_ns() - t0)
    total = time.perf_counter() - t_all
    lat.sort()
    pct = lambda p: lat[min(len(lat) - 1, int(p * len(lat)))] / 1000.0   # microseconds
    return {"queries_run": len(qs), "total_s": total, "mean_us": statistics.mean(lat) / 1000.0,
            "p50_us": pct(0.50), "p99_us": pct(0.99), "max_us": lat[-1] / 1000.0}

res["binary"] = run(lambda k: binary_search_recursive(sdata, k), queries)
res["hash"] = run(H.search, queries)
LIN_SAMPLE = 300                                     # linear is far too slow to run all 50,000 repeatedly
lin = run(lambda k: linear_search(data, k), queries[:LIN_SAMPLE])
lin["extrapolated_hour_s"] = lin["mean_us"] * REQ_PER_HOUR / 1e6
lin["note"] = f"measured on {LIN_SAMPLE} queries, extrapolated linearly to {REQ_PER_HOUR}"
res["linear"] = lin
for name in ("binary", "hash"):
    res[name]["hour_s"] = res[name]["total_s"]
res["linear"]["hour_s"] = lin["extrapolated_hour_s"]
for name in ("linear", "binary", "hash"):
    res[name]["cpu_utilisation_pct"] = res[name]["hour_s"] / 3600 * 100

# ---- Part B: daily update strategies ----------------------------------------
new_keys = []
while len(new_keys) < NEW_PER_DAY:
    k = rng.randrange(100_000_000, 1_000_000_000)
    if k not in present:
        new_keys.append(k); present.add(k)
upd = {}
t0 = time.perf_counter(); d2 = data + new_keys; s_full, _ = merge_sort(d2); upd["resort_full_mergesort_s"] = time.perf_counter() - t0
t0 = time.perf_counter(); _ = sorted(d2); upd["resort_full_timsort_s"] = time.perf_counter() - t0
t0 = time.perf_counter(); nk, _ = merge_sort(new_keys); s_merged = merge_sorted(sdata, nk); upd["sort_k_then_merge_s"] = time.perf_counter() - t0
assert s_merged == s_full
H2 = HashIndex(list(data))
t0 = time.perf_counter()
for k in new_keys:
    H2.insert(k)
upd["hash_incremental_insert_s"] = time.perf_counter() - t0
t0 = time.perf_counter(); H3 = HashIndex(d2); upd["hash_full_rebuild_s"] = time.perf_counter() - t0
assert all(H2.search(k) >= 0 for k in new_keys[:200])
res["daily_update"] = upd

# ---- Part C: break-even analysis (measured constants) -------------------------
lin_us = (0.9 * 11108.9 + 0.1 * 24228.7)             # overwritten below from results.json if present
try:
    base = json.load(open(os.path.join(OUT, "..", "Task_9_Experimental_Performance", "results.json")))[-1]
    lin_us = 0.9 * base["linear_us_hit"] + 0.1 * base["linear_us_miss"]
except Exception:
    pass
bin_us, hash_us = res["binary"]["mean_us"], res["hash"]["mean_us"]
be = {"linear_mean_us": lin_us, "binary_mean_us": bin_us, "hash_mean_us": hash_us}
be["searches_to_amortise_sort"] = res["sort_s"] * 1e6 / (lin_us - bin_us)
be["searches_to_amortise_hash"] = res["hash_build_s"] * 1e6 / (lin_us - hash_us)
be["hash_vs_binary_breakeven"] = res["hash_build_s"] - res["sort_s"]    # hash is cheaper to build -> no break-even needed
be["per_search_prep_overhead_us_binary"] = res["sort_s"] * 1e6 / res["requests_per_day"]
be["per_search_prep_overhead_us_hash"] = res["hash_build_s"] * 1e6 / res["requests_per_day"]
res["break_even"] = be

json.dump(res, open(os.path.join(OUT, "design_challenge_results.json"), "w"), indent=2)
print(json.dumps(res, indent=2))
