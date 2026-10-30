# Pseudocode 3 - `find_signature` (brute-force string matching, all occurrences)

**Input:** text `T[0..n-1]` (log line), pattern `P[0..m-1]` (signature)  
**Output:** every start index `i` with `T[i..i+m-1] = P` (overlaps included), increasing order

## 3A. Corrected algorithm

```
ALGORITHM FindSignatureCorrected(T[0..n-1], P[0..m-1])
    hits <- empty list
    if m = 0 then return hits                                 // H1: empty pattern matches nothing
    for i <- 0 to n - m do                                    // D5: n-m+1 windows (was n-m)
        j <- 0
        while j < m AND T[i+j] = P[j] do
            j <- j + 1
        end while
        if j = m then                                         // D6: full match <=> inner loop never stopped early
            append i to hits                                  //     (was 'j = m-1', also true on a last-char mismatch)
        end if
    end for
    return hits
```

* Window `i` costs `(length of matched prefix) + 1` comparisons, or `m` for a full match.
* Best `~n` comparisons (first char never matches), worst `~(n-m+1)*m` (e.g. `AAAA..A` vs `AA..AB`): `O(nm)`.
* If `m > n` the loop `0..n-m` is empty: result `[]`.

## 3B. Optimised algorithm (brute force without redundant work)

```
ALGORITHM FindSignatureOptimised(T[0..n-1], P[0..m-1])
    if m = 0 OR m > n then return []                          // O(1) guards, no scan
    hits  <- empty list
    first <- P[0]
    for i <- 0 to n - m do                                    // only windows that fit
        if T[i] != first then continue                        // 1 comparison, window dropped
        j <- 1                                                // P[0] already verified: never re-compared
        while j < m AND T[i+j] = P[j] do
            j <- j + 1
        end while
        if j = m then append i to hits
    end for
    return hits
```

### Optional extension - Horspool (skips alignments)

```
ALGORITHM FindSignatureHorspool(T[0..n-1], P[0..m-1])
    if m = 0 OR m > n then return []
    for each character c appearing in P[0..m-2] do
        shift[c] <- m - 1 - (last index of c in P[0..m-2])    // all other characters: shift = m
    i <- 0 ; hits <- empty list
    while i <= n - m do
        j <- m - 1
        while j >= 0 AND T[i+j] = P[j] do j <- j - 1          // compare right to left
        if j < 0 then append i to hits
        i <- i + shift[ T[i+m-1] ]                            // slide by the bad-character shift
    end while
    return hits
```

* Same output as 3A/3B, average about `n/m` comparisons; worst case still `O(nm)`.
