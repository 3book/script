#!/usr/bin/env python3
"""Markdown to PPTX Converter.

Usage:
    # Single file
    python md2pptx/convert.py input.md -o output.pptx

    # Directory batch processing
    python md2pptx/convert.py ./docs/ -o ./output/

    # Recursive batch processing
    python md2pptx/convert.py ./docs/ -o ./output/ --recursive

    # With options
    python md2pptx/convert.py input.md -o output.pptx --no-header --no-footer
"""

import argparse
import os
import sys
from pathlib import Path

# Ensure the md2pptx directory is on sys.path for flat imports
_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)

from parser import parse_document
from theme import Theme
from slide_builder import build_slides
from presentation import PresentationBuilder


def process_file(input_path: Path, output_path: Path, options: dict) -> int:
    """Convert a single markdown file to PPTX.

    Returns 0 on success, 1 on error.
    """
    try:
        # 1. Parse
        print(f"  Parsing: {input_path.name}")
        meta, h1_blocks, sections, base_dir = parse_document(str(input_path))

        # 2. Load theme
        theme = Theme(meta)

        # 3. Build slides
        slides = build_slides(meta, h1_blocks, sections)
        print(f"  Built {len(slides)} slides: "
              f"1 title + {len(slides) - 2} content + 1 ending")

        # 4. Build PPTX
        builder = PresentationBuilder(
            theme, meta, base_dir,
            show_header=not options.get("no_header", False),
            show_footer=not options.get("no_footer", False),
        )
        builder.set_document_metadata()

        for slide in slides:
            builder.build_slide(slide)

        builder.save(str(output_path))
        print(f"  OK: {output_path}")
        return 0

    except Exception as e:
        print(f"  ERROR: {input_path}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Convert Markdown files to PPTX presentations"
    )
    parser.add_argument(
        "input", help="Input markdown file or directory"
    )
    parser.add_argument(
        "-o", "--output", default=None,
        help="Output file or directory (default: same name with .pptx)"
    )
    parser.add_argument(
        "-r", "--recursive", action="store_true",
        help="Process directories recursively"
    )
    parser.add_argument(
        "--no-header", action="store_true",
        help="Disable header on slides"
    )
    parser.add_argument(
        "--no-footer", action="store_true",
        help="Disable footer with page numbers"
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: '{input_path}' does not exist", file=sys.stderr)
        sys.exit(1)

    options = {
        "no_header": args.no_header,
        "no_footer": args.no_footer,
    }

    # ── Single file ──────────────────────────────────────────
    if input_path.is_file():
        if not input_path.suffix.lower() in (".md", ".markdown"):
            print(f"Warning: '{input_path}' does not appear to be a markdown file")

        output = Path(args.output) if args.output else input_path.with_suffix(".pptx")
        rc = process_file(input_path, output, options)
        sys.exit(rc)

    # ── Directory batch ──────────────────────────────────────
    elif input_path.is_dir():
        output_dir = Path(args.output) if args.output else input_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        pattern = "**/*.md" if args.recursive else "*.md"
        md_files = sorted(input_path.glob(pattern))

        if not md_files:
            print(f"No .md files found in {input_path}")
            sys.exit(0)

        print(f"Found {len(md_files)} markdown file(s) in {input_path}\n")
        errors = 0
        for md_file in md_files:
            rel = md_file.relative_to(input_path)
            out_file = output_dir / rel.with_suffix(".pptx")
            out_file.parent.mkdir(parents=True, exist_ok=True)
            print(f"Processing: {md_file}")
            errors += process_file(md_file, out_file, options)
            print()

        if errors:
            print(f"Done with {errors} error(s).")
            sys.exit(1)
        else:
            print(f"Done. All {len(md_files)} file(s) converted successfully.")


if __name__ == "__main__":
    main()
