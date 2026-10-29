# Diagrams

A diagram is the right format when the question is about structure or flow: what the parts are, how they connect, who sends what to whom, and in what order. Start from "the picture" in the content core. Aim for a diagram that takes about 5 minutes to make. A dense poster takes much longer, and it teaches less.

## Choose the diagram by its question

| The reader asks | Diagram |
|---|---|
| What are the parts, and how do they connect? | Block or architecture diagram |
| Who sends what, in what order? | Sequence diagram with one lane per party (the best fit for protocols) |
| What happens step by step, with branches? | Flowchart |
| Which states exist, and what moves between them? | State machine |
| What contains what? | Nested boxes |
| How does a quantity change? | Plot with labeled axes and units |
| How do two options differ? | Two panels with the same layout, side by side |

## Rules

- One diagram, one idea. Two ideas need two diagrams, or one diagram with numbered stages.
- Keep about 7 main elements or fewer in one view. For a whole system, draw an overview of at most 7 groups first. Draw a second, zoomed-in diagram only if one group needs it, and offer it instead of cramming it in.
- Show the real mechanism, with real names and the values from the worked example. "Component A → Component B" teaches nothing.
- Labels follow the STE rules: short, concrete, one term per thing, and the same terms as the text. A label is a claim, so it must be as accurate as a sentence.
- Color has a meaning, and keeps that meaning in every diagram of the topic (for example: secret = orange, public = blue). Add a legend when color carries meaning, and also use a label or a shape, because some readers cannot see the color difference.
- Label each arrow with what moves along it: a message, data, or control. In a dense layout, the boxes at both ends can name it instead.
- Use one reading direction: left to right for time and flow, top to bottom for hierarchy.
- Put a one-line caption under the diagram that states the takeaway.

## How to draw

Write the diagram as an SVG file, `diagram.svg` in the output folder, even when you also show it some other way. The file is the library copy, and it is what you check.

- Give the root `<svg>` a `viewBox` and no fixed `width`/`height`, so it scales to any window.
- Add a background `<rect>` that fills the viewBox, so the diagram reads on dark viewers.
- Korean text: `font-family="Apple SD Gothic Neo, 'Noto Sans KR', sans-serif"`. Monospace fonts such as Menlo have no Hangul, so never put Korean in a monospace run.
- Size boxes from the text before you place them. Rough widths per character: Korean about 1.0 × font-size, Latin about 0.55 × font-size, monospace about 0.6 × font-size.

Then show it:

1. **An inline visual tool** in this environment (for example a `show_widget` or "visualize" tool that renders SVG in the chat): read its setup guidance (its `read_me`) and pass it the drawing, adapted to its color and size rules.
2. **A diagramming skill** (for example `artifact-diagramming`) when the diagram goes into a published artifact.
3. **No tool**: deliver the SVG file itself.

Use Mermaid only when the destination renders Mermaid (Obsidian, GitHub). It is fast, but it gives little control over layout.

## Check it

```bash
python3 <skill>/scripts/svg_preview.py diagram.svg
```

This renders `check/diagram.png` at the real aspect ratio with headless Chrome. Look at it, and fix:

- overlapping or clipped labels, crossing arrows, and text too small to read;
- any label that disagrees with `core.md` or the source. Re-read every label against them, because a wrong label looks as convincing as a right one.

Keep the check images in `check/`.
