# Part (f) – Final Algorithmic Design and Justification

## 1. One choice per module

| Module | Chosen algorithm | Time complexity | Extra memory | Reason for the choice |
|---|---|---|---|---|
| **1 – Order consolidation** | **Stable Merge Sort** (external k-way merge sort when the data exceeds RAM) | Θ(n log n) in every case; ≈ 2.2 × 10⁸ comparisons (worst case 223,222,785) for n = 10⁷ | Θ(n): 160 MB buffer for 160 MB of data (80 MB with a half-size buffer); external version needs only the run buffers | Only stable Θ(n log n) option with a guaranteed worst case; sequential access suits disk and parallel runs |
| **2 – Live leaderboard** | **Quick Sort with median-of-three pivot**, insertion-sort cut-off for small ranges and a Heap-Sort fallback (introsort guard) | Θ(n log n) on nearly sorted data (≈ 1.56 × 10⁶ comparisons for n = 10⁵ versus 5.0 × 10⁹ before); Θ(n log n) worst case with the guard | O(log n) stack (recurse into the smaller part) – in place | Fastest in practice, in place; the median-of-three pivot removes the sorted-input worst case; stability is not needed for scores |
| **3 – Order lookup** | **Binary Search, first-occurrence (lower-bound) variant** on Module 1's output | Θ(log n): 25 comparisons for n = 10⁷ (24 for the plain search) | O(1) | Needs no extra structure beyond the sorted list; returns the first (earliest-arriving) order among equal timestamps |
| **4 – Recommendation scores** | **Hybrid Strassen**: 1–3 recursion levels (cut-off 128–512, set by benchmark), optimised conventional kernel below the cut-off | Θ(n^2.807) asymptotically; with 3 levels 7.19 × 10⁸ multiplications versus 1.07 × 10⁹ for n = 1,024 | Θ(n²): 24 MiB for A, B, C plus temporaries (≈ 45 MiB naive, less with reuse) | Fewer multiplications for large n while avoiding the overhead that makes full recursion slow |

## 2. Main trade-off and a condition for changing each decision

| Module | Main trade-off of the decision | One condition under which I would change it |
|---|---|---|
| **1 – Merge Sort** | Extra Θ(n) memory (or disk I/O when external) is paid for stability and a guaranteed Θ(n log n). | If each payment gateway already delivers its orders in timestamp order, skip the full sort and do a direct **k-way merge of the gateway streams** (n·lg k with k = number of gateways, with ties broken by gateway order). |
| **2 – Quick Sort (median-of-three)** | Not stable and, without a guard, not worst-case safe; chosen for speed and in-place operation. | If only a tiny fraction of scores changes between refreshes (few inversions d ≪ n log n), switch to an **adaptive sort** (insertion sort or Timsort: about n + d work) or to incremental updates of the leaderboard; also if ties must keep a fixed order, use a stable sort or add seller ID as a tie-breaker. |
| **3 – Binary Search (first occurrence)** | The list must stay sorted (rebuilt nightly), and the first-occurrence variant costs one more comparison than the plain search. | If orders must be searchable **while new orders keep arriving** (the list is no longer static), or lookups are by order ID rather than timestamp, use an index structure instead – a B-tree or balanced tree for ordered access, or a hash index for exact-key lookups. |
| **4 – Hybrid Strassen** | Fewer multiplications are paid for with more additions, Θ(n²) temporary memory and slightly larger floating-point error. | If benchmarking on the production hardware shows the optimised BLAS/GPU kernel is faster (as it was in my single-core test at n = 1,024), or the matrices are sparse or need exact arithmetic, use the **conventional kernel**; if n grows to several thousand, more Strassen levels become worthwhile. |

## 3. Summary of expected improvement

| Module | Before | After | Improvement |
|---|---|---|---|
| 1 | Report misses deadline | ≈ 2.2 × 10⁸ comparisons, guaranteed, stable | meets the nightly window; audit order preserved |
| 2 | ≈ 5.0 × 10⁹ comparisons, depth ≈ 10⁵ | ≈ 1.6 × 10⁶ comparisons, depth ≈ 17 | ≈ 3,200 × fewer comparisons |
| 3 | up to 10⁷ comparisons (linear) | 25 comparisons | ≈ 400,000 × fewer comparisons, and the correct (first) order |
| 4 | 1.07 × 10⁹ multiplications | 7.2 × 10⁸ (3 levels); 2.8 × 10⁸ at full recursion, benchmark decides | 33–74 % fewer multiplications, but only measured speed counts |

## 4. Algorithm comparison (all four divide-and-conquer designs)

| Algorithm | Divide | Conquer | Combine | Recurrence | Solution | Space | Stable / in place |
|---|---|---|---|---|---|---|---|
| Merge Sort | split at middle, Θ(1) | sort both halves | merge, ≤ n − 1 comparisons | T(n) = 2T(n/2) + n − 1 | n lg n − n + 1 = Θ(n log n) | Θ(n) | stable / not in place |
| Quick Sort | partition around pivot, n − 1 comparisons | sort both parts | none | best 2T(n/2) + n − 1; worst T(n−1) + n − 1 | Θ(n log n); n(n−1)/2 = Θ(n²) | O(log n) – O(n) stack | not stable / in place |
| Binary Search | compare with middle, Θ(1) | search one half | none | T(n) = T(n/2) + 1 | ⌊lg n⌋ + 1 = Θ(log n) | O(1) | – |
| Strassen | split into 4 blocks, 10 sums | 7 block products | 8 additions | T(n) = 7T(n/2) + Θ(n²) | Θ(n^lg 7) = Θ(n^2.807) | Θ(n²) | – |

## 5. Closing recommendations

1. Deploy the stable Merge Sort for the nightly job, with the external variant as a safety net, and make the gateway k-way merge the first optimisation if gateway feeds are already ordered.
2. Replace the first-element pivot immediately (a few-line change); add the introsort guard and insertion-sort cut-off.
3. Switch support lookups to the first-occurrence binary search on the consolidated list; keep the list sorted and stable.
4. Benchmark the hybrid Strassen against the production BLAS before adopting it; adopt it only where it measurably wins.
