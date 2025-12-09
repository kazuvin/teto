"""Composite preset base - Subtitle style configuration"""

from typing import Union, Literal
from pydantic import BaseModel, Field

from ...core.types import ResponsiveSize
from ...layer.models import PartialStyle


class SubtitleStyleConfig(BaseModel):
    """字幕スタイル設定

    複合プリセットで使用する字幕スタイルの設定。
    """

    font_size: Union[int, ResponsiveSize] = Field(
        "base", description="フォントサイズ（数値またはxs/sm/base/lg/xl/2xl）"
    )
    font_color: str = Field("white", description="フォントカラー")
    google_font: str | None = Field(
        "Noto Sans JP", description="Google Fontsのフォント名"
    )
    font_weight: Literal["normal", "bold"] = Field(
        "normal", description="フォントの太さ"
    )
    stroke_width: Union[int, ResponsiveSize] = Field(
        0, description="縁取りの幅（数値またはxs/sm/base/lg/xl/2xl）"
    )
    stroke_color: str = Field("black", description="縁取りの色")
    outer_stroke_width: Union[int, ResponsiveSize] = Field(
        0, description="外側縁取りの幅（数値またはxs/sm/base/lg/xl/2xl）"
    )
    outer_stroke_color: str = Field("white", description="外側縁取りの色")
    bg_color: str | None = Field("black@0.5", description="背景色（透明度付き）")
    position: Literal["bottom", "top", "center"] = Field(
        "bottom", description="字幕位置"
    )
    appearance: Literal["plain", "background", "shadow", "drop-shadow"] = Field(
        "background", description="字幕スタイル"
    )
    margin_horizontal: int = Field(
        0,
        description="横方向のマージン（ピクセル）。キャラクターと字幕が被らないように調整",
        ge=0,
    )
    styles: dict[str, PartialStyle] = Field(
        default_factory=dict,
        description="部分スタイル定義（マークアップタグ名とスタイルのマッピング）",
    )


# 後方互換性のためのエイリアス（effects/ モジュールから再エクスポート）
# Note: ScenePreset, LayerPreset は effects/ モジュールで定義されています
#       presets/__init__.py から再エクスポートされます
