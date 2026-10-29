# learn-it

A Claude Code skill that turns "I want to understand X" into a custom explainer, in the format that makes X easiest to understand.

| Rung | Format | Best for |
|---|---|---|
| 1 | Text in STE style (ASD-STE100, relaxed to "80%") | definitions, procedures, quick orientation |
| 2 | Diagram (SVG) | structure, data flow, who sends what to whom |
| 3 | Interactive HTML page (the default) | most topics; anything with a knob to turn |
| 4 | Narrated 3Blue1Brown-style video (Manim + text-to-speech) | processes that unfold in time; math with a geometric picture |

The idea comes from Andrej Karpathy's advice on reading LLM output: ask for controlled-language writing, then diagrams, then web pages, then bespoke explainer videos. Code and intelligence are now cheap enough to build large, throwaway learning artifacts that were never worth making before.

## Install

```bash
npx skills add 5Donghwan/learn-it-skill -g
```

Update later with `npx skills update learn-it`.

## Use

```text
/learn-it KV cache in transformers                  → interactive HTML page (default)
/learn-it Diffie-Hellman key exchange as a video    → narrated Manim video
/learn-it Raft leader election, short, in STE       → text in chat
/learn-it ./paper.pdf as a diagram                  → diagram of a paper, file, or codebase
```

Every explainer starts from a `core.md`: a one-sentence answer, key ideas, a worked example, misconceptions, and check questions. Files go to `~/learn/<date>-<topic>/` (set `LEARN_DIR` to change this), so a later "now make it a video" builds on the same core. Before delivering, the skill checks its own output: screenshots of pages, a frame contact sheet of videos, and an STE pass over the prose.

Korean requests get Korean output that follows a Korean adaptation of the STE rules.

## Requirements

| Format | Needs |
|---|---|
| Text | nothing |
| Diagram | Google Chrome for the preview check (macOS `qlmanage` as a fallback) |
| HTML page | Google Chrome and Node 22+ for `page_check.mjs` |
| Video | `uv`; Homebrew `cairo` (and `pkgconf`, recommended); LaTeX for formulas (MacTeX, or BasicTeX with `standalone`, `preview`, `dvisvgm`) |

Run `bash learn-it/scripts/check_env.sh` to see what is present. Manim and the TTS engines install on demand into cached `uv` environments, so nothing is installed system-wide.

Narration engines, in the order the skill tries them:

1. ElevenLabs, when `ELEVENLABS_API_KEY` is set (paid; optional `ELEVENLABS_VOICE_ID`, `ELEVENLABS_MODEL_ID`).
2. Supertonic: local, free, 31 languages including Korean. It downloads a model of about 400 MB on first use.
3. Microsoft Edge online voices: free, no key, needs internet.
4. macOS `say`: offline.

Tested on macOS on Apple Silicon. The video pipeline assumes macOS fonts and paths.

## Layout

```text
learn-it/
├── SKILL.md       workflow: request → content core → STE writing → format → check → deliver
├── references/    ste.md (writing rules and the Korean adaptation), diagram.md, html.md, video.md
├── scripts/       tts.py, narrated_scene.py, render.sh, frames.py, finalize.py,
│                  page_check.mjs, svg_preview.py, ste_check.py, check_env.sh
└── evals/         test prompts, in the layout that `claude plugin eval` reads
```

## 한국어 안내

무언가를 배우고 싶을 때 쓰는 Claude Code 스킬이다. 주제를 주면 이해하기 가장 쉬운 형식으로 설명 자료를 만든다: STE 스타일 글, 다이어그램, 인터랙티브 HTML 페이지(기본값), 내레이션이 있는 3Blue1Brown 스타일 영상.

- 설치: `npx skills add 5Donghwan/learn-it-skill -g`
- 사용: `/learn-it 트랜스포머 KV 캐시`, `/learn-it 디피-헬먼 키 교환 영상으로`, `/learn-it Raft 리더 선출 STE로 짧게`
- 영상은 직접 요청할 때만 만든다. 20~40분쯤 걸린다.
- 결과물은 `~/learn/<날짜>-<주제>/`에 쌓인다. 주제마다 `core.md`가 남아서, 나중에 다른 형식으로 다시 만들 수 있다.
- 한국어 요청에는 STE 규칙을 한국어에 맞게 옮긴 규칙(STE-ko)으로 쓴다.

## License

MIT
