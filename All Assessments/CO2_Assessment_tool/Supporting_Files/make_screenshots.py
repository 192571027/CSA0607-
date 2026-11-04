"""
make_screenshots.py - renders source code and execution output to PNG images
("screenshots") for the report.  Code is syntax-highlighted with Pygments; terminal
output is drawn as a dark terminal window.  Run from Supporting_Files/:
    python make_screenshots.py
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont
from pygments import highlight
from pygments.formatters import ImageFormatter
from pygments.lexers import PythonLexer

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "Source_Code")
OUT = os.path.join(HERE, "..", "Report", "screenshots")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
os.makedirs(OUT, exist_ok=True)


def code_png(py_file, out_name, first=None, last=None):
    lines = open(os.path.join(SRC, py_file), encoding="utf-8").read().split("\n")
    start = (first or 1) - 1
    chunk = "\n".join(lines[start:last])
    fmt = ImageFormatter(font_name="DejaVu Sans Mono", font_size=15, line_numbers=True,
                         line_number_start=start + 1, style="default", image_pad=14,
                         line_number_bg="#f0f0f0", line_number_fg="#888888")
    with open(os.path.join(OUT, out_name), "wb") as f:
        f.write(highlight(chunk, PythonLexer(), fmt))


def terminal_png(command, text, out_name, max_lines=None):
    lines = text.rstrip("\n").split("\n")
    if max_lines:
        lines = lines[:max_lines]
    font = ImageFont.truetype(FONT, 15)
    cw = font.getbbox("M")[2]
    lh = 21
    width = max(max(len(l) for l in lines), len(command) + 2) * cw + 40
    height = (len(lines) + 2) * lh + 60
    img = Image.new("RGB", (width, height), "#1e1e1e")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, width, 30], fill="#3c3c3c")
    for k, c in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        d.ellipse([12 + k * 22, 9, 24 + k * 22, 21], fill=c)
    d.text((90, 7), "terminal - CO2_Debugging_Optimisation/Source_Code", font=ImageFont.truetype(FONT, 13), fill="#cccccc")
    y = 44
    d.text((16, y), "$ " + command, font=font, fill="#7ee787")
    y += lh + 4
    for l in lines:
        col = "#f85149" if "FAIL" in l else ("#7ee787" if "PASS" in l else "#e6e6e6")
        d.text((16, y), l, font=font, fill=col)
        y += lh
    img.save(os.path.join(OUT, out_name))


def run(cmd):
    return subprocess.run([sys.executable] + cmd.split()[1:], cwd=SRC, capture_output=True, text=True).stdout


if __name__ == "__main__":
    # --- source code screenshots
    code_png("original_sentinelops.py", "code_1_original_functions.png", 10, 49)
    code_png("corrected_sentinelops.py", "code_2_corrected_sort_blocklist.png", 28, 64)
    code_png("corrected_sentinelops.py", "code_3_corrected_signature_closest.png", 66, 110)
    code_png("optimised_sentinelops.py", "code_4_optimised_sort_blocklist.png", 30, 76)
    code_png("optimised_sentinelops.py", "code_5_optimised_signature.png", 81, 138)
    code_png("optimised_sentinelops.py", "code_6_optimised_closest.png", 143, 188)
    code_png("test_harness.py", "code_7_test_harness_excerpt.png", 85, 130)

    # --- execution screenshots
    terminal_png("python original_sentinelops.py", run("python original_sentinelops.py"), "out_1_original_run.png")
    terminal_png("python corrected_sentinelops.py", run("python corrected_sentinelops.py"), "out_2_corrected_run.png")
    terminal_png("python optimised_sentinelops.py", run("python optimised_sentinelops.py"), "out_3_optimised_run.png")
    dbg = run("python debug_session.py")
    terminal_png("python debug_session.py   (steps 0-2)", "\n".join(dbg.split("\n")[:46]), "out_4_debug_session_sort.png")
    harness = run("python test_harness.py")
    terminal_png("python test_harness.py   (summary)", "\n".join(harness.split("\n")[-14:]), "out_5_harness_summary.png")
    terminal_png("python test_harness.py   (ORIGINAL suite, first 40 lines)", "\n".join(harness.split("\n")[:44]), "out_6_harness_original_fails.png")
    exp = open(os.path.join(HERE, "experiments_run.log")).read()
    cl = exp.split("[4] closest_logins: distance computations")[1]
    short = []
    for l in cl.strip().split("\n"):
        short.append(l if len(l) < 150 else l[:147] + "...")
    terminal_png("python experiments.py   (closest_logins section)", "[4] closest_logins: distance computations\n" + "\n".join(short), "out_7_experiments_closest.png")
    print("screenshots written to", os.path.abspath(OUT))
