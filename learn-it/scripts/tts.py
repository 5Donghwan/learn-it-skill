#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["supertonic>=1.3", "edge-tts>=7", "av>=12"]
# ///
"""Make narration audio for a learn-it skill video.

    uv run tts.py script.json --out audio [--engine auto|elevenlabs|supertonic|edge|say]
                                          [--voice NAME] [--speed 1.0]

script.json:
    {"lang": "ko", "segments": [{"id": "s01", "text": "subtitle text",
                                 "speech": "optional: what the TTS reads instead"}]}

Writes <out>/<id>.wav (16-bit PCM, mono) and <out>/manifest.json:
    {"engine", "voice", "lang", "speed", "total_duration",
     "segments": [{"id", "text", "file", "duration", "hash"}]}

A segment is generated again only when its spoken text, engine, voice, or speed changed.
Silence at both ends of each clip is trimmed (0.1 s lead and 0.25 s tail are kept), so the
scene's own pause_after sets the gap between segments and `duration` is the speech itself.
Auto order: elevenlabs (when ELEVENLABS_API_KEY is set) -> supertonic (local) -> edge (online) -> say (macOS).
"""
from __future__ import annotations

import argparse
import array
import asyncio
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import wave
from pathlib import Path

DEFAULT_VOICES = {
    "elevenlabs": {"*": os.environ.get("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")},
    "supertonic": {"*": "M1"},
    "edge": {"ko": "ko-KR-SunHiNeural", "*": "en-US-AndrewMultilingualNeural"},
    "say": {"ko": "Yuna", "*": "Samantha"},
}


def default_voice(engine: str, lang: str) -> str:
    table = DEFAULT_VOICES[engine]
    return table.get(lang, table["*"])


def wav_duration(path: Path) -> float:
    with wave.open(str(path)) as w:
        return w.getnframes() / w.getframerate()


def write_pcm_wav(path: Path, pcm: bytes, rate: int) -> None:
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm)


