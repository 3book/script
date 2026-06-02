#!/usr/bin/env bash
# md2pptx — Markdown to PPTX Converter
# Team shared tool: call from any directory.
#   md2pptx.sh /path/to/report.md           → ./report.pptx
#   md2pptx.sh /path/to/docs/ -o ./out/     → ./out/*.pptx
# Image paths in markdown are resolved relative to the markdown file.

DIR="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$DIR/md2pptx/convert.py" "$@"
