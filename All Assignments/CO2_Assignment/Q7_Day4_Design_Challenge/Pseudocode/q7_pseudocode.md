# Q7 – Design Challenge: Closest-Pair Redesign – Pseudocode / Design Representation

Selected solution: **Q4 Brute-Force Closest Pair** (n(n−1)/2 distance calculations).

## A. Diagnosis (summary of evidence)
```
100% of work = pair loop ; distance evaluations grow as n(n−1)/2
the best distance improved only 8–19 times out of 0.1M–8M evaluations
>99.7% of pairs already differ by ≥ d_min in x alone  → provably irrelevant, yet evaluated
cause: pair set is fixed by n, independent of where the drones are; the current best is never used to discard pairs
```

## B. Design objective
```
O1 exact answer  O2 ≥99% fewer distance calculations at n=2000
O3 growth exponent < 1.5  O4 ≥10× faster at n=4000  O5 degenerate inputs handled
```

## C. Redesign R1 – Sorted sweep with pruning (property exploited: ordering along one axis)
```
SweepClosestPair(D[0..n-1])
    // preprocessing  – O(n) extra memory, n·log n comparisons
    ax ← axis (x or y) with the larger spread  max − min
    S  ← D sorted by coordinate ax
    best ← ∞
    for i ← 0 to n-2 do
        for j ← i+1 to n-1 do
            gap ← S[j].ax − S[i].ax                 // ≥ 0 because S is sorted
            if gap² ≥ best then break               // every later drone is even farther along ax
            d ← squared distance(S[i], S[j])
            if d < best then best ← d ; (bi,bj) ← (S[i], S[j])
        end for
    end for
    return best
```
Why it is exact: if gap² ≥ best, then dist² ≥ gap² ≥ best for this and all later j, so none can improve `best`.

## C'. Extension R2 – Grid (spatial bucketing) (property exploited: locality)
```
GridClosestPair(D)
    side ← sqrt(area / n)                            // ≈ one drone per cell
    insert each drone index into hash map cell(x/side, y/side)
    best ← min distance² over consecutive pairs D[i], D[i+1]        // cheap upper bound
    for each drone i
        r ← ceil( sqrt(best) / side )
        for every cell within r cells of cell(i):  compare i with drones j>i in that cell
            update best
    return best
```

## D. Predictions (made before running – see report)
```
P1 uniform: ~10–30 distance calcs per drone (≈20k–60k at n=2000)   P2 sort dominates total ops
P3 time at n=4000 20–50× faster   P4 clustered data: smaller benefit
P5 fixed x-axis on a vertical corridor stays ≈ n²; widest-axis fixes it
P6 grid great on uniform, degrades on clustered   P7 brute force wins for very small n
```

## E. Validation procedure
```
datasets: U uniform (same generator and seeds as Q4), C clustered, V vertical corridor
for each: run Brute, R1 (counted), R1 (timed), R2 ; assert identical minimum distance
record: sort comparisons, gap checks, distance calculations, cell lookups, time
extra: edge cases (2 points, duplicates, identical x) and small-n crossover timing
```
