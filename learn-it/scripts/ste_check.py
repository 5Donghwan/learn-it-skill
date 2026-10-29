#!/usr/bin/env python3
"""Flag sentences that may break the STE rules in references/ste.md.

    python3 ste_check.py answer.md        # Markdown or plain text
    python3 ste_check.py index.html       # the visible text of a page, plus Korean strings in its scripts
    python3 ste_check.py script.json      # the "text" and "speech" fields of a narration script
    python3 ste_check.py answer.md --steps   # also hold numbered items to the stricter step limit

It finds candidates; you decide. A flagged sentence can be fine (a formal definition, a necessary term).
Korean lengths count characters including spaces (60 for a description, 40 for a step).
English lengths count words (25 for a description, 20 for a step).
Standard library only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

HANGUL = re.compile(r"[가-힣]")
KO_CONNECTIVE = re.compile(r"[가-힣](?:고|며|는데|지만|므로|면서|어서|아서|해서|니까|도록|면)(?=[\s,])")
KO_PATTERNS = {
    "vague": ["매우", "상당히", "다소", "어느 정도", "굉장히", "꽤"],
    "hedge": ["라고 할 수 있다", "인 것으로 보인다", "것 같다"],
    "translationese": ["에 대한", "를 통해", "을 통해", "하는 것이 가능", "를 가진다", "을 가진다", "에 있어서", "하게 된다"],
    "passive": ["되어진", "에 의해"],
}
# Demonstratives only when they stand alone ("에이는" or "고해당" must not match).
KO_PRONOUN = re.compile(r"(?<![가-힣])(?:이것|그것|이는|해당)(?=[\s,은는이가을를의에])")
EN_PATTERNS = {
    "vague": [r"\bvery\b", r"\breally\b", r"\bquite\b", r"\bvarious\b", r"\ba lot\b",
              r"\bbasically\b", r"\bessentially\b", r"\bsimply\b"],
    "wordy": [r"\butili[sz]e", r"\bleverag", r"\bfacilitat", r"\bin order to\b", r"\bprior to\b",
              r"\bapproximately\b", r"\bsubsequently\b", r"\bdemonstrat", r"\bobtain", r"\binitiat", r"\btermina"],
    "passive?": [r"\b(?:is|are|was|were|be|been|being)\s+\w+ed\b"],
}


class VisibleText(HTMLParser):
    SKIP = {"script", "style", "svg", "code", "pre", "math", "head"}
    BLOCK = {"p", "li", "div", "section", "h1", "h2", "h3", "h4", "summary", "details", "br", "td", "th",
             "figcaption", "blockquote", "dt", "dd", "header", "footer", "article"}

    def __init__(self):
        super().__init__()
        self.depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.depth += 1
        elif tag in self.BLOCK:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.depth:
            self.depth -= 1
        elif tag in self.BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.depth:
            self.parts.append(data)


def units_from(path: Path) -> list[tuple[str, bool, str]]:
    """Return (location, is_numbered_item, text) units."""
    raw = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        data = json.loads(raw)
        out = []
        for seg in data.get("segments", []):
            for key in ("text", "speech"):
                if seg.get(key):
                    out.append((f"{seg.get('id', '?')}.{key}", False, seg[key]))
        return out
    out, in_code = [], False
    if path.suffix in (".html", ".htm"):
        # Text that scripts insert (stepper captions, results) lives in string literals.
        for script in re.findall(r"<script\b[^>]*>(.*?)</script>", raw, re.S | re.I):
            for lit in re.findall(r"`((?:[^`\\]|\\.)*)`|\"((?:[^\"\\\n]|\\.)*)\"|'((?:[^'\\\n]|\\.)*)'", script):
                text = next(s for s in lit if s is not None and s != "") if any(lit) else ""
                if len(HANGUL.findall(text)) >= 4:
                    text = re.sub(r"\$\{[^}]*\}", "X", re.sub(r"<[^>]+>", "", text))
                    out.append(("js", False, " ".join(text.split())))
        parser = VisibleText()
        parser.feed(raw)
        raw = "".join(parser.parts)
    for n, line in enumerate(raw.splitlines(), 1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        s = line.strip()
        if in_code or not s or s.startswith(("|", "#", ">")) or re.fullmatch(r"[-*_]{3,}", s):
            continue
        if re.match(r"\**(출처|Sources?|References?)\**\s*:", s):  # citations are not prose
            continue
        numbered = bool(re.match(r"\d+[.)]\s", s))
        s = re.sub(r"^(?:[-*+]|\d+[.)])\s+", "", s)
        s = re.sub(r"\*\*(.+?)\*\*|__(.+?)__", lambda m: m.group(1) or m.group(2), s)
        s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
        s = re.sub(r"`[^`]*`", "X", s)
        out.append((f"L{n}", numbered, s))
    return out


def sentences(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"(?<=[.?!。])\s+", text) if len(p.strip()) >= 4]


def is_korean(sentence: str) -> bool:
    hangul = len(HANGUL.findall(sentence))
    latin = len(re.findall(r"[A-Za-z]", sentence))
    return hangul >= 3 and (hangul >= 0.15 * (hangul + latin) or bool(re.search(r"[가-힣][.?!]?$", sentence)))


def check(sentence: str, numbered: bool, steps: bool) -> list[str]:
    flags = []
    if is_korean(sentence):
        limit = 40 if (numbered and steps) else 60
        if len(sentence) > limit:
            flags.append(f"len {len(sentence)}>{limit}")
        conns = len(KO_CONNECTIVE.findall(sentence))
        if conns >= 2:
            flags.append(f"{conns} connectives")
        for kind, words in KO_PATTERNS.items():
            hits = [w.strip() for w in words if w in sentence]
            if hits:
                flags.append(f"{kind}: {', '.join(hits)}")
        pronouns = sorted(set(KO_PRONOUN.findall(sentence)))
        if pronouns:
            flags.append(f"pronoun: {', '.join(pronouns)}")
        if len(re.findall(r"\([A-Za-z]{2,}[^)]*\)", sentence)) > 1:  # glosses like (key), not symbols like (q7)
            flags.append("2+ English parentheticals")
    else:
        words = len(re.findall(r"[A-Za-z0-9'’-]+", sentence))
        limit = 20 if (numbered and steps) else 25
        if words > limit:
            flags.append(f"{words} words>{limit}")
        for kind, pats in EN_PATTERNS.items():
            hits = sorted({m.group(0) for p in pats for m in re.finditer(p, sentence, re.I)})
            if hits:
                flags.append(f"{kind}: {', '.join(hits)}")
    return flags


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", type=Path)
    ap.add_argument("--steps", action="store_true", help="numbered items are procedure steps (stricter limit)")
    args = ap.parse_args()
    for path in args.files:
        total = flagged = 0
        lengths = []
        report = []
        seen = set()
        for loc, numbered, text in units_from(path):
            for s in sentences(text):
                if s in seen:  # e.g. a narration "speech" that repeats its "text"
                    continue
                seen.add(s)
                total += 1
                if re.search(r"[.?!。]$", s):  # sentences only; UI labels would skew the average
                    lengths.append(len(s))
                flags = check(s, numbered, args.steps)
                if flags:
                    flagged += 1
                    report.append(f"  {loc:>8}  [{'; '.join(flags)}]  {s[:90]}{'…' if len(s) > 90 else ''}")
        avg = sum(lengths) / len(lengths) if lengths else 0
        print(f"{path.name}: {total} sentences and labels, average sentence {avg:.0f} characters, {flagged} flagged")
        print("\n".join(report) if report else "  (nothing flagged)")


if __name__ == "__main__":
    sys.exit(main())
