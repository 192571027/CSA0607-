# CO2 – Debugging and Optimisation: SentinelOps SOC Alert-Triage Module

**Course:** CSA06 – Design and Analysis of Algorithms  **Assessment:** CO2 (50 marks)  
**Student:** `<Name / Reg. No.>`  **Repository:** `https://github.com/<your-username>/CO2_Debugging_Optimisation`

A junior developer's Python module sorts SOC alerts, checks a blocklist, scans logs for attack
signatures and finds the closest pair of login locations. It failed in production. This repository
contains the debugging (nine defects + one latent boundary defect), the optimisation, the analysis and the tests.

## Headline results

| Function | Defects | Optimisation | Measured effect |
|---|---|---|---|
| `sort_alerts` | D1 `j > 0`, D2 `alerts[j] = key` | insertion sort → stable Timsort | 10,000 random alerts: 22.4 M → 70,945 comparisons |
| `is_blocked` | D3 returns `False` on match, D4 premature `else: return False` | sequential search → hash-set index | b = 20,000, 2,000 queries: 30.1 M comparisons → 22,000 operations |
| `find_signature` | D5 `range(n - m)`, D6 `j == m - 1` | early-exit scan, first-char skip, guards (+ optional Horspool) | same comparison count as corrected; ≈ 3.7× faster; Horspool ≈ 4× fewer comparisons |
| `closest_logins` | D7 `min_dist = 0`, D8 `d > min_dist`, D9 inner loop over all `j` | squared distances, one `sqrt`, sort-by-x pruning | n = 8,000: 31,996,000 → 5,646 distance computations |

All 42 checks pass on the corrected and optimised modules (the original fails 32), plus a 3,000-trial differential test with 0 mismatches.

## Repository layout

```
CO2_Debugging_Optimisation/
├── Pseudocode/
│   ├── 01_sort_alerts.md          corrected + optimised pseudocode
│   ├── 02_is_blocked.md
│   ├── 03_find_signature.md
│   └── 04_closest_logins.md
├── Source_Code/
│   ├── original_sentinelops.py    verbatim original (nine defects) + run on test data
│   ├── corrected_sentinelops.py   minimal in-place fixes, each tagged D1..D9 / H1
│   ├── optimised_sentinelops.py   final production module (docstrings, comments)
│   ├── test_harness.py            42 checks x 3 modules + randomised differential test
│   ├── debug_session.py           applies the fixes one at a time and re-tests after each
│   ├── trace_demo.py              insertion trace, alignment table, pair table
│   └── experiments.py             part (d) measurements, graphs, CSV/JSON
├── Report/
│   ├── CO2_Report.pdf / .docx / .md   full report for parts (a)-(e)
│   ├── screenshots/               source-code and execution-output images
│   └── graphs/                    comparison graphs
├── Supporting_Files/
│   ├── test_data.json             course test data and expected outputs
│   ├── log_1 ... log_6 *.txt      execution logs (original, debug session, corrected, optimised, harness, traces)
│   ├── experiments_run.log, experiment_*.csv, experiment_results.json
│   └── make_screenshots.py        regenerates Report/screenshots
└── README.md
```

## How to run (Python 3.9+; the module itself uses only the standard library)

```bash
cd Source_Code
python original_sentinelops.py   # reproduce the failures
python debug_session.py          # one defect fixed at a time, re-tested after each fix
python corrected_sentinelops.py
python optimised_sentinelops.py
python test_harness.py           # exit code 0 = everything as expected
python trace_demo.py
pip install matplotlib pygments pillow    # only for the next two scripts
python experiments.py            # ~15 s; writes ../Supporting_Files and ../Report/graphs
```

## Notes

* Operation counts are exact and deterministic (fixed seed 2026); wall-clock timings depend on the machine.
* `find_signature_horspool` is an optional extension beyond the brute-force requirement; `find_signature` is the brute-force function.
* The 50,000-alert figures in the report are extrapolated from measured 10,000-alert runs.
