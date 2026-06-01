"""Image attribute parsing and Pillow-based transformations."""

import io
import os
import re
from typing import Optional, Tuple

from PIL import Image

from models import ImageAttr


# Typo correction map for common attribute misspellings
ATTR_CORRECTIONS = {
    "traansparency": "transparency",
    "transparancy": "transparency",
    "transparancy": "transparency",
    "szie": "size",
    "siz": "size",
    "width": "size_w",
    "height": "size_h",
}


def parse_image_attributes(attr_str: str) -> dict:
    """Parse extended image syntax {key1:val1,key2:val2,...} into a dict.

    Handles:
    - Empty braces `{}`
    - Trailing commas
    - Simple typos via correction map
    - Size format: `width*height` or `w*h`

    Examples:
        '{transparency:50,size:100*400,}' -> {'transparency': '50', 'size': '100*400'}
        '{}' -> {}
    """
    if not attr_str:
        return {}

    # Strip braces
    inner = attr_str.strip().strip("{}").strip()
    if not inner:
        return {}

    result = {}
    # Split by comma, handling trailing comma
    parts = [p.strip() for p in inner.split(",") if p.strip()]

    for part in parts:
        if ":" not in part:
            continue
        key, _, val = part.partition(":")
        key = key.strip()
        val = val.strip()

        # Apply typo corrections
        if key in ATTR_CORRECTIONS:
            key = ATTR_CORRECTIONS[key]

        result[key] = val

    return result


def parse_size(size_str: str) -> Tuple[Optional[int], Optional[int]]:
    """Parse size string like '100*400' into (width, height) tuple.

    Also handles 'w*h', 'WxH', 'WxH', single numbers.
    """
    if not size_str:
        return None, None

    # Try various separators
    for sep in ("*", "x", "X", "×"):
        if sep in size_str:
            parts = size_str.split(sep)
            try:
                w = int(parts[0].strip())
                h = int(parts[1].strip())
                return w, h
            except (ValueError, IndexError):
                pass

    # Try single number
    try:
        val = int(size_str.strip())
        return val, val
    except ValueError:
        pass

    return None, None


def make_image_attr(path: str, alt: str, attr_dict: dict) -> ImageAttr:
    """Build an ImageAttr from parsed attribute dict."""
    img = ImageAttr(path=path, alt=alt)

    # Handle transparency
    if "transparency" in attr_dict:
        try:
            img.transparency = int(attr_dict["transparency"])
        except ValueError:
            pass

    # Handle size
    raw_size = attr_dict.get("size", "")
    if raw_size:
        w, h = parse_size(raw_size)
        img.size_w = w
        img.size_h = h

    return img


def apply_transparency(img: Image.Image, transparency: int) -> Image.Image:
    """Apply alpha transparency to an image.

    Uses a pre-computed LUT for efficient pixel mapping instead of lambda
    (which is painfully slow on large images).

    Args:
        img: PIL Image
        transparency: 0-100 where 0=opaque, 100=fully transparent

    Returns:
        New RGBA PIL Image with adjusted alpha channel.
    """
    if transparency <= 0:
        return img

    transparency = min(100, max(0, transparency))
    alpha_factor = 1.0 - (transparency / 100.0)

    if img.mode != "RGBA":
        img = img.convert("RGBA")

    # Pre-compute lookup table for fast pixel mapping
    lut = [int(i * alpha_factor) for i in range(256)]
    r, g, b, a = img.split()
    a = a.point(lut)
    img = Image.merge("RGBA", (r, g, b, a))
    return img


def apply_resize(img: Image.Image, width: Optional[int], height: Optional[int]) -> Image.Image:
    """Resize an image, preserving aspect ratio if only one dimension given.

    Args:
        img: PIL Image
        width: target width in pixels (or None)
        height: target height in pixels (or None)

    Returns:
        Resized PIL Image.
    """
    if width is None and height is None:
        return img

    orig_w, orig_h = img.size

    if width and height:
        return img.resize((width, height), Image.LANCZOS)
    elif width:
        ratio = width / orig_w
        new_h = int(orig_h * ratio)
        return img.resize((width, new_h), Image.LANCZOS)
    elif height:
        ratio = height / orig_h
        new_w = int(orig_w * ratio)
        return img.resize((new_w, height), Image.LANCZOS)

    return img


def process_image(image_attr: ImageAttr, base_dir: str) -> Optional[io.BytesIO]:
    """Load and transform an image, returning a BytesIO stream for python-pptx.

    Args:
        image_attr: ImageAttr with path, transparency, size
        base_dir: base directory for resolving relative paths

    Returns:
        BytesIO stream of the processed image, or None if file not found.
    """
    path = image_attr.path
    if not os.path.isabs(path):
        path = os.path.join(base_dir, path)

    if not os.path.isfile(path):
        print(f"  WARNING: Image not found: {path}")
        return None

    try:
        img = Image.open(path)
    except Exception as e:
        print(f"  WARNING: Cannot open image {path}: {e}")
        return None

    # Apply transformations
    if image_attr.transparency is not None and image_attr.transparency > 0:
        img = apply_transparency(img, image_attr.transparency)

    if image_attr.size_w or image_attr.size_h:
        img = apply_resize(img, image_attr.size_w, image_attr.size_h)

    # Save to BytesIO
    buf = io.BytesIO()
    # Preserve format if possible, otherwise save as PNG (supports RGBA)
    fmt = img.format or "PNG"
    if fmt.upper() == "JPEG" and img.mode in ("RGBA", "LA", "P"):
        fmt = "PNG"  # JPEG doesn't support alpha
    img.save(buf, format=fmt)
    buf.seek(0)
    return buf
