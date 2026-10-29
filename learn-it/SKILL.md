---
name: learn-it
description: Teach the user a topic by building a custom explainer in the format that makes it easiest to understand — STE-style text (ASD-STE100 controlled language), a diagram, an interactive HTML page, or a narrated 3Blue1Brown-style animated video (Manim + local text-to-speech). Use this whenever the user types /learn-it, or says they want to learn, study, or really understand a concept, algorithm, protocol, paper, codebase, diff, or something an LLM produced ("배우고 싶어", "공부하고 싶어", "이해가 안 돼", "이해시켜줘", "HTML로 설명해줘", "설명 영상 만들어줘", "3b1b 스타일로", "STE로 써줘", "다이어그램으로 보여줘", "make me an explainer"), even if they do not name a format. Skip it for quick factual lookups and one-line definitions.
---

# Learn it

Turn "I want to understand X" into a custom explainer. The approach comes from Andrej Karpathy: code and intelligence are now cheap, so build large, bespoke, throwaway learning artifacts that were never worth making before. Each rung below usually teaches better than the one before it, and costs more time:

| Rung | Format | Best for | Build time |
|---|---|---|---|
| 1 | Text in STE style | definitions, procedures, quick orientation | 1–3 min |
| 2 | Diagram | structure, data flow, who sends what to whom | about 5 min |
| 3 | Interactive HTML page | most topics; anything with a knob to turn | 15–30 min |
| 4 | Narrated video (Manim) | processes that unfold in time; math with a geometric picture | 20–40 min |

Match the effort to the rung. For a text answer on a well-known topic, answer from what you know and check only the facts that you are unsure of. Keep deep research and verification for pages, videos, and recent or niche topics.

## 1. Pin down the request

Work these out from the message and the context. Ask a question only when the topic itself is unclear: picking a format and offering another one costs less than a round of questions.

- **Topic or source.** A concept ("KV cache"), or material to explain: a file, a paper (PDF, arXiv), a URL, a diff, or output that an LLM made in this conversation. Read the source before you explain it. For a folder or a codebase, read what the question needs (entry points, the main flow, the files the user names) and skip tests, vendored code, and generated files unless they matter.
- **Format.** Use the format the user names ("영상으로", "as a diagram", "HTML"). If they name none, make the **HTML page**, because it holds text, diagrams, and interaction in one place. "전부" or "all" means: text in chat, then the page (it contains the diagrams), then the video.
- **Reader.** Use what you know about the user (memory, conversation, field). Default: technically literate and new to this topic. Skip what they already know, and anchor new ideas to things they know well.
- **Language.** Write in the user's language. Korean requests get Korean output that follows the Korean rules in `references/ste.md`.
- **Size.** One sitting: a page the user finishes in 10–15 minutes, or a video of 2–5 minutes. Split a bigger topic into a series and say so.

For a video, tell the user before you start that it takes about 20–40 minutes, then go.

## 2. Build the content core first

Read `references/ste.md` now. Everything you write from here on follows it, `core.md` included.

Every format renders the same core, so get the core right before you think about visuals. A polished explainer makes its errors more convincing, not less. Write `core.md` in the output folder for every format, text included: it takes a minute, it keeps the answers to the check questions, and the next rung builds on it.

1. **One-sentence answer**: what it is and why it matters (two short sentences are fine).
2. **Key ideas**: 3–7, in dependency order, so that each one uses only earlier ones.
3. **The picture**: the one mental model or visual that makes the topic click.
4. **Worked example**: real numbers or a real input, small enough to follow by hand.
5. **Misconceptions**: 1–3 mistakes that a smart beginner makes.
6. **Check questions**: 3 questions that test understanding rather than recall, with answers.
7. **Sources**: when you researched.

Accuracy:
- Research first when the topic is recent, niche, or tied to a specific paper or library version (web search, the paper, the official docs). Do not trust memory for numbers, dates, API names, or citations.
- Compute every number in the worked example. Run code when the arithmetic is not trivial.
- When something is uncertain or disputed, say so in the explainer.

## 3. Write every sentence in STE style

All prose follows "80% ASD-STE100": the discipline of Simplified Technical English, relaxed where strictness would hurt learning. This covers `core.md`, chat text, diagram labels, page copy, and narration. The core of `references/ste.md`:

- One sentence, one idea: about 20 words for a step, 25 for a description (Korean: about 40 and 60 characters, spaces included).
- One term, one meaning. Define each term at first use and never swap in a synonym.
- Active voice, present tense, and a named actor ("the verifier checks…", "검증자가 ~를 확인한다").
- Concrete words and real values, not "very", "some", "상당히".
- Numbered lists for steps, with the condition before the action.
- Relaxation: one clearly labeled analogy per idea is allowed, after the literal explanation.

"STE로" means this default mode. Only "strict STE" or "100% STE" turns on strict mode, which drops the relaxations.

## 4. Make the format

Read the reference for the chosen format before you start:

- **Text**: answer in chat, in the "~다" style. Length: about 1,500–2,500 Korean characters (300–500 English words). For "짧게" or "brief": about 600–1,000 characters, with the one-sentence answer, 3 key ideas, one small example, and 1–2 questions. Order: one-sentence answer, key ideas, worked example, misconceptions (one line each, optional), check questions, and one source line if you researched. Do not show the answers. Ask the user to try the questions first, because recall is what makes an idea stick; the answers wait in `core.md` for their reply.
- **Diagram**: `references/diagram.md`
- **HTML page**: `references/html.md`
- **Video**: `references/video.md` (pipeline, helper scripts, Manim pitfalls)

Files go to `${LEARN_DIR:-$HOME/learn}/<YYYY-MM-DD>-<slug>/`, where the slug is a short ASCII kebab-case name for the topic: slug `kv-cache`, folder `2026-10-22-kv-cache`, video `kv-cache.mp4`. If the user names another place, use it. Later rungs of the same topic go into the same folder, even on a later day. One library lets the user come back to old explainers, and lets you climb the ladder from the same `core.md`.

## 5. Look at it before you hand it over

Generated output fails in ways that a clean run does not show: labels that overlap, text that runs off the screen, Korean glyphs that render as boxes (□□), a slider that changes nothing, a sentence that carries three ideas. Before you deliver, check it the way the user will meet it. `<skill>` below is this skill's folder.

- **Text**: write the answer to `answer.md` in the output folder, then run `python3 <skill>/scripts/ste_check.py answer.md`.
- **Diagram**: `python3 <skill>/scripts/svg_preview.py diagram.svg`, look at the PNG, and re-read every label against `core.md`.
- **HTML page**: `node <skill>/scripts/page_check.mjs index.html` and `python3 <skill>/scripts/ste_check.py index.html`. When the page goes to an artifact tool, that tool's one-look check rule wins (see `references/html.md`).
- **Video**: `ste_check.py script.json` before you make the audio, and the `frames.py` contact sheet before the final render.

`ste_check.py` only finds candidates. Fix the real problems, then deliver.

## 6. Deliver and offer the next rung

- Show the result where the user is. Diagram: an inline visual tool when one exists, or else the SVG file. HTML page: an artifact or publishing tool when one exists, or else `open index.html`. Video: `open` the mp4, and also send it with a file-sending tool when one exists.
- For text, the chat message is the explainer. End it with the next-rung line, without a separate summary.
- For the other formats, write 2–3 lines in chat: what you made, where it is, and how to use it ("슬라이더로 시퀀스 길이를 바꿔 보세요"). Conversational lines like these use the polite form ("~요", "~습니다"); the explainer itself uses "~다".
- End with one line that offers the next rung up, or the natural next topic. Do not paste the explainer again in chat.
