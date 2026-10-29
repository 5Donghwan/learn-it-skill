# Interactive HTML explainer page

This is the default format: one HTML page that a learner works through in 10–15 minutes. The page earns its place over plain text through interaction. The reader changes something and sees the result.

## Decide where the page goes, first

The destination changes how you write the file.

- **An artifact or publishing tool exists** (for example `Artifact`): load its design guidance before you write (for example the `artifact-design` skill) and follow its page contract. Where it differs from this file, it wins. Typical rules: write page content only, with no doctype, `html`, `head`, or `body` tags; load scripts only from the allowed CDNs and stylesheets only from Google Fonts; define every color as a light and dark token.
- **No such tool**: write a full document with `<!doctype html>`, `<meta charset="utf-8">`, a viewport meta, and `[hidden]{display:none!important}` in the CSS, so that `el.hidden = true` hides an element that also has a `display` rule.

## Page structure

1. **Header**: the title, the one-sentence answer, and "After this page you can: …" with 2–3 concrete abilities.
2. **The picture**: the core diagram, near the top.
3. **Mechanism, step by step**: for an algorithm, a protocol, or a pipeline, use a stepper (Prev/Next buttons and the arrow keys). Each step highlights one part of the diagram and shows 1–2 STE sentences.
4. **Playground**: at least one widget where the reader changes the input that carries the insight (sequence length, key size, learning rate, number of nodes) and sees the effect at once.
5. **Worked example**: the example from the core with real values, driven by the same code as the playground.
6. **Common misconceptions**: short items, each with the correct statement.
7. **Check your understanding**: the 3 check questions, with each answer hidden until the reader clicks (`<details>` works).
8. **Glossary and sources**: each term in one STE sentence, and links to the sources if you researched.

A short topic can merge sections 3–5. Keep sections 1, 4, and 7, because they make the page better than text. Diagrams inside the page follow the rules in `references/diagram.md`; they need no separate `diagram.svg`.

## Keep the numbers honest

Every number that the page states must come from the same code as the playground. Put the formulas in one pure function (for example `facts(params)`), fill each number in the text from it (`<span data-k="flops"></span>`), and test that function in Node against values that you computed by hand. Never hard-code a number that the code can compute.

## Design

- One file with inline CSS and JS and no build step. Load a library only when it does substantial work for the page.
- Readable text: body 17–18 px, `max-width: 70ch` for text columns, line height about 1.7 for Korean.
- Korean fonts: `Noto Sans KR` or `IBM Plex Sans KR` from Google Fonts (Pretendard is not on Google Fonts), with the fallback stack `"Apple SD Gothic Neo", "Noto Sans KR", system-ui, sans-serif`. Monospace fonts have no Hangul, so never put Korean in a monospace run.
- Light and dark themes through `prefers-color-scheme`.
- Colors have the same meaning as in the diagrams. Add a legend where color carries meaning.
- Motion shows change (a value moves, a step advances). Keep it at 200–600 ms, and respect `prefers-reduced-motion`.
- The page works at phone width, because the user may read it on a phone: no sideways scroll, controls large enough to touch, and tables that turn into stacked cards when narrow.
- Math: MathML (`<math>`), which every current browser renders with no library and no stylesheet. KaTeX also works for heavy math, but an artifact page must inline its stylesheet.
- Charts: if the environment has a data-visualization skill (for example `dataviz`), follow it.

## Check it

**When you publish through an artifact tool**, its check rules win, because the user is waiting for a link. Take one look (the tool's preview if it offers one, or else one run of `page_check.mjs`), make one pass of fixes, run the `facts()` test once in Node, and publish. Do not loop.

**For a local page**, check it the way a reader meets it:

1. `node <skill>/scripts/page_check.mjs index.html` (Node 22+ and Chrome). It renders at desktop width and at true phone width, in light and dark. It saves full-page screenshot slices in `check/`, and reports console errors, failed loads, and sideways scroll. It also moves every slider, clicks every button, and opens every `<details>`, and reports any errors that this causes. Look at the light slices at both widths and the top dark slice, and fix what you see.
2. `python3 <skill>/scripts/ste_check.py index.html`. It also checks the Korean strings inside scripts, such as stepper captions.
3. Run the `facts()` test in Node.

`page_check.mjs` renders a file without a doctype inside the artifact skeleton, so it also previews artifact content locally.

## Deliver

- With an artifact tool, publish the page there: the user can then open it on any device.
- Otherwise, run `open index.html`.
- In both cases, keep the page in the output folder.
