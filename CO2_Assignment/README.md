# CO2 Assignment – Brute-Force and Exhaustive-Search Techniques
**Course:** CSA06 Design and Analysis of Algorithms  **Student:** Rithika G  **Language:** Python 3.12

All seven questions (Q1–Q6 and the Day-4 Design Challenge Q7) are implemented, tested, measured and documented.
Operation counts (comparisons, moves, pairs, distance calculations, side tests, candidates) are the primary evidence; execution time is supporting evidence only.

## Repository structure
```
CO2_Assignment/
├── Q1_Sorting_Algorithms/            Selection / Bubble / Insertion under different data conditions
├── Q2_Sequential_Search/             comparison counts, operating boundary, 1 → 20 facilities
├── Q3_Brute_Force_String_Matching/   best-like, engineered and realistic cases, alphabet effect
├── Q4_Brute_Force_Closest_Pair/      C(n,2) derivation, growth, 1-second scalability limit
├── Q5_Brute_Force_Convex_Hull/       half-plane decision rule, tests, visualisation, correctness argument
├── Q6_Exhaustive_Search/             subset enumeration, 2^n growth, deployment boundary
├── Q7_Day4_Design_Challenge/         diagnose → redesign (sorted sweep + grid) → validate
│   (each folder:  Pseudocode/  Implementation_Code/  Output_Screenshots/ [+ raw_data/ graphs])
├── Final_Report/CO2_Assignment_Report.docx      full report (all answers, tables, graphs, analysis)
├── tools/render_screenshot.py        turns console output into terminal-style PNG screenshots
├── run_all.py                        runs every program, stores output text + screenshots
└── README.md
```

## How to run
```bash
pip install matplotlib pillow python-docx
python run_all.py                       # runs Q1–Q7, writes console output, CSV data, graphs, screenshots
python Final_Report/build_report.py     # rebuilds the Word report from the generated data
# or run a single question:
cd Q4_Brute_Force_Closest_Pair/Implementation_Code && python q4_closest_pair.py
```
Run time ≈ 1–2 minutes (Q6 exhaustive search at n = 22 takes ≈ 8 s; Q7 ≈ 20 s). All datasets use fixed seeds, so every operation count is reproducible; times vary by machine.

## Where to find each deliverable
| Required item | Location |
|---|---|
| Pseudocode (Q1–Q7) | `Qx_*/Pseudocode/qx_pseudocode.md` |
| Source code (Q1–Q7) | `Qx_*/Implementation_Code/*.py` |
| Execution screenshots | `Qx_*/Output_Screenshots/Qx_execution_screenshot_p*.png` (+ `Qx_console_output.txt`) |
| Raw experimental data | `Qx_*/Output_Screenshots/raw_data/*.csv` |
| Graphs / visualisations | `Qx_*/Output_Screenshots/*_graph_*.png`, `q5_hull_visualisation.png` |
| Full report | `Final_Report/CO2_Assignment_Report.docx` |

## Key results (details and evidence in the report)
| Q | Result |
|---|---|
| Q1 | All 18 comparison predictions matched exactly. For the 95%-ordered scenario Insertion Sort needs ≈20× fewer comparisons than Selection/Bubble; Bubble needs 984 passes because appended small elements move left one place per pass. **Recommendation: Insertion Sort.** |
| Q2 | Successful search = position, unsuccessful = n; cost ∝ q·n. 1 hangar → 20 facilities multiplies sequential cost ×396 vs ×20 for a hash index. |
| Q3 | Same n = 10,000, m = 8: 9,993 vs 79,944 comparisons depending only on text/pattern structure. |
| Q4 | Pairs = n(n−1)/2 exactly; time exponent ≈ 2.0; 1-second limit ≈ 4,300 drones. |
| Q5 | Edge test from half-plane geometry; full version = n(n−1)(n−2)/2 tests; early-exit prediction (≈ n²) was NOT supported until scan order was randomised. |
| Q6 | 2^n candidates; +2 packages ≈ ×4 time; 22 packages ≈ 7.7 s; deploy for ≤ 21 packages (10 s limit). |
| Q7 | Closest-pair redesign (sorted sweep with pruning): 99.84% fewer distance calculations at n = 2000, ≈300× faster at n = 4000, near-linear growth; fails on adversarial two-line layouts (grid extension handles them). |


