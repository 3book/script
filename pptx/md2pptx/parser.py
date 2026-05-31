"""YAML frontmatter + markdown body parser using a line-by-line state machine."""

import os
import re
from typing import List, Tuple

import yaml

from models import MetaInfo, Section, SubSection, Block, ImageAttr
from image_processor import parse_image_attributes, make_image_attr


def parse_yaml_frontmatter(text: str) -> Tuple[MetaInfo, str]:
    """Extract YAML frontmatter from markdown text.

    Args:
        text: Full markdown file content.

    Returns:
        Tuple of (MetaInfo, remaining_body_text).
    """
    meta = MetaInfo()

    # Check for YAML frontmatter between --- delimiters
    if not text.startswith("---"):
        return meta, text

    # Find closing ---
    end_idx = text.find("---", 3)
    if end_idx == -1:
        return meta, text

    yaml_str = text[3:end_idx].strip()
    body = text[end_idx + 3:].strip()

    if not yaml_str:
        return meta, body

    try:
        data = yaml.safe_load(yaml_str)
    except yaml.YAMLError as e:
        print(f"  WARNING: YAML parse error: {e}, using defaults")
        return meta, body

    if not isinstance(data, dict):
        return meta, body

    # --- Normalize into MetaInfo ---

    # Top-level Title
    if "Title" in data:
        meta.title = str(data["Title"])
    elif "title" in data:
        meta.title = str(data["title"])

    # Company info (supports both flat and nested)
    company = data.get("Company", data.get("company", {}))
    if isinstance(company, dict):
        meta.company_name = str(company.get("name", company.get("Name", "")))
        meta.company_logo = str(company.get("logo", company.get("Logo", "")))
    elif isinstance(company, str):
        meta.company_name = company

    # Document info (supports both nested and flat)
    doc = data.get("Document", data.get("document", {}))
    if isinstance(doc, dict):
        meta.title = meta.title or str(doc.get("Title", doc.get("title", "")))
        meta.doc_code = str(doc.get("docCode", doc.get("doc_code", "")))
        meta.doc_rev = str(doc.get("docRev", doc.get("doc_rev", "")))
        meta.author = str(doc.get("First Made By (Author)",
                                  doc.get("author", "")))
        meta.date = str(doc.get("First Made Date",
                                 doc.get("date", "")))

        # Font settings from Document block
        font_data = doc.get("Font", doc.get("font", None))
        if isinstance(font_data, dict):
            for pt, color in font_data.items():
                try:
                    meta.font_sizes[int(pt)] = str(color)
                except (ValueError, TypeError):
                    pass

        fc = doc.get("FontColor", doc.get("fontColor", doc.get("font_color", "")))
        if fc:
            meta.font_color = str(fc)

    # Top-level overrides for doc fields
    for key, attr in [("docCode", "doc_code"), ("docRev", "doc_rev"),
                      ("First Made Date", "date"), ("First Made By (Author)", "author")]:
        if key in data and not getattr(meta, attr):
            setattr(meta, attr, str(data[key]))

    meta.output_format = str(data.get("output", data.get("Output", "pptx")))

    return meta, body


# Regex patterns
RE_H1 = re.compile(r"^#\s+(.*)")
RE_H2 = re.compile(r"^##\s+(.*)")
RE_H3 = re.compile(r"^###\s+(.*)")
RE_BULLET = re.compile(r"^(\s*)[-*]\s+(.*)")
RE_IMAGE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)(\{[^}]*\})?\s*$")
RE_IMAGE_INLINE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)(\{[^}]*\})?")
RE_FENCE = re.compile(r"^```(\w*)$")
RE_EMPTY = re.compile(r"^\s*$")


# State machine states
STATE_INIT = "INIT"
STATE_H1 = "HEADING_1"
STATE_H2 = "HEADING_2"
STATE_H3 = "HEADING_3"
STATE_CODE = "CODE_BLOCK"
STATE_LIST = "LIST"
STATE_PARAGRAPH = "PARAGRAPH"


