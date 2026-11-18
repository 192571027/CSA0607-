# CSA06 – Design and Analysis of Algorithms
## Assignment 4 – Part I (CO4A): Algorithmic Design Through Pseudocode

**Name:** Rithika G
**Department:** Computer Science and Engineering
**Course Outcome:** CO4 – Solve optimization problems using Dynamic Programming and Greedy strategies

This repository holds the **language-independent pseudocode** for all six tasks of the assignment.
No programming language is used, as required by the assignment. The full reasoning, traces and
adversarial tests are in the submitted report.

## Repository structure

| File | Task | Technique |
| --- | --- | --- |
| `pseudocode/task1_fractional_load_vehicle.txt` | Task 1 | Greedy – fractional loading (value/weight ratio) |
| `pseudocode/task2_job_sequencing.txt` | Task 2 | Greedy – job sequencing with deadlines |
| `pseudocode/task3_knapsack_01_dp.txt` | Task 3 | Dynamic programming – 0/1 knapsack with reconstruction |
| `pseudocode/task4_wordbreak_repaired.txt` | Task 4 | Debugging – WordBreak (faulty vs repaired condition) |
| `pseudocode/task5_shortest_paths.txt` | Task 5 | Greedy shortest path, Bellman-Ford, Floyd |
| `pseudocode/task6_energy_aware_scheduling.txt` | Task 6 | Dynamic programming – weighted interval scheduling |

## Key results (hand-traced)

| Task | Result |
| --- | --- |
| 1 | Sort by value/weight ratio; load whole packages, then a fraction of the last one |
| 2 | Jobs A–E: schedule C, A, D, total profit 180. With B's profit changed to 70: B, A, D, profit 190 |
| 3 | Capacity 7: select items Q and R, value 45 |
| 4 | Faulty algorithm fails on Text = "catxdog", Dictionary = {cat, dog} at DP[7]; fix adds `DP[j] = TRUE` |
| 5 | Distances from A: B = 4, C = 6, D = 7, E = 10 (path A-B-C-D-E) |
| 6 | Select J2, J5, J7, J8; total energy-saving value 200 |

## Notation

`←` assignment, `∞` infinity, arrays are 1-indexed, `substring(Text, j, i)` = characters j+1 … i.

## How to publish this repository on GitHub

```bash
cd CSA06-CO4A-Pseudocode
git init
git add .
git commit -m "Add CSA06 Assignment 4A pseudocode"
git branch -M main
git remote add origin https://github.com/<your-username>/CSA06-CO4A-Pseudocode.git
git push -u origin main
```
