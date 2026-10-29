# Task 6 - Recurrence Relation Formulation (3 marks)

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