def parse_markdown_body(text: str) -> Tuple[List[Block], List[Section]]:
    """Parse markdown body into sections using a state machine.

    Args:
        text: Markdown body text (after YAML frontmatter removed).

    Returns:
        Tuple of (h1_blocks, sections).
        - h1_blocks: Blocks found in the H1 area (before first ##) — used for title slide
        - sections: List of Section objects (one per ## heading)
    """
    lines = text.split("\n")
    h1_blocks: List[Block] = []
    sections: List[Section] = []
    current_section: Section = None
    current_subsection: SubSection = None
    current_block_list: List[Block] = h1_blocks
    state = STATE_INIT
    code_lang = ""
    code_lines: List[str] = []

    def flush_blocks():
        """Add pending blocks to the current context."""
        pass  # blocks are added directly

    def add_block(block: Block):
        """Add a block to the current active list."""
        nonlocal current_block_list
        current_block_list.append(block)

    def current_blocks():
        nonlocal current_block_list, current_section, current_subsection
        if current_subsection:
            return current_subsection.blocks
        elif current_section:
            return current_section.blocks
        else:
            return h1_blocks

    i = 0
    while i < len(lines):
        line = lines[i]

        # --- Code block handling (spans multiple lines) ---
        if state == STATE_CODE:
            fence_match = RE_FENCE.match(line)
            if fence_match:
                # End of code block
                code_content = "\n".join(code_lines)
                block_type = Block.BLOCK_MERMAID if code_lang == "mermaid" else Block.BLOCK_CODE
                blk = Block(type=block_type, content=code_content, language=code_lang)
                current_blocks().append(blk)
                code_lines = []
                code_lang = ""
                # Fall back to previous state
                if current_subsection:
                    state = STATE_H3
                elif current_section:
                    state = STATE_H2
                else:
                    state = STATE_INIT
            else:
                code_lines.append(line)
            i += 1
            continue

        # Check for fenced code block start
        fence_match = RE_FENCE.match(line)
        if fence_match:
            code_lang = fence_match.group(1)
            code_lines = []
            state = STATE_CODE
            i += 1
            continue

        # --- Heading detection ---
        h1_match = RE_H1.match(line)
        if h1_match:
            state = STATE_H1
            content = h1_match.group(1).strip()
            if content:
                h1_blocks.append(Block(type=Block.BLOCK_TEXT, content=content))
            i += 1
            continue

        h2_match = RE_H2.match(line)
        if h2_match:
            state = STATE_H2
            heading = h2_match.group(1).strip()
            current_section = Section(heading=heading)
            current_subsection = None
            current_block_list = current_section.blocks
            sections.append(current_section)
            i += 1
            continue

        h3_match = RE_H3.match(line)
        if h3_match:
            state = STATE_H3
            heading = h3_match.group(1).strip()
            current_subsection = SubSection(heading=heading)
            current_block_list = current_subsection.blocks
            if current_section:
                current_section.subsections.append(current_subsection)
            i += 1
            continue

        # --- Empty line ---
        if RE_EMPTY.match(line):
            if state == STATE_LIST:
                state = STATE_INIT if not current_section else STATE_H2
            i += 1
            continue

        # --- Bullet list ---
        bullet_match = RE_BULLET.match(line)
        if bullet_match:
            indent = bullet_match.group(1)
            level = len(indent) // 2 if indent else 0
            text = bullet_match.group(2).strip()

            # Check for inline image in bullet text
            img_match = RE_IMAGE_INLINE.search(text)
            if img_match:
                alt = img_match.group(1)
                path = img_match.group(2)
                attr_str = img_match.group(3) or ""
                attr_dict = parse_image_attributes(attr_str)
                img_attr = make_image_attr(path, alt, attr_dict)
                blk = Block(type=Block.BLOCK_IMAGE, content=path,
                            level=level, image_attr=img_attr)
            else:
                blk = Block(type=Block.BLOCK_BULLET, content=text, level=level)
            current_blocks().append(blk)
            state = STATE_LIST
            i += 1
            continue

        # --- Standalone image ---
        img_match = RE_IMAGE.match(line)
        if img_match:
            alt = img_match.group(1)
            path = img_match.group(2)
            attr_str = img_match.group(3) or ""
            attr_dict = parse_image_attributes(attr_str)
            img_attr = make_image_attr(path, alt, attr_dict)

            # Check if this looks like a background indicator
            if alt.lower() in ("first", "title-bg", "titlebg") and not current_section:
                blk = Block(type=Block.BLOCK_IMAGE, content=path,
                            image_attr=img_attr)
                h1_blocks.append(blk)
            elif alt.lower() in ("last", "ending-bg", "endingbg") and not current_section:
                blk = Block(type=Block.BLOCK_IMAGE, content=path,
                            image_attr=img_attr)
                h1_blocks.append(blk)
            else:
                blk = Block(type=Block.BLOCK_IMAGE, content=path,
                            image_attr=img_attr)
                current_blocks().append(blk)

            i += 1
            continue

        # --- Regular text / paragraph ---
        line_stripped = line.strip()
        if line_stripped:
            # Check for inline image
            img_match = RE_IMAGE_INLINE.search(line_stripped)
            if img_match:
                alt = img_match.group(1)
                path = img_match.group(2)
                attr_str = img_match.group(3) or ""
                attr_dict = parse_image_attributes(attr_str)
                img_attr = make_image_attr(path, alt, attr_dict)
                blk = Block(type=Block.BLOCK_IMAGE, content=path,
                            image_attr=img_attr)
            else:
                blk = Block(type=Block.BLOCK_TEXT, content=line_stripped)
            current_blocks().append(blk)
            state = STATE_PARAGRAPH

        i += 1

    return h1_blocks, sections


def parse_document(filepath: str) -> Tuple[MetaInfo, List[Block], List[Section], str]:
    """Full parse pipeline: read file, extract YAML frontmatter, parse body.

    Args:
        filepath: Path to the markdown file.

    Returns:
        Tuple of (MetaInfo, h1_blocks, sections, base_directory).
    """
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    base_dir = os.path.dirname(os.path.abspath(filepath))
    meta, body = parse_yaml_frontmatter(text)
    h1_blocks, sections = parse_markdown_body(body)

    return meta, h1_blocks, sections, base_dir
