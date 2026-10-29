#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["imageio-ffmpeg>=0.5"]
# ///
"""Copy the rendered video to its final place and embed its subtitles as a selectable track.

    uv run finalize.py media/videos/scene/1080p60/Explainer.mp4 --out ~/learn/2026-10-22-topic/topic.mp4

Uses the .srt that Manim wrote next to the video (or --srt). The subtitle track shows in
QuickTime (View > Subtitles), IINA, and VLC. A copy of the .srt is kept next to the output.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

import imageio_ffmpeg


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--srt", type=Path)
    ap.add_argument("--lang", default="kor", help="ISO 639-2 code of the subtitles (kor, eng, ...)")
    args = ap.parse_args()

    srt = args.srt or args.video.with_suffix(".srt")
    out = args.out.expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    if srt.exists() and srt.stat().st_size > 0:
        subprocess.run(
            [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-i", str(args.video), "-i", str(srt),
             "-map", "0", "-map", "1", "-c", "copy", "-c:s", "mov_text",
             "-metadata:s:s:0", f"language={args.lang}", str(out)],
            check=True,
        )
        shutil.copy(srt, out.with_suffix(".srt"))
    else:
        shutil.copy(args.video, out)
    print(out)


if __name__ == "__main__":
    main()
