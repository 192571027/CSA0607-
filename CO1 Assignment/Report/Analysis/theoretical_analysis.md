# Theoretical analysis (Tasks 2-7)

## Task 2 - Identify the Basic Operation

The basic operation is the operation executed most often in the innermost part of the algorithm, whose count grows with n and therefore dominates the running time. Every other statement (index arithmetic, assignments, function-call overhead) is executed at most a constant number of times per basic operation, so counting basic operations measures the algorithm's growth rate independently of hardware.

**Table 2.1 - Basic operations**

| Algorithm | Basic operation | Where it occurs | Why it is appropriate | How its count changes with n |
|---|---|---|---|---|
| A - Linear search | Comparison A[i] = key | Body of the single for-loop; once per examined record | It is the only work inside the loop; loop control is proportional to it. Each execution examines exactly one record. | Between 1 and n. It grows in direct proportion to n for failed searches (always n) and on average for successful ones ((n+1)/2). |
| B - Binary search | Three-way comparison of key with A[mid] | Once per recursive call (once per level of the recursion) | Each call performs exactly one such comparison and then discards half of the range, so the number of calls equals the number of comparisons. | Equals the number of times n can be halved: at most floor(log2 n)+1. Multiplying n by 1,000 adds only about 10 comparisons. |
| B - Preprocessing (merge sort) | Comparison of two elements in Merge | Inner while-loop of Merge | Each comparison moves one element to the output, so total work is proportional to comparisons. | About n log2 n - n comparisons for random input. |
| C - Hash table | Comparison A[idx] = key inside the chain (the hash computation is one O(1) step per search) | For-loop over the chain of bucket h(key) | Hashing costs the same for every n, so the part that can vary is the chain scan; its length is the only n-dependent cost. | Expected chain length is alpha = n/m (about 0.75 here), independent of n if m grows with n. So it stays about 1-2 comparisons for any n. |
| C - Preprocessing (build) | Hash computation + append, once per record | Loop of BuildHash | Exactly n executions, each O(1). | Exactly n. |

**Relation to behaviour.** In A the operation count is governed by *where the key is*, in B by *how many times the range can be halved* (a property of n only), in C by *how crowded the key's bucket is* (a property of the load factor, not of n). These three different dependencies are exactly what produce the linear, logarithmic and constant growth derived in Task 3 and confirmed by counters in Task 9.


## Task 3 - Mathematical Time-Complexity Derivation

Notation: **n** = number of records (input size); **C(n)** = number of basic operations; **T(n) = c x C(n) + c0**, where c is the constant cost of one basic operation. **q** = number of searches performed after preprocessing.

## A - Linear search

If the key is at position i (1-based) the loop executes the comparison exactly i times; if it is absent the loop runs to the end, n times.

```text
C_best = 1     C_worst = n     C_unsuccessful = n
```

Average case for a successful search, assuming each of the n positions is equally likely (probability 1/n):

```text
C_avg(success) = sum_{i=1..n} i * (1/n) = (1/n) * n(n+1)/2 = (n+1)/2
```

If a fraction p of queries is successful and (1-p) unsuccessful:

```text
C_avg = p(n+1)/2 + (1-p)n = n(1 - p/2) + p/2
```

Since T(n) = c*C(n)+c0 and C(n) is a linear function of n in every case, T(n) belongs to Theta(n) (worst and unsuccessful case). Preprocessing = 0. Cost of q searches: **q x n** (worst case) or about **q x n/2** (successful average).

## B - Binary search + merge sort

**Search.** Each call performs one comparison and passes a sub-array of at most floor(n/2) elements to the next call, so C(n) = C(floor(n/2)) + 1 with C(0)=0, C(1)=1. Unrolling for n = 2^k: C(n) = k + 1 = log2 n + 1; the exact worst-case count for any n is C_worst(n) = floor(log2 n) + 1 (proved in Task 7). Best case C_best = 1 (key at the middle position).

**Average (successful) for n = 2^k - 1.** In the complete decision tree there are 2^(i-1) elements found after exactly i comparisons (levels i = 1..k). Therefore

```text
C_avg = (1/n) * sum_{i=1..k} i * 2^(i-1) = ((k-1) * 2^k + 1) / n = ((n+1)/n) * log2(n+1) - 1
```

