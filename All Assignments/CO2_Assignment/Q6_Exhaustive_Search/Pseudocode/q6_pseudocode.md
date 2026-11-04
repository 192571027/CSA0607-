# Q6 – Exhaustive Search (Humanitarian Airlift): Pseudocode

## 1. Representation and algorithm
```
Candidate = n-bit mask ; bit k = 1 ⇔ package k is loaded ; 2ⁿ candidates

ExhaustiveSearch(weight[0..n-1], value[0..n-1], LIMIT)
    bestValue ← 0 ; bestMask ← 0 ; examined ← 0 ; feasible ← 0
    for mask ← 0 to 2ⁿ - 1 do                       // GENERATE every subset exactly once
        examined ← examined + 1
        w ← 0 ; v ← 0
        for k ← 0 to n-1 do                         // EVALUATE weight and value
            if bit k of mask = 1 then w ← w + weight[k] ; v ← v + value[k]
        end for
        if w ≤ LIMIT then                           // FEASIBILITY check
            feasible ← feasible + 1
            if v > bestValue then bestValue ← v ; bestMask ← mask    // RETAIN best
    end for
    return bestValue, bestMask, examined, feasible
```

## 2. Predictions
```
candidates = 2ⁿ (each package: in/out) ; +1 package doubles, +10 packages ×1024
item checks = n·2ⁿ ; time ≈ c·n·2ⁿ  (+2 packages → ≈ ×4.4)
```

## 3. Verification and experiments
```
Correctness: 5 packages → list all 32 subsets by hand-checkable table → optimum
             200 random instances (n ≤ 12) compared with a dynamic-programming reference
Growth     : n = 8,10,12,…,22 ; payload = ½ total weight ; record 2ⁿ, feasible, checks, time
Deployment : response limit 10 s ; n_max = largest n with c·n·2ⁿ ≤ 10 s
```
