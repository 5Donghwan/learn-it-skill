#!/usr/bin/env bash
# Render a NarratedScene with Manim in an isolated, cached uv environment.
#   bash render.sh scene.py Explainer [l|m|h|k]    l = 480p15 draft (default), h = 1080p60 final
# Run it from the video folder (the one with audio/ and scene.py).
# Prints the path of the mp4. Manim writes a matching .srt next to it.
set -euo pipefail
scripts_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
scene_file="$1"; scene="$2"; quality="${3:-l}"
export PYTHONPATH="$scripts_dir${PYTHONPATH:+:$PYTHONPATH}"

# pycairo (a Manim dependency) is built from source once, and the build needs pkg-config.
# With no pkg-config on PATH, borrow the pkgconf binary from PyPI for that build.
# The permanent fix is `brew install pkgconf`.
if ! command -v pkg-config >/dev/null 2>&1 && [ -z "${PKG_CONFIG:-}" ] && command -v brew >/dev/null 2>&1; then
  if PKG_CONFIG="$(uvx --quiet --from pkgconf python -c 'import os,pkgconf; print(os.path.join(os.path.dirname(pkgconf.__file__), ".bin", "pkgconf"))' 2>/dev/null)"; then
    brew_prefix="$(brew --prefix)"
    macos_major="$(sw_vers -productVersion | cut -d. -f1)"
    export PKG_CONFIG
    export PKG_CONFIG_PATH="$brew_prefix/lib/pkgconfig:$brew_prefix/share/pkgconfig:$brew_prefix/Library/Homebrew/os/mac/pkgconfig/$macos_major${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}"
  fi
fi

uv run --no-project --python 3.12 --with "manim>=0.19" \
  manim render -q"$quality" --config_file "$scripts_dir/manim.cfg" --media_dir ./media "$scene_file" "$scene" >&2

stem="$(basename "$scene_file" .py)"
ls -t ./media/videos/"$stem"/*/"$scene".mp4 | head -1
