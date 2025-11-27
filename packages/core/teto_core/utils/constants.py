"""定数定義（レスポンシブ対応）"""

from .size_utils import get_scale_factor

# 基準解像度（1080p）での値
BASE_LINE_SPACING = 28
BASE_TEXT_PADDING = 10
BASE_BG_PADDING_X = 20
BASE_BG_PADDING_Y = 10
BASE_BG_RADIUS = 15
BASE_MARGIN_BOTTOM = 60
BASE_MARGIN_TOP = 50
BASE_MAX_TEXT_WIDTH_OFFSET = 200

# 文字列定数（スケールしない）
PUNCTUATION_CHARS = "。！？、，"


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


# 下位互換性のため、1080pの値をデフォルトとして公開
LINE_SPACING = BASE_LINE_SPACING
TEXT_PADDING = BASE_TEXT_PADDING
BG_PADDING_X = BASE_BG_PADDING_X
BG_PADDING_Y = BASE_BG_PADDING_Y
BG_RADIUS = BASE_BG_RADIUS
MARGIN_BOTTOM = BASE_MARGIN_BOTTOM
MARGIN_TOP = BASE_MARGIN_TOP
MAX_TEXT_WIDTH_OFFSET = BASE_MAX_TEXT_WIDTH_OFFSET
