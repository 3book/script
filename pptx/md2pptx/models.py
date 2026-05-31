"""Data models for the markdown-to-PPTX converter."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MetaInfo:
    """Metadata extracted from YAML frontmatter."""
    title: str = ""
    company_name: str = ""
    company_logo: str = ""
    doc_code: str = ""
    doc_rev: str = ""
    author: str = ""
    date: str = ""
    font_sizes: dict = field(default_factory=dict)  # {pt: "#color"}
    font_color: str = "#000000"
    output_format: str = "pptx"


@dataclass
class ImageAttr:
    """Image attributes parsed from extended markdown syntax {key:val,...}."""
    path: str = ""
    alt: str = ""
    transparency: Optional[int] = None   # 0-100, 0=opaque
    size_w: Optional[int] = None         # width in pixels
    size_h: Optional[int] = None         # height in pixels


@dataclass
class Block:
    """A single content block — discriminated by `type` field."""
    BLOCK_TEXT = "text"
    BLOCK_BULLET = "bullet"
    BLOCK_CODE = "code"
    BLOCK_IMAGE = "image"
    BLOCK_MERMAID = "mermaid"

    type: str = "text"           # "text" | "bullet" | "code" | "image" | "mermaid"
    content: str = ""            # text content or image path
    level: int = 0               # indentation level for nested bullets
    image_attr: Optional[ImageAttr] = None
    language: str = ""           # for code blocks (e.g., "bash", "mermaid")


@dataclass
class SubSection:
    """A subsection (### heading) within a section."""
    heading: str = ""
    blocks: list = field(default_factory=list)  # list[Block]


@dataclass
class Section:
    """A section (## heading) containing subsections and/or blocks."""
    heading: str = ""
    subsections: list = field(default_factory=list)   # list[SubSection]
    blocks: list = field(default_factory=list)         # list[Block] — pre-subsection content
    background_image: Optional[str] = None


@dataclass
class Slide:
    """A slide to be rendered in the PPTX."""
    LAYOUT_TITLE = "title"
    LAYOUT_CONTENT = "content"
    LAYOUT_ENDING = "ending"

    layout_type: str = "content"    # "title" | "content" | "ending"
    columns: int = 1                # 1-4
    title: str = ""
    subsections: list = field(default_factory=list)   # list[SubSection]
    blocks: list = field(default_factory=list)         # list[Block]
    background_image: Optional[str] = None
    is_text_image_layout: bool = False  # 2-col: text left, image right
