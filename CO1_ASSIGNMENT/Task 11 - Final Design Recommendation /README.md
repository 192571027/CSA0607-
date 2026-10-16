# Task 11 - Final Design Recommendation 

**Recommendation for the original (general-purpose) problem: keep the registration numbers in a sorted array and use binary search; sort once with merge sort (or the system sort) and re-merge new records in batches.** The hash table is the strongest alternative and is adopted in Task 12 once the workload is known.

## Why this choice - evidence from analysis and experiment

**Table 11.1 - Criteria-based comparison**

| Criterion | A  Linear | B  Sort + binary | C  Hash |
|---|---|---|---|
| Search cost, theory | Theta(n) | Theta(log n), worst case guaranteed | Theta(1) expected, Theta(n) worst |
| Measured search at n = 1M (hit / miss) | 10,789 / 25,355 us | 3.17 / 3.91 us | 0.54 / 0.43 us |
| Preprocessing (theory) | none | Theta(n log n) | Theta(n) |
| Preprocessing measured, n = 1M | 0 | 2.53 s (own merge sort); 0.27 s with built-in sort | 1.13 s |
| Preprocessing paid back after (searches) | - | ~235 searches | ~105 searches |
| Extra memory at n = 1M | 0 | 8 MB (one pointer per record) | 97 MB (about 12x more) |
| Supports ordered / range / prefix queries (e.g. all students of one batch) | no (full scan) | yes - contiguous range | no |
| Depends on hash quality / worst-case guarantee | n/a | no - deterministic | yes |
| Practical as n grows | No - cost grows with n | Yes - 20 -> 24 comparisons for 1M -> 10M | Yes - if table is resized with n |

- **Why not linear search?** At 1,000,000 records one lookup takes 10.8 ms on average and 25.4 ms when the number is not present. Its only advantage - no preprocessing - disappears after roughly 100-200 searches (Table 9.4), a tiny number for a university system.
- **Why binary search rather than the (faster) hash table in the *general* case?** (i) Guaranteed worst case of 20 comparisons for 10^6 records, whatever the key pattern; (ii) 12 times less extra memory (8 MB vs 97 MB); (iii) a sorted array answers range/prefix questions that administrators actually ask (all registration numbers of one admission year); (iv) it is about 6x slower than the hash table in the single-key benchmark (2.5x in the mixed 50,000-request run of Task 12) - a difference of only a few microseconds per search; (v) it only needs a comparison order on keys. When nothing is known about update or query frequency, this is the most robust choice.

## Trade-offs and limitations

- **Preprocessing cost.** Sorting 1M records took 2.5 s with the simple merge sort (the pure-Python built-in sort needs 0.27 s). It must be repeated or repaired when records are added: inserting into the middle of a sorted array costs O(n) per record, so new records should be collected and merged in batches (sort the k new keys, then one linear merge - 0.24 s for 2,000 keys at n = 1M, Task 12).
- **Memory/caching.** Binary search touches scattered memory locations; at n = 10^6 each level cost about twice as much as at n = 10^3 (Task 10).
- **Scalability.** Extrapolating the measured n log n behaviour, sorting 10 million records would take about 30 s in this implementation (extrapolation, not measured); a search would need 24 comparisons. Beyond main-memory sizes the same idea generalises to disk-based B-trees, which are the multi-way relatives of binary search.
- **Not recommended** if the data change continuously (every insert needs a re-sort or a tree structure), or if memory is not a concern and only exact-match lookups are needed - the situation analysed in Task 12.

![Figure 11.1 - Total cost of each design as the number of searches grows (n = 1M)](../Report/Tables_and_Graphs/fig6_total_cost_vs_searches.png)

*Figure 11.1 - Total cost of each design as the number of searches grows (n = 1M)*
