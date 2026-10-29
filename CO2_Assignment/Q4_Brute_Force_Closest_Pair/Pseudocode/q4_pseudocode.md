# Q4 – Brute-Force Closest Pair: Pseudocode

## 1. Algorithm
```
BruteForceClosestPair(D[0..n-1])           // D[i] = (x_i, y_i)
    best ← ∞ ; pairs ← 0 ; calcs ← 0
    for i ← 0 to n-2 do
        for j ← i+1 to n-1 do              // j > i : each unordered pair exactly once
            pairs ← pairs + 1
            d ← (x_i - x_j)² + (y_i - y_j)²    // squared distance, no square root needed
            calcs ← calcs + 1
            if d < best then best ← d ; (bi, bj) ← (i, j)
        end for
    end for
    return (bi, bj, √best, pairs, calcs)
```

## 2. Derivation of the number of candidate pairs
```
pairs = Σ_{i=0}^{n-2} (n-1-i) = (n-1)+(n-2)+…+1 = n(n-1)/2 = C(n,2)
ordered pairs (i≠j) would be n(n-1): every pair twice.  Growth Θ(n²).
```

## 3. Predictions
```
pairs examined = distance calculations = n(n-1)/2 for every input
time ≈ c·n² ; doubling n multiplies time by ≈ 4
```

## 4. Experiment & scalability procedure
```
for n in {100, 250, 500, 1000, 2000, 4000, 8000}
    generate n uniform random points in 10,000 × 10,000 ; run ; record pairs, calcs, time
fit t = c·n² (least squares) ; log-log slope
acceptable response time T_acc = 1.0 s   (one position-report interval)
n_max ← sqrt(T_acc / c)
```
