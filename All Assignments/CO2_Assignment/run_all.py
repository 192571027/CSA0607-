"""Run every implementation, save the console output, and render screenshots.
Usage:  python run_all.py          (needs: python3, matplotlib, pillow)
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
JOBS = [
    ("Q1_Sorting_Algorithms", "q1_sorting.py"),
    ("Q2_Sequential_Search", "q2_sequential_search.py"),
    ("Q3_Brute_Force_String_Matching", "q3_string_matching.py"),
    ("Q4_Brute_Force_Closest_Pair", "q4_closest_pair.py"),
    ("Q5_Brute_Force_Convex_Hull", "q5_convex_hull.py"),
    ("Q6_Exhaustive_Search", "q6_exhaustive_search.py"),
    ("Q7_Day4_Design_Challenge", "q7_redesign_closest_pair.py"),
]
sys.path.insert(0, os.path.join(ROOT, "tools"))
from render_screenshot import render  # noqa: E402

for folder, script in JOBS:
    code = os.path.join(ROOT, folder, "Implementation_Code")
    outd = os.path.join(ROOT, folder, "Output_Screenshots")
    q = folder.split("_")[0]
    print("Running", folder, "...")
    r = subprocess.run([sys.executable, script], cwd=code, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr)
        raise SystemExit("failed: " + script)
    txt = os.path.join(outd, q + "_console_output.txt")
    open(txt, "w", encoding="utf-8").write(r.stdout)
    for f in render(txt, "python3 " + script, os.path.join(outd, q + "_execution_screenshot")):
        print("   ", os.path.relpath(f, ROOT))
