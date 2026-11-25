# CO5 Assignment 5 - Search, Complexity and Approximation Engineering

Backtracking, tractability and approximation algorithms.

**Student:** [Your name]  **Roll no.:** [Your roll number]

## Repository structure

```
CO5_Assignment_5/
├── Source_Code/
│   ├── Task_B1_Graph_Colouring/        graph_colouring.py   + output.txt
│   ├── Task_B2_Adversarial_Search/     adversarial_search.py + output.txt
│   ├── Task_B3_Exact_vs_Approximation/ exact_vs_approx.py    + output.txt
│   └── Task_B4_Bin_Packing/            bin_packing.py        + output.txt
├── Report/
│   ├── CO5_Assignment_5_Report.pdf     consolidated report (Part A + Part B)
│   └── build_report.py                 regenerates the PDF from the output.txt files
└── README.md
```

## Requirements

* Python 3.9+ (Task programs use the standard library only)
* For rebuilding the report only: `pip install reportlab matplotlib`

## How to run

```bash
cd Source_Code/Task_B1_Graph_Colouring        && python graph_colouring.py
cd Source_Code/Task_B2_Adversarial_Search     && python adversarial_search.py
cd Source_Code/Task_B3_Exact_vs_Approximation && python exact_vs_approx.py
cd Source_Code/Task_B4_Bin_Packing            && python bin_packing.py
```

Each program asserts its own correctness (valid colourings, equal minimax/alpha-beta values, valid vertex covers,
heuristic >= optimum >= lower bound) and prints a results table. Approximate run times: B1 about 10 s (the plain
backtracking baseline on a 40-vertex graph dominates), B2 about 2 s, B3 about 15 s, B4 about 5 s. All random
instances use fixed seeds, so node counts are reproducible; timings vary by machine.

## Summary of tasks

| Task | Problem | Methods | Key result |
|------|---------|---------|-----------|
| B1 | Graph colouring / chromatic number | Plain backtracking, MRV + forward checking + symmetry breaking, Welsh-Powell greedy | 3,726,540 vs 75 nodes on a 40-vertex graph, same chromatic number |
| B2 | Adversarial search | Minimax vs alpha-beta (+ move ordering), Tic-Tac-Toe and Connect-4 | 98.7% fewer nodes (TTT), 99.1% fewer (Connect-4, depth 6), identical values |
| B3 | Minimum vertex cover | Brute force, branch and bound, 2-approximation, greedy | Ratio never exceeds 2; bound is tight on K(6,6); B&B reached its limit near n = 50 |
| B4 | Bin packing | NF, FF, BF, FFD, BFD vs exact branch and bound | FFD/BFD mean 1.011 x optimum; 298 bins vs lower bound 294 at n = 1000 |

## Notes and limitations

* In B4, two instances (marked `*` in `output.txt`) hit the exact solver's 2,000,000-node cap, so the "optimum" shown
  there is the best packing found, not a proven optimum.
* The Connect-4 evaluation function is intentionally simple; B2 measures search efficiency, not playing strength.
