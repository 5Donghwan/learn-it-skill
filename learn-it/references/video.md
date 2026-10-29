# Narrated explainer video (3Blue1Brown style)

A video is worth its cost when the idea is a process that unfolds in time (an algorithm that runs, a protocol that exchanges messages, a function that changes shape) or math with a geometric picture. The pipeline:

storyboard → narration script → audio → Manim scene synced to the audio → draft render → look at frames → fix → final render → finish.

Everything runs through `uv` in isolated, cached environments. Nothing is installed system-wide. The scripts are in this skill's `scripts/` folder; below, `$S` means that folder (for example `~/.claude/skills/learn-it/scripts`). Work in `<output folder>/video/` and run every command from there.

## Contents

1. Check the environment
2. Storyboard
3. Narration script
4. Audio
5. Scene code
6. Render
7. Look at the frames
8. Finish and deliver
9. Manim pitfalls
10. Narration engines

## 1. Check the environment

```bash
bash $S/check_env.sh
```

It installs nothing. It reports what is present and what is missing. If a system package is missing, tell the user the exact command and ask before you install it. The first render after a cache reset downloads and builds Manim (1–3 minutes). Later renders start in seconds.

## 2. Storyboard (`storyboard.md`)

Plan 4–8 scenes for 2–5 minutes. For each scene, write the one idea, what the viewer sees (objects and motion), and what the narrator says.

The 3Blue1Brown principles that matter most:

- Open with a question or a puzzle, not a definition. The viewer must want the answer before they get it.
- Go from a concrete example to the general rule. Show small real numbers before symbols.
- One visual idea per scene. Clear the screen between ideas.
- Keep identity on screen. Transform an object into its next form (`Transform`, `ReplacementTransform`, `TransformMatchingTex`) instead of fading one out and another in, so the eye follows the idea.
- Color has a meaning and keeps it for the whole video (for example: secret = orange, public = blue).
- Put little text on screen. The narration carries the words; the screen carries shapes, labels, and equations.
- Pause after each key reveal (0.5–1 s of stillness).
- End with a recap of the core picture and one question to think about.

## 3. Narration script (`script.json`)

```json
{
  "lang": "ko",
  "segments": [
    {"id": "s01", "text": "두 사람이 도청되는 채널로 같은 비밀 키를 만들 수 있을까?"},
    {"id": "s02", "text": "앨리스는 g^a mod p를 보낸다.",
     "speech": "앨리스는 g의 a제곱을 p로 나눈 나머지를 보낸다."}
  ]
}
```

- One segment is one beat of the storyboard: usually 1–3 sentences, 5–20 s of audio.
- `text` becomes the subtitle. `speech` (optional) is what the TTS reads. Write formulas, symbols, abbreviations, and foreign names the way a person says them, because TTS engines read "g^a mod p" or "디피-헬먼" badly. Drop hyphens from spoken names ("디피 헬먼").
- Korean numbers in `speech`: write them in Hangul, the way they are read. Counters take native numerals ("세 번", "두 개", "열한 칸"). Math values and labels take Sino-Korean numerals ("오의 삼제곱", "이십삼"). A digit leaves the choice to the TTS, and it often picks the wrong one.
- Narration follows the STE rules in spoken form: short sentences, one idea each, the same term every time. Describe what is on screen now ("파란 점이 오른쪽으로 간다").
- Length: Korean TTS speaks about 7.5 characters per second (spaces included), and each segment adds a 0.4 s pause, so a 3-minute video is about 1,150 characters in about 20 segments. English is about 150 words per minute, so about 450 words.
- Run `python3 $S/ste_check.py script.json` before you make the audio. A fix costs nothing now, and a new TTS run plus a re-render later.

## 4. Audio

```bash
uv run $S/tts.py script.json --out audio
```

This writes `audio/<id>.wav` and `audio/manifest.json`, with the duration of each segment. It trims the silence that TTS engines put at both ends of a clip, so `duration` is the speech itself. It generates a segment again only when its text changed, so iterate freely. The engine is chosen for you (see section 10). Use `--engine` to force one, `--voice` to pick a voice, and `--speed 1.1` to speak 10% faster. With ElevenLabs, tell the user the character count that the script prints (it is what they pay for).

## 5. Scene code (`scene.py`)

Subclass `NarratedScene`. `with self.narrate("s01") as seg:` starts that segment's audio at the current time and adds its subtitles. When the block ends, the scene waits until the audio finishes, plus a short pause. Inside the block, fit the animations to `seg.duration`, and use `seg.remaining()` for the time left in the segment.

```python
from manim import *
from narrated_scene import NarratedScene, KText

class Explainer(NarratedScene):
    def construct(self):
        with self.narrate("s01") as seg:
            q = KText("도청되는 채널로 비밀 키를 만들 수 있을까?", font_size=40)
            self.play(Write(q), run_time=min(2.5, seg.duration * 0.6))

        with self.narrate("s02") as seg:
            self.play(q.animate.scale(0.7).to_edge(UP), run_time=0.8)
            a = MathTex(r"A = g^{a} \bmod p", color=BLUE).shift(LEFT * 3)
            self.play(FadeIn(a, shift=UP), run_time=1)
            self.play(Indicate(a), run_time=seg.remaining())
```

