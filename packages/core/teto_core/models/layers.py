from pydantic import BaseModel, Field
from typing import TYPE_CHECKING, Union, Literal
from ..types import ResponsiveSize

if TYPE_CHECKING:
    from .effects import AnimationEffect


class BaseLayer(BaseModel):
    """レイヤーの基底クラス"""

    start_time: float = Field(0.0, description="開始時間（秒）", ge=0)
    duration: float | None = Field(None, description="継続時間（秒）。None の場合は自動", ge=0)


class VideoLayer(BaseLayer):
    """動画レイヤー"""

    type: Literal["video"] = "video"
    path: str = Field(..., description="動画ファイルパス")
    volume: float = Field(1.0, description="音量 (0.0-1.0)", ge=0, le=1.0)
    effects: list["AnimationEffect"] = Field(default_factory=list, description="アニメーション効果")


class ImageLayer(BaseLayer):
    """画像レイヤー"""

    type: Literal["image"] = "image"
    path: str = Field(..., description="画像ファイルパス")
    duration: float = Field(..., description="表示時間（秒）", gt=0)
    effects: list["AnimationEffect"] = Field(default_factory=list, description="アニメーション効果")


class AudioLayer(BaseLayer):
    """音声レイヤー"""

    type: Literal["audio"] = "audio"
    path: str = Field(..., description="音声ファイルパス")
    volume: float = Field(1.0, description="音量 (0.0-1.0)", ge=0, le=1.0)


class SubtitleItem(BaseModel):
    """字幕アイテム"""

    text: str = Field(..., description="字幕テキスト")
    start_time: float = Field(..., description="開始時間（秒）", ge=0)
    end_time: float = Field(..., description="終了時間（秒）", ge=0)


class SubtitleLayer(BaseModel):
    """字幕レイヤー"""

    type: Literal["subtitle"] = "subtitle"
    items: list[SubtitleItem] = Field(default_factory=list, description="字幕アイテムのリスト")
    font_size: Union[int, ResponsiveSize] = Field("base", description="フォントサイズ（数値またはxs/sm/base/lg/xl/2xl）")
    font_color: str = Field("white", description="フォントカラー")
    font_family: str | None = Field(None, description="フォントファミリー（フォントファイルパス）")
    font_weight: Literal["normal", "bold"] = Field("normal", description="フォントの太さ")
    stroke_width: Union[int, ResponsiveSize] = Field(0, description="縁取りの幅（数値またはxs/sm/base/lg/xl/2xl）")
    stroke_color: str = Field("black", description="縁取りの色")
    outer_stroke_width: Union[int, ResponsiveSize] = Field(0, description="外側縁取りの幅（数値またはxs/sm/base/lg/xl/2xl）")
    outer_stroke_color: str = Field("white", description="外側縁取りの色")
    bg_color: str | None = Field("black@0.5", description="背景色（透明度付き）")
    position: Literal["bottom", "top", "center"] = Field("bottom", description="字幕位置")
    appearance: Literal["plain", "background"] = Field("background", description="字幕スタイル（plain: 通常テキスト、background: 角丸半透明背景）")

# Forward reference の解決
from .effects import AnimationEffect
VideoLayer.model_rebuild()
ImageLayer.model_rebuild()
