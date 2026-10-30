# Pseudocode 1 - `sort_alerts` (sort by severity, highest first, stable)

**Input:** `A[0..n-1]`, each element `(id, severity)`  
**Output:** `A` rearranged so severity is non-increasing; equal severities keep arrival order

## 1A. Corrected algorithm (insertion sort - brute-force / decrease-by-one)

```
ALGORITHM SortAlertsCorrected(A[0..n-1])
    for i <- 1 to n-1 do
        key <- A[i]
        j   <- i - 1
        while j >= 0 AND A[j].severity < key.severity do      // D1: j >= 0, not j > 0
            A[j+1] <- A[j]                                    // shift the weaker alert right
            j <- j - 1
        end while
        A[j+1] <- key                                         // D2: gap is at j+1, not j
    end for
    return A
```

* Loop invariant: before iteration `i`, `A[0..i-1]` holds the first `i` alerts in sorted order.
* Stability: elements move only while **strictly** smaller (`<`), so an equal-severity alert is never jumped.
* Comparisons: best (already ordered) `n-1`; worst (reverse) `n(n-1)/2`; in general `I + (n-1) - r`
  (`I` = inversions, `r` = insertions that reach the front).  Time `O(n + I)`, `O(n^2)` worst.

## 1B. Optimised algorithm (adaptive, stable merge-based sort = Timsort)

```
ALGORITHM SortAlertsOptimised(A[0..n-1])
    // Timsort: find natural runs, extend short runs by binary insertion sort,
    // merge runs under stack invariants; merges take the LEFT element on ties => stable.
    SortStableDescendingBy(A, key = severity)                 // reverse order keeps ties in arrival order
    return A
```

* Already / nearly sorted input -> long natural runs -> about `n` comparisons, `O(n)`.
* Worst case `O(n log n)` comparisons; extra space `O(n)` (versus `O(1)` for insertion sort).
* Output identical to 1A for every input (checked by the differential test).
