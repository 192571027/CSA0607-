# Q2 – Sequential Search: Pseudocode

## 1. Sequential search with comparison counter
```
SequentialSearch(R[0..n-1], key)        // R[i] = (ToolID, TechID, IssueTime, Bay)
    comps ← 0
    for i ← 0 to n-1 do
        comps ← comps + 1
        if R[i].ToolID = key then return (i, comps)
    end for
    return (-1, comps)                  // unsuccessful: exactly n comparisons
```

## 2. Predictions
```
successful search, key at position p (1-based) : p comparisons
best 1 ; worst n ; average over all keys (n+1)/2 ; unsuccessful n
expected cost when a fraction s of requests succeed : s(n+1)/2 + (1-s)n
```

## 3. Experiment design
```
Experiment 1: n ∈ {100, 1000, 10000, 100000}
    targets: first, 25%, middle, 75%, last, absent key, average over all keys
Experiment 2: expected comparisons for success rates s = 100%, 90%, 50%, 10%
Experiment 3: measure machine speed r (comparisons/second) with full scans
Criteria  C1: one worst-case lookup ≤ 50 ms           → n ≤ 0.05·r
          C2: q lookups/s use ≤ 10% of a core          → q·(n/2) ≤ 0.10·r
Boundary table: utilisation = 100·q·(n/2)/r  for grid of n and q
```

## 4. Changed-condition simulation (1 hangar → 20 facilities)
```
Simulate(n_steady, n_ops)
    L ← list of n_steady issued tools ; H ← hash table of the same tools
    for each of n_ops operations (40% lookup, 30% issue, 30% return)
        lookup : seqCost += position of tool in L   (+1) ; hashCost += 1
        issue  : append to L ; insert into H
        return : seqCost += position of tool in L (+1) ; remove from L ; remove from H ; hashCost += 1
    return seqCost, hashCost
Compare (n=500, 5,000 ops) with (n=10,000, 100,000 ops)
```

## 5. Decision rule
```
if q·n/2 ≤ budget (10% of one core) and single-lookup latency ≤ 50 ms → keep sequential search
else → index the records by ToolID (hash table: O(1) lookup, issue, return)
alternative: keep one small list per facility (partitioning keeps n and q per list unchanged)
```
