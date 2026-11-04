"""Builds CO2_Assignment_Report.docx from the raw data / console output produced by run_all.py."""
import csv
import glob
import math
import os
import re

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
Q = {k: [d for d in os.listdir(ROOT) if d.startswith(k + "_")][0] for k in ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7")}


def out(q, *p):
    return os.path.join(ROOT, Q[q], "Output_Screenshots", *p)


def rd(q, name):
    with open(out(q, "raw_data", name), newline="") as f:
        return list(csv.reader(f))


def console(q):
    return open(out(q, q + "_console_output.txt"), encoding="utf-8").read()


def grab(q, pat, grp=1, cast=float):
    m = re.search(pat, console(q))
    return cast(m.group(grp).replace(",", ""))


doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Inches(8.27), Inches(11.69)
for s in ("left_margin", "right_margin"):
    setattr(sec, s, Inches(0.9))
sec.top_margin = sec.bottom_margin = Inches(0.9)
st = doc.styles["Normal"]
st.font.name = "Calibri"
st.font.size = Pt(10.5)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
st.paragraph_format.space_after = Pt(5)
for name, size, col in (("Heading 1", 17, "1F3864"), ("Heading 2", 13, "2E5597"), ("Heading 3", 11.5, "2E5597")):
    h = doc.styles[name]
    h.font.name = "Calibri"
    h.font.size = Pt(size)
    h.font.bold = True
    h.font.color.rgb = RGBColor.from_string(col)
    h.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")


def shade(cell, color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tcPr.append(shd)


def P(text="", bold=False, italic=False, size=None, align=None, color=None, after=None):
    p = doc.add_paragraph()
    # allow **bold** inline segments
    parts = re.split(r"(\*\*.+?\*\*)", text)
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            r = p.add_run(part[2:-2])
            r.bold = True
        else:
            r = p.add_run(part)
            r.bold = bold
        r.italic = italic
        if size:
            r.font.size = Pt(size)
        if color:
            r.font.color.rgb = RGBColor.from_string(color)
    if align == "c":
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if after is not None:
        p.paragraph_format.space_after = Pt(after)
    return p


def B(text, level=0):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.left_indent = Inches(0.25 + 0.25 * level)
    p.paragraph_format.space_after = Pt(2)
    parts = re.split(r"(\*\*.+?\*\*)", text)
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            p.add_run(part[2:-2]).bold = True
        else:
            p.add_run(part)
    return p


def H(text, lvl=1):
    return doc.add_heading(text, lvl)


def CODE(text, size=8.5):
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = t.rows[0].cells[0]
    shade(c, "F2F2F2")
    c.paragraphs[0].text = ""
    lines = text.strip("\n").split("\n")
    for i, ln in enumerate(lines):
        p = c.paragraphs[0] if i == 0 else c.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(ln)
        r.font.name = "Consolas"
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
        r.font.size = Pt(size)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def TABLE(headers, rows, widths=None, size=8.5, hdr="1F3864", zebra=True, bold_last=False):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]
        c.text = ""
        r = c.paragraphs[0].add_run(str(h))
        r.bold = True
        r.font.size = Pt(size)
        r.font.color.rgb = RGBColor(255, 255, 255)
        shade(c, hdr)
    for ri, row in enumerate(rows):
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(str(v))
            r.font.size = Pt(size)
            if bold_last and ri == len(rows) - 1:
                r.bold = True
            cells[i].paragraphs[0].paragraph_format.space_after = Pt(0)
            if zebra and ri % 2 == 1:
                shade(cells[i], "EAF0FA")
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Inches(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def IMG(path, width=6.4, caption=None):
    doc.add_picture(path, width=Inches(width))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    if caption:
        P(caption, italic=True, size=9, align="c", color="555555")


def PB():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def fmt(x):
    return "{:,}".format(int(x))


# =============================================================== COVER
for _ in range(4):
    P("")
P("DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING", bold=True, size=14, align="c", color="1F3864")
P("CSA06  Design and Analysis of Algorithms", bold=True, size=13, align="c")
P("")
P("ASSIGNMENT 2 – CO2", bold=True, size=24, align="c", color="1F3864")
P("Brute-Force and Exhaustive-Search Techniques", size=14, align="c")
P("Sorting · Sequential Search · String Matching · Closest Pair · Convex Hull · Exhaustive Search · Day-4 Design Challenge",
  italic=True, size=10.5, align="c")
P("")
P("Complete Assignment Report", bold=True, size=16, align="c")
P("Predict → Design → Implement → Measure → Analyse → Evaluate → Diagnose → Redesign → Validate", italic=True, size=10, align="c")
for _ in range(3):
    P("")
TABLE(["Item", "Details"], [
    ["Student name", "RITHIKA G"],
    ["Register number / Section", "______________________"],
    ["Course Outcome", "CO2 – Apply Brute Force technique to solve sorting, searching, Closest-Pair and Convex-Hull problems"],
    ["Nature / Marks", "Individual · 50 marks"],
    ["GitHub repository", "https://github.com/<your-username>/CO2_Assignment   (add your link here)"],
    ["Implementation language", "Python 3.12 (matplotlib for graphs)"],
], widths=[1.9, 4.5], size=10, zebra=False)
PB()

# =============================================================== CONTENTS / EVIDENCE MAP
H("Contents and evidence map", 1)
TABLE(["Question", "Topic", "Marks", "Code", "Pseudocode", "Raw data"], [
    ["Q1", "Sorting under different data conditions", "6", "q1_sorting.py", "q1_pseudocode.md", "q1_*.csv"],
    ["Q2", "Sequential search – engineering boundary", "4", "q2_sequential_search.py", "q2_pseudocode.md", "q2_*.csv"],
    ["Q3", "Brute-force string matching behaviour", "6", "q3_string_matching.py", "q3_pseudocode.md", "q3_*.csv"],
    ["Q4", "Brute-force closest pair", "6", "q4_closest_pair.py", "q4_pseudocode.md", "q4_*.csv"],
    ["Q5", "Brute-force convex hull from geometry", "7", "q5_convex_hull.py", "q5_pseudocode.md", "q5_*.csv"],
    ["Q6", "Exhaustive search & combinatorial growth", "8", "q6_exhaustive_search.py", "q6_pseudocode.md", "q6_growth.csv"],
    ["Q7", "Day-4 Design Challenge (closest-pair redesign)", "13", "q7_redesign_closest_pair.py", "q7_pseudocode.md", "q7_*.csv"],
], widths=[0.6, 2.4, 0.5, 1.6, 1.2, 0.8], size=8.5)
P("**Method note.** For every question the operation counts (comparisons, moves, pairs, distance calculations, side tests, "
  "candidates) are the primary evidence; execution time is reported only as supporting evidence. Predictions were derived from the "
  "algorithm structure and recorded in the program output before the measurements were printed. Where a prediction turned out to be "
  "wrong, this is stated openly in the report. All input data are produced by seeded random generators, so every count in this report "
  "is exactly reproducible (times vary slightly between runs and machines).")
P("**Environment.** Interpreted Python 3.12 on a cloud container. All time-based limits (response-time limits, maximum n) therefore apply "
  "to this environment; compiled code would run roughly 50–100× faster, which shifts those limits but never changes the growth laws.")
PB()

# =============================================================== Q1
H("Q1 – Sorting Under Different Data Conditions (6 marks)", 1)
H("1.1 Problem and question", 2)
P("A fulfilment centre sorts orders by dispatch-priority score. Should Selection, Bubble or Insertion Sort always be preferred, or does the "
  "choice depend on the input? About 95% of existing orders are already in order, and small batches of new orders arrive periodically.")
H("1.2 Predictions made before implementation (with algorithmic reasons)", 2)
TABLE(["Input condition", "Selection Sort", "Bubble Sort (early exit)", "Insertion Sort"], [
    ["Already sorted", "n(n−1)/2 comparisons – scans the whole unsorted part every pass; 0 swaps", "n−1 comparisons (one pass, no swap → stop)", "n−1 comparisons, 0 shifts"],
    ["Reverse sorted", "n(n−1)/2 comparisons, only ⌊n/2⌋ swaps", "n(n−1)/2 comparisons and swaps (worst case)", "n(n−1)/2 comparisons and shifts (worst case)"],
    ["Random", "n(n−1)/2 comparisons, <n swaps", "≈ n²/2 comparisons, swaps = inversions ≈ n²/4", "≈ n²/4 comparisons and shifts"],
    ["95% sorted + small batch appended (D1)", "Unchanged: n(n−1)/2 – not adaptive", "Each appended order moves left ONE place per pass → passes ≈ distance travelled → close to n passes", "Cost = (n−1) + inversions; only the few appended orders move → cheap"],
    ["All priorities equal (edge)", "n(n−1)/2 comparisons, 0 swaps", "n−1 comparisons, 0 swaps", "n−1 comparisons, 0 shifts"],
], widths=[1.5, 1.7, 1.8, 1.6], size=8.5)
P("Exact formulae used for the predictions: Bubble moves = Insertion shifts = number of inversions; Bubble passes = 1 + max(number of larger "
  "elements to the left of any element) because an element can move left only one position per pass; Insertion comparisons = inversions + (n−1) − z, "
  "where z is the number of elements smaller than everything before them. The program computes these from an independent inversion count "
  "before running any sort.")
H("1.3 Test data design (n = 1000)", 2)
TABLE(["ID", "Dataset", "Purpose"], [
    ["D1", "950 existing orders already sorted + 50 NEW orders with random priority appended at the end", "Contrasting dataset 1 – the real scenario (95% ordered)"],
    ["D2", "Strictly reverse-sorted priorities", "Contrasting dataset 2 – significantly disordered, worst case"],
    ["D3", "All 1000 orders have the same priority", "Edge case of my own – ties; tests stability and adaptiveness"],
    ["D1b", "Sorted, then 5% of orders displaced by ≤ 5 positions", "Shows that 'nearly sorted' depends on WHERE the disorder is"],
    ["D0 / D0b", "Random / already sorted", "Baselines"],
    ["Stability", "1000 orders, only 5 distinct priorities", "Checks whether equal-priority orders keep arrival order"],
], widths=[0.7, 3.7, 2.2], size=8.5)
H("1.4 Algorithms (pseudocode summary)", 2)
CODE("""InsertionSort(A):  for i←1..n-1: v←A[i]; j←i-1
                    while j≥0 and A[j]>v: A[j+1]←A[j]; j←j-1      // count 1 comparison per test
                    A[j+1]←v
BubbleSort(A):     repeat passes: swap adjacent out-of-order pairs; stop when a pass makes no swap
SelectionSort(A):  for i←0..n-2: find index m of the minimum in A[i..n-1]; swap A[i],A[m] if m≠i""")
P("Full pseudocode: Q1_Sorting_Algorithms/Pseudocode/q1_pseudocode.md. Counted: comparisons, moves (swaps/shifts), time (best of 3).", italic=True, size=9.5)
H("1.5 Results – operation counts (n = 1000)", 2)
rows = []
for r in rd("Q1", "q1_dataset_results.csv")[1:]:
    rows.append([r[0].split(":")[0].split(" (")[0], r[2], fmt(r[3]), fmt(r[4]), fmt(r[5]), r[9], "%.2f" % float(r[7]), "yes" if r[8] == "True" else "no"])
TABLE(["Dataset", "Algorithm", "Comparisons", "Moves", "Predicted comp.", "Pred. check", "Time ms", "Stable*"], rows,
      widths=[1.55, 0.85, 0.95, 0.85, 0.95, 0.65, 0.6, 0.55], size=8)
P("*Stable on that particular dataset (the dedicated stability test is below). Observed Bubble passes equalled the prediction in every case "
  "(e.g. 984 on D1, 7 on D1b, 999 on D2, 1 on sorted/equal data).", italic=True, size=9)
P("**Stability test (5 priority levels):** Selection sorted=True, stable=**False**; Bubble stable=True; Insertion stable=True.")
IMG(out("Q1", "q1_graph_operations_by_dataset.png"), 6.0, "Figure 1.1 – Total key operations (comparisons + moves) by input condition, log scale")
H("1.6 Scaling for the real scenario (95% ordered + 5% appended batch)", 2)
rows = []
d = {}
for r in rd("Q1", "q1_scaling_95pct_sorted.csv")[1:]:
    d.setdefault(r[0], {})[r[1]] = r
for n, v in d.items():
    rows.append([n, fmt(v["Selection"][2]), fmt(v["Bubble"][2]), fmt(v["Insertion"][2]), "%.1f×" % (int(v["Selection"][2]) / int(v["Insertion"][2])),
                 "%.1f / %.1f / %.1f" % (float(v["Selection"][4]), float(v["Bubble"][4]), float(v["Insertion"][4]))])
TABLE(["n", "Selection comps", "Bubble comps", "Insertion comps", "Sel/Ins", "Time ms (Sel / Bub / Ins)"], rows,
      widths=[0.6, 1.1, 1.1, 1.1, 0.7, 1.9], size=8.5)
IMG(out("Q1", "q1_graph_scaling_95pct.png"), 6.2, "Figure 1.2 – Growth for the 95%-ordered scenario")
H("1.7 Prediction versus observation", 2)
B("**All predicted comparison counts matched the observed counts exactly (18/18)**, and Bubble/Insertion moves equalled the inversion count. "
  "The reasoning about how each algorithm works is therefore validated, not just the trend.")
B("**Selection Sort** performed n(n−1)/2 = 499,500 comparisons on every input – even on sorted data – confirming it is not adaptive. It has the "
  "fewest moves (e.g. 525 swaps on the reverse-sorted data against ≈499,000 for the other two), which matters only when a move is expensive.")
B("**Insertion Sort** is strongly adaptive: 999 comparisons on sorted/equal data, 25,757 on D1 (19× fewer than Selection) and 1,203 on D1b.")
B("**Bubble Sort was the surprise in magnitude.** On D1 it needed 984 passes and 499,380 comparisons – almost as many as Selection Sort – although "
  "95% of the data was in order. The appended low-priority orders must travel far to the left and Bubble Sort moves an element left only one place per "
  "pass. On D1b (disorder only local) it needed just 7 passes and 6,972 comparisons. The lesson: “nearly sorted” is not one property – the position "
  "and distance of the disorder decide the cost.")
B("On the reverse-sorted data Bubble and Insertion reach their worst case (≈ n²/2 = 499,500 comparisons) – the prediction table is confirmed.")
B("**Edge case D3:** with all-equal priorities Bubble and Insertion cost n−1 comparisons and no moves, while Selection still costs 499,500. "
  "Because Selection Sort swaps non-adjacent elements it is not stable (stability test: False), which would reorder equal-priority orders – "
  "unacceptable for first-come-first-served dispatch.")
H("1.8 Design decision – recommendation", 2)
P("**Recommendation: Insertion Sort.** Not “one algorithm always”: for random or reversed data all three are quadratic and the choice would be "
  "driven by move cost and stability. For this fulfilment centre the evidence is specific:")
B("Cost is (n−1) + inversions. With 95% of orders in place only the new batch creates inversions: at n = 3000 Insertion needs 223,195 comparisons "
  "against 4,498,500 for Selection and 4,494,314 for Bubble (≈20×), and runs ≈10× faster.")
B("It is stable (equal-priority orders keep arrival order), in place (O(1) memory) and online – each newly arriving order can be inserted at a cost "
  "equal to its displacement.")
B("Bubble Sort is rejected because of the observed ‘small element at the end’ behaviour (984 passes); Selection Sort because it ignores existing order and is unstable.")
B("**Limits of the recommendation:** its advantage disappears if batches become large or arrive in reverse priority order; the cost is k·n/2 shifts for a "
  "batch of k orders. Monitor the inversion count; if batches grow beyond roughly a quarter of the list, a sort with O(n log n) behaviour (outside the scope of CO2) "
  "or sorting the batch and merging should be considered.")
PB()

# =============================================================== Q2
H("Q2 – When Is Sequential Search an Appropriate Engineering Choice? (4 marks)", 1)
H("2.1 Design and prediction", 2)
P("Records (Tool ID, Technician ID, Issue Time, Work Bay) are held in an unordered list; the search key is the Tool ID. Prediction: a successful search for "
  "the key at position p costs exactly p comparisons (best 1, worst n, average over all keys (n+1)/2); an unsuccessful search costs exactly n. "
  "If a fraction s of requests succeed, the expected cost is s(n+1)/2 + (1−s)n.")
CODE("""SequentialSearch(R, key): comps←0
    for i←0..n-1: comps←comps+1 ; if R[i].ToolID = key then return (i, comps)
    return (-1, comps)""")
H("2.2 Experiments and comparison-count evidence", 2)
rows = [[fmt(r[0]), fmt(r[1]), fmt(r[2]), fmt(r[3]), fmt(r[4]), fmt(r[5]), fmt(r[6]), "%.1f" % float(r[7]), "%.1f" % float(r[8])] for r in rd("Q2", "q2_comparisons_by_position.csv")[1:]]
TABLE(["n", "first", "25%", "middle", "75%", "last", "unsuccessful", "avg all keys (measured)", "(n+1)/2"], rows,
      widths=[0.7, 0.5, 0.65, 0.65, 0.65, 0.65, 0.85, 1.1, 0.7], size=8.5)
P("(For n = 100,000 the average is taken over 2,000 random keys, hence 50,412.7 against 50,000.5.) The measured counts equal the predictions exactly.", italic=True, size=9)
IMG(out("Q2", "q2_graph_comparisons.png"), 6.3, "Figure 2.1 – Left: comparisons against list size (log–log). Right: total work for the same operation mix, before and after growth.")
B("**Successful searches** cost the position of the record: 1 (first) … n (last); averaged over all keys (n+1)/2. Cost is linear in n.")
B("**Unsuccessful searches** always cost the full n – the worst case – because absence can only be established by examining every record. "
  "If half the requests are for tools that are not currently issued, the expected cost rises from 0.50n to 0.75n; at 10% success it is 0.95n.")
H("2.3 Operating boundary", 2)
rate = grab("Q2", r"Mean measured rate r = ([\d.]+) million") * 1e6
P("**Acceptability criteria I defined.** C1: one worst-case lookup must complete within 50 ms (feels instant on a technician's screen) → n ≤ 0.05·r. "
  "C2: all lookups together must use at most 10%% of one core, leaving headroom → q·(n/2) ≤ 0.10·r, i.e. q·n ≤ 0.2·r. "
  "Measured speed of this environment: r ≈ %.1f million comparisons/second (interpreted Python)." % (rate / 1e6))
P("So C1 allows n up to ≈ %s records (one query is never the problem), and C2 gives **q·n ≤ ≈ %.1f × 10⁶**: e.g. n = 500 → up to ≈ %s lookups/s; "
  "n = 10,000 → ≈ %s/s; n = 100,000 → ≈ %s/s; n = 1,000,000 → ≈ %.1f/s." % (fmt(rate * 0.05), 0.2 * rate / 1e6, fmt(round(0.2 * rate / 500, -2)),
  fmt(round(0.2 * rate / 1e4, -1)), fmt(round(0.2 * rate / 1e5)), 0.2 * rate / 1e6))
bt = rd("Q2", "q2_boundary_table.csv")
rows = []
for r in bt[1:]:
    rows.append([fmt(r[0])] + [("%.3f" % float(x)) + ("*" if float(x) > 10 else "") for x in r[1:]])
TABLE(["n \\ lookups per second"] + [h.replace("q=", "").replace("/s", "") for h in bt[0][1:]], rows, widths=[1.3] + [0.85] * 6, size=8.5)
P("Core utilisation (%) caused by lookups; * exceeds the 10% budget.", italic=True, size=9)
P("**Answer.** Sequential search is a reasonable choice when (i) the list is small enough that q·n stays below the budget (hundreds to a few thousand "
  "records with at most a few lookups per second), (ii) the list is unordered and changes constantly, so keeping a sorted order or an index would cost more "
  "than the searches it saves (issue = append, return = search + delete, no maintenance), and (iii) simplicity and reliability matter. "
  "I stop recommending it when the **product** q·n of records and request rate exceeds about %.1f×10⁶ per second in this environment (or ~50× more if compiled), "
  "or when most searches are unsuccessful and latency is critical – whichever comes first. Dataset size alone or frequency alone is not the criterion; their product is." % (0.2 * rate / 1e6))
H("2.4 Changed condition – 20 maintenance facilities", 2)
P("Assumptions (explicit, replaceable by real figures): one hangar ≈ 500 tools issued and ≈ 5,000 operations/day; 20 facilities centralised ≈ 10,000 tools and "
  "≈ 100,000 operations/day; mix 40% lookup, 30% issue, 30% return (a return must first find the record). The same operation mix was simulated for a sequential "
  "list and for a hash index keyed on Tool ID.")
rows = [[r[0], fmt(r[1]), fmt(r[2]), fmt(r[3]), fmt(r[4])] for r in rd("Q2", "q2_changed_condition.csv")[1:]]
TABLE(["Scenario", "Tools in service", "Operations", "Sequential comparisons", "Hash probes"], rows, widths=[1.9, 1.0, 1.0, 1.5, 1.0], size=8.5)
B("Records ×20 and requests ×20 make the sequential cost grow ×396 (≈ 20×20), because every request scans a list that is itself 20× longer. "
  "The hash index grows only ×20 (with requests).")
B("In absolute terms, 3.5×10⁸ comparisons/day ≈ %.0f s of CPU per day, and peak utilisation (10× the average rate) is ≈ %.2f%% of one core against my 10%% budget. "
  "**So, honestly, with these assumptions the original recommendation still passes both criteria**, with about a %.0f× margin left." % (
      grab("Q2", r"that is ([\d.]+) s of CPU/day"), grab("Q2", r"n=10,000\): ([\d.]+)%"), 10 / grab("Q2", r"n=10,000\): ([\d.]+)%")))
B("**Re-evaluated recommendation:** (a) If every facility keeps its own list, n and q per list are unchanged and sequential search remains appropriate. "
  "(b) For one central system I would replace it by a hash index on Tool ID: it costs one dictionary, supports O(1) issue/return/lookup and removes the "
  "q·n scaling, so a further ≈ 20× growth (or much burstier automated lookups such as barcode scans at every issue and return) cannot break the response-time criterion. "
  "(c) A sorted array with binary search is not a good fit because the list changes continuously (O(n) insertions).")
PB()

# =============================================================== Q3
H("Q3 – Engineering the Behaviour of Brute-Force String Matching (6 marks)", 1)
H("3.1 Algorithm and cost model", 2)
CODE("""BruteForceMatch(T[0..n-1], P[0..m-1]):  comps←0
    for i←0..n-m:                  // n-m+1 alignments
        j←0
        while j<m: comps←comps+1 ; if T[i+j]≠P[j] break ; j←j+1
        if j=m: report match at i""")
P("Work at an alignment = (length of the matching prefix) + 1, at most m. Total work therefore depends on how long partial matches are, not on n and m alone.")
H("3.2 Designed tests and predictions (made before execution; n = 10,000, m = 8)", 2)
rows = [[r[0].split(":")[0].strip(), r[0].split(":", 1)[1].strip()[:70], fmt(float(r[3])), fmt(r[4]), "%.3f" % (int(r[4]) / float(r[3])), r[5]] for r in rd("Q3", "q3_tests.csv")[1:]]
TABLE(["Test", "Text / pattern", "Predicted", "Observed", "Obs/Pred", "Matches"], rows, widths=[0.5, 3.3, 0.8, 0.8, 0.7, 0.6], size=8)
TABLE(["Test", "Why the prediction was made"], [
    ["T1 (low work)", "Pattern starts with ‘X’, which never occurs in aaaa…a: every alignment fails on the FIRST comparison → n−m+1 = 9,993."],
    ["T2 (engineered)", "Text A^n, pattern A^7B: every alignment matches 7 characters and fails on the 8th → m per alignment → (n−m+1)·m = 79,944."],
    ["T3 (my choice)", "Realistic synthetic log, signature ‘password’. Expected cost per alignment E = 1 + f(p0) + f(p0)f(p1) + … from the character frequencies of the log text → 10,155."],
    ["T4 (extra)", "Pattern equals the first 8 characters; algorithm stops at the first match → exactly m = 8 comparisons."],
], widths=[1.2, 5.4], size=8.5)
IMG(out("Q3", "q3_graph_comparisons.png"), 6.3, "Figure 3.1 – Left: identical n and m, very different work. Right: growth of the engineered case with n and m.")
H("3.3 Additional experiments", 2)
P("**Alphabet size** (random texts, n = 10,000, m = 8): comparisons per alignment were 1.986 (2 symbols), 1.332 (4), 1.143 (8), 1.038 (26) and 1.016 (62); "
  "observed totals agreed with the frequency-based prediction to within 0.1%. **Scaling of the engineered case**: comparisons equalled (n−m+1)·m exactly for all 15 "
  "combinations of n (1,000–16,000) and m (4, 8, 16); on random lowercase text the same n and m cost ≈ n comparisons regardless of m (e.g. 16,612–16,657 for n = 16,000).")
H("3.4 Inquiry – prediction versus experiment and explanation", 2)
B("T1, T2 and T4 matched their predictions exactly. T3 was 1.4% above the prediction (10,302 vs 10,155): the independence assumption behind E ignores that the "
  "signature genuinely occurs 25 times (25 × 8 = 200 comparisons) and that words in a log repeat. The model is good but not exact for real text.")
B("**Why does one input need much more work?** T1 and T2 have the same n and m, yet T2 costs 8.0× more (79,944 vs 9,993; 8.00 vs 1.00 comparisons per alignment). "
  "In T1 each alignment is rejected immediately; in T2 each alignment re-reads m−1 characters that the previous alignment already matched.")
B("**Characteristics that create repeated comparisons:** (1) a pattern whose prefix is repetitive and resembles the text (long partial matches), "
  "(2) a text that is itself repetitive / low-entropy, (3) a small alphabet (binary text costs ≈ 2 per alignment, 62-symbol text ≈ 1.02), and (4) a mismatch located "
  "at the END of the pattern. After a mismatch the algorithm shifts by exactly one and discards everything it learned, so the same text character may be compared up to m times.")
B("**What this shows about evaluating an algorithm by input size only:** n and m do not determine the work; it ranges from n−m+1 to (n−m+1)·m for identical sizes. "
  "Big-O worst case Θ(nm) describes T2, while typical log text behaves like Θ(n). An honest evaluation needs the input distribution and a bound on the worst case. "
  "In a security setting this matters twice: average behaviour is acceptable (≈1.03 comparisons/char) but an attacker who can influence log content could craft repetitive input "
  "and force the worst case, so the system must be tested with adversarial data and not only with typical logs.")
PB()

# =============================================================== Q4
H("Q4 – Closest Pair and the Cost of Examining Every Possibility (6 marks)", 1)
H("4.1 Design", 2)
B("**Candidate pairs:** every unordered pair {Di, Dj}.")
B("**Avoiding duplicates:** (Di, Dj) and (Dj, Di) have the same distance, so the inner loop starts at j = i+1 (and i ≠ j is automatic). "
  "An ordered i ≠ j scan would examine 999,000 pairs for n = 1000 instead of 499,500.")
B("**Distance:** squared Euclidean distance dx²+dy² – it has the same minimiser as the true distance, so the square root is avoided.")
CODE("""BruteForceClosestPair(D): best←∞
    for i←0..n-2: for j←i+1..n-1:
        d←(xi-xj)²+(yi-yj)² ; pairs←pairs+1 ; calcs←calcs+1 ; if d<best: best←d,(bi,bj)←(i,j)""")
H("4.2 Mathematical derivation of the number of pairs", 2)
P("Drone 0 is paired with n−1 later drones, drone 1 with n−2, …, drone n−2 with 1, drone n−1 with none:")
P("S = (n−1) + (n−2) + … + 2 + 1 = Σ_{k=1}^{n−1} k = n(n−1)/2 = C(n,2) = n!/(2!(n−2)!)", bold=True, align="c")
P("Check by pairing: writing the sum forwards and backwards gives n−1 columns each summing to n, i.e. 2S = n(n−1). "
  "Hence pairs = Θ(n²): C(2n,2)/C(n,2) = 2(2n−1)/(n−1) → 4 as n grows, i.e. doubling n quadruples the pairs (observed 4.001–4.008).")
H("4.3 Experimental results (random drones in a 10 km × 10 km airspace)", 2)
rows = [[fmt(r[0]), fmt(r[1]), fmt(r[2]), fmt(r[3]), "%.4f" % float(r[4]), "%.3f" % float(r[5])] for r in rd("Q4", "q4_bruteforce_results.csv")[1:]]
TABLE(["n", "Pairs examined", "Distance calculations", "n(n−1)/2", "Time (s)", "Closest distance (m)"], rows, widths=[0.6, 1.2, 1.4, 1.2, 0.8, 1.3], size=8.5)
c = grab("Q4", r"c = ([\d.e+-]+) s/n\^2")
slope = grab("Q4", r"slope of measured time = ([\d.]+)")
nmax = grab("Q4", r"= (\d+) drones \(this environment\)", cast=int)
P("Pairs examined = distance calculations = n(n−1)/2 for every n (exact equality, prediction confirmed). Pair counts multiplied by 4.001–4.008 for each doubling of n "
  "(theory: → 4); time multiplied by 3.6–4.4. A least-squares fit t(n) = c·n² gives c = %.2e s and the log–log slope of the measured times is %.3f (theory 2). A correctness check "
  "against an independent itertools.combinations minimum passed for n = 2, 3, 10, 50, 200." % (c, slope))
IMG(out("Q4", "q4_graph_growth.png"), 6.5, "Figure 4.1 – Pairs (theory vs measured), execution time with fit and 1-second limit, and log–log growth")
H("4.4 Scalability inquiry", 2)
P("**Acceptable response time (my definition): 1.0 second** – the monitoring system receives a new position report every second, so a collision check that takes longer yields stale "
  "results. With the fitted model, t(n) ≤ 1 s up to **n ≈ %s drones** in this environment; the measured 4,000 drones took ≈0.8 s and 8,000 drones ≈3 s, so the method becomes impractical "
  "between 4,000 and 5,000 drones. Extrapolation: 10,000 drones → ≈5.5 s; 50,000 → ≈2 min; 100,000 → ≈9 min. A compiled implementation ~50× faster would raise the limit only by √50 ≈ 7× "
  "(to ≈ 30,000 drones) because the cost is quadratic." % fmt(nmax))
P("**Where the inefficiency originates.** All pairs are examined, although a pair can only matter if its drones are close. Nearly all of the n(n−1)/2 pairs are far apart and can never "
  "be the answer, yet each costs a full distance evaluation. The brute-force method uses no geometric information (position, ordering) and never uses what is already known "
  "(the best distance so far) to discard other pairs. A redesigned strategy must (a) avoid comparing pairs that cannot beat the current best, by exploiting ordering or locality "
  "of the data, and (b) pay for that with a cheap preprocessing step – this is exactly the Q7 design challenge.")
PB()

# =============================================================== Q5
H("Q5 – Deriving a Convex Hull Algorithm from a Geometric Principle (7 marks)", 1)
H("5.1 From the geometric principle to a decision rule (my derivation)", 2)
B("**Two points define a line.** For Pi = (x1, y1) and Pj = (x2, y2): a·x + b·y = c with a = y2−y1, b = x1−x2, c = x1·y2 − y1·x2.")
B("**Position of another point.** For Pk = (x, y) compute s = a·x + b·y − c. This equals the cross product (Pj−Pi)×(Pk−Pi): s > 0 → left of the directed line Pi→Pj, "
  "s < 0 → right, s = 0 → on the line. With integer coordinates the test is exact (no rounding errors).")
B("**Examining the rest:** compute s for every other point Pk (n−2 tests).")
B("**Condition for a hull edge:** all non-zero values of s have the same sign. Points with s = 0 (collinear) are allowed only if they lie within the segment PiPj, so that points in the middle "
  "of an edge are not mistaken for corners and a longer collinear stretch is not split.")
B("**Constructing the boundary:** if all s > 0, the whole set is on the left of Pi→Pj, so this is a counter-clockwise edge: succ[i] = j (if all s < 0 use succ[j] = i). "
  "Starting at the lexicographically smallest vertex and following succ[] reads the polygon in counter-clockwise order. Duplicate stations are removed first.")
CODE("""for i←0..n-2: for j←i+1..n-1:
    pos←neg←false ; ok←true
    for each k≠i,j: s←Side(Pi,Pj,Pk) ; tests++
         s>0 → pos←true ; s<0 → neg←true ; s=0 and Pk outside segment PiPj → ok←false,break
         if pos and neg → ok←false,break
    if ok: (pos ? succ[i]←j : neg ? succ[j]←i : both directions)  // all-collinear case
follow succ[] from the smallest vertex""")
H("5.2 Test configurations and visualisation", 2)
TABLE(["Test", "Configuration", "Distinct n", "Hull vertices", "Side tests (early exit)", "Side tests (no early exit)"],
      [[r[0].split(":")[0], r[0].split(":", 1)[1].strip(), r[1], r[2], fmt(r[3]), fmt(r[4])] for r in rd("Q5", "q5_test_configs.csv")[1:]],
      widths=[0.4, 2.8, 0.6, 0.7, 0.95, 0.95], size=8)
IMG(out("Q5", "q5_hull_visualisation.png"), 6.6, "Figure 5.1 – Computed boundaries (red). T1 mixed, T2 challenge (collinear edge points, duplicates), T3 collinear, T4 all-on-hull")
B("**T1:** 6 boundary + 14 interior stations → hull of 6 vertices.")
B("**T2 (designed to challenge the algorithm):** square corners, extra points lying exactly on the edges (s = 0), duplicate stations, and interior points on the diagonal. "
  "The edge-midpoints are correctly NOT reported as corners and duplicates do not create zero-length edges; result = 4 vertices.")
B("**T3:** all points collinear – the only accepted pair is the two extreme points. **T4:** 16 points on a circle – every point is a vertex (largest possible hull).")
B("**Validation:** each result equals an independent reference hull (Andrew's monotone chain, used only for checking), and 300 random sets on a 13×13 grid (full of ties, duplicates and collinear points) produced 0 mismatches.")
H("5.3 Computational growth", 2)
rows = [[r[0], r[1], fmt(r[2]), fmt(r[3]), fmt(r[4]), "%.3f" % float(r[5]), "%.3f" % float(r[6])] for r in rd("Q5", "q5_growth.csv")[1:]]
TABLE(["n", "Hull h", "Tests, early exit", "Tests, full", "n(n−1)(n−2)/2", "Time early (s)", "Time full (s)"], rows, widths=[0.5, 0.6, 1.1, 1.1, 1.2, 0.9, 0.9], size=8.5)
IMG(out("Q5", "q5_graph_growth.png"), 6.2, "Figure 5.2 – Side tests against n (log–log) and execution time")
B("**Prediction for the full version:** C(n,2) pairs × (n−2) tests = n(n−1)(n−2)/2 → Θ(n³). Confirmed exactly (full/theory = 1.000 for every n); each doubling of n multiplies the work by 8.1–9.5; log–log slope 3.08.")
B("**Prediction for the early-exit version – NOT supported.** I predicted that stopping a pair as soon as both signs have appeared would make random inputs behave close to n². "
  "Observed: slope 2.79 and each doubling still multiplied the work by 6.2–7.7; early exit lowered the constant (≈5× fewer tests at n = 320) but not the growth order.")
B("**Explanation and test of it:** my implementation scanned the ‘other points’ in x-sorted order, so neighbouring points tend to lie on the same side of a line and the opposite side is found late. "
  "Scanning in random order on the same inputs reduced the tests 12.9× at n = 320 (3,377,844 → 261,732) and the slope to 2.15, i.e. about n². The hypothesis is supported: for random data the cost depends on scan order.")
B("**Worst case:** for points on a circle the early-exit version still needs 35–63% of the full n(n−1)(n−2)/2 tests (e.g. 707,602 for n = 160) – the cubic worst case remains, as every hull edge needs all n−2 tests.")
H("5.4 Correctness inquiry – why an accepted edge belongs to the outer boundary", 2)
P("Let L be the line through Pi and Pj, and suppose every other point lies in one closed half-plane H bounded by L.")
B("**(a)** A half-plane is convex, and the convex hull is the smallest convex set containing all points, so the hull ⊆ H: the whole hull lies on one side of L.")
B("**(b)** Pi and Pj belong to the point set, so they lie in the hull and on L; by convexity the segment PiPj also lies in the hull, and it lies on L.")
B("**(c)** A point of the hull that lies on L cannot be an interior point: every neighbourhood of it contains points of the empty side of L, which are outside H and therefore outside the hull. "
  "So PiPj consists of boundary points, i.e. it is part of the outer boundary.")
B("**Completeness:** conversely every edge of the hull lies on a supporting line (a line touching the hull with the entire hull on one side), so it passes the test; no edge is missed. "
  "**Rejection:** if some Pk lies strictly on the other side of L, then Pi, Pj and Pk would put points of the hull on both sides of L, so the segment PiPj passes through the interior of the hull and is not boundary. "
  "The collinear-in-segment rule handles the remaining degenerate case: a point on L outside segment PiPj means the supporting line contains a longer boundary edge, and PiPj is only part of it.")
PB()

# =============================================================== Q6
H("Q6 – Exhaustive Search and Combinatorial Growth (8 marks)", 1)
H("6.1 Exhaustive-search design (student-designed)", 2)
TABLE(["Design question", "Decision"], [
    ["Representing a candidate", "An n-bit integer mask; bit k = 1 ⇔ package k is loaded. Subsets and masks 0 … 2ⁿ−1 correspond one-to-one."],
    ["Generating candidates", "for mask in 0 … 2ⁿ−1 – every subset exactly once, no duplicates, none missed."],
    ["Feasibility", "Sum the weights of the selected bits; feasible if total ≤ payload limit."],
    ["Evaluating", "Sum the values of the selected bits (only for feasible candidates it is compared)."],
    ["Retaining the best", "Keep (bestValue, bestMask); replace only on a strictly higher value (ties keep the first found)."],
], widths=[1.7, 4.9], size=9)
CODE("""for mask←0..2ⁿ-1: w←v←0
    for k←0..n-1: if bit k of mask: w←w+weight[k] ; v←v+value[k]
    if w ≤ LIMIT and v > bestValue: bestValue←v ; bestMask←mask""")
H("6.2 Correctness check on a verifiable instance", 2)
TABLE(["ID", "Package", "Weight", "Value"], [["1", "Medical kit", "4", "10"], ["2", "Water", "6", "7"], ["3", "Food", "5", "8"], ["4", "Blankets", "3", "4"], ["5", "Radio", "2", "6"]],
      widths=[0.5, 2.0, 0.9, 0.9], size=9)
P("Payload limit = 10. All 2⁵ = 32 subsets were listed independently in the program output (mask, packages, weight, value, status); 17 are feasible. The best feasible subset in the table is "
  "{1, 4, 5} = Medical kit + Blankets + Radio: weight 9, value 20 (e.g. {1,3}: 9 kg → 18; {3,4,5}: 10 kg → 18; {1,2}: 10 kg → 17). "
  "The algorithm returned value 20 with exactly this subset, examined 32 candidates and found 17 feasible. A further cross-check on 200 random instances (n ≤ 12) against an independent dynamic-programming "
  "optimum produced 0 mismatches.")
H("6.3 Growth investigation", 2)
P("**Prediction before experimenting:** each package is independently in or out, so the number of candidates is 2×2×…×2 = 2ⁿ. One extra package doubles the search space, two extra packages "
  "quadruple it, ten extra multiply it by 1,024. Because each candidate needs about n item checks, the work is ≈ n·2ⁿ, so +2 packages should multiply the time by a little more than 4.")
rows = [[r[0], fmt(r[1]), fmt(r[2]), fmt(r[3]), fmt(r[4]), "%.3f" % float(r[5]), fmt(r[6])] for r in rd("Q6", "q6_growth.csv")[1:]]
TABLE(["n", "Candidates examined", "2ⁿ", "Feasible", "Item checks (n·2ⁿ)", "Time (s)", "Best value"], rows, widths=[0.4, 1.2, 1.0, 1.0, 1.3, 0.8, 0.8], size=8.5)
IMG(out("Q6", "q6_graph_growth.png"), 6.5, "Figure 6.1 – Candidates (theory vs measured), execution time with 10-s limit, fraction of feasible candidates")
B("Candidates examined = 2ⁿ exactly for all seven sizes (8 to 22); every optimum equalled the dynamic-programming optimum. Each +2 packages multiplied the candidates by exactly 4.0 and the item checks by 4.4–5.0; the measured time by roughly 4–5 (see the Time column).")
B("About half of all subsets are feasible when the limit is half of the total weight, so feasibility alone does not remove a significant part of the search space: the algorithm still generates and weighs the infeasible half.")
H("6.4 Inquiry – why does a small increase in packages cause a dramatic increase in effort?", 2)
P("Because the size of the problem input grows linearly (n items) while the size of the solution space grows exponentially: it is multiplied by 2 for each new package, not increased by a fixed amount. "
  "Each new package can be combined with every one of the existing 2ⁿ subsets, once loaded and once left out, so adding a package creates as many new candidates as there were before. "
  "The effort per candidate is small and constant (about 1.7 µs here), so the dramatic growth comes entirely from the number of candidates: 2²² ≈ 4.2 million at n = 22, but 2³⁰ ≈ 1.07 billion at n = 30 (256× more for only eight more packages) and 2⁵⁰ ≈ 1.1×10¹⁵ at n = 50. "
  "Intuition about ‘a few more packages’ is linear, and exponential growth defeats it. Faster hardware does not help much either: a machine 100× faster adds only log₂100 ≈ 6.6 packages.")
H("6.5 Deployment decision", 2)
c6 = grab("Q6", r"c = ([\d.e+-]+) s ;")
P("**Chosen fixed response time: 10 seconds.** A loading plan is prepared before take-off, so a planner can wait a few seconds, but the plan must be re-run several times as packages arrive or the "
  "payload limit changes; beyond about 10 s this ‘what-if’ loop becomes too slow in an emergency.")
rows = []
for n in (20, 21, 22, 23, 24, 26, 30, 40, 50):
    t = c6 * n * 2 ** n
    ts = "%.1f s" % t if t < 120 else ("%.1f min" % (t / 60) if t < 7200 else ("%.1f h" % (t / 3600) if t < 86400 else ("%.1f days" % (t / 86400) if t < 3.15e7 else "%.1e years" % (t / 3.15e7))))
    meas = {r[0]: "%.2f s" % float(r[5]) for r in rd("Q6", "q6_growth.csv")[1:]}
    rows.append([n, fmt(2 ** n), meas.get(str(n), "—"), ts, "within 10 s" if t <= 10 else "too slow"])
TABLE(["n", "Candidates", "Measured time", "Predicted time = c·n·2ⁿ", "Verdict"], rows, widths=[0.5, 1.6, 1.2, 1.9, 1.1], size=8.5)
P("The model was validated at n = 22 (predicted ≈ 7.2 s, measured ≈ 7.7 s). **Decision: I would deploy the exhaustive solution for at most 21 packages** (≈ %.1f s predicted – a %.1f× safety margin for slower machines and "
  "heavier inputs)" % (c6*21*2**21, 10/(c6*21*2**21)) + ". n = 22 passes on this machine but leaves only ≈ 25% margin, and n = 24 (≈ 31 s) fails. For larger loads a different strategy that reduces the candidate set (e.g. pruning "
  "partial selections that already exceed the limit, or a dynamic-programming formulation) is required; compiled code would move the boundary only to about 28 packages.")
PB()

# =============================================================== Q7
H("Q7 – Day-4 Design Challenge: Diagnose, Redesign and Validate (13 marks)", 1)
P("**Selected solution: Q4 Brute-Force Closest Pair** (drone collision-risk monitoring). It shows the clearest limitation as n grows: quadratic growth that reaches the 1-second limit at ≈ 4,300 drones, "
  "and the evidence of Q4 already points to the cause.")
H("A. Diagnose the computational bottleneck (2 marks)", 2)
rows = [[fmt(r[0]), fmt(r[1]), r[2], "%.4f%%" % (100 * int(r[2]) / int(r[1])), fmt(r[3]), "%.2f%%" % (100 * int(r[3]) / int(r[1])), "%.3f" % float(r[4])] for r in rd("Q7", "q7_diagnosis.csv")[1:]]
TABLE(["n", "Distance calcs", "Times best improved", "Useful evaluations", "Pairs with |Δx| ≥ d_min", "% of all pairs", "Time (s)"], rows,
      widths=[0.5, 1.0, 0.9, 0.9, 1.2, 0.9, 0.7], size=8.5)
B("**Where the effort is spent:** 100% in the double loop – one distance evaluation per pair; there is no other phase.")
B("**Which operation grows:** distance evaluations, n(n−1)/2, quadratic (measured exponent ≈ 2.0 in Q4).")
B("**Unnecessary / repeated work:** yes. The best distance improved only 8–19 times in 0.12–8 million evaluations (< 0.02% useful), and **99.7–100% of all pairs already differ by at least the final minimum distance in the x-coordinate alone**, "
  "so they provably cannot be the closest pair and could have been rejected without computing a distance.")
B("**Characteristic of the original algorithm that causes this:** the set of candidates is fixed by n and does not depend on where the drones are; the algorithm is blind to geometry and never uses the best distance found so far to discard anything. "
  "Information from one comparison is not reused for others.")
H("B. Design objective (2 marks)", 2)
P("The redesign must discard pairs that cannot beat the current best distance, by exploiting ordering/locality of the data, and remain exact. Measurable objectives:")
TABLE(["ID", "Objective", "Measure"], [
    ["O1", "Exactness – identical minimum distance to the original on every test", "assert on all datasets"],
    ["O2", "Reduce distance calculations by ≥ 99% at n = 2000 (uniform)", "1,999,000 → ≤ 19,990"],
    ["O3", "Sub-quadratic growth of the work", "log–log slope < 1.5 (original 2.0)"],
    ["O4", "Execution time (including preprocessing) ≥ 10× faster at n = 4000", "seconds, same machine"],
    ["O5", "Degenerate / adversarial layouts must be identified, not hidden", "dedicated datasets"],
], widths=[0.5, 4.0, 2.1], size=9)
H("C. Revised computational strategy (4 marks)", 2)
P("**Design idea R1 – sorted sweep with pruning.** For any two drones the Euclidean distance is at least the difference of their x-coordinates (or y-coordinates). So if the drones are ordered along one axis and the "
  "gap along that axis between drone i and a later drone j is already ≥ the best distance found so far, then j and every drone after j are too far away to improve the answer – the inner loop can stop. "
  "This is derived from the diagnosis (the |Δx| ≥ d_min observation), not copied from a named algorithm.")
CODE("""SweepClosestPair(D):
    ax ← axis with the larger spread (max−min)          // preprocessing: 4(n−1) comparisons
    S  ← D sorted by coordinate ax                      // preprocessing: ≈ n·log2 n comparisons, O(n) memory
    best ← ∞
    for i ← 0..n-2:
        for j ← i+1..n-1:
            gap ← S[j].ax − S[i].ax                     // one cheap check instead of a distance
            if gap² ≥ best: break                       // all later j are even farther along ax
            d ← squared distance(S[i], S[j]) ; if d < best: best ← d""")
TABLE(["Question in the brief", "Answer for R1"], [
    ["What changed?", "Candidate pairs are no longer all C(n,2); each drone is compared only with its successors inside a shrinking window."],
    ["Which property is exploited?", "Ordering along one axis + the triangle-type bound distance ≥ |coordinate gap| + the continuously improving best distance."],
    ["Which operations are avoided?", "Distance calculations for pairs outside the window (> 99.8% of them)."],
    ["Preprocessing?", "Yes: sort along the widest axis, ≈ n·log₂n comparisons (27,291 at n = 2000) plus a spread check."],
    ["Extra memory?", "O(n) – a sorted copy (or index array) of the drones."],
    ["New trade-offs?", "(i) Preprocessing cost can dominate for tiny n; (ii) worst case is still Θ(n²) for layouts where many drones share nearly equal coordinates on the chosen axis; (iii) the axis choice matters; (iv) slightly more complex code."],
], widths=[1.9, 4.7], size=8.5)
P("**Extension R2 – spatial grid (locality).** Drones are hashed into square cells of side ≈ √(area/n); an upper bound on the answer is first taken from the n−1 consecutive pairs; each drone is then compared only with drones in "
  "the cells within ⌈√best / side⌉ cells. Preprocessing O(n), memory O(n). R2 is a second prototype that tests whether a different property (nearness instead of order) removes the weakness of R1.")
H("D. Predictions made before testing the redesign (1 mark)", 2)
TABLE(["#", "Prediction (written before running R1/R2)", "Measure"], [
    ["P1", "On uniform data R1 needs ~10–30 distance calculations per drone (≈ 20,000–60,000 at n = 2000, ≥ 97% fewer)", "distance calculations"],
    ["P2", "R1's total operations are dominated by the sorting step, ≈ n·log₂n", "comparison counts"],
    ["P3", "Time at n = 4000 improves ≈ 20–50×, and the advantage grows with n", "seconds"],
    ["P4", "Clustered data: R1 still helps but less (many drones inside the pruning window)", "distance calculations"],
    ["P5", "Sweeping on a fixed x-axis over a narrow vertical corridor will not prune (≈ n²); the widest-axis choice repairs it", "distance calculations"],
    ["P6", "R2 is excellent on uniform data but degrades on clustered data (cell size tuned to average density)", "distance calculations"],
    ["P7", "For very small n (< ≈ 30) the original is as fast or faster", "time per call"],
], widths=[0.4, 4.9, 1.3], size=8.5)
H("E. Implement and validate (2 marks)", 2)
P("Same test conditions: the uniform data are generated by the Q4 generator with the same seeds; every result of R1 and R2 was asserted equal to the brute-force minimum (all True). Key operations counted: sort comparisons, gap checks, distance calculations, cell lookups; times are additional evidence.")
res = rd("Q7", "q7_original_vs_redesign.csv")
hdr = res[0]
U = [r for r in res[1:] if r[0].startswith("U")]
rows = [[fmt(r[1]), fmt(r[2]), fmt(r[3]), fmt(r[4]), fmt(r[5]), "%.2f%%" % float(r[6]), fmt(r[8]), "%.4f" % float(r[10]), "%.4f" % float(r[11]), "%.4f" % float(r[12])] for r in U]
P("**Uniform random data (original → redesign):**", after=2)
TABLE(["n", "Original calcs", "R1 sort comps", "R1 gap checks", "R1 calcs", "R1 reduction", "R2 calcs", "t orig (s)", "t R1 (s)", "t R2 (s)"], rows,
      widths=[0.45, 0.85, 0.7, 0.7, 0.6, 0.65, 0.65, 0.6, 0.55, 0.55], size=7.5)
Cd = [r for r in res[1:] if r[0].startswith("C")]
rows = [[fmt(r[1]), fmt(r[2]), fmt(r[5]), "%.2f%%" % float(r[6]), fmt(r[8]), fmt(r[9]), "%.4f" % float(r[10]), "%.4f" % float(r[11]), "%.4f" % float(r[12])] for r in Cd]
P("**Clustered data (5 Gaussian clusters, σ = 150 m):**", after=2)
TABLE(["n", "Original calcs", "R1 calcs", "R1 reduction", "R2 calcs", "R2 max drones/cell", "t orig", "t R1", "t R2"], rows, widths=[0.5, 0.9, 0.7, 0.8, 0.8, 0.9, 0.6, 0.6, 0.6], size=8)
V1 = [r for r in res[1:] if r[0] == "V corridor fixed-x"]
V2 = [r for r in res[1:] if r[0] == "V corridor widest-axis"]
W = [r for r in res[1:] if r[0].startswith("W")]
rows = [[fmt(a[1]), fmt(a[2]), fmt(a[5]), fmt(b[5])] for a, b in zip(V1, V2)]
P("**Vertical corridor (x-spread 1 m) – effect of axis choice:**", after=2)
TABLE(["n", "Original calcs", "R1 sorted on fixed x-axis", "R1 on widest axis"], rows, widths=[0.7, 1.4, 2.0, 1.8], size=8.5)
rows = [[fmt(r[1]), fmt(r[2]), fmt(r[5]) + " (%.0f%%)" % (100 * int(r[5]) / int(r[2])), fmt(r[8]) + " (%.1f%%)" % (100 * int(r[8]) / int(r[2]))] for r in W]
P("**Adversarial data – two parallel vertical lines 10 km apart (y-spread 5 km):**", after=2)
TABLE(["n", "Original calcs", "R1 calcs (% of original)", "R2 calcs (% of original)"], rows, widths=[0.7, 1.4, 2.0, 1.8], size=8.5)
sm = rd("Q7", "q7_small_n_crossover.csv")
P("**Small inputs (time per call, µs):** " + "; ".join("n=%s: original %s, R1 %s" % (r[0], r[1], r[2]) for r in sm[1:]) + ". The original is faster up to n ≈ 10; R1 wins from n ≈ 20.")
IMG(out("Q7", "q7_graph_original_vs_redesign.png"), 6.6, "Figure 7.1 – Original versus redesign: operations, time and clustered-data behaviour")
H("F. Defend the final design (2 marks)", 2)
sp = grab("Q7", r"O4 speed-up at n=4000   : R1 ([\d.]+)x faster ; R2 ([\d.]+)x")
sp2 = grab("Q7", r"O4 speed-up at n=4000   : R1 ([\d.]+)x faster ; R2 ([\d.]+)x", 2)
TABLE(["Objective / prediction", "Result", "Verdict"], [
    ["O1 exactness", "All runs (uniform, clustered, corridor, two-lines, edge cases) equal the brute-force minimum", "Met"],
    ["O2 ≥99% fewer calcs at n=2000", "1,999,000 → 3,214 (99.84% fewer)", "Met"],
    ["O3 slope < 1.5", "Distance calcs slope 0.86; total key operations (sort + gaps + calcs) slope 1.06 (original 2.00)", "Met"],
    ["O4 ≥10× faster at n=4000", "R1 ≈ %.0f× faster, R2 ≈ %.0f× faster (0.8 s → ≈ 3 ms and ≈ 15 ms)" % (sp, sp2), "Met"],
    ["O5 degenerate inputs", "Corridor repaired by axis choice (593,180 → 55 calcs). Two-lines layout defeats R1 (50% of original, still quadratic); R2 handles it (3.4–9.7%)", "Partly: weakness identified"],
    ["P1 ~20–60k calcs at n=2000", "Observed 3,214 – much better than predicted (≈1.6 per drone)", "Direction right, magnitude wrong"],
    ["P2 sorting dominates", "Sort 27,291 vs gap checks 5,212 vs distance calcs 3,214 (≈ 76% of 35,717 operations)", "Supported"],
    ["P3 20–50× faster", "≈ 300× at n = 4000, and growing with n (≈ 600× at n = 8000)", "Supported, underestimated"],
    ["P4 clustered data helps less", "R1 reduction was 99.95% – as good as uniform", "NOT supported"],
    ["P5 fixed axis stays ≈ n²", "Fixed x-axis still did 7–35% of the original (not quite n²) but ≈ 10,000× more than widest-axis (593,180 vs 55 at n = 4000)", "Qualitatively supported, quantitatively wrong"],
    ["P6 grid degrades on clusters", "Grid needed 525,548 calcs vs 4,074 for R1 at n = 4000 (129×); on uniform data only 21,657", "Supported"],
    ["P7 original wins for tiny n", "Original faster for n ≤ 10, R1 faster from n = 20", "Supported"],
], widths=[1.8, 3.8, 1.0], size=8)
B("**Why P4 failed:** I assumed dense clusters put more drones inside the pruning window. But the window width is the best distance found so far, which shrinks automatically with local density – denser data gives a smaller "
  "window. The pruning rule adapts to density; what it cannot adapt to is many drones with the same coordinate on the sweep axis (the corridor and two-lines cases).")
B("**A lesson from the grid prototype:** my first version of R2 was only 1.1× faster at n = 4000 although it computed 99.7% fewer distances. The cause was a hidden O(n) `min(xs)` call recomputed for every drone – an operation my counters did not "
  "count. After moving it out of the loop R2 became ≈ 50× faster. Operation counts are only reliable evidence if they cover all the work.")
B("**Magnitude of improvement:** distance calculations fall by 96–99.97% (n = 100 – 8000); total key operations scale as n log n instead of n²; at 8,000 drones the original needs ≈ 3 s and R1 ≈ 5 ms. "
  "The 1-second acceptability limit moves from ≈ 4,300 drones to far beyond the largest size tested: R1 needed ≈ 5 ms at 8,000 drones and its operation count grows almost linearly (slope 1.06), so by extrapolation (not measured beyond 8,000) 100,000 drones would take well under a second.")
B("**New costs and trade-offs:** preprocessing (sort, n log₂n) and O(n) extra memory; the algorithm now depends on data layout – the two-parallel-lines input gives exactly 50% of the original work (still Θ(n²)), so R1 has no better worst-case guarantee than brute force "
  "for adversarial positions. R2 fixes that case but is sensitive to cell size and clustering and has more code and a hash structure.")
B("**When the original is still preferable:** very small fleets (n ≤ 10–15), where preprocessing costs more than it saves; when all pairwise distances are needed anyway; when simplicity and verifiability are more important than speed; and as a reference implementation for testing the faster ones (it was used as the oracle for every assertion in this assignment).")
B("**Does the redesign address the diagnosed limitation?** Yes for the layouts a drone fleet actually produces (random, clustered, corridor): the diagnosed cause – evaluating pairs that cannot matter – is removed and the objectives O1–O4 are met. "
  "It does not address adversarial layouts, so a production design should combine the sweep with a safeguard (axis selection, detection of high work counters, or a grid fallback).")
PB()

# =============================================================== Overall
H("Overall conclusions and recommendations", 1)
TABLE(["Q", "Main finding (evidence)", "Recommendation"], [
    ["Q1", "Predicted counts matched exactly (18/18). Selection ignores order; Bubble is hurt by late-arriving small elements (984 passes); Insertion costs n−1+inversions.", "Insertion Sort for a 95%-ordered stream; revisit if batches exceed ≈ 25% of the list."],
    ["Q2", "Cost p or n comparisons; work ∝ q·n; growth ×396 for ×20 records and ×20 requests, but still within a 10% CPU budget under stated assumptions.", "Sequential per facility; hash index on Tool ID for a central system."],
    ["Q3", "Same n and m: 9,993 vs 79,944 comparisons; alphabet size and repetition decide the work.", "Test with adversarial logs; do not rely on n and m alone."],
    ["Q4", "n(n−1)/2 exactly; time exponent ≈ 2.0; 1-s limit at ≈ 4,300 drones.", "Brute force only for small fleets; redesign beyond a few thousand drones."],
    ["Q5", "Edge test derived from half-plane geometry; full version exactly n(n−1)(n−2)/2; early exit does not change the order unless the scan order is randomised (slope 2.79 → 2.15).", "Brute-force hull only for small point sets (≈ a few hundred)."],
    ["Q6", "2ⁿ candidates, +2 packages ≈ ×4 time; 22 packages ≈ 7.7 s.", "Deploy for ≤ 21 packages; use pruning or DP beyond."],
    ["Q7", "Sorted sweep: 99.84% fewer distance calcs at n=2000, ≈ 300× faster at n=4000, sub-quadratic growth; weak on adversarial layouts; grid complements it.", "Adopt sweep with axis choice (+ grid fallback); keep brute force as test oracle and for tiny n."],
], widths=[0.4, 3.9, 2.3], size=8.5)
P("**Reflection.** In all seven questions operation counts predicted behaviour better than timing could, and the most valuable results were the ones where my prediction was wrong (early-exit hull growth, "
  "clustered-data pruning, the grid's hidden cost): each wrong prediction pointed to a property of the algorithm I had not understood. A brute-force algorithm is therefore not just a baseline to be replaced; "
  "its cost model tells us exactly which work to remove.")
PB()

# =============================================================== Appendix
H("Appendix A – Execution output screenshots", 1)
P("Terminal-style captures of the actual program output for each question (the full text is also stored as Qx_console_output.txt in every Output_Screenshots folder).", italic=True, size=9.5)
for qk in ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7"):
    H("Execution output – " + qk, 2)
    for f in sorted(glob.glob(out(qk, qk + "_execution_screenshot_p*.png"))):
        IMG(f, 6.3)
    PB()
H("Appendix B – Repository contents", 1)
CODE("""CO2_Assignment/
├── Q1_Sorting_Algorithms/        Pseudocode/  Implementation_Code/  Output_Screenshots/ (+ raw_data/)
├── Q2_Sequential_Search/         ...
├── Q3_Brute_Force_String_Matching/
├── Q4_Brute_Force_Closest_Pair/
├── Q5_Brute_Force_Convex_Hull/
├── Q6_Exhaustive_Search/
├── Q7_Day4_Design_Challenge/
├── Final_Report/CO2_Assignment_Report.docx
├── tools/render_screenshot.py    run_all.py    README.md""", size=9)

doc.save(os.path.join(ROOT, "Final_Report", "CO2_Assignment_Report.docx"))
print("saved")
