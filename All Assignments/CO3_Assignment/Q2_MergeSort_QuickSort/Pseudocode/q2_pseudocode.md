# Q2 Pseudocode

## Merge Sort
```
MERGE_SORT(A):
    if |A| <= 1 return A
    mid = |A| / 2
    L = MERGE_SORT(A[0..mid-1]);  R = MERGE_SORT(A[mid..end])    // DIVIDE: always balanced
    return MERGE(L, R)                                           // COMBINE: <= n-1 comparisons
```
T(n) = 2T(n/2) + n - 1  =>  Theta(n log n) for EVERY input. Recursion depth = ceil(log2 n) + 1.

## Quick Sort (stated pivot strategy: last element; out-of-place partition)
```
QUICK_SORT(A):
    if |A| <= 1 return A
    p = A[last]
    L = [x in A[0..last-1] : x <  p]
    R = [x in A[0..last-1] : x >= p]                   // DIVIDE (n-1 comparisons) - sizes depend on data
    return QUICK_SORT(L) + [p] + QUICK_SORT(R)         // COMBINE: concatenation, no work
```
Balanced split: T(n) = 2T(n/2) + n  => O(n log n), depth ~ log2 n.
Worst split (n-1 : 0): T(n) = T(n-1) + n - 1 => n(n-1)/2 = O(n^2), depth n.
Split ratio r : (1-r) always: depth = log(n) / log(1/r), still O(n log n) for any constant r.

Input construction (Student A):
* balanced: place the median LAST, then recursively arrange each half before it (function `balanced_input`)
* severely unbalanced: already sorted (or reverse sorted) data -> pivot is always the min/max
* 90:10: `skewed(values, 0.9)`

## Joint design question - information to collect before choosing
Input size, degree of presortedness / duplicates, whether adversarial input is possible, stability requirement,
memory limits (merge needs O(n) extra, in-place quick sort O(log n) stack), data type (comparison cost, linked
list vs array), need for worst-case guarantees (real-time), cache behaviour, parallelism.
