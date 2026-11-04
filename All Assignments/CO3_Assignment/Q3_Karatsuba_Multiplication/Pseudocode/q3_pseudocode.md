# Q3 Pseudocode

## Standard multiplication
```
SCHOOLBOOK(x, y):  for each digit y_j: for each digit x_i: res[i+j] += x_i * y_j (with carries)   // n^2 digit mults
```
## Karatsuba
```
KARATSUBA(x, y):
    n = max(digits(x), digits(y))
    if n == 1: return x * y                       // base case
    m = n / 2;  B = 10^m
    (a, b) = (x div B, x mod B)                   // x = a*B + b      DIVIDE
    (c, d) = (y div B, y mod B)                   // y = c*B + d
    z2 = KARATSUBA(a, c)
    z0 = KARATSUBA(b, d)
    z1 = KARATSUBA(a + b, c + d) - z2 - z0        // = ad + bc  (saves 1 of 4 multiplications)
    return z2 * B^2 + z1 * B + z0                 // COMBINE: shifts, additions/subtractions O(n)
```
**Why 3 not 4:** x*y = ac*B^2 + (ad+bc)*B + bd. Since (a+b)(c+d) = ac + ad + bc + bd, ad+bc is obtained
from one product minus ac and bd.

**Recurrence:** T(n) = 3T(n/2) + cn. Master theorem: a=3, b=2, log_b a = log2 3 ~ 1.585 > 1
=> T(n) = Theta(n^log2(3)) ~ Theta(n^1.585) vs Theta(n^2) for the standard method.
(Recursion tree: level i has 3^i subproblems of size n/2^i, level cost (3/2)^i * cn is geometric and
dominated by the leaves: 3^(log2 n) = n^log2 3.)

## Joint conclusion (why asymptotics are not everything)
Big-O hides constants and lower-order terms; Karatsuba adds additions, splitting, recursion/call overhead and
temporary numbers (a+b may have an extra digit). For small n the cheap n^2 loop wins; the crossover (here ~256-512
digits in pure Python, hybrid cutoff ~16 digits) depends on hardware, language and implementation.
