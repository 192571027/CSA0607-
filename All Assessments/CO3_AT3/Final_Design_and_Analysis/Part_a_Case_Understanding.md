# Part (a) – Understanding the Case

KartIQ records about 10,000,000 orders a day and ranks 100,000 sellers. Four symptoms were reported: the nightly report misses its deadline, the leaderboard freezes during sales, order lookups take seconds, and recommendations refresh only once a day. Each symptom maps to one module.

| Module | Computational requirement | Key issues | Consequence of a poor algorithm choice |
|---|---|---|---|
| **1 – Nightly order consolidation** | Sort 10,000,000 (timestamp, order ID) records by timestamp once per night. | **Stability**: equal timestamps from different payment gateways must stay in arrival order (auditors reconcile gateway by gateway). **Scale/time**: must finish inside the nightly window, so a guaranteed Θ(n log n) is needed. **Memory**: 160 MB of data (16 B/record), and a copy doubles that; data may not fit in RAM. | An unstable sort (Quick Sort, Heap Sort) silently reorders tied orders and breaks the audit. A quadratic sort needs about 5 × 10¹³ comparisons (n²/2) and never finishes; Quick Sort's own worst case is the same. A sort that cannot spill to disk fails with out-of-memory. |
| **2 – Live seller leaderboard** | Re-sort 100,000 scores every few seconds. | **Nearly sorted input** (few scores change between refreshes). **Worst-case behaviour**: the current first-element pivot hits the Θ(n²) worst case on sorted/nearly sorted data, with recursion depth ≈ n. **Latency** must be small and predictable; in-place sorting is desirable; stability is not required. | n(n−1)/2 ≈ 5.0 × 10⁹ comparisons per refresh and a recursion depth of ≈ 100,000 (stack overflow risk): the leaderboard freezes, exactly during sale events when refreshes are most frequent. |
| **3 – Order lookup** | Find an order by timestamp in the consolidated list; return the **first** order when several share the timestamp. | **Sorted-data precondition**: binary search is only valid on the output of Module 1 (sorted by the search key). **Duplicates**: the standard search returns an arbitrary match. **Many lookups** by support staff, so per-lookup cost matters. | Linear search costs up to 10,000,000 comparisons per lookup (seconds). Binary search on unsorted data returns wrong "not found" answers; standard binary search on sorted data returns the wrong one of several equal timestamps. |
| **4 – Recommendation scores** | Compute C = A × B for n × n matrices, n = 1,024, so the refresh is not limited to once a day. | **Matrix size**: n³ = 1,073,741,824 multiplications for the conventional method. **Power-of-two size** (1,024 = 2¹⁰ suits recursion). **Extra memory** of recursive methods (Θ(n²) temporaries). **Practical speed**: additions, cache behaviour and numerical error can erase Strassen's theoretical gain. | The conventional method needs about 1.07 × 10⁹ multiplications and 2.15 × 10⁹ arithmetic operations per refresh, so it cannot be repeated frequently. Using Strassen blindly (recursing to 1 × 1) saves only 8 % of arithmetic, uses extra memory, and was slower than a tuned kernel in testing. |

## How the modules depend on each other

```
 Module 1 (stable sort) ──sorted, stable list──► Module 3 (binary search, first occurrence)
 Module 2 (leaderboard sort)   – independent       Module 4 (matrix product)   – independent
```

Module 3's correctness depends on two guarantees from Module 1: the list is sorted by timestamp, and ties are in arrival order (so "first in list" means "first to arrive").
