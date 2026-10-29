# Q5 – Brute-Force Convex Hull: Pseudocode (derived from the geometric principle)

## 1. From geometry to computation
```
Line through Pi=(x1,y1), Pj=(x2,y2):  a·x + b·y = c
    a = y2 - y1 ,  b = x1 - x2 ,  c = x1·y2 - y1·x2
Side of a third point Pk=(x,y):  s = a·x + b·y - c      (= cross product (Pj-Pi)×(Pk-Pi))
    s > 0 : left of Pi→Pj      s < 0 : right      s = 0 : on the line
Edge rule: PiPj is a hull edge  ⇔  all non-zero s share one sign
           AND every point with s = 0 lies within segment PiPj
```

## 2. Algorithm
```
BruteForceHull(P)
    P ← distinct points of P, sorted ; n ← |P| ; tests ← 0
    if n ≤ 2 then return P
    succ ← empty map
    for i ← 0 to n-2 do
        for j ← i+1 to n-1 do
            pos ← false ; neg ← false ; ok ← true
            for k ← 0 to n-1, k ≠ i, k ≠ j do
                s ← Side(Pi, Pj, Pk) ; tests ← tests + 1
                if s > 0 then pos ← true
                else if s < 0 then neg ← true
                else if Pk not inside segment PiPj then ok ← false ; break
                if pos and neg then ok ← false ; break        // early exit
            end for
            if ok then
                if pos then succ[i] ← j              // whole set on the left: counter-clockwise edge
                else if neg then succ[j] ← i
                else succ[i] ← j ; succ[j] ← i       // every point collinear
        end for
    end for
    start ← smallest key of succ ; hull ← [P[start]] ; cur ← succ[start]
    while cur ≠ start do append P[cur] to hull ; cur ← succ[cur]
    return hull, tests
```

## 3. Predicted work
```
without early exit : C(n,2)·(n-2) = n(n-1)(n-2)/2 side tests  → Θ(n³)
with early exit    : lower constant; predicted ≈ n² growth for random points (to be tested)
```

## 4. Tests
```
T1 6 boundary + 14 interior stations
T2 square with collinear points on its edges, duplicates, interior diagonal points
T3 all points collinear (degenerate)
T4 16 points on a circle (every point on the hull – worst case for early exit)
Randomised: 300 sets on a 13×13 grid, compare with an independent hull (monotone chain)
Growth: random sets n = 10…320 ; sorted scan vs random scan ; circle family
```
