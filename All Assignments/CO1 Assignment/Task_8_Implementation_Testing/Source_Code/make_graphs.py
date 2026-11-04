"""make_graphs.py - builds all figures for Task 9/10/12 from results.json and design_challenge_results.json."""
import json, math, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
OUT = os.path.join(ROOT, "Report", "Tables_and_Graphs")
os.makedirs(OUT, exist_ok=True)
R = json.load(open(os.path.join(ROOT, "Task_9_Experimental_Performance", "results.json")))
D = json.load(open(os.path.join(ROOT, "Task_12_Design_Challenge", "design_challenge_results.json")))
ns = [r["n"] for r in R]
C = {"linear": "#d62728", "binary": "#1f77b4", "hash": "#2ca02c"}
plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.alpha": .3})

def save(name):
    plt.tight_layout(); plt.savefig(os.path.join(OUT, name), dpi=160); plt.close()

# Fig 1: search time (log-log)
fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
for i, (kind, title) in enumerate((("hit", "Successful search"), ("miss", "Unsuccessful search"))):
    for a, lab, mk in (("linear", "Linear search  O(n)", "o"), ("binary", "Recursive binary search  O(log n)", "s"), ("hash", "Hash table  O(1) expected", "^")):
        ax[i].loglog(ns, [r[f"{a}_us_{kind}"] for r in R], marker=mk, color=C[a], label=lab)
    ax[i].set_title(title + " - mean time per search"); ax[i].set_xlabel("n (records)"); ax[i].set_ylabel("microseconds")
    ax[i].legend(fontsize=8)
save("fig1_search_time_loglog.png")

# Fig 2: linear-scale zoom of binary vs hash
plt.figure(figsize=(6.2, 4.2))
for a, lab, mk in (("binary", "Recursive binary search", "s"), ("hash", "Hash table", "^")):
    plt.plot(ns, [r[f"{a}_us_hit"] for r in R], marker=mk, color=C[a], label=lab)
plt.xscale("log"); plt.xlabel("n (records)"); plt.ylabel("microseconds (successful)"); plt.title("Binary vs hash (linear y-axis)"); plt.legend()
save("fig2_binary_vs_hash_zoom.png")

# Fig 3: comparisons vs theory
plt.figure(figsize=(7, 4.4))
plt.loglog(ns, [r["linear_cmp_avg_hit"] for r in R], "o", color=C["linear"], label="Linear - measured")
plt.loglog(ns, [r["theory"]["linear_avg_hit"] for r in R], "--", color=C["linear"], label="Linear - theory (n+1)/2")
plt.loglog(ns, [r["binary_cmp_avg_hit"] for r in R], "s", color=C["binary"], label="Binary - measured")
plt.loglog(ns, [r["theory"]["binary_avg_hit"] for r in R], "--", color=C["binary"], label="Binary - theory ~log2(n+1)-1")
plt.loglog(ns, [r["hash_cmp_avg_hit"] for r in R], "^", color=C["hash"], label="Hash - measured")
plt.loglog(ns, [r["theory"]["hash_avg_hit"] for r in R], "--", color=C["hash"], label="Hash - theory 1+alpha/2")
plt.xlabel("n (records)"); plt.ylabel("mean key comparisons (successful)"); plt.title("Comparison counts: experiment vs theory"); plt.legend(fontsize=8)
save("fig3_comparisons_vs_theory.png")

# Fig 4: preprocessing
plt.figure(figsize=(6.6, 4.4))
plt.loglog(ns, [r["sort_time_s"] for r in R], "s-", color=C["binary"], label="Merge sort (own, pure Python)")
plt.loglog(ns, [r["timsort_builtin_s"] for r in R], "d-", color="gray", label="Python built-in sorted() (reference)")
plt.loglog(ns, [r["hash_build_s"] for r in R], "^-", color=C["hash"], label="Hash table build")
k = R[-1]["sort_time_s"] / (R[-1]["n"] * math.log2(R[-1]["n"]))
plt.loglog(ns, [k * n * math.log2(n) for n in ns], "k:", label="c * n log n (fitted at n=1M)")
plt.xlabel("n (records)"); plt.ylabel("seconds"); plt.title("Preprocessing cost"); plt.legend(fontsize=8)
save("fig4_preprocessing.png")

