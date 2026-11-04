# Task 7 - Solving the Recurrence Relations (4 marks)

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