For n = 1,000,000 this is 19.93 - 1 = 18.93 comparisons - so the average is only about one comparison smaller than the worst case, because half of all elements sit on the bottom level. For an unsuccessful search every one of the n+1 gaps is reached after about log2(n+1) comparisons.

**Preprocessing (merge sort).** The merge step compares the heads of two sorted lists and outputs one element per comparison, so merging lists of total size m takes at most m - 1 comparisons (at least m/2). Hence W(n) = 2W(n/2) + n - 1, W(1)=0, which solves (Task 7) to

```text
W(n) = n log2 n - n + 1      so merge sort is Theta(n log n) in every case; best case (n/2) log2 n
```

**Overall for q searches:**

```text
T_B(n, q) = [ n log2 n - n + 1 ]  +  q * [ floor(log2 n) + 1 ]   =   Theta(n log n + q log n)
```

## C - Hash table (separate chaining)

With m buckets and n keys, load factor alpha = n/m. Under the *simple uniform hashing* assumption (each key equally likely to fall into any bucket, independently) the expected length of a chain is alpha.

**Unsuccessful search** scans the whole chain: C = alpha. **Successful search:** the key that was inserted i-th has, on average, (i-1)/m keys ahead of it in its chain, so the average over all keys is

```text
C_avg(success) = (1/n) * sum_{i=1..n} [ 1 + (i-1)/m ] = 1 + (n-1)/(2m) = 1 + alpha/2 - alpha/(2n)  ~  1 + alpha/2
```

Both are independent of n when m grows proportionally to n (alpha constant = 0.75), so T(n) = c*(1+alpha/2)+c_hash = Theta(1) expected. Worst case: every key lands in one bucket and the chain scan becomes linear, C_worst = n, T = Theta(n) (extremely unlikely with a good hash function).

**Preprocessing.** Allocating m = Theta(n) slots and inserting n keys with O(1) work each gives Theta(n). **Overall for q searches:**

```text
T_C(n, q) = n + q * (1 + alpha/2)   =   Theta(n + q)   (expected)
```

## Combined comparison of preprocessing + searching

**Table 3.1 - Complexity functions**

| Algorithm | Preprocessing | One search (worst / avg) | Total for q searches |
|---|---|---|---|
| A  Linear | 0 | n  /  (n+1)/2 | Theta(q n) |
| B  Sort + binary | Theta(n log n) | floor(log2 n)+1  /  ~log2 n - 1 | Theta(n log n + q log n) |
| C  Hash | Theta(n) | n  /  1 + alpha/2 (expected) | Theta(n + q) expected |

**Worked example (n = 1,000,000; q = 50,000 searches, 90% successful):** A needs about 2.76e+10 comparisons; B needs about 1.96e+07 (of which 18,674,355 are the one-off sort); C needs about 1.07e+06 (of which 1,000,000 are the one-off build). Counting comparisons only, the sort has paid for itself after about n log2 n / (n/2) = 2 log2 n = 40 searches; in measured time (Table 9.4) the break-even is a few hundred searches because one comparison inside the Python sort loop costs more than one inside the tight linear-search loop.


## Task 4 - Best, Average and Worst-Case Analysis

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


## Task 5 - Asymptotic Analysis

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


## Task 6 - Recurrence Relation Formulation

The recursive approach is **recursive binary search** (Approach B). The recurrence is derived directly from the code in Section 1.

**Table 6.1 - Components of the recurrence**

| Component | Value for BinarySearch(A, key, lo, hi) | Reason (from the algorithm) |
|---|---|---|
| Input size of the original problem | n = hi - lo + 1 (number of elements still under consideration) | The call only ever looks at A[lo..hi]. |
| Number of recursive calls | a = 1 | After comparing with A[mid], the code takes exactly one of the two branches (left or right); the other half is never examined. |
| Size of the sub-problem | left: mid - lo = floor((n-1)/2);  right: hi - mid = floor(n/2).  Worst case (larger half): floor(n/2), i.e. n/b with b = 2 | mid is the centre of the range. |
| Work outside the recursive call | f(n) = 1 basic operation (one comparison key : A[mid]); computing mid and the range tests are O(1) | No loop is executed in one call. |
| Base cases | n = 0 (lo > hi): C(0) = 0 comparisons, returns -1.   n = 1: C(1) = 1 comparison | Empty range ends the recursion. |

Combining the components (counting comparisons in the worst case):

