"""レスポンシブサイズ計算ユーティリティ"""

from typing import Union
from ..core.constants import (
    BASE_WIDTH,
    SIZE_SCALE_MAP,
    BASE_FONT_SIZE,
    BASE_BORDER_WIDTH,
    BASE_PADDING,
    BASE_MARGIN,
    BASE_LINE_SPACING,
    BASE_TEXT_PADDING,
    BASE_BG_PADDING_X,
    BASE_BG_PADDING_Y,
    BASE_BG_RADIUS,
    BASE_MARGIN_BOTTOM,
    BASE_MARGIN_TOP,
    BASE_MAX_TEXT_WIDTH_OFFSET,
)
from ..core.types import ResponsiveSize


def get_scale_factor(video_width: int) -> float:
    """解像度に基づくスケール係数を計算（平方根スケーリング）

    幅の平方根を使用することで、縦動画や正方形動画でも
    適度なサイズの字幕を表示できるようにする。

    Args:
        video_width: 動画の幅（ピクセル）

    Returns:
        スケール係数

    Examples:
        >>> get_scale_factor(1920)  # 16:9 FHD
        1.0
        >>> get_scale_factor(3840)  # 16:9 4K
        2.0
        >>> get_scale_factor(1080)  # 9:16 or 1:1
        0.75
    """
    import math

    return math.sqrt(video_width / BASE_WIDTH)


def get_responsive_constants(video_width: int) -> dict:
    """解像度に応じた定数を計算

    Args:
        video_width: 動画の幅

    Returns:
        定数の辞書
    """
    scale = get_scale_factor(video_width)

    return {
        "LINE_SPACING": int(BASE_LINE_SPACING * scale),
        "TEXT_PADDING": int(BASE_TEXT_PADDING * scale),
        "BG_PADDING_X": int(BASE_BG_PADDING_X * scale),
        "BG_PADDING_Y": int(BASE_BG_PADDING_Y * scale),
        "BG_RADIUS": int(BASE_BG_RADIUS * scale),
        "MARGIN_BOTTOM": int(BASE_MARGIN_BOTTOM * scale),
        "MARGIN_TOP": int(BASE_MARGIN_TOP * scale),
        "MAX_TEXT_WIDTH_OFFSET": int(BASE_MAX_TEXT_WIDTH_OFFSET * scale),
    }


def calculate_size(
    size: Union[int, ResponsiveSize],
    video_width: int,
    base_value: int = BASE_FONT_SIZE,
) -> int:
    """サイズを計算（幅ベース）

    Args:
        size: サイズ（数値またはEnum）
        video_width: 動画の幅
        base_value: 基準値（1920pxでの値）

    Returns:
        計算されたピクセル値

    Examples:
        >>> calculate_size(48, 1920)
        48
        >>> calculate_size("base", 1920, BASE_FONT_SIZE)
        48
        >>> calculate_size("base", 3840, BASE_FONT_SIZE)  # 4K
        96
        >>> calculate_size("lg", 1920, BASE_FONT_SIZE)
        72
        >>> calculate_size("base", 1080, BASE_FONT_SIZE)  # 9:16
        27
    """
    # 数値の場合はそのまま返す
    if isinstance(size, int):
        return size

    # Enumの場合はスケール計算
    scale_factor = get_scale_factor(video_width)
    size_scale = SIZE_SCALE_MAP.get(size, 1.0)

    return int(base_value * scale_factor * size_scale)


def calculate_font_size(size: Union[int, ResponsiveSize], video_width: int) -> int:
    """フォントサイズを計算

    Args:
        size: フォントサイズ（数値またはEnum）
        video_width: 動画の幅

    Returns:
        計算されたフォントサイズ（ピクセル）
    """
    return calculate_size(size, video_width, BASE_FONT_SIZE)


def calculate_stroke_width(size: Union[int, ResponsiveSize], video_width: int) -> int:
    """縁取り幅を計算

    Args:
        size: 縁取り幅（数値またはEnum）
        video_width: 動画の幅

    Returns:
        計算された縁取り幅（ピクセル）
    """
    return calculate_size(size, video_width, BASE_BORDER_WIDTH)


def calculate_padding(size: Union[int, ResponsiveSize], video_width: int) -> int:
    """パディングを計算

    Args:
        size: パディング（数値またはEnum）
        video_width: 動画の幅

    Returns:
        計算されたパディング（ピクセル）
    """
    return calculate_size(size, video_width, BASE_PADDING)


def calculate_margin(size: Union[int, ResponsiveSize], video_width: int) -> int:
    """マージンを計算

    Args:
        size: マージン（数値またはEnum）
        video_width: 動画の幅

    Returns:
        計算されたマージン（ピクセル）
    """
    return calculate_size(size, video_width, BASE_MARGIN)
