# Task 5 - Asymptotic Analysis (3 marks)

**Table 5.1 - Asymptotic classification**

| Algorithm / quantity | O (upper) | Omega (lower) | Theta (tight) | Comment |
|---|---|---|---|---|
| A  Linear search, any input | O(n) | Omega(1) | none for 'all inputs' | Best case Theta(1), worst case Theta(n) - no single Theta covers every input. |
| A  Linear, failed search / worst case | O(n) | Omega(n) | Theta(n) | Every record is inspected. |
| B  Binary search, any input | O(log n) | Omega(1) | none for 'all inputs' | Worst case and failed search: Theta(log n). |
| B  Merge sort (preprocessing) | O(n log n) | Omega(n log n) | Theta(n log n) | Same in best, average, worst; comparison sorting cannot beat n log n. |
| C  Hash search, expected | O(1) | Omega(1) | Theta(1) expected | Worst case O(n) if all keys collide. |
| C  Hash build | O(n) | Omega(n) | Theta(n) | Every record must be touched. |

**Ordering of growth rates.** 1  <<  log n  <<  n  <<  n log n. For example, lim (log2 n)/n = 0 (by L'Hopital, (1/(n ln 2))/1 -> 0), so log n grows strictly slower than n, and n/log2 n -> infinity: the advantage of B over A *grows without bound* as n grows. Likewise the advantage of C over B grows like log n.

## Meaning for the university database (1,000 to 1,000,000+ records)

**Table 5.2 - Operation counts at the required sizes**

| n | A  Linear (avg / worst) | B  Binary (worst) | C  Hash (expected) | Factor n grows | A grows by | B grows by | C grows by |
|---|---|---|---|---|---|---|---|
| 1,000 | 500 / 1,000 | 10 | ~1.4 | - | - | - | - |
| 10,000 | 5,000 / 10,000 | 14 | ~1.4 | 10x | 10x | 1.4x | 1x |
| 100,000 | 50,000 / 100,000 | 17 | ~1.4 | 10x | 10x | 1.2x | 1x |
| 1,000,000 | 500,000 / 1,000,000 | 20 | ~1.4 | 10x | 10x | 1.2x | 1x |

- When the database grows 1,000-fold, linear search does **1,000 times more work per query**; its cost increase is the same as the data increase, so it eventually becomes impractical even if it is acceptable at 1,000 records.
- Binary search does only **twice** as much work (10 to 20 comparisons) - the 1,000-fold growth costs about 10 extra comparisons. The price is the Theta(n log n) sort, paid once and again whenever the data changes.
- The hash table's per-query work does not change at all as n grows (provided the table is sized with n). Its price is Theta(n) memory for the table and the loss of key order.
- Because O-notation hides constants, the asymptotic ranking says nothing about small n (at n = 1,000 the three are all microseconds) - this is why Tasks 9-10 measure real behaviour, and why preprocessing (a constant-factor/lower-order cost per search when q is large) must be examined together with the number of searches q.
