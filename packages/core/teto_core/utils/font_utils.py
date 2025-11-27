"""フォント関連のユーティリティ関数"""

import platform
from pathlib import Path
from PIL import ImageFont


def load_font(
    font_path: str | None,
    font_size: int,
    font_weight: str = "normal"
) -> ImageFont.FreeTypeFont:
    """フォントを読み込む

    Args:
        font_path: フォントファイルパス
        font_size: フォントサイズ
        font_weight: フォントの太さ（"normal" または "bold"）

    Returns:
        読み込んだフォント
    """
    try:
        # カスタムフォントパスが指定されている場合
        if font_path and Path(font_path).exists():
            return ImageFont.truetype(font_path, font_size)

        # システムフォントを検索
        system_font = find_system_font(font_weight)
        if system_font:
            return ImageFont.truetype(system_font, font_size)

        return ImageFont.load_default()
    except Exception:
        return ImageFont.load_default()


def find_system_font(font_weight: str = "normal") -> str | None:
    """システムに応じた日本語フォントを探す

    Args:
        font_weight: フォントの太さ（"normal" または "bold"）

    Returns:
        フォントファイルパス（見つからない場合はNone）
    """
    system = platform.system()
    font_paths = []

    if system == "Darwin":  # macOS
        if font_weight == "bold":
            font_paths = [
                "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
                "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
                "/System/Library/Fonts/Hiragino Sans GB.ttc",
                "/Library/Fonts/Arial Unicode.ttf",
            ]
        else:
            font_paths = [
                "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
                "/System/Library/Fonts/Hiragino Sans GB.ttc",
                "/Library/Fonts/Arial Unicode.ttf",
            ]
    elif system == "Windows":
        if font_weight == "bold":
            font_paths = [
                "C:/Windows/Fonts/yugothicb.ttf",
                "C:/Windows/Fonts/yugothic.ttf",
                "C:/Windows/Fonts/msgothic.ttc",
            ]
        else:
            font_paths = [
                "C:/Windows/Fonts/yugothic.ttf",
                "C:/Windows/Fonts/msgothic.ttc",
            ]
    else:  # Linux
        if font_weight == "bold":
            font_paths = [
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            ]
        else:
            font_paths = [
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            ]

    for font_path in font_paths:
        if Path(font_path).exists():
            return font_path

    return None
