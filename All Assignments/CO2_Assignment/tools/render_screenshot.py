"""Render captured console output as terminal-style PNG 'screenshots'.
Usage: python render_screenshot.py output.txt "command shown in title bar" out_prefix [lines_per_page]
"""
import sys
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def render(txt_path, command, prefix, per_page=48):
    lines = open(txt_path, encoding="utf-8").read().replace("\t", "    ").split("\n")
    while lines and not lines[-1].strip():
        lines.pop()
    font = ImageFont.truetype(FONT, 14)
    bold = ImageFont.truetype(FONT.replace("Mono.ttf", "Mono-Bold.ttf"), 14)
    cw = font.getlength("M")
    lh = 19
    width = int(min(max(max(len(l) for l in lines), len(command) + 12), 175) * cw) + 40
    pages = [lines[i:i + per_page] for i in range(0, len(lines), per_page)]
    out = []
    for pi, pg in enumerate(pages, 1):
        h = 40 + 34 + lh * (len(pg) + 2) + 20
        img = Image.new("RGB", (width, h), "#1e1e1e")
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, width, 30], fill="#3a3a3a")
        for k, col in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
            d.ellipse([12 + 22 * k, 9, 24 + 22 * k, 21], fill=col)
        d.text((90, 7), "Terminal  -  page %d/%d" % (pi, len(pages)), font=font, fill="#cccccc")
        y = 40
        d.text((14, y), "$ " + command, font=bold, fill="#7ee787")
        y += 34
        for l in pg:
            col = "#d4d4d4"
            s = l.strip()
            if s.startswith(("=", "#")) or s.isupper():
                col = "#79c0ff"
            d.text((14, y), l[:175], font=font, fill=col)
            y += lh
        name = "%s_p%d.png" % (prefix, pi)
        img.save(name)
        out.append(name)
    return out


if __name__ == "__main__":
    n = int(sys.argv[4]) if len(sys.argv) > 4 else 48
    for f in render(sys.argv[1], sys.argv[2], sys.argv[3], n):
        print(f)
