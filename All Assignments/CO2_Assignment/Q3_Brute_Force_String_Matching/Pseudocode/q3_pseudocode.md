# Q3 – Brute-Force String Matching: Pseudocode

## 1. Algorithm (counts character comparisons)
```
BruteForceMatch(T[0..n-1], P[0..m-1])
    comps ← 0 ; hits ← empty list
    for i ← 0 to n-m do                // n-m+1 alignments
        j ← 0
        while j < m do
            comps ← comps + 1
            if T[i+j] ≠ P[j] then break
            j ← j + 1
        end while
        if j = m then append i to hits
    end for
    return hits, comps
```

## 2. Predictions made before executing the tests
```
Work for alignment i = (length of matched prefix at i) + 1   (≤ m)

T1  text aaaa…a (n), pattern "Xerror!!"   first character never matches
        comps = n-m+1
T2  text AAAA…A (n), pattern AAAAAAAB      m-1 matches then one mismatch, every alignment
        comps = (n-m+1)·m
T3  realistic log text, pattern "password"
        E = 1 + f(p0) + f(p0)f(p1) + … (m terms) , f(c) = relative frequency of c in text
        comps ≈ (n-m+1)·E
T4  pattern = first m characters of text, stop at first match
        comps = m
Scaling: worst case grows like n·m ; best case like n ; alphabet size k: E → 1 + 1/k + …
```

## 3. Experiment design
```
for each test: print prediction → run algorithm → print observed, ratio, matches
verify matches against Python str.startswith scan
Extra A: random texts over alphabets of size 2,4,8,26,62 (m = 8)
Extra B: engineered case for n ∈ {1000…16000}, m ∈ {4,8,16}, compare with random text
```
