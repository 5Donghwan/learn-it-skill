"""Narration-synced Manim scene for the learn-it skill.

    from manim import *
    from narrated_scene import NarratedScene, KText

    class Explainer(NarratedScene):
        def construct(self):
            with self.narrate("s01") as seg:      # audio/s01.wav starts playing now
                self.play(Write(KText("제목")), run_time=min(2, seg.duration))
                self.play(..., run_time=seg.remaining())
            # leaving the block waits until s01 ends (plus a short pause)

Reads audio/manifest.json (written by tts.py); set NARRATION_MANIFEST to use another path.
Subtitles go into the .srt file that Manim writes next to the video.
After rendering, writes timeline.json (segment start/end times) for frames.py.
"""
from __future__ import annotations

import json
import os
import platform
import re
from contextlib import contextmanager
from pathlib import Path

from manim import Scene, Text, config

KFONT = os.environ.get("LEARN_KFONT") or ("Apple SD Gothic Neo" if platform.system() == "Darwin" else "Noto Sans CJK KR")
BACKGROUND = "#0f1117"


def KText(text: str, **kwargs) -> Text:
    """Text with a font that has Korean glyphs. Use it for all Korean on screen."""
    kwargs.setdefault("font", KFONT)
    return Text(text, **kwargs)


class Segment:
    def __init__(self, scene: Scene, entry: dict, base: Path):
        self.scene = scene
        self.id = entry["id"]
        self.text = entry["text"]
        self.file = str(base / entry["file"])
        self.duration = float(entry["duration"])
        self.start = scene.renderer.time
        self.sentences: list[tuple[str, float, float]] = []  # (text, offset, duration), filled by narrate()

    def elapsed(self) -> float:
        return self.scene.renderer.time - self.start

    def remaining(self, minimum: float = 0.3) -> float:
        """Seconds of narration left in this segment (at least `minimum`, so it is a valid run_time)."""
        return max(minimum, self.duration - self.elapsed())

    def sentence_start(self, i: int) -> float:
        """Estimated seconds from the segment start to sentence i (0-based), by character share."""
        return self.sentences[i][1]

    def wait_until(self, t: float) -> None:
        """Wait until t seconds after the segment started; do nothing if that time has passed."""
        gap = t - self.elapsed()
        if gap > 1 / config.frame_rate:
            self.scene.wait(gap)


class NarratedScene(Scene):
    pause_after = 0.4  # seconds of silence after each segment

    def setup(self):
        super().setup()
        self.camera.background_color = BACKGROUND
        path = Path(os.environ.get("NARRATION_MANIFEST", "audio/manifest.json")).resolve()
        data = json.loads(path.read_text(encoding="utf-8"))
        self._entries = {e["id"]: e for e in data["segments"]}
        self._base = path.parent
        self._timeline: list[dict] = []

    @contextmanager
    def narrate(self, seg_id: str, pause: float | None = None):
        if seg_id not in self._entries:
            raise KeyError(f"segment {seg_id!r} is not in the narration manifest")
        seg = Segment(self, self._entries[seg_id], self._base)
        self.add_sound(seg.file)
        self._add_subtitles(seg)
        yield seg
        left = seg.duration + (self.pause_after if pause is None else pause) - seg.elapsed()
        if left > 1 / config.frame_rate:
            self.wait(left)
        self._timeline.append({"id": seg.id, "text": seg.text, "start": round(seg.start, 3),
                               "end": round(seg.start + seg.duration, 3)})

    def _add_subtitles(self, seg: Segment) -> None:
        # One subtitle per sentence; each gets a share of the audio time by its length.
        parts = [p.strip() for p in re.split(r"(?<=[.!?。？！])\s+", seg.text) if p.strip()]
        total = sum(len(p) for p in parts) or 1
        offset = 0.0
        for p in parts:
            share = seg.duration * len(p) / total
            self.add_subcaption(p, duration=share, offset=offset)
            seg.sentences.append((p, offset, share))
            offset += share

    def tear_down(self):
        super().tear_down()
        used = {t["id"] for t in self._timeline}
        unused = [k for k in self._entries if k not in used]
        if unused:
            print(f"[narrated_scene] segments never narrated: {', '.join(unused)}")
        Path("timeline.json").write_text(json.dumps(self._timeline, ensure_ascii=False, indent=2), encoding="utf-8")
