"""Scene preset base interface"""

from abc import ABC, abstractmethod
from typing import Union, Literal
from pydantic import BaseModel, Field

from ...effect.models import AnimationEffect
from ...core.types import ResponsiveSize
from ...layer.models import PartialStyle


class SubtitleStyleConfig(BaseModel):
    """字幕スタイル設定"""

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
    styles: dict[str, PartialStyle] = Field(
        default_factory=dict,
        description="部分スタイル定義（マークアップタグ名とスタイルのマッピング）",
    )


class ScenePreset(ABC):
    """シーンプリセット（Strategy）

    シーン毎のエフェクト設定を定型化するインターフェース。

    Note:
        出力設定と字幕スタイルは Script モデルで直接指定する。
        トランジションは Scene モデルで直接指定する。
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """プリセット名"""
        ...

    @abstractmethod
    def get_image_effects(self) -> list[AnimationEffect]:
        """画像レイヤーに適用するエフェクトを取得

        Returns:
            list[AnimationEffect]: エフェクトリスト
        """
        ...

    @abstractmethod
    def get_video_effects(self) -> list[AnimationEffect]:
        """動画レイヤーに適用するエフェクトを取得

        Returns:
            list[AnimationEffect]: エフェクトリスト
        """
        ...


# 後方互換性のためのエイリアス
LayerPreset = ScenePreset
