from enum import Enum
from pydantic import BaseModel, Field, field_validator
from typing import TYPE_CHECKING, Union, Literal
from ..core.types import ResponsiveSize


class PositionPreset(str, Enum):
    """プリセット位置の列挙型"""

    TOP_LEFT = "top-left"
    TOP_RIGHT = "top-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_RIGHT = "bottom-right"
    CUSTOM = "custom"  # x, y を直接指定


if TYPE_CHECKING:
    from ..effect.models import AnimationEffect, TransitionConfig


class BaseLayer(BaseModel):
    """レイヤーの基底クラス"""

    duration: float | None = Field(
        None, description="継続時間（秒）。None の場合は自動", ge=0
    )


class OverlayBaseLayer(BaseLayer):
    """オーバーレイレイヤーの基底クラス（自由配置用）"""

    start_time: float = Field(0.0, description="開始時間（秒）", ge=0)


class VideoLayer(BaseLayer):
    """動画レイヤー"""

    type: Literal["video"] = "video"
    path: str = Field(..., description="動画ファイルパス")
    volume: float = Field(1.0, description="音量 (0.0-1.0)", ge=0, le=1.0)
    loop: bool | None = Field(
        None,
        description="ナレーションより動画が短い場合にループ再生するか（None=True）",
    )
    effects: list["AnimationEffect"] = Field(
        default_factory=list, description="アニメーション効果"
    )
    transition: "TransitionConfig | None" = Field(
        None, description="次のクリップへのトランジション"
    )


class ImageLayer(BaseLayer):
    """画像レイヤー"""

    type: Literal["image"] = "image"
    path: str = Field(..., description="画像ファイルパス")
    duration: float = Field(..., description="表示時間（秒）", gt=0)
    effects: list["AnimationEffect"] = Field(
        default_factory=list, description="アニメーション効果"
    )
    transition: "TransitionConfig | None" = Field(
        None, description="次のクリップへのトランジション"
    )


class AudioLayer(OverlayBaseLayer):
    """音声レイヤー"""

    type: Literal["audio"] = "audio"
    path: str = Field(..., description="音声ファイルパス")
    volume: float = Field(1.0, description="音量 (0.0-1.0)", ge=0, le=1.0)


class StampLayer(OverlayBaseLayer):
    """スタンプレイヤー（装飾的な画像オーバーレイ）"""

    type: Literal["stamp"] = "stamp"
    path: str = Field(..., description="画像ファイルパス")
    duration: float = Field(..., description="表示時間（秒）", gt=0)
    position_x: Union[int, float] = Field(
        0, description="X座標（ピクセルまたは0-1の割合）"
    )
    position_y: Union[int, float] = Field(
        0, description="Y座標（ピクセルまたは0-1の割合）"
    )
    scale: float = Field(1.0, description="スケール", gt=0)
    opacity: float = Field(1.0, description="透明度（0.0〜1.0）", ge=0.0, le=1.0)
    position_preset: PositionPreset | None = Field(
        None, description="プリセット位置（指定時はposition_x, position_yより優先）"
    )
    margin: int = Field(
        20, description="プリセット使用時の端からの余白（ピクセル）", ge=0
    )
    effects: list["AnimationEffect"] = Field(
        default_factory=list, description="アニメーション効果"
    )

    @field_validator("opacity")
    @classmethod
    def validate_opacity(cls, v: float) -> float:
        """透明度が0.0〜1.0の範囲であることを確認"""
        if not 0.0 <= v <= 1.0:
            raise ValueError("opacity must be between 0.0 and 1.0")
        return v


class SubtitleItem(BaseModel):
    """字幕アイテム"""

    text: str = Field(..., description="字幕テキスト")
    start_time: float = Field(..., description="開始時間（秒）", ge=0)
    end_time: float = Field(..., description="終了時間（秒）", ge=0)


class PartialStyle(BaseModel):
    """部分スタイル定義（マークアップで適用）

    字幕テキスト内で部分的にスタイルを変更する際に使用。
    指定されたフィールドのみがデフォルトスタイルを上書きする。

    Example:
        ```json
        {
            "styles": {
                "emphasis": {"font_color": "red", "font_weight": "bold"},
                "highlight": {"font_color": "yellow"}
            }
        }
        ```
    """

    font_color: str | None = Field(None, description="フォントカラー")
    font_weight: Literal["normal", "bold"] | None = Field(
        None, description="フォントの太さ"
    )


class SubtitleLayer(BaseModel):
    """字幕レイヤー"""

    type: Literal["subtitle"] = "subtitle"
    items: list[SubtitleItem] = Field(
        default_factory=list, description="字幕アイテムのリスト"
    )

    # 部分スタイル定義
    styles: dict[str, PartialStyle] = Field(
        default_factory=dict,
        description="マークアップタグ名とスタイルのマッピング（例: {'emphasis': {'font_color': 'red'}}）",
    )

    # デフォルトフォント設定
    font_size: Union[int, ResponsiveSize] = Field(
        "base", description="フォントサイズ（数値またはxs/sm/base/lg/xl/2xl）"
    )
    font_color: str = Field("white", description="フォントカラー")
    google_font: str | None = Field(
        None, description="Google Fontsのフォント名（例: 'Noto Sans JP', 'Roboto'）"
    )
    font_weight: Literal["normal", "bold"] = Field(
        "normal", description="フォントの太さ"
    )

    # 縁取り設定（レイヤー全体で統一）
    stroke_width: Union[int, ResponsiveSize] = Field(
        0, description="縁取りの幅（数値またはxs/sm/base/lg/xl/2xl）"
    )
    stroke_color: str = Field("black", description="縁取りの色")
    outer_stroke_width: Union[int, ResponsiveSize] = Field(
        0, description="外側縁取りの幅（数値またはxs/sm/base/lg/xl/2xl）"
    )
    outer_stroke_color: str = Field("white", description="外側縁取りの色")

    # 背景・位置設定
    bg_color: str | None = Field("black@0.5", description="背景色（透明度付き）")
    position: Literal["bottom", "top", "center"] = Field(
        "bottom", description="字幕位置"
    )
    appearance: Literal["plain", "background", "shadow", "drop-shadow"] = Field(
        "background",
        description="字幕スタイル（plain: 通常テキスト、background: 角丸半透明背景、shadow: シャドウ付き、drop-shadow: ぼかしシャドウ付き）",
    )


# Forward reference の解決
from ..effect.models import AnimationEffect, TransitionConfig  # noqa: E402

VideoLayer.model_rebuild()
ImageLayer.model_rebuild()
StampLayer.model_rebuild()
