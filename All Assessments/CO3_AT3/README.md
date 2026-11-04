# CO3_AT3 – Divide-and-Conquer Engine of KartIQ (CSA06 Case Study)

Course: CSA06 – Design and Analysis of Algorithms  |  Assessment: CO3 case study (individual)

| Student name | Reg. No. |
|---|---|
Rithika.G(192571027)

This repository analyses and redesigns four modules of the KartIQ retail analytics platform with divide-and-conquer algorithms, and covers all six parts (a)–(f) of the case study.

## Repository layout

```
CO3_AT3/
├── Module_1_Merge_Sort/                       Nightly order consolidation   (part b)
│   ├── Pseudocode/merge_sort_pseudocode.txt
│   ├── Source_Code/merge_sort.py
│   └── Report/Module_1_Merge_Sort_Report.md   (+ merge_sort_comparisons.png)
├── Module_2_Quick_Sort/                       Live seller leaderboard       (part c)
│   ├── Pseudocode/quick_sort_pseudocode.txt
│   ├── Source_Code/quick_sort.py
│   └── Report/Module_2_Quick_Sort_Report.md   (+ quick_sort_comparisons.png)
├── Module_3_Binary_Search/                    Order lookup                  (part d)
│   ├── Pseudocode/binary_search_pseudocode.txt
│   ├── Source_Code/binary_search.py
│   └── Report/Module_3_Binary_Search_Report.md (+ binary_search_comparisons.png)
├── Module_4_Strassen_Matrix_Multiplication/   Recommendation scores         (part e)
│   ├── Pseudocode/strassen_pseudocode.txt
│   ├── Source_Code/strassen.py
│   └── Report/Module_4_Strassen_Report.md     (+ strassen_comparison.png)
├── Final_Design_and_Analysis/
│   ├── Part_a_Case_Understanding.md           (part a)
│   └── Part_f_Final_Design.md                 (part f)
├── Supporting_Files/
│   ├── datasets/                              sample inputs from the brief
│   ├── outputs/                               saved console output of every program
│   └── screenshots/                           (add your own screenshots here – see below)
└── README.md
```

## How to run

Requires Python 3.8+ with `numpy` and `matplotlib` (`pip install numpy matplotlib`). Each program is self-contained and prints its traces, experiments and calculations; it also regenerates its graph into the module's `Report/` folder.

```bash
python3 Module_1_Merge_Sort/Source_Code/merge_sort.py
python3 Module_2_Quick_Sort/Source_Code/quick_sort.py
python3 Module_3_Binary_Search/Source_Code/binary_search.py
python3 Module_4_Strassen_Matrix_Multiplication/Source_Code/strassen.py
```

Run times are a few seconds each on a laptop. Timing results in Module 4 depend on the machine.

## Key results

| Module | Algorithm | Result |
|---|---|---|
| 1 | Stable Merge Sort | Sample sorted in 9 comparisons with ties kept in arrival order; T(n) = 2T(n/2) + n − 1 = n lg n − n + 1; worst case 223,222,785 comparisons for n = 10⁷; 160 MB data + 160 MB buffer; external k-way merge for larger data |
| 2 | Quick Sort, median-of-three | First-element pivot: n(n−1)/2 = 4,999,950,000 comparisons for n = 10⁵ nearly sorted; median-of-three ≈ 1,560,965 (≈ 3,200× fewer) |
| 3 | Binary Search (first occurrence) | T(n) = T(n/2) + 1 = ⌊lg n⌋ + 1 = 24 comparisons for n = 10⁷ (25 for the first-occurrence variant) |
| 4 | Hybrid Strassen | Sample C = [[50, 38], [38, 34]] with 7 products; n = 1,024: 282,475,249 vs 1,073,741,824 multiplications, but only 8.2 % fewer total operations; slower than BLAS in the single-core test |

## Screenshots

The brief asks for screenshots of source code and outputs. Run each program in your own terminal or IDE and save the screenshots into `Supporting_Files/screenshots/`; the text outputs in `Supporting_Files/outputs/` show what you should see.
