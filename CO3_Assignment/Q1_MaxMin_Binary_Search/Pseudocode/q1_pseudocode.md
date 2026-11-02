# Q1 Pseudocode

## Part A - Max/Min (Divide and Conquer)
```
MAXMIN(A, lo, hi):               // returns (min, max) of A[lo..hi]
    if lo == hi:      return (A[lo], A[lo])                  // base: 0 comparisons
    if hi == lo + 1:  // base: 1 comparison
        if A[lo] < A[hi] return (A[lo], A[hi]) else return (A[hi], A[lo])
    mid = (lo + hi) / 2
    (min1, max1) = MAXMIN(A, lo, mid)            // DIVIDE into two halves
    (min2, max2) = MAXMIN(A, mid+1, hi)
    return (smaller(min1,min2), larger(max1,max2))   // COMBINE: 2 comparisons
```
**Decomposition:** n -> n/2 + n/2 (tournament tree; each subproblem returns a (min,max) pair).

**Recurrence:** T(n) = 2T(n/2) + 2, T(2) = 1, T(1) = 0
Solving for n = 2^k: T(n) = 3n/2 - 2 (unroll: T(n)=2^(k-1)*1 + 2(2^(k-1)-1) = n/2 + n - 2).
Independent scans: 2(n-1) comparisons. Saving ~ 25% for large n.

**Note for Student B (discrepancy):** for n that is not a power of two, the uneven halves create extra
size-3/size-5 subproblems whose combine step costs 2, so the observed count exceeds ceil(3n/2)-2
(e.g. n=100 -> 162 vs 148, n=10000 -> 15902 vs 14998). The bound ceil(3n/2)-2 is achievable for all n by
pairing elements first (n/2 pair comparisons, then max among larger ones and min among smaller ones).

## Part B - Binary Search
```
BINARY_SEARCH(A, target):        // A sorted ascending
    lo = 0; hi = n-1
    while lo <= hi:
        mid = (lo + hi) / 2
        if A[mid] == target: return mid
        else if A[mid] < target: lo = mid + 1     // discard A[lo..mid]: all <= A[mid] < target
        else:                    hi = mid - 1     // discard A[mid..hi]: all >= A[mid] > target
    return NOT_FOUND                               // search space empty
```
**Recurrence:** T(n) = T(n/2) + 1, T(1) = 1  =>  T(n) = floor(log2 n) + 1 = O(log n).
Termination: the interval length strictly decreases at least by half each iteration and reaches 0.
