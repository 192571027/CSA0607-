"""make_screenshots.py - renders source files and captured console output as PNG images
(for the report). Replace with real terminal screenshots from your own machine if preferred."""
import os, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def render(text, path, title, max_lines=None, bg=(30, 30, 30), fg=(220, 220, 220), size=15):
    lines = text.rstrip().split("\n")
    if max_lines:
        lines = lines[:max_lines]
    f = ImageFont.truetype(FONT, size)
    lh = size + 5
    w = max(60, min(max(len(l) for l in lines), 130)) * (size * 0.6) + 40
    h = lh * len(lines) + 70
    img = Image.new("RGB", (int(w), int(h)), bg)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w, 30], fill=(60, 60, 60))
    for i, c in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))):
        d.ellipse([10 + i * 20, 9, 22 + i * 20, 21], fill=c)
    d.text((80, 7), title, font=ImageFont.truetype(FONT, 13), fill=(200, 200, 200))
    y = 42
    for l in lines:
        d.text((20, y), l[:130], font=f, fill=fg)
        y += lh
    img.save(path)


def read(p):
    return open(os.path.join(ROOT, p)).read()


out = os.path.join(ROOT, "Report", "Output_Screenshots")
src = os.path.join(ROOT, "Report", "Source_Code_Screenshots")
render("$ python test_algorithms.py\n" + open("/tmp/test_out.txt").read(), os.path.join(out, "output_unit_tests.png"), "terminal - unit tests", size=14)
render("$ python run_experiments.py\n" + open("/tmp/run_out.txt").read(), os.path.join(out, "output_experiments.png"), "terminal - run_experiments.py", size=14)
import json
D = json.load(open(os.path.join(ROOT, "Task_12_Design_Challenge", "design_challenge_results.json")))
dc = ["$ python design_challenge.py   (summary)", ""]
dc.append(f"One hour of traffic = {D['requests_per_hour']:,} searches on n = {D['n']:,}   ({D['requests_per_second']:.1f} req/s)")
for k in ("linear", "binary", "hash"):
    x = D[k]
    dc.append(f"  {k:7s} mean {x['mean_us']:>10.2f} us  p50 {x['p50_us']:>10.2f}  p99 {x['p99_us']:>10.2f}  max {x['max_us']:>10.1f}  "
              f"hour {x['hour_s']:>8.2f} s  ({x['cpu_utilisation_pct']:.3f}% of 1 core)")
dc.append("")
dc.append(f"Preprocessing: merge sort {D['sort_s']:.2f} s | hash build {D['hash_build_s']:.2f} s")
dc.append(f"Daily update with {D['new_records_per_day']:,} new records:")
for k, v in D["daily_update"].items():
    dc.append(f"  {k:30s} {v:8.3f} s")
dc.append(f"Searches needed to amortise sort: {D['break_even']['searches_to_amortise_sort']:.0f} | hash build: {D['break_even']['searches_to_amortise_hash']:.0f}")
render("\n".join(dc), os.path.join(out, "output_design_challenge.png"), "terminal - design_challenge.py", size=14)

for name, rel in (("algorithms", "Task_8_Implementation_Testing/Source_Code/algorithms.py"),
                  ("tests", "Task_8_Implementation_Testing/Source_Code/test_algorithms.py"),
                  ("experiments", "Task_8_Implementation_Testing/Source_Code/run_experiments.py")):
    lines = read(rel).split("\n")
    # split long files into chunks of 55 lines so text stays legible
    for part, start in enumerate(range(0, len(lines), 55), 1):
        render("\n".join(f"{start + i + 1:3d}  {l}" for i, l in enumerate(lines[start:start + 55])),
               os.path.join(src, f"src_{name}_{part}.png"), os.path.basename(rel), size=14)
print("screenshots written")
