#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["av>=12", "pillow>=10"]
# ///
"""Make a contact sheet of video frames, to check the layout by eye.

    uv run frames.py video.mp4 [--timeline timeline.json] [--at end|mid|both] [--n 12] [--out frames]

With timeline.json (written by NarratedScene in the folder you rendered from), it takes one frame per
narration segment: by default at the segment's end, where the layout is fullest and overlaps show
(--at mid catches animations in progress; --at both does both). Without a timeline: --n evenly spaced frames.
Writes <out>/NN_<seconds>s.png and <out>/sheet.png (a labeled grid).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import av
from PIL import Image, ImageDraw, ImageFont

FONT_CANDIDATES = [
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]


def load_font(size: int):
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def grab(video: Path, times: list[float]) -> list[Image.Image]:
    images = []
    with av.open(str(video)) as container:
        stream = container.streams.video[0]
        for t in times:
            container.seek(int(t / stream.time_base), stream=stream, backward=True)
            image = None
            for frame in container.decode(stream):
                image = frame.to_image()
                if frame.time is not None and frame.time >= t:
                    break
            images.append(image)
    return images


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", type=Path)
    ap.add_argument("--timeline", type=Path, default=Path("timeline.json"))
    ap.add_argument("--at", choices=["end", "mid", "both"], default="end", help="where in each segment to sample")
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--out", type=Path, default=Path("frames"))
    ap.add_argument("--tile", type=int, default=640, help="tile width in the sheet")
    args = ap.parse_args()

    with av.open(str(args.video)) as c:
        duration = float(c.duration / av.time_base) if c.duration else 0.0

    if args.timeline.exists():
        timeline = json.loads(args.timeline.read_text(encoding="utf-8"))
        picks = []
        for i, t in enumerate(timeline):
            label = f'{t["id"]}  {t["text"][:28]}'
            next_start = timeline[i + 1]["start"] if i + 1 < len(timeline) else duration
            if args.at in ("mid", "both"):
                picks.append(((t["start"] + t["end"]) / 2, ("mid " if args.at == "both" else "") + label))
            if args.at in ("end", "both"):
                picks.append((max(t["start"], min(t["end"], next_start) - 0.05), ("end " if args.at == "both" else "") + label))
        picks.append((max(0.0, duration - 0.1), "last frame"))
    else:
        picks = [(duration * (i + 0.5) / args.n, "") for i in range(args.n)]

    args.out.mkdir(parents=True, exist_ok=True)
    images = grab(args.video, [t for t, _ in picks])

    font = load_font(18)
    cols = 3
    tile_w = args.tile
    first = next(im for im in images if im is not None)
    tile_h = round(first.height * tile_w / first.width)
    label_h = 30
    rows = -(-len(images) // cols)
    sheet = Image.new("RGB", (cols * tile_w, rows * (tile_h + label_h)), "white")
    draw = ImageDraw.Draw(sheet)
    for i, ((t, label), im) in enumerate(zip(picks, images)):
        if im is None:
            continue
        im.save(args.out / f"{i:02d}_{t:06.1f}s.png")
        x, y = (i % cols) * tile_w, (i // cols) * (tile_h + label_h)
        sheet.paste(im.resize((tile_w, tile_h)), (x, y + label_h))
        draw.text((x + 6, y + 5), f"{i:02d} · {int(t // 60)}:{t % 60:04.1f}  {label}", fill="black", font=font)
    sheet.save(args.out / "sheet.png")
    print(args.out / "sheet.png")


if __name__ == "__main__":
    main()
