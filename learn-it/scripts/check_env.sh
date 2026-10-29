#!/usr/bin/env bash
# Report what the learn-it skill's video pipeline needs, and what is present. Installs nothing.
ok()   { printf '  ok    %s\n' "$*"; }
miss() { printf '  MISS  %s\n' "$*"; }
note() { printf '  --    %s\n' "$*"; }

echo "Core"
if command -v uv >/dev/null 2>&1; then ok "uv $(uv --version | awk '{print $2}')"
else miss "uv: install with 'brew install uv' (it runs Manim and TTS in cached, isolated environments)"; fi
if command -v latex >/dev/null 2>&1 && command -v dvisvgm >/dev/null 2>&1 \
   && kpsewhich standalone.cls >/dev/null 2>&1 && kpsewhich preview.sty >/dev/null 2>&1; then
  ok "LaTeX with dvisvgm, standalone, preview (MathTex works)"
elif command -v latex >/dev/null 2>&1; then
  miss "LaTeX is missing parts that MathTex needs (dvisvgm, standalone.cls, or preview.sty): 'sudo tlmgr install standalone preview dvisvgm'"
else
  note "LaTeX not found: MathTex fails. Use Text for formulas, or install with 'brew install --cask basictex'"
fi

echo "Manim build (needed once, to build pycairo)"
if [ "$(uname)" = Darwin ]; then
  if brew list cairo >/dev/null 2>&1; then ok "cairo"; else miss "cairo: install with 'brew install cairo'"; fi
  if command -v pkg-config >/dev/null 2>&1 || command -v pkgconf >/dev/null 2>&1; then ok "pkg-config"
  else note "pkg-config not on PATH: render.sh borrows pkgconf from PyPI. Permanent fix: 'brew install pkgconf'"; fi
fi
if command -v uv >/dev/null 2>&1 && uv run --offline --no-project --python 3.12 --with "manim>=0.19" python -c "import manim" >/dev/null 2>&1; then
  ok "manim is built and cached"
else
  note "manim is not cached yet: the first render downloads and builds it (1-3 min)"
fi

echo "Narration engines (auto order: elevenlabs -> supertonic -> edge -> say)"
if [ -n "${ELEVENLABS_API_KEY:-}" ]; then ok "elevenlabs: key is set (paid, best quality)"
else note "elevenlabs: set ELEVENLABS_API_KEY to use it (paid, best quality)"; fi
if [ -d "$HOME/.cache/supertonic3" ]; then ok "supertonic: model cached (local, free)"
else note "supertonic: local and free; downloads a ~400 MB model on first use"; fi
note "edge: free Microsoft online voices; needs internet, no key"
if command -v say >/dev/null 2>&1; then ok "say: $(say -v '?' | grep -c ko_KR) Korean voices (offline, robotic)"
else note "say: not available (macOS only)"; fi
