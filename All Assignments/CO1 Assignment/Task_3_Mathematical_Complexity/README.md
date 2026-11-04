# Task 3 - Mathematical Time-Complexity Derivation (6 marks)

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
