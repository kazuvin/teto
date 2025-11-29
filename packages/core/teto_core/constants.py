"""定数定義（レスポンシブ対応）

このモジュールはプロジェクト全体で使用される定数を一元管理します。
"""

from typing import Literal

# ============================================================================
# 型定義
# ============================================================================

# レスポンシブサイズ型
ResponsiveSize = Literal["xs", "sm", "base", "lg", "xl", "2xl"]


# ============================================================================
# 基準解像度
# ============================================================================

# 基準解像度（1080p）
BASE_HEIGHT = 1080


# ============================================================================
# スケールマップ
# ============================================================================

# 各サイズのスケール係数
SIZE_SCALE_MAP = {
    "xs": 0.5,
    "sm": 0.75,
    "base": 1.0,
    "lg": 1.5,
    "xl": 2.0,
    "2xl": 3.0,
}


# ============================================================================
# 基準値（1080pでの値）
# ============================================================================

# フォント関連
BASE_FONT_SIZE = 48

# ボーダー・縁取り関連
BASE_BORDER_WIDTH = 3

# パディング関連
BASE_PADDING = 20
BASE_TEXT_PADDING = 10
BASE_BG_PADDING_X = 20
BASE_BG_PADDING_Y = 10

# ラディウス（角丸）関連
BASE_RADIUS = 15
BASE_BG_RADIUS = 15

# マージン関連
BASE_MARGIN = 60
BASE_MARGIN_BOTTOM = 60
BASE_MARGIN_TOP = 50

# スペーシング関連
BASE_LINE_SPACING = 28

# その他のサイズ
BASE_MAX_TEXT_WIDTH_OFFSET = 200


# ============================================================================
# カラーマップ
# ============================================================================

COLOR_MAP = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "gray": (128, 128, 128),
}


# ============================================================================
# 文字列定数
# ============================================================================

# 句読点文字（スケールしない）
PUNCTUATION_CHARS = "。！？、，"


# ============================================================================
# ヘルパー関数
# ============================================================================

def get_scale_factor(video_height: int) -> float:
    """解像度に基づくスケール係数を計算

    Args:
        video_height: 動画の高さ（ピクセル）

    Returns:
        スケール係数

    Examples:
        >>> get_scale_factor(1080)
        1.0
        >>> get_scale_factor(2160)  # 4K
        2.0
        >>> get_scale_factor(720)
        0.6666666666666666
    """
    return video_height / BASE_HEIGHT


def get_responsive_constants(video_height: int) -> dict:
    """解像度に応じた定数を計算

    Args:
        video_height: 動画の高さ

    Returns:
        定数の辞書
    """
    scale = get_scale_factor(video_height)

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


# ============================================================================
# 下位互換性のための定数エクスポート（1080pの値をデフォルトとして公開）
# ============================================================================

LINE_SPACING = BASE_LINE_SPACING
TEXT_PADDING = BASE_TEXT_PADDING
BG_PADDING_X = BASE_BG_PADDING_X
BG_PADDING_Y = BASE_BG_PADDING_Y
BG_RADIUS = BASE_BG_RADIUS
MARGIN_BOTTOM = BASE_MARGIN_BOTTOM
MARGIN_TOP = BASE_MARGIN_TOP
MAX_TEXT_WIDTH_OFFSET = BASE_MAX_TEXT_WIDTH_OFFSET
