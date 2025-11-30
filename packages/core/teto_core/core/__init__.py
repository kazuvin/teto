"""Core module - Common types, constants, enums, and base classes"""

from .types import ResponsiveSize
from .base import ProcessorBase
from .constants import (
    BASE_HEIGHT,
    SIZE_SCALE_MAP,
    COLOR_MAP,
    BASE_FONT_SIZE,
    BASE_BORDER_WIDTH,
    BASE_PADDING,
    BASE_TEXT_PADDING,
    BASE_BG_PADDING_X,
    BASE_BG_PADDING_Y,
    BASE_RADIUS,
    BASE_BG_RADIUS,
    BASE_MARGIN,
    BASE_MARGIN_BOTTOM,
    BASE_MARGIN_TOP,
    BASE_LINE_SPACING,
    BASE_MAX_TEXT_WIDTH_OFFSET,
    PUNCTUATION_CHARS,
)

__all__ = [
    "ResponsiveSize",
    "ProcessorBase",
    "BASE_HEIGHT",
    "SIZE_SCALE_MAP",
    "COLOR_MAP",
    "BASE_FONT_SIZE",
    "BASE_BORDER_WIDTH",
    "BASE_PADDING",
    "BASE_TEXT_PADDING",
    "BASE_BG_PADDING_X",
    "BASE_BG_PADDING_Y",
    "BASE_RADIUS",
    "BASE_BG_RADIUS",
    "BASE_MARGIN",
    "BASE_MARGIN_BOTTOM",
    "BASE_MARGIN_TOP",
    "BASE_LINE_SPACING",
    "BASE_MAX_TEXT_WIDTH_OFFSET",
    "PUNCTUATION_CHARS",
]
