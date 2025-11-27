"""Utility functions for teto_core"""

from .color_utils import COLOR_MAP, parse_color, parse_background_color
from .font_utils import load_font, find_system_font
from .image_utils import (
    create_rounded_rectangle,
    create_text_image_with_pil,
    wrap_text_japanese_aware,
)
from .time_utils import format_srt_time, format_vtt_time
from .constants import (
    LINE_SPACING,
    TEXT_PADDING,
    BG_PADDING_X,
    BG_PADDING_Y,
    BG_RADIUS,
    MARGIN_BOTTOM,
    MARGIN_TOP,
    MAX_TEXT_WIDTH_OFFSET,
    PUNCTUATION_CHARS,
)

__all__ = [
    # Color utilities
    "COLOR_MAP",
    "parse_color",
    "parse_background_color",
    # Font utilities
    "load_font",
    "find_system_font",
    # Image utilities
    "create_rounded_rectangle",
    "create_text_image_with_pil",
    "wrap_text_japanese_aware",
    # Time utilities
    "format_srt_time",
    "format_vtt_time",
    # Constants
    "LINE_SPACING",
    "TEXT_PADDING",
    "BG_PADDING_X",
    "BG_PADDING_Y",
    "BG_RADIUS",
    "MARGIN_BOTTOM",
    "MARGIN_TOP",
    "MAX_TEXT_WIDTH_OFFSET",
    "PUNCTUATION_CHARS",
]