# Fig 5: sort comparisons vs n log2 n
plt.figure(figsize=(6.2, 4.2))
plt.loglog(ns, [r["sort_comparisons"] for r in R], "s-", color=C["binary"], label="merge sort comparisons (measured)")
plt.loglog(ns, [r["sort_nlogn_bound"] for r in R], "k--", label="n log2 n")
plt.xlabel("n"); plt.ylabel("comparisons"); plt.title("Merge sort: measured vs n log n"); plt.legend()
save("fig5_sort_comparisons.png")

# Fig 6: total cost vs number of searches at n = 1M
r = R[-1]
qs = [10 ** e for e in range(0, 8)]
lin = r["linear_us_hit"] * .9 + r["linear_us_miss"] * .1
plt.figure(figsize=(7, 4.4))
plt.loglog(qs, [q * lin / 1e6 for q in qs], color=C["linear"], label="Linear: q * t_linear")
plt.loglog(qs, [r["sort_time_s"] + q * r["binary_us_hit"] / 1e6 for q in qs], color=C["binary"], label="Sort + binary: T_sort + q * t_bin")
plt.loglog(qs, [r["hash_build_s"] + q * r["hash_us_hit"] / 1e6 for q in qs], color=C["hash"], label="Hash: T_build + q * t_hash")
plt.axvline(D["requests_per_day"], color="k", ls=":"); plt.text(D["requests_per_day"] * 1.1, 0.05, "1.2 M searches/day", rotation=90, fontsize=8)
plt.xlabel("number of searches q (n = 1,000,000)"); plt.ylabel("total seconds"); plt.title("Total cost = preprocessing + searching"); plt.legend(fontsize=8)
save("fig6_total_cost_vs_searches.png")

# Fig 7: growth over 1000x data
g = {a: R[-1][f"{a}_us_hit"] / R[0][f"{a}_us_hit"] for a in ("linear", "binary", "hash")}
th = {"linear": R[-1]["n"] / R[0]["n"], "binary": math.log2(R[-1]["n"]) / math.log2(R[0]["n"]), "hash": 1.0}
plt.figure(figsize=(6.4, 4.2))
x = range(3); w = .38
plt.bar([i - w / 2 for i in x], [th[a] for a in g], w, label="Theoretical growth factor", color="#999999")
plt.bar([i + w / 2 for i in x], [g[a] for a in g], w, label="Observed growth factor", color=[C[a] for a in g])
plt.yscale("log"); plt.xticks(list(x), ["Linear", "Binary", "Hash"]); plt.ylabel("time(n=1M) / time(n=1K)")
plt.title("Growth of search time as n grows 1000x"); plt.legend(fontsize=8)
for i, a in enumerate(g):
    plt.text(i + w / 2, g[a] * 1.15, f"{g[a]:.1f}x", ha="center", fontsize=8)
    plt.text(i - w / 2, th[a] * 1.15, f"{th[a]:.1f}x", ha="center", fontsize=8)
save("fig7_growth_factor.png")

# Fig 8: one hour of traffic
plt.figure(figsize=(6.4, 4.2))
vals = [D["linear"]["hour_s"], D["binary"]["hour_s"], D["hash"]["hour_s"]]
b = plt.bar(["Linear\n(extrapolated)", "Sort + binary", "Hash index"], vals, color=[C["linear"], C["binary"], C["hash"]])
plt.yscale("log"); plt.ylabel("CPU seconds for 50,000 searches"); plt.title("One hour of traffic on 1,000,000 records")
for bar, v in zip(b, vals):
    plt.text(bar.get_x() + bar.get_width() / 2, v * 1.2, f"{v:.2f} s" if v < 100 else f"{v:.0f} s", ha="center", fontsize=9)
save("fig8_hourly_workload.png")

# Fig 9: daily update
u = D["daily_update"]
labs = ["Full re-sort\n(merge sort)", "Sort k +\nmerge O(n+k)", "Hash full\nrebuild", "Hash\nincremental"]
vals = [u["resort_full_mergesort_s"], u["sort_k_then_merge_s"], u["hash_full_rebuild_s"], u["hash_incremental_insert_s"]]
plt.figure(figsize=(7, 4.2))
b = plt.bar(labs, vals, color=[C["binary"], C["binary"], C["hash"], C["hash"]])
plt.yscale("log"); plt.ylabel("seconds"); plt.title(f"Nightly update: {D['new_records_per_day']:,} new records into 1,000,000")
for bar, v in zip(b, vals):
    plt.text(bar.get_x() + bar.get_width() / 2, v * 1.2, f"{v:.3f} s", ha="center", fontsize=9)
save("fig9_daily_update.png")
print("graphs written to", os.path.abspath(OUT))
