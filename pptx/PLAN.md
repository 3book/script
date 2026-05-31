# Implementation Plan: Markdown-to-PPTX Converter

## Context

Building a reusable Python script that converts markdown files (with YAML frontmatter metadata) to professional PPTX presentations. The tool targets company document types: project reports, proposals, technical training materials. The reference input is `RAG 从零开始：概念、原理与实现.md` with Boeing branding, and the requirements are specified in ` propose.md`.

**Environment:** Python 3.10.12, python-pptx 1.0.2 installed, PyYAML + Pillow available

## File Structure

All scripts placed in a single flat directory `md2pptx/` — no nested packages.

```
/home/xxxx/work/aiFpga/pptx/
├── md2pptx/
│   ├── convert.py              # CLI entry point + orchestrator (single-file and batch)
│   ├── models.py               # Dataclasses: MetaInfo, ImageAttr, Block, Section, Slide
│   ├── parser.py               # YAML frontmatter + markdown body state machine parser
│   ├── theme.py                # Theme manager (colors, fonts, logo, defaults)
│   ├── image_processor.py      # Image attribute parsing + Pillow transformations
│   ├── slide_builder.py        # Layout detection: 1/2/3/4 columns, text+image, code
│   ├── presentation.py         # PPTX generation — builds slides from Slide objects
│   ├── template.md             # Markdown template example (demonstrates all features)
│   └── requirements.txt        # python-pptx, PyYAML, Pillow
├── assets/                     # Static assets (already exist)
└── output/                     # Generated PPTX files
```

## Implementation Steps

### Phase 1: Foundation (models & theme)
1. **`requirements.txt`** — python-pptx>=1.0.2, PyYAML>=5.4, Pillow>=9.0
2. **`md2pptx/models.py`** — Dataclasses:
   - `MetaInfo`: title, company_name, company_logo, doc_code, doc_rev, author, date, font_sizes (dict mapping pt→color), output_format
   - `ImageAttr`: path, alt, transparency (0-100), width, height
   - `Block`: type ("text"|"bullet"|"code"|"image"|"mermaid"), content, level, image_attr, language
   - `SubSection`: heading, blocks[]
   - `Section`: heading, subsections[], blocks[] (pre-subsection content)
   - `Slide`: layout_type ("title"|"content"|"ending"), columns (1-4), title, subsections, blocks, background_image, is_text_image_layout
3. **`md2pptx/theme.py`** — Boeing-inspired defaults:
   - Title (H1): 48pt, #880000; Section (H2): 36pt, #005566; Subsection (H3): 24pt, #000088; Body: 16pt, #660088; Code: 11pt monospace
   - Logo loading/caching; header/footer configuration
   - Accept overrides from YAML MetaInfo font settings

### Phase 2: Parsing (YAML + Markdown)
4. **`md2pptx/parser.py`** — `parse_yaml_frontmatter()`:
   - Extract `---` delimited YAML from file start
   - Normalize both YAML formats (flat structure in actual file vs nested `Document:` format in spec)
   - Apply typo-tolerant field matching; fall back to defaults for missing fields
5. **`md2pptx/parser.py`** — `parse_markdown_body()`:
   - Line-by-line state machine (not markdown library — preserves structural hierarchy)
   - States: INIT, HEADING_1, HEADING_2, HEADING_3, CODE_BLOCK, LIST, PARAGRAPH
   - Detect images in H1 area (before first `##`) → title/ending background candidates
   - Parse `![](){...}` extended image syntax via image_processor
   - Tag fenced code blocks by language (mermaid vs other)
6. **`md2pptx/parser.py`** — `parse_document()` full pipeline (read file, parse frontmatter, parse body)
7. **`md2pptx/image_processor.py`**:
   - `parse_image_attributes()`: Parse `{transparency:50,size:100*400,}` → dict; typo correction map (e.g., "traansparency" → "transparency"); handle empty `{}`
   - `apply_transparency()`, `apply_resize()` using Pillow (LANCZOS), output BytesIO streams for python-pptx insertion

