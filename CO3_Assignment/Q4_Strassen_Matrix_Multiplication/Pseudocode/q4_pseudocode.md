# Q4 Pseudocode

## Conventional block multiplication (8 block products)
Split A, B into four n/2 x n/2 blocks:
C11 = A11B11 + A12B21;  C12 = A11B12 + A12B22;  C21 = A21B11 + A22B21;  C22 = A21B12 + A22B22
T(n) = 8T(n/2) + O(n^2) => Theta(n^3).

## Strassen (7 block products)
```
STRASSEN(A, B):
    if n <= cutoff: return CONVENTIONAL(A, B)
    split into A11..A22, B11..B22                              // DIVIDE
    M1 = STRASSEN(A11 + A22, B11 + B22)
    M2 = STRASSEN(A21 + A22, B11)
    M3 = STRASSEN(A11,       B12 - B22)
    M4 = STRASSEN(A22,       B21 - B11)
    M5 = STRASSEN(A11 + A12, B22)
    M6 = STRASSEN(A21 - A11, B11 + B12)
    M7 = STRASSEN(A12 - A22, B21 + B22)
    C11 = M1 + M4 - M5 + M7;  C12 = M3 + M5                    // COMBINE: 18 block additions/subtractions in total
    C21 = M2 + M4;            C22 = M1 - M2 + M3 + M6
```
**Correctness check (example C12):** M3 + M5 = A11(B12 - B22) + (A11 + A12)B22 = A11B12 + A12B22 ✔.
C22: M1 - M2 + M3 + M6 = (A11+A22)(B11+B22) - (A21+A22)B11 + A11(B12-B22) + (A21-A11)(B11+B12) = A21B12 + A22B22 ✔
(expand and cancel; verified numerically by the program on integer matrices).

**Recurrence:** T(n) = 7T(n/2) + cn^2 => Theta(n^log2 7) ~ Theta(n^2.807). Multiplications = 7^k for n = 2^k.

**Padding:** if n is not a power of two, pad A and B with zero rows/columns up to m = 2^ceil(log2 n), multiply, crop the
top-left n x n of the result. Cost: up to ~4x more cells (e.g. n=129 -> 256).

## Joint engineering decision
Use conventional (BLAS-tuned) multiplication for small/medium matrices, non-power-of-two sizes, when numerical stability
or cache behaviour matters, memory is tight, or sparsity/structure can be exploited; Strassen only for very large dense
matrices with a tuned cutoff.
