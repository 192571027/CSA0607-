# Q5 Pseudocode

## Brute force (CO2)
```
for i < j: d = dist(P[i], P[j]); keep the minimum        // n(n-1)/2 distance computations, O(n^2)
```
## Divide and Conquer
```
CLOSEST(P):                       // P pre-sorted by x once; recursion also returns points sorted by y
    if |P| <= 3: brute force; return (best, pair, P sorted by y)       // base case
    midx = x-coordinate of median point
    (dL, pairL, YL) = CLOSEST(left half)                                // DIVIDE by vertical line x = midx
    (dR, pairR, YR) = CLOSEST(right half)
    d = min(dL, dR)
    Y = MERGE(YL, YR)                                                   // sorted by y in O(n)
    strip = [p in Y : |p.x - midx| < d]                                 // only points within d of the line
    for each p in strip:
        compare p with following points q in strip while q.y - p.y < d  // at most ~7 candidates
    return (best, pair, Y)                                              // COMBINE
```
Each recursive call returns: the closest distance/pair in its half and its points sorted by y.

**Why the boundary needs special treatment:** the closest pair may have one point on each side of the dividing
line; neither recursive call sees it.
**Why the strip is cheap:** any pair with distance < d must lie within d of the line; in a d x 2d rectangle of the
strip at most 8 points can coexist with all pairwise distances >= d (4 per d x d square), so each point only needs its
next <= 7 neighbours in y-order.

**Recurrence:** T(n) = 2T(n/2) + O(n) (merge + strip scan) => O(n log n) (with x-sort done once).
