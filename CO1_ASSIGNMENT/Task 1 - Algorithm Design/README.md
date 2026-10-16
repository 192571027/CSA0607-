# Task 1 - Algorithm Design 

The problem is **membership search with retrieval**: given a registration number (a 9-digit integer key) decide whether it exists among n student records and return its position. Three algorithms from three different design paradigms were selected. Iterative and recursive forms of the same idea are deliberately **not** counted as different approaches.

**Table 1.1 - The three approaches**

| # | Algorithm | Design strategy | Style | Preprocessing | Why it is investigated |
|---|---|---|---|---|---|
| A | Linear (sequential) search | Brute force | Iterative | None | Baseline. Works on the raw, unsorted table; the cost every smarter design must beat. |
| B | Binary search on a sorted array | Decrease-and-conquer (problem halves each step); preprocessing by divide-and-conquer (merge sort) | Recursive | Merge sort, O(n log n) | Exploits ordering of keys. Shows the trade-off 'pay once to sort, then search very cheaply'. |
| C | Hash table with separate chaining | Space-time trade-off (input enhancement by hashing) | Iterative (chain walk) | Build table, O(n) | Gives (expected) constant-time lookup; shows what extra memory can buy. |

## Approach A - Linear search (iterative, brute force)

**Idea.** Examine records one after another from the first position until the key is found or the table ends. No assumption about order is needed, therefore no preprocessing.

```text
ALGORITHM LinearSearch(A[0..n-1], key)
    for i <- 0 to n-1 do
        if A[i] = key then          // basic operation
            return i
    return -1                       // not found
```

**Justification.** It is the simplest correct method, it is the natural benchmark, and for tiny databases or one-off queries its zero preprocessing may actually be optimal.

## Approach B - Recursive binary search on a sorted array

**Idea.** If the registration numbers are kept in sorted order, compare the key with the middle element. Equality ends the search; otherwise the key can only lie in one half, so the other half is discarded and the same procedure is applied recursively to the remaining half. **Preprocessing:** the records must first be sorted; merge sort (divide-and-conquer, guaranteed O(n log n)) is used, and its cost is included in every analysis.

```text
ALGORITHM BinarySearch(A[lo..hi], key)          // A is sorted
    if lo > hi then return -1              // base case: empty range
    mid <- floor((lo + hi) / 2)
    if A[mid] = key then return mid        // basic operation: key vs A[mid]
    if key < A[mid] then
        return BinarySearch(A, key, lo, mid-1)    // recurse on left half
    else
        return BinarySearch(A, key, mid+1, hi)    // recurse on right half

ALGORITHM MergeSort(A[0..n-1])             // preprocessing
    if n <= 1 then return A
    L <- MergeSort(A[0..n/2-1]);  Rr <- MergeSort(A[n/2..n-1])
    return Merge(L, Rr)                    // linear merge of two sorted lists
```

**Justification.** It is the classic example of a recursive algorithm whose recurrence can be formulated and solved (Tasks 6-7), and it represents the 'sort once, search many times' strategy.

## Approach C - Hash table with separate chaining

**Idea.** A hash function h(key) maps a registration number directly to one of m buckets (m is a prime near n/0.75, so the load factor is alpha = n/m = 0.75). Every bucket holds a short chain of record indices. Searching computes h(key) and scans only that one chain. **Preprocessing:** every record is inserted once into its bucket. The hash function used is Knuth's multiplicative hash, h(k) = ((k x 2654435761) mod 2^32) mod m, which spreads even sequential registration numbers evenly.

```text
ALGORITHM BuildHash(A[0..n-1])                   // preprocessing
    m <- next_prime(n / 0.75);  T[0..m-1] <- empty
    for i <- 0 to n-1 do
        append i to chain T[ h(A[i]) ]

ALGORITHM HashSearch(T, A, key)
    chain <- T[ h(key) ]
    for each index idx in chain do
        if A[idx] = key then         // basic operation
            return idx
    return -1
```

**Justification.** It breaks the comparison-based lower bound of Omega(log n) for searching by using the key's *value* rather than only comparing keys, and it represents the memory-for-speed strategy.

> **Note:** Return value: all three algorithms return a position (index) for a found key and -1 otherwise. In a production system each slot would additionally hold a pointer to the full student record; this changes memory use by a constant factor only.
