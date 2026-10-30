# Pseudocode 4 - `closest_logins` (closest pair of login locations)

**Input:** `E[0..n-1]`, each `(x, y)` in km  
**Output:** `((i, j), d)` - indices `i < j` of the closest pair and their distance;
ties -> lexicographically smallest `(i, j)`; `n < 2` -> `(NONE, +infinity)`

## 4A. Corrected algorithm (brute force over all unordered pairs)

```
ALGORITHM ClosestLoginsCorrected(E[0..n-1])
    minDist <- +infinity                                      // D7: was 0
    pair    <- NONE
    for i <- 0 to n-2 do
        for j <- i+1 to n-1 do                                // D9: unordered pairs only (was j over 0..n-1)
            d <- sqrt( (E[i].x - E[j].x)^2 + (E[i].y - E[j].y)^2 )
            if d < minDist then                               // D8: '<' keeps the closest (was '>')
                minDist <- d
                pair    <- (i, j)
            end if
        end for
    end for
    return (pair, minDist)
```

* Distance computations (and square roots): exactly `n(n-1)/2` -> `Theta(n^2)` for every input.
  (The original evaluated `n^2`, including `n` self pairs and every pair twice.)

## 4B. Optimised algorithm (squared distances + sort-by-x sweep with pruning)

```
ALGORITHM ClosestLoginsOptimised(E[0..n-1])
    if n < 2 then return (NONE, +infinity)
    order <- indices 0..n-1 sorted by E[k].x                  // O(n log n)
    best  <- +infinity                                        // best SQUARED distance
    bestPair <- NONE
    for a <- 0 to n-2 do
        for b <- a+1 to n-1 do
            dx2 <- (X[b] - X[a])^2                            // X, Y = coordinates in sorted order
            if dx2 > best then break                          // PRUNE: every later point is even further in x
            d2 <- dx2 + (Y[b] - Y[a])^2                       // no square root
            cand <- (min(order[a], order[b]), max(order[a], order[b]))
            if d2 < best OR (d2 = best AND cand < bestPair) then   // keeps brute-force tie-break
                best <- d2 ; bestPair <- cand
            end if
        end for
    end for
    return (bestPair, sqrt(best))                             // ONE square root in total
```

* Correctness of the prune: for `b` beyond the break point `(X[b]-X[a])^2 > best`, so `d^2 > best` - the pair
  can neither beat nor tie the current best.  The test is strict `>` so tying pairs are still examined.
* Cost: `O(n log n)` for the sort + the number of unpruned pairs.  Worst case `Theta(n^2)` (all events share one x);
  on spread-out data the strip `|dx| <= sqrt(best)` holds only a handful of points, so the scan is near-linear.
* Square roots: `n(n-1)/2` -> `1`.
