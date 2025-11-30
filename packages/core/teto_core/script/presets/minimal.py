"""Minimal layer preset"""

from ...effect.models import AnimationEffect, TransitionConfig
from ...output_config.models import OutputConfig
from .base import LayerPreset, SubtitleStyleConfig


class MinimalPreset(LayerPreset):
    """ミニマルプリセット（シンプル、エフェクトなし）"""

    @property
    def name(self) -> str:
        return "minimal"

    def get_output_config(self, output_path: str = "output.mp4") -> OutputConfig:
        return OutputConfig(
            path=output_path,
            width=1920,
            height=1080,
            fps=30,
            codec="libx264",
        )

    def get_subtitle_style(self) -> SubtitleStyleConfig:
        return SubtitleStyleConfig(
            font_size="base",
            font_color="white",
            google_font="Noto Sans JP",
            appearance="plain",
            position="bottom",
        )

    def get_image_effects(self) -> list[AnimationEffect]:
        return []  # エフェクトなし

    def get_video_effects(self) -> list[AnimationEffect]:
        return []

    def get_transition(self) -> TransitionConfig | None:
        return None  # カット（トランジションなし）