To land an animation on a later sentence of the same segment, wait for it: `seg.wait_until(seg.sentence_start(1))` waits until the second sentence starts (estimated from its share of the characters).

`KText` is `Text` with a font that has Korean glyphs. Put all Korean in `KText`. Use LaTeX (`MathTex`, `Tex`) only for math. `NarratedScene` sets a dark background; change it with `self.camera.background_color` in `construct` if the topic needs a light one.

## 6. Render

```bash
bash $S/render.sh scene.py Explainer l    # draft: 480p15, fast
bash $S/render.sh scene.py Explainer h    # final: 1080p60
```

For a 3-minute scene with about 190 animations, `l` takes about 30 s, `m` (720p30) about 35 s, and `h` about 70 s. Use `m` when a heavy scene renders slowly. Run a render in the background if it can take longer than a command timeout. The script prints the path of the mp4. The pydub "SyntaxWarning" lines and Manim's "Some options were not used" warning are harmless. Manim writes a matching `.srt` next to it, and `NarratedScene` writes `timeline.json` in the current folder. When a render fails, read the traceback from the bottom: most errors are a wrong keyword argument or LaTeX that does not compile.

## 7. Look at the frames

```bash
uv run $S/frames.py <draft.mp4> --out frames
```

This writes `frames/sheet.png`, with one frame from the end of each narration segment, labeled with the time and the segment id, plus each frame as its own PNG. The end of a segment is where its layout is fullest, so overlaps show there. Add `--at both` to also see the middle of each segment, which shows whether an element appears when the narration names it. Look at the sheet (and open a single frame when you need detail). Check:

- Nothing overlaps, and nothing is cut off at the edge of the frame.
- Korean text renders (no □ boxes), and every equation is correct.
- Text is large enough to read on a phone (`font_size` 28 or more for body text).
- What is on screen matches what the narration says at that moment.

Fix the scene and render the draft again until the sheet is clean. Only then render the final quality.

## 8. Finish and deliver

```bash
uv run $S/finalize.py <final.mp4> --out <output folder>/<slug>.mp4 --lang kor
```

This copies the video and embeds the subtitles as a track that the viewer can switch on (QuickTime: View → Subtitles). Then `open` the mp4, and send it with a file-sending tool if one exists. Keep `storyboard.md`, `script.json`, and `scene.py` in the folder so that the video can be changed later.

## 9. Manim pitfalls

- The frame is about 14.2 × 8 units. Keep content inside x ∈ [−6.5, 6.5] and y ∈ [−3.6, 3.6]. Place objects with `.to_edge()`, `.next_to()`, `VGroup(...).arrange(DOWN, buff=0.4)`, and `arrange_in_grid()`. Hand-tuned coordinates are the main cause of overlap.
- `Text` does not wrap. Break long lines yourself (`"첫 줄\n둘째 줄"`), and use `.scale_to_fit_width(12)` when a line is too wide.
- Before a new idea, remove the old objects: `self.play(*[FadeOut(m) for m in self.mobjects])`.
- To color part of an equation, split it into parts: `MathTex("g", "^{a}", r"\bmod p")`, then `eq[1].set_color(ORANGE)`.
- `Write` is slow on long text, because it draws stroke by stroke. Use `FadeIn` for anything longer than a short title.
- To dim objects, use `.fade(0.7)` or `set_stroke(opacity=…)`. `set_opacity()` also sets the fill, so open paths, arcs, and circles turn into filled shapes.
- Fade out the objects you added. If you add objects one by one and later wrap them in a new `VGroup` to fade them, the originals can stay on screen. Keep a reference to each group that you add, and remove that group.
- A `run_time` must be greater than 0. `seg.remaining()` already returns at least 0.3 s.
- If `check_env.sh` reports no LaTeX, use `Text` with Unicode for math (`gᵃ mod p`).
- Prefer Manim's standard colors (`BLUE`, `TEAL`, `YELLOW`, `ORANGE`, `RED`, `GREEN`, `GREY_B`): they read well on the dark background.

## 10. Narration engines

| Engine | Runs on | Quality | Setup | Voices |
|---|---|---|---|---|
| `elevenlabs` | ElevenLabs API (paid) | best | `ELEVENLABS_API_KEY`; optional `ELEVENLABS_VOICE_ID`, `ELEVENLABS_MODEL_ID` (default `eleven_multilingual_v2`) | any multilingual voice reads Korean |
| `supertonic` | local CPU (Supertone, ONNX, 31 languages) | good | none; the first use downloads a ~400 MB model | `M1`–`M5`, `F1`–`F5` |
| `edge` | Microsoft Edge online voices (free, no key; the text goes to Microsoft) | very good | none; needs internet | `ko-KR-SunHiNeural`, `ko-KR-InJoonNeural`, `en-US-AndrewMultilingualNeural` |
| `say` | macOS, offline | robotic | built in | `Yuna` (Korean), `Samantha` (English) |

The automatic order is `elevenlabs` (only when the key is set) → `supertonic` → `edge` → `say`. If an engine fails, `tts.py` moves to the next one and uses it for every segment, so the voice stays the same through the video. If the user prefers another default, they can pass `--engine`, or say so once and you can remember it.
