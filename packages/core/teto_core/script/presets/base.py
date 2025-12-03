"""Layer preset base interface"""

from abc import ABC, abstractmethod
from typing import Union, Literal
from pydantic import BaseModel, Field

from ...effect.models import AnimationEffect, TransitionConfig
from ...output_config.models import OutputConfig
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


class LayerPreset(ABC):
    """レイヤー設定プリセット（Strategy）

    動画のレイヤー設定（エフェクト、フォント、トランジション）を
    定型化するインターフェース。
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """プリセット名"""
        ...

    @abstractmethod
    def get_output_config(self, output_path: str = "output.mp4") -> OutputConfig:
        """出力設定を取得

        Args:
            output_path: 出力ファイルパス

        Returns:
            OutputConfig: 出力設定
        """
        ...

    @abstractmethod
    def get_subtitle_style(self) -> SubtitleStyleConfig:
        """字幕スタイル設定を取得

        Returns:
            SubtitleStyleConfig: 字幕スタイル設定
        """
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

    @abstractmethod
    def get_transition(self) -> TransitionConfig | None:
        """トランジション設定を取得

        Returns:
            TransitionConfig | None: トランジション設定（Noneの場合はカット）
        """
        ...
