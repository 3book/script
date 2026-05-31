"""Theme manager — colors, fonts, logo, and slide dimensions."""

import os
from models import MetaInfo


class Theme:
    """Holds visual theme configuration, with Boeing-inspired defaults.
    Can be overridden by MetaInfo font settings from YAML frontmatter.
    """

    # --- Default color palette (Boeing-inspired) ---
    DEFAULT_FONT_SIZES = {
        48: "#880000",   # Title (H1 / document title)
        36: "#005566",   # Section heading (H2)
        24: "#000088",   # Subsection heading (H3)
        16: "#660088",   # Body text
    }
    DEFAULT_BODY_SIZE = 16
    DEFAULT_FONT_COLOR = "#333333"
    DEFAULT_CODE_FONT_SIZE = 11
    DEFAULT_CODE_FONT_NAME = "Consolas"
    DEFAULT_BODY_FONT_NAME = "Microsoft YaHei"
    DEFAULT_HEADING_FONT_NAME = "Microsoft YaHei"
    ACCENT_COLOR = "#0033A0"    # Boeing blue

    # --- Slide dimensions (16:9 widescreen) ---
    SLIDE_WIDTH_INCHES = 13.333
    SLIDE_HEIGHT_INCHES = 7.5

    # --- Margins (inches) ---
    MARGIN_LEFT = 0.5
    MARGIN_RIGHT = 0.5
    MARGIN_TOP = 0.5
    MARGIN_BOTTOM = 0.5
    COLUMN_GAP = 0.2

    # --- Logo dimensions (inches) ---
    LOGO_WIDTH = 1.2
    LOGO_HEIGHT = 0.6

    def __init__(self, meta: MetaInfo):
        self.meta = meta

        # Merge YAML font sizes with defaults
        self.font_sizes = dict(self.DEFAULT_FONT_SIZES)
        if meta.font_sizes:
            for pt, color in meta.font_sizes.items():
                if isinstance(pt, int) or (isinstance(pt, str) and pt.isdigit()):
                    self.font_sizes[int(pt)] = color

        # Body font size (point value) — separate from color
        self.body_size = self.DEFAULT_BODY_SIZE  # 16pt
        # Extract just the size from the key
        self.title_font_size = max((k for k in self.font_sizes if k >= 40), default=48)
        self.section_font_size = max((k for k in self.font_sizes if 30 <= k < 40), default=36)
        self.subsection_font_size = max((k for k in self.font_sizes if 20 <= k < 30), default=24)

        self.body_font_color = meta.font_color or self.DEFAULT_FONT_COLOR
        self.body_font_name = self.DEFAULT_BODY_FONT_NAME
        self.heading_font_name = self.DEFAULT_HEADING_FONT_NAME
        self.code_font_name = self.DEFAULT_CODE_FONT_NAME
        self.code_font_size = self.DEFAULT_CODE_FONT_SIZE

        # Resolve logo path
        self.logo_path = self._resolve_logo_path()

    def _resolve_logo_path(self) -> str:
        """Resolve the company logo path relative to the markdown file's directory."""
        logo_rel = self.meta.company_logo
        if not logo_rel:
            return ""
        # Try relative to the project root (assets/)
        base = os.path.dirname(os.path.abspath(__file__))  # md2pptx/
        pptx_dir = os.path.dirname(base)  # pptx/
        candidate = os.path.join(pptx_dir, logo_rel)
        if os.path.isfile(candidate):
            return candidate
        # Try bare path
        if os.path.isfile(logo_rel):
            return os.path.abspath(logo_rel)
        return ""

    @property
    def content_width(self) -> float:
        return self.SLIDE_WIDTH_INCHES - self.MARGIN_LEFT - self.MARGIN_RIGHT

    @property
    def content_height(self) -> float:
        return self.SLIDE_HEIGHT_INCHES - self.MARGIN_TOP - self.MARGIN_BOTTOM

    def column_width(self, n_cols: int) -> float:
        """Width of a single column given `n_cols` (1-4)."""
        if n_cols <= 1:
            return self.content_width
        total_gap = self.COLUMN_GAP * (n_cols - 1)
        return (self.content_width - total_gap) / n_cols

    def column_left(self, col_idx: int, n_cols: int) -> float:
        """Left position of column `col_idx` (0-based)."""
        cw = self.column_width(n_cols)
        return self.MARGIN_LEFT + col_idx * (cw + self.COLUMN_GAP)

    def font_color_for_size(self, pt: int) -> str:
        """Get the font color for a given point size."""
        return self.font_sizes.get(pt, self.DEFAULT_FONT_COLOR)

    def title_color(self) -> str:
        return self.font_sizes.get(self.title_font_size, "#880000")

    def section_color(self) -> str:
        return self.font_sizes.get(self.section_font_size, "#005566")

    def subsection_color(self) -> str:
        return self.font_sizes.get(self.subsection_font_size, "#000088")
