# CO1_AT1 – Scalability Audit of "ShopSphere"

**Course:** CSA06 – Design and Analysis of Algorithms
**Assessment:** CO1 – Assessment Tool 1 (IT Application-Based Problem Solving)
**Student Name / Reg. No.:** RITHIKA.G 192571027______________________

## Problem
Audit five back-end modules of the ShopSphere e-commerce platform (duplicate detector M1, API rate limiter M2,
product search S1/S2, recommendation engine M4, sales analytics M5) for a catalogue growing from
n = 100,000 to n = 1,000,000 products, assuming 10^8 basic operations/second and a 10-minute nightly window.

## Repository structure
```

 CO1_AT1/
   ├── Source_Code.py/         
   ├── Report/             
   └── README.md
```

## How to run
```bash
cd Question_1/Source_Code
python shopsphere_audit.py          # Python 3.8+, standard library only
pip install matplotlib              # optional: only needed to regenerate growth_chart.png
```
The program executes every module, counts basic operations, compares them with the closed forms derived in the
report, and prints the scalability table for n = 1,000,000.

## Key results
| Module | Exact count / solution | Time | Space |
|---|---|---|---|
| M1 duplicate detector | n(n-1)/2 | Θ(n²) | Θ(1) |
| M2 rate limiter | 2^⌈log₂n⌉ − 1 (1023 for n = 1024) | Θ(n) – the Θ(n log n) claim is wrong | Θ(1) |
| S1 sequential search | avg = p(n+1)/2 + (1-p)n = 750,000.25 (n = 10⁶, p = 0.5) | Θ(n) | Θ(1) |
| S2 binary search | T(n) = 1 + log₂n | Θ(log n) | iterative Θ(1), recursive Θ(log n) |
| M4 current / redesign | 2n² − n / n(log₂n + 1) | Θ(n²) / Θ(n log n) | – |
| M5 sales analytics | n + n·L(L+1)/2 (extended Master Theorem, k = 1) | Θ(n log² n) | – |
| Report generator f(n) | 3n² + 10n log₂n + 50 (c₁ = 3, c₂ = 63, n₀ = 1) | Θ(n²), not O(n) | – |

**Fail the 10-minute window at n = 10⁶:** M1 (83 min), M4 current (5.6 h), report generator (8.3 h) →
redesign with hashing / sorting (M1) and the non-replicated divide-and-conquer design (M4).
