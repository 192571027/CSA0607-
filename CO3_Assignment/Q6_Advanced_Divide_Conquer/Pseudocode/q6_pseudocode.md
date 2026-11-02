# Q6 Pseudocode

## A. Median of Medians (deterministic selection of k-th smallest)
```
SELECT(A, k):
    if |A| <= 5: sort and return A[k]
    split A into groups of 5; take the median of each group          // n/5 medians
    p = SELECT(medians, |medians|/2)                                 // median of medians = pivot
    L = {x < p}, E = {x == p}, G = {x > p}
    if k < |L|: return SELECT(L, k)
    if k < |L|+|E|: return p
    return SELECT(G, k - |L| - |E|)
```
**Why partitions are never terrible:** at least half of the n/5 medians are <= p, and each of those groups contributes
3 elements <= p => >= 3n/10 elements on each side, so the recursive call has <= 7n/10 + 6 elements.
**Recurrence:** T(n) <= T(n/5) + T(7n/10 + 6) + cn; since 1/5 + 7/10 = 9/10 < 1 => T(n) = O(n) worst case.
(QuickSelect: T(n) = T(n-1) + n = O(n^2) worst case; random pivot: expected O(n) but no guarantee.)
Verification (Student B): pivot quality controls how fast the problem shrinks - good pivots give geometric decrease
(O(n) total), bad pivots decrease by 1 per step (O(n^2) total).

## B. Meet-in-the-Middle Subset Sum
```
MITM(A, T):
    split A into halves H1 (n/2 items), H2 (n/2 items)               // DIVIDE the ITEMS
    S1 = all 2^(n/2) subset sums of H1;  S2 = all 2^(n/2) subset sums of H2
    sort S1 ascending, S2 ascending
    i = 0, j = |S2|-1
    while i < |S1| and j >= 0:                                       // COMBINE by two pointers
        s = S1[i] + S2[j]
        if s == T return YES; else if s < T: i++ else j--
    return NO
```
Brute force: 2^n subsets. MITM: O(2^(n/2) * n) time (sorting) and O(2^(n/2)) memory.
Trade-off: exponentially less time for exponentially more memory than brute force's O(n) memory
(n=40: 10^12 -> ~10^6 sums, ~16 MB). Verification (Student A): work is the sum of two small enumerations plus a
linear merge, instead of the product of both halves' choices; storage buys the ability to look up complements.
