"""フォント関連のユーティリティ関数"""

import platform
from pathlib import Path
from PIL import ImageFont


def load_font(font_path: str | None, font_size: int) -> ImageFont.FreeTypeFont:
    """フォントを読み込む

    Args:
        font_path: フォントファイルパス
        font_size: フォントサイズ

    Returns:
        読み込んだフォント
    """
    try:
        if font_path and Path(font_path).exists():
            return ImageFont.truetype(font_path, font_size)
        else:
            return ImageFont.load_default()
    except Exception:
        return ImageFont.load_default()


def find_system_font() -> str | None:
    """システムに応じた日本語フォントを探す

    Returns:
        フォントファイルパス（見つからない場合はNone）
    """
    system = platform.system()
    font_paths = []

    if system == "Darwin":  # macOS
        font_paths = [
            "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
        ]
    elif system == "Windows":
        font_paths = [
            "C:/Windows/Fonts/yugothic.ttf",
            "C:/Windows/Fonts/msgothic.ttc",
        ]
    else:  # Linux
        font_paths = [
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        ]

    for font_path in font_paths:
        if Path(font_path).exists():
            return font_path

    return None