```text
C(n) = C( floor(n/2) ) + 1   for n >= 2,        C(1) = 1,   C(0) = 0
```

In terms of running time T(n) = T(n/2) + Theta(1), T(1) = Theta(1).

## Recurrence of the preprocessing step (merge sort)

MergeSort makes **two** recursive calls on halves of size n/2 and then performs a linear merge costing at most n - 1 comparisons:

```text
W(n) = 2 W(n/2) + (n - 1)   for n >= 2,        W(1) = 0
```

Because the sort is a part of the total cost of approach B, its recurrence is solved in Task 7 as well.


## Task 7 - Solving the Recurrence Relations

## 7.1  Binary search: C(n) = C(floor(n/2)) + 1,  C(1) = 1

**Method selection.** The recurrence has the standard divide-and-conquer form T(n) = a T(n/b) + f(n) with a = 1, b = 2, f(n) = 1, so both the *Master Theorem* and the *backward-substitution (iteration)* method apply. The iteration method is shown first because it exposes the structure; the Master Theorem confirms it; induction (substitution method) proves the exact floor/ceiling form.

### (a) Backward substitution, n = 2^k

```text
C(n) = C(n/2) + 1
     = [C(n/4) + 1] + 1 = C(n/4) + 2
     = C(n/8) + 3
     ...
     = C(n/2^i) + i
```

The recursion stops when n/2^i = 1, i.e. i = k = log2 n. Then C(n) = C(1) + log2 n = 1 + log2 n  (so C(n) in Theta(log n)).

### (b) Master Theorem

a = 1, b = 2, so n^(log_b a) = n^(log2 1) = n^0 = 1. Since f(n) = 1 = Theta(n^0) = Theta(n^(log_b a)), **Case 2** applies and T(n) = Theta(n^(log_b a) log n) = **Theta(log n)**.

### (c) Substitution (induction) for the exact worst case on any n

**Claim:** C(n) = floor(log2 n) + 1 for all n >= 1. *Base:* C(1) = 1 = floor(log2 1)+1. *Step:* assume it holds for all smaller values and let 2^k <= n < 2^(k+1), so floor(log2 n) = k. Then 2^(k-1) <= floor(n/2) < 2^k, hence floor(log2 floor(n/2)) = k-1, and

```text
C(n) = C(floor(n/2)) + 1 = (k - 1 + 1) + 1 = k + 1 = floor(log2 n) + 1.   QED
```

### (d) Verification against the experiment

**Table 7.1 - Prediction vs observation**

| n | floor(log2 n) + 1 (predicted worst) | Max comparisons observed |
|---|---|---|
| 1,000 | 10 | 10 |
| 10,000 | 14 | 14 |
| 100,000 | 17 | 17 |
| 1,000,000 | 20 | 20 |

**Interpretation.** The solution grows by one comparison every time n doubles. Going from 1,000 to 1,000,000 records (1,000 times more data) adds just 10 comparisons; the recursion depth never exceeds 20, so there is no risk of stack overflow, and the algorithm scales extremely well - but only for sorted data.

## 7.2  Merge sort (preprocessing): W(n) = 2W(n/2) + n - 1,  W(1) = 0

**Master Theorem:** a = 2, b = 2, f(n) = n - 1 = Theta(n) = Theta(n^(log2 2)). Case 2 gives **Theta(n log n)**. **Iteration (n = 2^k):**

```text
W(n) = 2W(n/2) + (n-1)
     = 4W(n/4) + (n-2) + (n-1)
     = 2^i W(n/2^i) + i*n - (2^i - 1)
     i = log2 n :  W(n) = n*0 + n log2 n - (n - 1) = n log2 n - n + 1
```

**Check:** substituting W(n) = n log2 n - n + 1 on the right-hand side gives 2[(n/2)(log2 n - 1) - n/2 + 1] + n - 1 = n log2 n - n + 1. The experiment sorted 1,000,000 random numbers with 18,674,355 comparisons, between the best case (n/2)log2 n = 9.97 x 10^6 and the worst case n log2 n - n + 1 = 18.93 x 10^6. Random data is close to, but slightly below, the worst case: the known average for random input is about n log2 n - 1.25 n = 18.68 x 10^6, which matches the measurement.

**Interpretation.** The sort needs about n log2 n comparisons - for a million records, about 19 million - which is why preprocessing dominates for a small number of queries and is negligible when q is large.
