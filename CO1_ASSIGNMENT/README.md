# CO1 Assignment - Efficient Search Strategy for a Large-Scale Student Record System

**Course:** CSA06 Design and Analysis of Algorithms  |  **Student:** RITHIKA G  |  **Register No.:** 192571027

## 1. Project overview
A university stores student records identified by a unique registration number. The database grows from 1,000 to 1,000,000+ records and the system must decide whether a registration number exists and return its position. This project designs, analyses (mathematically), implements and experimentally compares **three different algorithmic strategies**, recommends one, and then re-evaluates the design for the **Day-4 challenge: 50,000 searches per hour on 1,000,000 records with new records added once per day**.

## 2. Algorithms implemented
| # | Algorithm | Paradigm | Style | Preprocessing | Search (worst / expected) |
|---|-----------|----------|-------|---------------|---------------------------|
| A | Linear search | Brute force | Iterative | none | Theta(n) |
| B | Binary search on sorted array | Decrease-and-conquer (sorting by divide-and-conquer merge sort) | **Recursive** | merge sort, Theta(n log n) | Theta(log n); recurrence C(n)=C(floor(n/2))+1 |
| C | Hash table, separate chaining | Hashing (space-time trade-off) | Iterative | build, Theta(n) | Theta(n) worst / Theta(1) expected |

## 3. Key results (n = 1,000,000, Python 3.12, one machine)
| | Linear | Sort + binary | Hash |
|---|---|---|---|
| Mean successful search | ~10.8 ms | ~3 us | ~0.5 us |
| Worst-case comparisons observed | 1,000,000 | 20 (= floor(log2 n)+1) | 5 (max chain) |
| Preprocessing | 0 | ~2.5 s (own merge sort) | ~1.1 s |
| One hour of traffic (50,000 searches) | ~12 min CPU (extrapolated) | ~0.2 s | ~0.1 s |

* **Task 11 recommendation:** sorted array + binary search (guaranteed worst case, small memory, ordered queries).
* **Task 12 decision: MODIFY** - keep the sorted master copy but serve exact-match lookups from a hash index extended/rebuilt in a nightly batch. See `Task_12_Design_Challenge/README.md`.

(Numbers vary with hardware; counts of basic operations and growth rates do not.)

## 4. How to run
Requirements: Python 3.9+; `matplotlib` and `Pillow` only for graphs/screenshots (`pip install matplotlib pillow`).
```bash
cd Task_8_Implementation_Testing/Source_Code
python test_algorithms.py       # 12 unit tests
python run_experiments.py       # benchmark 1K/10K/100K/1M  (~2-3 min)  -> ../../Task_9_Experimental_Performance/results.*
python run_experiments.py --quick   # sizes up to 100,000 only
python design_challenge.py      # Task 12 experiments               -> ../../Task_12_Design_Challenge/
python make_graphs.py           # figures -> ../../Report/Tables_and_Graphs/
python make_screenshots.py      # optional: rendered code/output images
```
Data are generated with fixed seeds (`data_gen.py`), so every run uses the same datasets.

## 5. Repository structure
```
CO1_Assignment/
|-- README.md
|-- Task_1_Algorithm_Design/            design, pseudocode, justification
|-- Task_2_Basic_Operation/
|-- Task_3_Mathematical_Complexity/
|-- Task_4_Case_Analysis/
|-- Task_5_Asymptotic_Analysis/
|-- Task_6_Recurrence_Formulation/
|-- Task_7_Recurrence_Solution/
|-- Task_8_Implementation_Testing/
|   `-- Source_Code/                    algorithms.py, data_gen.py, test_algorithms.py,
|                                       run_experiments.py, design_challenge.py, make_graphs.py, make_screenshots.py
|-- Task_9_Experimental_Performance/    results.csv, results.json (+ tables/graphs in README)
|-- Task_10_Theory_vs_Experiment/
|-- Task_11_Final_Recommendation/
|-- Task_12_Design_Challenge/           design_challenge_results.json
`-- Report/
    |-- Source_Code_Screenshots/
    |-- Output_Screenshots/
    |-- Analysis/                       theoretical_analysis.md, experimental_analysis.md
    |-- Tables_and_Graphs/              fig1 ... fig9 (.png)
    `-- Documentation/                  CO1_Assignment_Report.docx (+ .pdf)
```
Each `Task_*` folder contains a `README.md` with the full write-up of that task.

## 6. Notes on evidence
* Linear search for the one-hour Day-4 test was measured on 300 queries and extrapolated to 50,000 (stated in the report); binary and hash were run with all 50,000.
* The images in `Report/Output_Screenshots` and `Report/Source_Code_Screenshots` are rendered from the real console output and source files; replace them with screenshots from your own machine if your instructor requires native screenshots.
