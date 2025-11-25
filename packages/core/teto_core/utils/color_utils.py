"""カラー関連のユーティリティ関数"""

# カラーマッピングの定数
COLOR_MAP = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "gray": (128, 128, 128),
}


def parse_color(color: str) -> tuple[int, int, int]:
    """色名をRGBタプルに変換する

    Args:
        color: 色名（例: "white", "black", "red"）

    Returns:
        RGB値のタプル（例: (255, 255, 255)）
    """
    return COLOR_MAP.get(color.lower(), (255, 255, 255))


def parse_background_color(bg_color: str | None) -> tuple[tuple[int, int, int], float]:
    """背景色と不透明度をパースする

    Args:
        bg_color: 背景色の文字列 (例: "black@0.5")

    Returns:
        (RGB色, 不透明度)のタプル

    Examples:
        >>> parse_background_color("black@0.5")
        ((0, 0, 0), 0.5)
        >>> parse_background_color("red@0.8")
        ((255, 0, 0), 0.8)
        >>> parse_background_color(None)
        ((0, 0, 0), 0.5)
    """
    if not bg_color:
        bg_color = "black@0.5"

    opacity = 0.5
    color_part = bg_color

    if "@" in bg_color:
        color_part, opacity_part = bg_color.split("@")
        opacity = float(opacity_part)

    color_rgb = parse_color(color_part)
    return color_rgb, opacity
