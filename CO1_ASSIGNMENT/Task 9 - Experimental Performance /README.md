# Task 9 - Experimental Performance 

All values below come from run_experiments.py (raw data: results.csv / results.json in Task_9_Experimental_Performance). Measured on one machine, so absolute values will differ on another computer; the **growth behaviour** is what matters.

**Table 9.1 - Mean time per search (microseconds)**

| n | A Linear hit | B Binary hit | C Hash hit | A Linear miss | B Binary miss | C Hash miss |
|---|---|---|---|---|---|---|
| 1,000 | 8.692 | 0.756 | 0.152 | 18.02 | 0.956 | 0.146 |
| 10,000 | 99.16 | 1.462 | 0.218 | 274.80 | 1.583 | 0.171 |
| 100,000 | 1,310.90 | 1.675 | 0.591 | 2,276.68 | 2.898 | 0.267 |
| 1,000,000 | 10,789.28 | 3.175 | 0.539 | 25,355.30 | 3.910 | 0.434 |

**Table 9.2 - Key comparisons (basic operations)**

| n | A avg (hit) | A worst | B avg (hit) | B worst | C avg (hit) | C avg (miss) | C max chain |
|---|---|---|---|---|---|---|---|
| 1,000 | 485 | 1,000 | 8.98 | 10 | 1.333 | 0.729 | 4 |
| 10,000 | 5,201 | 10,000 | 12.37 | 14 | 1.364 | 0.751 | 5 |
| 100,000 | 50,121 | 100,000 | 15.73 | 17 | 1.377 | 0.712 | 6 |
| 1,000,000 | 501,371 | 1,000,000 | 18.93 | 20 | 1.401 | 0.777 | 5 |

**Table 9.3 - Preprocessing time and extra memory**

| n | Merge sort comparisons | Merge sort s | Built-in sorted() s | Hash build s | Sorted copy MB | Hash index MB |
|---|---|---|---|---|---|---|
| 1,000 | 8,712 | 0.0008 | 0.0001 | 0.0002 | 0.01 | 0.09 |
| 10,000 | 120,390 | 0.0099 | 0.0010 | 0.0025 | 0.08 | 0.96 |
| 100,000 | 1,536,237 | 0.1783 | 0.0144 | 0.0398 | 0.80 | 9.65 |
| 1,000,000 | 18,674,355 | 2.5307 | 0.2741 | 1.1288 | 8.00 | 96.64 |

**Table 9.4 - Break-even number of searches in measured time (successful-search timings)**

| n | Searches q so that sort pays for itself (B vs A) | Searches q so that hash build pays for itself (C vs A) |
|---|---|---|
| 1,000 | 102 | 25 |
| 10,000 | 101 | 25 |
| 100,000 | 136 | 30 |
| 1,000,000 | 235 | 105 |

![Figure 9.1 - Search time vs n (log-log). Linear slope ~1; binary and hash almost flat.](../Report/Tables_and_Graphs/fig1_search_time_loglog.png)

*Figure 9.1 - Search time vs n (log-log). Linear slope ~1; binary and hash almost flat.*

![Figure 9.2 - Binary search vs hash table on a linear y-axis](../Report/Tables_and_Graphs/fig2_binary_vs_hash_zoom.png)

*Figure 9.2 - Binary search vs hash table on a linear y-axis*

![Figure 9.3 - Measured comparison counts against the theoretical formulas](../Report/Tables_and_Graphs/fig3_comparisons_vs_theory.png)

*Figure 9.3 - Measured comparison counts against the theoretical formulas*

![Figure 9.4 - Preprocessing time vs n](../Report/Tables_and_Graphs/fig4_preprocessing.png)

*Figure 9.4 - Preprocessing time vs n*

![Figure 9.5 - Merge sort comparisons vs n log2 n](../Report/Tables_and_Graphs/fig5_sort_comparisons.png)

*Figure 9.5 - Merge sort comparisons vs n log2 n*

![Figure 9.6 - Total cost (preprocessing + q searches) at n = 1,000,000](../Report/Tables_and_Graphs/fig6_total_cost_vs_searches.png)

*Figure 9.6 - Total cost (preprocessing + q searches) at n = 1,000,000*

![Figure 9.7 - Console output of run_experiments.py](../Report/Output_Screenshots/output_experiments.png)

*Figure 9.7 - Console output of run_experiments.py*

Raw data: `results.csv`, `results.json`. Reproduce with `python ../Task_8_Implementation_Testing/Source_Code/run_experiments.py`.
