"""PPTX generation — builds slides from Slide objects using python-pptx."""

import os
from typing import Optional

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

from models import MetaInfo, Slide, Section, SubSection, Block
from theme import Theme
from image_processor import process_image


def _parse_color(hex_color: str) -> RGBColor:
    """Parse a hex color string (e.g., '#880000' or '880000') into RGBColor."""
    c = hex_color.strip().lstrip("#")
    if len(c) == 6:
        return RGBColor(int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16))
    return RGBColor(0, 0, 0)


class PresentationBuilder:
    """Builds a PPTX presentation from Slide objects."""

    def __init__(self, theme: Theme, meta: MetaInfo, base_dir: str,
                 show_header: bool = True, show_footer: bool = True):
        self.theme = theme
        self.meta = meta
        self.base_dir = base_dir
        self.show_header = show_header
        self.show_footer = show_footer

        self.prs = Presentation()
        self.prs.slide_width = Inches(Theme.SLIDE_WIDTH_INCHES)
        self.prs.slide_height = Inches(Theme.SLIDE_HEIGHT_INCHES)

        self.slide_number = 0

    # ── Public API ─────────────────────────────────────────────

    def set_document_metadata(self):
        """Set PPTX document properties."""
        cp = self.prs.core_properties
        if self.meta.title:
            cp.title = self.meta.title
        if self.meta.author:
            cp.author = self.meta.author
        if self.meta.company_name:
            cp.subject = f"{self.meta.company_name} - {self.meta.doc_code or ''}"

    def build_slide(self, slide: Slide):
        """Dispatch slide building to the appropriate method."""
        self.slide_number += 1

        if slide.layout_type == Slide.LAYOUT_TITLE:
            self._build_title_slide(slide)
        elif slide.layout_type == Slide.LAYOUT_ENDING:
            self._build_ending_slide(slide)
        else:
            self._build_content_slide(slide)

    def save(self, output_path: str):
        """Save the presentation to a file."""
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        self.prs.save(output_path)

    # ── Slide builders ────────────────────────────────────────

    def _build_title_slide(self, slide: Slide):
        """Build the title slide with centered layout."""
        prs_slide = self.prs.slides.add_slide(self._blank_layout())

        # Background image
        if slide.background_image:
            self._add_background(prs_slide, slide.background_image)

        # Company logo (bottom-center on title slide)
        if self.theme.logo_path and os.path.isfile(self.theme.logo_path):
            logo_left = Inches((Theme.SLIDE_WIDTH_INCHES - Theme.LOGO_WIDTH) / 2)
            logo_top = Inches(Theme.SLIDE_HEIGHT_INCHES - Theme.LOGO_HEIGHT - 0.8)
            prs_slide.shapes.add_picture(
                self.theme.logo_path,
                logo_left, logo_top,
                Inches(Theme.LOGO_WIDTH), Inches(Theme.LOGO_HEIGHT)
            )

        # Title — centered, large
        title_text = slide.title or self.meta.title or "Untitled"
        title_top = Inches(1.8)
        title_height = Inches(1.2)
        self._add_textbox(
            prs_slide,
            Inches(Theme.MARGIN_LEFT + 1.0), title_top,
            Inches(Theme.SLIDE_WIDTH_INCHES - Theme.MARGIN_LEFT - Theme.MARGIN_RIGHT - 2.0),
            title_height,
            title_text,
            font_size=Pt(48),
            font_color=self.theme.title_color(),
            bold=True,
            font_name=self.theme.heading_font_name,
            alignment=PP_ALIGN.CENTER,
            vertical_anchor=MSO_ANCHOR.MIDDLE,
        )

        # Author
        y_offset = Inches(3.3)
        if self.meta.author:
            self._add_textbox(
                prs_slide,
                Inches(Theme.MARGIN_LEFT + 1.0), y_offset,
                Inches(Theme.SLIDE_WIDTH_INCHES - Theme.MARGIN_LEFT - Theme.MARGIN_RIGHT - 2.0),
                Inches(0.5),
                f"Author: {self.meta.author}",
                font_size=Pt(18),
                font_color=self.theme.body_font_color,
                font_name=self.theme.body_font_name,
                alignment=PP_ALIGN.CENTER,
            )
            y_offset += Inches(0.45)

        # Date
        if self.meta.date:
            self._add_textbox(
                prs_slide,
                Inches(Theme.MARGIN_LEFT + 1.0), y_offset,
                Inches(Theme.SLIDE_WIDTH_INCHES - Theme.MARGIN_LEFT - Theme.MARGIN_RIGHT - 2.0),
                Inches(0.5),
                f"Date: {self.meta.date}",
                font_size=Pt(16),
                font_color=self.theme.body_font_color,
                font_name=self.theme.body_font_name,
                alignment=PP_ALIGN.CENTER,
            )
            y_offset += Inches(0.45)

        # Company name
        if self.meta.company_name:
            self._add_textbox(
                prs_slide,
                Inches(Theme.MARGIN_LEFT + 1.0), y_offset,
                Inches(Theme.SLIDE_WIDTH_INCHES - Theme.MARGIN_LEFT - Theme.MARGIN_RIGHT - 2.0),
                Inches(0.5),
                self.meta.company_name,
                font_size=Pt(18),
                font_color=_parse_color(self.theme.ACCENT_COLOR),
                font_name=self.theme.body_font_name,
                alignment=PP_ALIGN.CENTER,
            )

        # Doc code bottom-left
        if self.meta.doc_code:
            self._add_textbox(
                prs_slide,
                Inches(0.5), Inches(Theme.SLIDE_HEIGHT_INCHES - 0.6),
                Inches(3), Inches(0.4),
                f"{self.meta.doc_code}  Rev: {self.meta.doc_rev or '1.0'}",
                font_size=Pt(10),
                font_color="#888888",
                font_name=self.theme.body_font_name,
            )

    def _build_content_slide(self, slide: Slide):
        """Build a content slide with multi-column layout."""
        prs_slide = self.prs.slides.add_slide(self._blank_layout())

        # Header bar with logo + company name
        if self.show_header:
            self._add_header(prs_slide)

        # Section title
        title_top = Inches(Theme.MARGIN_TOP)
        if self.show_header:
            title_top = Inches(Theme.MARGIN_TOP + 0.5)
        self._add_textbox(
            prs_slide,
            Inches(Theme.MARGIN_LEFT), title_top,
            Inches(self.theme.content_width), Inches(0.7),
            slide.title,
            font_size=Pt(self.theme.section_font_size),
            font_color=self.theme.section_color(),
            bold=True,
            font_name=self.theme.heading_font_name,
        )

        # Content area starts below title
        content_top_in = title_top.inches + 0.85
        content_height_in = Theme.SLIDE_HEIGHT_INCHES - content_top_in - Theme.MARGIN_BOTTOM
        if self.show_footer:
            content_height_in -= 0.5

        content_top = Inches(content_top_in)
        content_height = Inches(content_height_in)

        # --- Render content ---
        if slide.is_text_image_layout:
            self._render_text_image_layout(prs_slide, slide, content_top, content_height)
        elif slide.subsections:
            self._render_column_layout(prs_slide, slide, content_top, content_height)
        elif slide.blocks:
            self._render_single_column_blocks(prs_slide, slide, content_top, content_height)

        # Footer with page number
        if self.show_footer:
            self._add_page_number(prs_slide)

    def _build_ending_slide(self, slide: Slide):
        """Build the ending/closing slide."""
        prs_slide = self.prs.slides.add_slide(self._blank_layout())

        # Background image
        if slide.background_image:
            self._add_background(prs_slide, slide.background_image)

        # Company logo centered
        if self.theme.logo_path and os.path.isfile(self.theme.logo_path):
            logo_left = Inches((Theme.SLIDE_WIDTH_INCHES - Theme.LOGO_WIDTH * 2) / 2)
            logo_top = Inches(2.0)
            prs_slide.shapes.add_picture(
                self.theme.logo_path,
                logo_left, logo_top,
                Inches(Theme.LOGO_WIDTH * 2), Inches(Theme.LOGO_HEIGHT * 2)
            )

        # "Thank You" message
        self._add_textbox(
            prs_slide,
            Inches(Theme.MARGIN_LEFT + 1.0), Inches(4.0),
            Inches(Theme.SLIDE_WIDTH_INCHES - Theme.MARGIN_LEFT - Theme.MARGIN_RIGHT - 2.0),
            Inches(1.0),
            "Thank You",
            font_size=Pt(48),
            font_color=self.theme.title_color(),
            bold=True,
            font_name=self.theme.heading_font_name,
            alignment=PP_ALIGN.CENTER,
        )

        # Company info
        info_lines = []
        if self.meta.company_name:
            info_lines.append(self.meta.company_name)
        if self.meta.doc_code:
            info_lines.append(f"{self.meta.doc_code}  Rev: {self.meta.doc_rev or '1.0'}")
        if info_lines:
            self._add_textbox(
                prs_slide,
                Inches(Theme.MARGIN_LEFT + 1.0), Inches(5.2),
                Inches(Theme.SLIDE_WIDTH_INCHES - Theme.MARGIN_LEFT - Theme.MARGIN_RIGHT - 2.0),
                Inches(0.8),
                "\n".join(info_lines),
                font_size=Pt(16),
                font_color=self.theme.body_font_color,
                font_name=self.theme.body_font_name,
                alignment=PP_ALIGN.CENTER,
            )

    # ── Layout renderers ───────────────────────────────────────

    def _render_single_column_blocks(self, prs_slide, slide: Slide,
                                     top: Inches, height: Inches):
        """Render blocks in a single column — used when no subsections exist."""
        blocks = slide.blocks
        if not blocks:
            return

        y = top.inches if hasattr(top, 'inches') else top / 914400
        line_height = Pt(22)

        for block in blocks:
            if block.type == Block.BLOCK_BULLET:
                self._add_textbox(
                    prs_slide,
                    Inches(Theme.MARGIN_LEFT + 0.3 * block.level), Inches(y),
                    Inches(self.theme.content_width - 0.3 * block.level), line_height,
                    f"• {block.content}",
                    font_size=Pt(self.theme.body_size),
                    font_color=self.theme.body_font_color,
                    font_name=self.theme.body_font_name,
                )
                y += 0.32
            elif block.type == Block.BLOCK_TEXT:
                self._add_textbox(
                    prs_slide,
                    Inches(Theme.MARGIN_LEFT), Inches(y),
                    Inches(self.theme.content_width), line_height,
                    block.content,
                    font_size=Pt(self.theme.body_size),
                    font_color=self.theme.body_font_color,
                    font_name=self.theme.body_font_name,
                )
                # Estimate text height — rough
                text_len = len(block.content)
                line_count = max(1, text_len // 80 + 1)
                y += 0.32 * line_count
            elif block.type == Block.BLOCK_IMAGE:
                img_top = y
                self._add_image_block(prs_slide, block,
                                      Inches(Theme.MARGIN_LEFT), Inches(img_top),
                                      Inches(self.theme.content_width * 0.8),
                                      Inches(3.0))
                y += 3.2
            elif block.type == Block.BLOCK_CODE:
                self._render_code_block(prs_slide, block,
                                        Inches(Theme.MARGIN_LEFT), Inches(y),
                                        Inches(self.theme.content_width),
                                        Inches(2.0))
                y += 2.2
            elif block.type == Block.BLOCK_MERMAID:
                self._render_mermaid_block(prs_slide, block,
                                           Inches(Theme.MARGIN_LEFT), Inches(y),
                                           Inches(self.theme.content_width),
                                           Inches(2.5))
                y += 2.7

    def _render_column_layout(self, prs_slide, slide: Slide,
                              top, height):
        """Render subsections in an N-column grid.

        Args:
            top, height: Inches objects (or EMU ints) for position.
        """
        n_cols = slide.columns
        subsections = slide.subsections

        # Convert to float inches for arithmetic
        y = top.inches if hasattr(top, 'inches') else top / 914400
        ht = height.inches if hasattr(height, 'inches') else height / 914400

        # Pre-subsection blocks first (full width)
        if slide.blocks:
            pre_blocks = [b for b in slide.blocks if b.type != Block.BLOCK_IMAGE]
            for b in pre_blocks:
                if b.type in (Block.BLOCK_BULLET, Block.BLOCK_TEXT):
                    self._add_textbox(
                        prs_slide,
                        Inches(Theme.MARGIN_LEFT), Inches(y),
                        Inches(self.theme.content_width), Pt(22),
                        b.content if b.type == Block.BLOCK_TEXT else f"• {b.content}",
                        font_size=Pt(self.theme.body_size),
                        font_color=self.theme.body_font_color,
                        font_name=self.theme.body_font_name,
                    )
                    y += 0.32
            y += 0.2

        for idx, subsection in enumerate(subsections):
            col_idx = idx % n_cols

            col_left = self.theme.column_left(col_idx, n_cols)
            col_w = self.theme.column_width(n_cols)

            # Subsection heading
            self._add_textbox(
                prs_slide,
                Inches(col_left), Inches(y),
                Inches(col_w), Inches(0.4),
                subsection.heading,
                font_size=Pt(self.theme.subsection_font_size),
                font_color=self.theme.subsection_color(),
                bold=True,
                font_name=self.theme.heading_font_name,
            )
            item_y = y + 0.45

            # Bullet items in this column
            for block in subsection.blocks:
                if block.type == Block.BLOCK_BULLET:
                    self._add_textbox(
                        prs_slide,
                        Inches(col_left + 0.2 * block.level), Inches(item_y),
                        Inches(col_w - 0.2 * block.level), Pt(22),
                        f"• {block.content}",
                        font_size=Pt(self.theme.body_size),
                        font_color=self.theme.body_font_color,
                        font_name=self.theme.body_font_name,
                    )
                    item_y += 0.28
                elif block.type == Block.BLOCK_TEXT:
                    self._add_textbox(
                        prs_slide,
                        Inches(col_left), Inches(item_y),
                        Inches(col_w), Pt(22),
                        block.content,
                        font_size=Pt(self.theme.body_size),
                        font_color=self.theme.body_font_color,
                        font_name=self.theme.body_font_name,
                    )
                    item_y += 0.28
                elif block.type == Block.BLOCK_IMAGE:
                    self._add_image_block(prs_slide, block,
                                          Inches(col_left), Inches(item_y),
                                          Inches(col_w * 0.8),
                                          Inches(1.5))
                    item_y += 1.7

    def _render_text_image_layout(self, prs_slide, slide: Slide,
                                  top: Inches, height: Inches):
        """Render 2-column layout: text (left) + image (right)."""
        total_w = self.theme.content_width
        text_w = total_w * 0.55
        img_w = total_w * 0.40
        gap = total_w * 0.05

        text_left = Inches(Theme.MARGIN_LEFT)
        img_left = Inches(Theme.MARGIN_LEFT + text_w + gap)

        # Separate blocks
        text_blocks = [b for b in slide.blocks
                       if b.type in (Block.BLOCK_TEXT, Block.BLOCK_BULLET)]
        image_blocks = [b for b in slide.blocks
                        if b.type == Block.BLOCK_IMAGE]

        # Render text blocks on the left
        y = top.inches if hasattr(top, 'inches') else top / 914400
        for block in text_blocks:
            prefix = "• " if block.type == Block.BLOCK_BULLET else ""
            self._add_textbox(
                prs_slide,
                text_left, Inches(y),
                Inches(text_w), Pt(22),
                f"{prefix}{block.content}",
                font_size=Pt(self.theme.body_size),
                font_color=self.theme.body_font_color,
                font_name=self.theme.body_font_name,
            )
            y += 0.32

        # Render image blocks on the right
        img_y = top.inches if hasattr(top, 'inches') else top / 914400
        for block in image_blocks:
            self._add_image_block(prs_slide, block,
                                  img_left, Inches(img_y),
                                  Inches(img_w), Inches(3.5))
            img_y += 3.7

    # ── Helpers ────────────────────────────────────────────────

    def _add_textbox(self, slide, left, top, width, height,
                     text: str, font_size=Pt(16), font_color="#333333",
                     bold=False, font_name="Microsoft YaHei",
                     alignment=PP_ALIGN.LEFT,
                     vertical_anchor=MSO_ANCHOR.TOP):
        """Add a formatted text box to a slide."""
        if not text:
            return

        txBox = slide.shapes.add_textbox(left, top, width, height)
        tf = txBox.text_frame
        tf.word_wrap = True
        tf.auto_size = None

        p = tf.paragraphs[0]
        p.text = text
        p.font.size = font_size
        p.font.color.rgb = _parse_color(font_color) if isinstance(font_color, str) else font_color
        p.font.bold = bold
        p.font.name = font_name
        p.alignment = alignment

        # Set East Asian font
        for run in p.runs:
            run.font.name = font_name

        return txBox

    def _add_image_block(self, slide, block: Block, left, top, width, height):
        """Add an image to a slide, with transformations applied."""
        if not block.image_attr:
            return

        img_stream = process_image(block.image_attr, self.base_dir)
        if img_stream is None:
            # Placeholder rectangle
            shape = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE, left, top, width, height
            )
            shape.fill.solid()
            shape.fill.fore_color.rgb = RGBColor(200, 200, 200)
            tf = shape.text_frame
            tf.paragraphs[0].text = f"[Image: {block.content}]"
            tf.paragraphs[0].font.size = Pt(10)
            tf.paragraphs[0].font.color.rgb = RGBColor(100, 100, 100)
            return

        # python-pptx add_picture from BytesIO
        slide.shapes.add_picture(img_stream, left, top, width, height)

    def _render_code_block(self, prs_slide, block: Block,
                           left, top, width, height):
        """Render a code block with monospace font and light background."""
        # Background rectangle
        shape = prs_slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, left, top, width, height
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = RGBColor(245, 245, 245)
        shape.line.fill.background()

        # Code text
        txBox = prs_slide.shapes.add_textbox(
            left + Inches(0.15), top + Inches(0.1),
            width - Inches(0.3), height - Inches(0.2)
        )
        tf = txBox.text_frame
        tf.word_wrap = True

        code_lines = block.content.split("\n")
        for i, code_line in enumerate(code_lines[:20]):  # limit lines
            if i == 0:
                p = tf.paragraphs[0]
            else:
                p = tf.add_paragraph()

            # Truncate very long lines
            display_line = code_line[:100] + ("..." if len(code_line) > 100 else "")
            p.text = display_line
            p.font.size = Pt(self.theme.code_font_size)
            p.font.color.rgb = RGBColor(40, 40, 40)
            p.font.name = self.theme.code_font_name

        if len(code_lines) > 20:
            p = tf.add_paragraph()
            p.text = f"... ({len(code_lines) - 20} more lines)"
            p.font.size = Pt(9)
            p.font.color.rgb = RGBColor(150, 150, 150)

    def _render_mermaid_block(self, prs_slide, block: Block,
                              left, top, width, height):
        """Render a mermaid diagram as a placeholder."""
        shape = prs_slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, left, top, width, height
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = RGBColor(240, 248, 255)
        shape.line.color.rgb = RGBColor(100, 150, 200)

        tf = shape.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = "[Mermaid Diagram]"
        p.font.size = Pt(14)
        p.font.color.rgb = RGBColor(0, 100, 150)
        p.font.bold = True
        p.alignment = PP_ALIGN.CENTER

        p2 = tf.add_paragraph()
        p2.text = block.content[:200]
        p2.font.size = Pt(9)
        p2.font.color.rgb = RGBColor(80, 80, 80)
        p2.alignment = PP_ALIGN.CENTER

    def _add_background(self, slide, image_path: str):
        """Add a full-slide background image."""
        img_stream = process_image(
            type('ImageAttr', (), {'path': image_path, 'transparency': None,
                                    'size_w': None, 'size_h': None})(),
            self.base_dir
        )
        if img_stream:
            slide.shapes.add_picture(
                img_stream,
                Inches(0), Inches(0),
                Inches(Theme.SLIDE_WIDTH_INCHES), Inches(Theme.SLIDE_HEIGHT_INCHES)
            )

    def _add_header(self, slide):
        """Add a header bar with logo and company name."""
        if self.theme.logo_path and os.path.isfile(self.theme.logo_path):
            slide.shapes.add_picture(
                self.theme.logo_path,
                Inches(Theme.SLIDE_WIDTH_INCHES - Theme.LOGO_WIDTH - 0.3),
                Inches(0.15),
                Inches(Theme.LOGO_WIDTH), Inches(Theme.LOGO_HEIGHT)
            )

        if self.meta.company_name:
            self._add_textbox(
                slide,
                Inches(Theme.MARGIN_LEFT), Inches(0.15),
                Inches(4), Inches(0.35),
                self.meta.company_name,
                font_size=Pt(11),
                font_color="#888888",
                font_name=self.theme.body_font_name,
            )

        # Thin line under header
        line = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(Theme.MARGIN_LEFT), Inches(0.55),
            Inches(self.theme.content_width), Inches(0.005)
        )
        line.fill.solid()
        line.fill.fore_color.rgb = _parse_color(self.theme.ACCENT_COLOR)
        line.line.fill.background()

    def _add_page_number(self, slide):
        """Add page number in footer."""
        self._add_textbox(
            slide,
            Inches(Theme.SLIDE_WIDTH_INCHES - 1.0),
            Inches(Theme.SLIDE_HEIGHT_INCHES - 0.5),
            Inches(0.7), Inches(0.35),
            str(self.slide_number),
            font_size=Pt(10),
            font_color="#888888",
            font_name=self.theme.body_font_name,
            alignment=PP_ALIGN.RIGHT,
        )

    def _blank_layout(self):
        """Get the blank slide layout."""
        # Use index 6 (blank) if available, otherwise index 0
        try:
            return self.prs.slide_layouts[6]
        except IndexError:
            return self.prs.slide_layouts[0]
