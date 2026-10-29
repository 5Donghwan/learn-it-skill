#!/usr/bin/env python3
"""Render an SVG to PNG at its real aspect ratio, to check a diagram by eye.

    python3 svg_preview.py diagram.svg [--out check/diagram.png] [--width 1600] [--dark]

Uses headless Chrome (a throwaway profile; the user's profile is never touched), so the result matches
what a browser shows. Without Chrome it falls back to macOS qlmanage, which makes a square thumbnail:
then the SVG must have a viewBox and no fixed width/height, or qlmanage crops it without warning.
Standard library only.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
]


def svg_size(svg: str) -> tuple[float, float]:
    vb = re.search(r'viewBox="\s*[-\d.]+[\s,]+[-\d.]+[\s,]+([\d.]+)[\s,]+([\d.]+)', svg)
    if vb:
        return float(vb.group(1)), float(vb.group(2))
    w = re.search(r'<svg[^>]*\swidth="([\d.]+)', svg)
    h = re.search(r'<svg[^>]*\sheight="([\d.]+)', svg)
    if w and h:
        return float(w.group(1)), float(h.group(1))
    sys.exit("the SVG has neither a viewBox nor width/height; add a viewBox")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("svg", type=Path)
    ap.add_argument("--out", type=Path, help="PNG path (default: check/<name>.png next to the SVG)")
    ap.add_argument("--width", type=int, default=1600, help="PNG width in pixels")
    ap.add_argument("--dark", action="store_true", help="dark page background, to check a dark-theme diagram")
    args = ap.parse_args()

    svg_path = args.svg.resolve()
    out = (args.out or svg_path.parent / "check" / (svg_path.stem + ".png")).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    vw, vh = svg_size(svg_path.read_text(encoding="utf-8"))
    width = args.width
    height = max(1, round(width * vh / vw))

    chrome = next((c for c in CHROME_CANDIDATES if c and Path(c).exists()), None)
    if chrome:
        bg = "#111318" if args.dark else "#ffffff"
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "preview.html"
            page.write_text(
                f'<!doctype html><meta charset="utf-8"><style>html,body{{margin:0;background:{bg}}}'
                f"img{{display:block;width:{width}px;height:{height}px}}</style>"
                f'<img src="{svg_path.as_uri()}">',
                encoding="utf-8",
            )
            subprocess.run(
                [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={tmp}/profile",
                 "--allow-file-access-from-files", f"--window-size={width},{height}",
                 "--virtual-time-budget=2000", f"--screenshot={out}", page.as_uri()],
                check=True, capture_output=True,
            )
    elif shutil.which("qlmanage"):
        print("Chrome not found; using qlmanage (square thumbnail; needs a viewBox and no fixed width/height)")
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["qlmanage", "-t", "-s", str(width), "-o", tmp, str(svg_path)], check=True, capture_output=True)
            shutil.move(str(Path(tmp) / (svg_path.name + ".png")), out)
    else:
        sys.exit("no renderer found: install Google Chrome, or view the SVG in a browser")
    print(f"{out}  ({width}x{height}; SVG is {vw:g}x{vh:g})")


if __name__ == "__main__":
    main()