### Phase 3: Slide Building (layout detection)
8. **`md2pptx/slide_builder.py`** — `build_slides()`:
   - Title slide: content from H1 area + first image as background
   - Content slides: one per `##` section
   - Ending slide: always appended with company info + closing text
   - Column detection: count `###` subsections → column count (capped at 4); mermaid/code → 1 column; image+text → 2 column text+image layout

### Phase 4: PPTX Generation (python-pptx)
9. **`md2pptx/presentation.py`** — `PresentationBuilder` class:
   - `__init__`: 16:9 widescreen (13.333" × 7.5"), load theme
   - `set_document_metadata()`: title, author, company, revision
   - `build_title_slide()`: centered title/subtitle/author/date, logo, optional background image
   - `build_content_slide()`: N-column layout with proper margins (0.5" all sides), column_gap 0.2"
   - `build_ending_slide()`: company name/logo, closing "Thank You", optional background
   - Helpers: `_add_textbox()`, `_add_bullet_list()`, `_add_code_block()`, `_add_image_to_slide()`, `_add_background()`, `_add_page_number()`
   - `save()`: write .pptx file

### Phase 5: CLI Entry Point + Template
10. **`md2pptx/convert.py`** — argparse CLI:
    - Single file: `python md2pptx/convert.py input.md -o output.pptx`
    - Directory batch: `python md2pptx/convert.py ./docs/ -o ./output/`
    - Recursive: add `--recursive` flag
    - Options: `--theme`, `--no-header`, `--no-footer`
    - Error handling: per-file try/except with error counting, non-zero exit on any failure
11. **`md2pptx/template.md`** — Markdown template example demonstrating all features:
    - Complete YAML frontmatter with Company + Document metadata
    - `#` — title page area with `![First]` and `![last]` backgrounds
    - `##` — section titles → slide titles
    - `###` — subsection → column headers
    - `-` — bullet lists (including nested)
    - `![alt](path){attrs}` — images with attributes (transparency, size)
    - ` ``` ` — fenced code blocks
    - ` ```mermaid` — mermaid diagrams
    - Inline **bold** text
    - Text+image parallel layout examples
    - 1/2/3/4 column demonstration sections

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Custom line-by-line parser (not markdown library) | Preserves heading/list hierarchy needed for slide layout; markdown→HTML loses structure |
| Blank slides with absolute positioning (not slide layouts) | Full layout control; avoids dependency on PPTX template layouts |
| Column count = `###` count within `##` section | Simple heuristic matching natural markdown grouping |
| Pre-process images with Pillow (transparency, resize) → BytesIO | python-pptx accepts file-like objects; Pillow handles transforms PPTX can't do natively |
| Mermaid: text placeholder unless mmdc available | Avoids Node.js dependency; can upgrade later |
| Boeing-inspired default color scheme | Matches the reference document's company branding |

## Edge Cases Handled
- Missing YAML frontmatter → all defaults, log warning
- Malformed YAML → catch YAMLError, fallback to defaults
- Missing image files → skip, log warning, continue
- Missing logo → omit from slides
- Typo in image attributes (`traansparency`) → correction map
- Empty `{}` image attributes → no transformations
- >4 `###` subsections → cap at 4 columns, warn
- Chinese text → use widely-available CJK fonts (Microsoft YaHei, SimSun)

## Verification

1. Run `python md2pptx/convert.py "RAG 从零开始：概念、原理与实现.md" -o output/test.pptx`
2. Verify output .pptx has:
   - Title slide: centered title, author "二大爷", date, Boeing logo
   - ~6 content slides (one per `##` section)
   - Correct column layouts (e.g., "为什么需要 RAG?" has 2 columns from 2x `###`)
   - Code block on "从零搭建" slide with monospace font
   - Images on slides with proper sizing
   - Ending slide with Boeing branding
3. Test batch mode on a directory
4. Test edge cases: no frontmatter, missing assets, malformed YAML
5. Manual visual review of generated PPTX
