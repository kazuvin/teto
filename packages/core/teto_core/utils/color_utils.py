"""カラー関連のユーティリティ関数"""

from ..constants import COLOR_MAP


def parse_color(color: str) -> tuple[int, int, int]:
    """色名またはHEX形式の色をRGBタプルに変換する

    Args:
        color: 色名（例: "white", "black", "red"）またはHEX形式（例: "#DADADA", "#FFF"）

    Returns:
        RGB値のタプル（例: (255, 255, 255)）
    """
    # HEX形式の場合
    if color.startswith("#"):
        hex_color = color[1:]

        # 3桁のHEX形式（#FFFなど）を6桁に展開
        if len(hex_color) == 3:
            hex_color = "".join([c * 2 for c in hex_color])

        # 6桁のHEX形式をRGBに変換
        if len(hex_color) == 6:
            try:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                return (r, g, b)
            except ValueError:
                # 変換エラーの場合はデフォルト（白）を返す
                return (255, 255, 255)

    # 色名の場合
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
        return (0, 0, 0), 0.5

    opacity = 0.5
    color_part = bg_color

    if "@" in bg_color:
        color_part, opacity_part = bg_color.split("@")
        opacity = float(opacity_part)

    color_rgb = parse_color(color_part)
    return color_rgb, opacity
