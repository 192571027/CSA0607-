# Q1 – Sorting Under Different Data Conditions: Pseudocode

Records are `(priority, order_id)`; sorting is on `priority` only.
`C` = comparisons counter, `M` = moves counter (swaps or shifts).

## 1. Selection Sort
```
SelectionSort(A[0..n-1])
    C ← 0 ; M ← 0
    for i ← 0 to n-2 do
        m ← i
        for j ← i+1 to n-1 do
            C ← C + 1
            if A[j].priority < A[m].priority then m ← j
        end for
        if m ≠ i then swap A[i], A[m] ; M ← M + 1
    end for
    return A, C, M
```

## 2. Bubble Sort (with early-exit flag)
```
BubbleSort(A[0..n-1])
    C ← 0 ; M ← 0
    for p ← 0 to n-2 do
        swapped ← false
        for j ← 0 to n-2-p do
            C ← C + 1
            if A[j].priority > A[j+1].priority then
                swap A[j], A[j+1] ; M ← M + 1 ; swapped ← true
        end for
        if swapped = false then break          // list is sorted
    end for
    return A, C, M
```

## 3. Insertion Sort
```
InsertionSort(A[0..n-1])
    C ← 0 ; M ← 0
    for i ← 1 to n-1 do
        v ← A[i] ; j ← i-1
        while j ≥ 0 do
            C ← C + 1
            if A[j].priority > v.priority then
                A[j+1] ← A[j] ; M ← M + 1 ; j ← j - 1
            else break
        end while
        A[j+1] ← v
    end for
    return A, C, M
```

## 4. Prediction procedure (written BEFORE running)
```
Predict(values[0..n-1])
    inv       ← number of pairs i<j with values[i] > values[j]
    maxLeft   ← max over positions of (number of larger elements to its left)
    z         ← number of positions i≥1 whose value is smaller than every earlier value
    Selection : comparisons = n(n-1)/2
    Bubble    : moves = inv ; passes = min(n-1, maxLeft+1) ;
                comparisons = Σ_{p=0}^{passes-1} (n-1-p)
    Insertion : moves = inv ; comparisons = inv + (n-1) - z
```

## 5. Experiment design
```
Datasets (n = 1000 unless stated):
  D0  random                      (baseline)
  D0b already sorted              (baseline)
  D1  95% sorted + 5% NEW orders appended      (contrasting dataset 1 – business scenario)
  D1b 95% in place, 5% displaced ≤ 5 places    (variation of D1)
  D2  strictly reverse sorted                  (contrasting dataset 2 – significantly disordered)
  D3  all priorities equal                     (EDGE CASE of my own)
  Extra: 5 distinct priority levels → stability test
for each dataset: run the three sorts, record C, M, time (best of 3)
compare to Predict(); verify output is sorted; check stability
Scaling: 95%-sorted scenario for n = 250, 500, 1000, 2000, 3000
```

## 6. Decision rule
```
if most data already ordered and new data is a small batch → InsertionSort
   (cost = (n-1) + inversions, ≈ n when almost nothing is out of place)
```
