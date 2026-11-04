# Task 4 - Best, Average and Worst-Case Analysis (4 marks)

## A - Linear search

- **Best case - the key is the first record.** The first comparison succeeds: C = 1, T = Theta(1). It occurs because the search order is fixed from the front of the table; no property of n matters.
- **Average case - the key is equally likely at any position.** On average half of the table is scanned before the key is met: C = (n+1)/2. A successful search is therefore only about twice as fast as a failed one, but both are Theta(n).
- **Worst case - the key is the last record or absent.** Nothing can be concluded about absence until all n records have been inspected: C = n. Absent keys are the *typical* worst case in a registration system (typos, students who never enrolled).

## B - Binary search (on the sorted array)

- **Best case - the key is at the middle index.** It is found in the first call, C = 1, Theta(1).
- **Average case.** Half the elements are on the deepest level of the implicit decision tree and a quarter on the next, so the average successful search needs ((n+1)/n) log2(n+1) - 1 comparisons, i.e. about **log2 n - 1**; Theta(log n).
- **Worst case - the key is absent or located on the deepest level.** The range must be halved until it is empty: C = floor(log2 n) + 1. The difference between best, average and worst arises only from *when* the middle probe happens to hit the key; the range shrinks by half in every case, which is why even the worst case is logarithmic and the data order (random, nearly sorted) does not matter after sorting.
- **Preprocessing (merge sort).** Best, average and worst are all Theta(n log n): the number of levels (log n) is fixed and each level does about n work; only the constant changes (best (n/2) log n if the halves are already ordered, worst n log n - n + 1).

## C - Hash table

- **Best case - the key sits alone (first) in its bucket**, C = 1; for an absent key whose bucket is empty, C = 0 (only the hash is computed).
- **Average case - keys are spread uniformly.** The chain has expected length alpha (0.75): C = 1 + alpha/2 for successful and alpha for unsuccessful searches, independent of n. Theta(1).
- **Worst case - all (or very many) keys collide into the same bucket.** The structure degenerates to one linked list and C = n, Theta(n). It occurs for a poor hash function (e.g. k mod m with systematically structured registration numbers) or deliberately chosen keys. The multiplicative hash and the measured maximum chain length (at most 6 for any tested n) show that this does not happen in practice here.

**Table 4.1 - Case summary and measured counts**

| Algorithm | Best | Average (successful) | Worst | Measured at n = 1,000,000 (best / avg / worst) |
|---|---|---|---|---|
| A  Linear | 1 | (n+1)/2 | n | 1 / 501,371 / 1,000,000 |
| B  Binary | 1 | ~log2(n+1) - 1 | floor(log2 n)+1 | 1 / 18.93 / 20 |
| C  Hash | 1 (0 if empty bucket) | 1 + alpha/2 | n | 1 / 1.40 / 5 (max chain observed) |
