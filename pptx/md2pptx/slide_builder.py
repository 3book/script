"""Layout detection and slide construction."""

from typing import List, Optional

from models import (
    MetaInfo, Section, SubSection, Block, Slide, ImageAttr,
)


def _has_mermaid(section: Section) -> bool:
    """Check if a section contains a mermaid diagram block."""
    for b in section.blocks:
        if b.type == Block.BLOCK_MERMAID:
            return True
    for ss in section.subsections:
        for b in ss.blocks:
            if b.type == Block.BLOCK_MERMAID:
                return True
    return False


def _has_code(section: Section) -> bool:
    """Check if a section contains a code block."""
    for b in section.blocks:
        if b.type == Block.BLOCK_CODE:
            return True
    for ss in section.subsections:
        for b in ss.blocks:
            if b.type == Block.BLOCK_CODE:
                return True
    return False


def _has_image(section: Section) -> bool:
    """Check if a section contains an image block."""
    for b in section.blocks:
        if b.type == Block.BLOCK_IMAGE:
            return True
    for ss in section.subsections:
        for b in ss.blocks:
            if b.type == Block.BLOCK_IMAGE:
                return True
    return False


def _collect_all_blocks(section: Section) -> List[Block]:
    """Collect all blocks from a section (including subsections)."""
    all_blocks = list(section.blocks)
    for ss in section.subsections:
        all_blocks.extend(ss.blocks)
    return all_blocks


def _detect_text_image_split(section: Section) -> bool:
    """Detect if a section should use text+image 2-column layout.

    Returns True if:
    - No subsections
    - Has at least one image block
    - Has some text/bullet blocks
    """
    if section.subsections:
        return False

    has_img = False
    has_text = False
    for b in section.blocks:
        if b.type == Block.BLOCK_IMAGE:
            has_img = True
        elif b.type in (Block.BLOCK_TEXT, Block.BLOCK_BULLET):
            has_text = True
    return has_img and has_text


def build_slides(meta: MetaInfo, h1_blocks: List[Block],
                 sections: List[Section]) -> List[Slide]:
    """Build a list of Slide objects from parsed markdown content.

    Args:
        meta: Document metadata.
        h1_blocks: Blocks from the H1 area (before first ##).
        sections: Parsed Section objects.

    Returns:
        List of Slide objects ready for PPTX generation.
    """
    slides: List[Slide] = []

    # --- Title slide ---
    title_slide = _build_title_slide(meta, h1_blocks)
    slides.append(title_slide)

    # --- Content slides (one per section) ---
    for section in sections:
        slide = _build_content_slide(section)
        slides.append(slide)

    # --- Ending slide ---
    ending_slide = _build_ending_slide(meta, h1_blocks)
    slides.append(ending_slide)

    return slides


def _build_title_slide(meta: MetaInfo, h1_blocks: List[Block]) -> Slide:
    """Build the title/first slide from H1 area content."""
    slide = Slide(layout_type=Slide.LAYOUT_TITLE, columns=1)

    # Collect title text blocks
    text_blocks = [b for b in h1_blocks if b.type == Block.BLOCK_TEXT]

    if text_blocks:
        slide.title = text_blocks[0].content
        slide.blocks = text_blocks[:]  # may contain multiple text lines
    elif meta.title:
        slide.title = meta.title
    else:
        slide.title = "Untitled"

    # Find title background image (alt="First" or first image in H1 area)
    for b in h1_blocks:
        if b.type == Block.BLOCK_IMAGE:
            img_alt = (b.image_attr.alt if b.image_attr else "").lower()
            if img_alt in ("first", "title-bg", "titlebg") or not slide.background_image:
                slide.background_image = b.content
                break

    return slide


def _build_ending_slide(meta: MetaInfo, h1_blocks: List[Block]) -> Slide:
    """Build the ending slide."""
    slide = Slide(layout_type=Slide.LAYOUT_ENDING, columns=1)
    slide.title = "Thank You"

    # Find ending background image (alt="last" or second image in H1 area)
    bg_images = [b for b in h1_blocks
                 if b.type == Block.BLOCK_IMAGE]
    for b in bg_images:
        img_alt = (b.image_attr.alt if b.image_attr else "").lower()
        if img_alt in ("last", "ending-bg", "endingbg"):
            slide.background_image = b.content
            break
    # If no explicit ending bg but there are 2+ images, use the last one
    if not slide.background_image and len(bg_images) >= 2:
        slide.background_image = bg_images[-1].content

    return slide


def _build_content_slide(section: Section) -> Slide:
    """Build a content slide from a section, detecting layout.

    Layout detection logic:
    1. Mermaid or code block → 1 column, special rendering
    2. No subsections + image + text → 2 column text+image
    3. Subsection count → that's the column count (capped at 4)
    4. Default → 1 column
    """
    slide = Slide(
        layout_type=Slide.LAYOUT_CONTENT,
        title=section.heading,
    )

    n_subsections = len(section.subsections)

    # Special: mermaid block
    if _has_mermaid(section) or _has_code(section):
        slide.columns = 1
        slide.subsections = section.subsections
        slide.blocks = section.blocks
        return slide

    # Text + image layout (no subsections)
    if _detect_text_image_split(section):
        slide.columns = 2
        slide.is_text_image_layout = True
        slide.blocks = section.blocks
        return slide

    # Column count based on subsections
    if n_subsections in (0, 1):
        slide.columns = 1
    elif n_subsections == 2:
        slide.columns = 2
    elif n_subsections == 3:
        slide.columns = 3
    else:
        slide.columns = 4
        if n_subsections > 4:
            print(f"  WARNING: Section '{section.heading}' has {n_subsections} subsections, "
                  f"capped at 4 columns")

    slide.subsections = section.subsections
    slide.blocks = section.blocks

    return slide