def trim_silence(path: Path, lead: float = 0.1, tail: float = 0.25, threshold_db: float = -40.0) -> None:
    """Cut the silence at both ends of a 16-bit mono WAV, keeping a short lead and tail."""
    with wave.open(str(path)) as w:
        rate, width, channels = w.getframerate(), w.getsampwidth(), w.getnchannels()
        samples = array.array("h", w.readframes(w.getnframes()))
    if width != 2 or channels != 1 or not samples:
        return
    if sys.byteorder == "big":
        samples.byteswap()
    limit = 32768 * 10 ** (threshold_db / 20)
    window = max(1, rate // 100)  # 10 ms
    loud = [i for i in range(0, len(samples), window) if max(map(abs, samples[i:i + window])) > limit]
    if not loud:
        return
    start = max(0, loud[0] - int(lead * rate))
    end = min(len(samples), loud[-1] + window + int(tail * rate))
    kept = samples[start:end]
    if sys.byteorder == "big":
        kept.byteswap()
    write_pcm_wav(path, kept.tobytes(), rate)


def to_wav(src: Path, dst: Path, rate: int = 24000) -> None:
    """Decode any audio file to 16-bit mono WAV with PyAV (no ffmpeg binary needed)."""
    import av

    resampler = av.AudioResampler(format="s16", layout="mono", rate=rate)
    with av.open(str(src)) as inp, wave.open(str(dst), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        for frame in inp.decode(audio=0):
            for f in resampler.resample(frame):
                w.writeframes(f.to_ndarray().tobytes())
        for f in resampler.resample(None):
            w.writeframes(f.to_ndarray().tobytes())


class ElevenLabs:
    rate = 24000  # pcm_44100 needs a Pro plan; pcm_24000 works on every plan

    def __init__(self, voice: str, lang: str, speed: float):
        self.key = os.environ.get("ELEVENLABS_API_KEY")
        if not self.key:
            raise RuntimeError("ELEVENLABS_API_KEY is not set")
        self.voice, self.speed = voice, speed
        self.model = os.environ.get("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")

    def __call__(self, text: str, out: Path) -> None:
        body = {"text": text, "model_id": self.model}
        if self.speed != 1.0:
            body["voice_settings"] = {"speed": self.speed}
        req = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice}?output_format=pcm_{self.rate}",
            data=json.dumps(body).encode(),
            headers={"xi-api-key": self.key, "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                pcm = r.read()
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"ElevenLabs HTTP {e.code}: {e.read()[:300]!r}") from None
        write_pcm_wav(out, pcm, self.rate)


class Supertonic:
    def __init__(self, voice: str, lang: str, speed: float):
        from supertonic import TTS  # first use downloads the model (~400 MB) to ~/.cache

        self.tts = TTS(auto_download=True)
        self.style = self.tts.get_voice_style(voice)
        self.lang, self.speed = lang, 1.05 * speed

    def __call__(self, text: str, out: Path) -> None:
        wav, _ = self.tts.synthesize(text, voice_style=self.style, speed=self.speed, lang=self.lang)
        self.tts.save_audio(wav, str(out))


class Edge:
    def __init__(self, voice: str, lang: str, speed: float):
        import edge_tts  # noqa: F401  (fail early if missing)

        self.voice = voice
        self.rate = f"{round((speed - 1) * 100):+d}%"

    def __call__(self, text: str, out: Path) -> None:
        import edge_tts

        mp3 = out.with_suffix(".mp3")
        asyncio.run(edge_tts.Communicate(text, self.voice, rate=self.rate).save(str(mp3)))
        to_wav(mp3, out)
        mp3.unlink()


class Say:
    def __init__(self, voice: str, lang: str, speed: float):
        if not shutil.which("say"):
            raise RuntimeError("the macOS 'say' command is not available")
        self.cmd = ["say", "-v", voice] + (["-r", str(round(180 * speed))] if speed != 1.0 else [])

    def __call__(self, text: str, out: Path) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write(text)
        try:
            subprocess.run(
                self.cmd + ["-f", f.name, "-o", str(out), "--file-format=WAVE", "--data-format=LEI16@22050"],
                check=True,
            )
        finally:
            os.unlink(f.name)


ENGINES = {"elevenlabs": ElevenLabs, "supertonic": Supertonic, "edge": Edge, "say": Say}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("script", type=Path)
    ap.add_argument("--out", type=Path, default=Path("audio"))
    ap.add_argument("--engine", default="auto", choices=["auto", *ENGINES])
    ap.add_argument("--voice", help="voice for the engine (with --engine auto: for the first engine tried)")
    ap.add_argument("--speed", type=float, default=1.0, help="1.0 = normal, 1.1 = 10%% faster")
    args = ap.parse_args()

    data = json.loads(args.script.read_text(encoding="utf-8"))
    lang = data.get("lang", "ko")
    segments = data["segments"]
    ids = [s["id"] for s in segments]
    if len(ids) != len(set(ids)):
        sys.exit("segment ids must be unique")

    args.out.mkdir(parents=True, exist_ok=True)
    manifest_path = args.out / "manifest.json"
    previous = {}
    if manifest_path.exists():
        previous = {s["id"]: s for s in json.loads(manifest_path.read_text(encoding="utf-8"))["segments"]}

    if args.engine == "auto":
        order = (["elevenlabs"] if os.environ.get("ELEVENLABS_API_KEY") else []) + ["supertonic", "edge", "say"]
    else:
        order = [args.engine]

    chars = sum(len(s.get("speech") or s["text"]) for s in segments)
    print(f"{len(segments)} segments, {chars} characters to speak", file=sys.stderr)

    for i, engine in enumerate(order):
        voice = args.voice if (args.voice and i == 0) else default_voice(engine, lang)
        try:
            synth = None
            entries = []
            for s in segments:
                speech = s.get("speech") or s["text"]
                digest = hashlib.sha1(f"{engine}|{voice}|{args.speed}|trim1|{speech}".encode()).hexdigest()[:12]
                wav = args.out / f"{s['id']}.wav"
                old = previous.get(s["id"])
                if not (old and old.get("hash") == digest and wav.exists()):
                    synth = synth or ENGINES[engine](voice, lang, args.speed)
                    synth(speech, wav)
                    trim_silence(wav)
                duration = round(wav_duration(wav), 3)
                entries.append({"id": s["id"], "text": s["text"], "file": wav.name, "duration": duration, "hash": digest})
                print(f"  {s['id']}: {duration:5.1f}s", file=sys.stderr)
            break
        except Exception as e:  # fall back to the next engine, with a consistent voice for every segment
            print(f"[{engine}] failed: {type(e).__name__}: {e}", file=sys.stderr)
            if engine == order[-1]:
                sys.exit("no TTS engine worked")
    total = round(sum(e["duration"] for e in entries), 2)
    manifest = {"engine": engine, "voice": voice, "lang": lang, "speed": args.speed,
                "total_duration": total, "segments": entries}
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"engine={engine} voice={voice} total={total:.1f}s -> {manifest_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
