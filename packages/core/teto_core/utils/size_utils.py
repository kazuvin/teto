"""レスポンシブサイズ計算ユーティリティ"""

from typing import Union
from ..constants import (
    BASE_HEIGHT,
    SIZE_SCALE_MAP,
    BASE_FONT_SIZE,
    BASE_BORDER_WIDTH,
    BASE_PADDING,
    BASE_MARGIN,
    get_scale_factor,
)
from ..types import ResponsiveSize


def calculate_size(
    size: Union[int, ResponsiveSize],
    video_height: int,
    base_value: int = BASE_FONT_SIZE
) -> int:
    """サイズを計算

    Args:
        size: サイズ（数値またはEnum）
        video_height: 動画の高さ
        base_value: 基準値（1080pでの値）

    Returns:
        計算されたピクセル値

    Examples:
        >>> calculate_size(48, 1080)
        48
        >>> calculate_size("base", 1080, BASE_FONT_SIZE)
        48
        >>> calculate_size("base", 2160, BASE_FONT_SIZE)  # 4K
        96
        >>> calculate_size("lg", 1080, BASE_FONT_SIZE)
        72
    """
    # 数値の場合はそのまま返す
    if isinstance(size, int):
        return size

    # Enumの場合はスケール計算
    scale_factor = get_scale_factor(video_height)
    size_scale = SIZE_SCALE_MAP.get(size, 1.0)

    return int(base_value * scale_factor * size_scale)


def calculate_font_size(
    size: Union[int, ResponsiveSize],
    video_height: int
) -> int:
    """フォントサイズを計算

    Args:
        size: フォントサイズ（数値またはEnum）
        video_height: 動画の高さ

    Returns:
        計算されたフォントサイズ（ピクセル）
    """
    return calculate_size(size, video_height, BASE_FONT_SIZE)


def calculate_stroke_width(
    size: Union[int, ResponsiveSize],
    video_height: int
) -> int:
    """縁取り幅を計算

    Args:
        size: 縁取り幅（数値またはEnum）
        video_height: 動画の高さ

    Returns:
        計算された縁取り幅（ピクセル）
    """
    return calculate_size(size, video_height, BASE_BORDER_WIDTH)


def calculate_padding(
    size: Union[int, ResponsiveSize],
    video_height: int
) -> int:
    """パディングを計算

    Args:
        size: パディング（数値またはEnum）
        video_height: 動画の高さ

    Returns:
        計算されたパディング（ピクセル）
    """
    return calculate_size(size, video_height, BASE_PADDING)


def calculate_margin(
    size: Union[int, ResponsiveSize],
    video_height: int
) -> int:
    """マージンを計算

    Args:
        size: マージン（数値またはEnum）
        video_height: 動画の高さ

    Returns:
        計算されたマージン（ピクセル）
    """
    return calculate_size(size, video_height, BASE_MARGIN)
