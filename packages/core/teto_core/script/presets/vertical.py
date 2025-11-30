"""Vertical video layer preset"""

from ...effect.models import AnimationEffect, TransitionConfig
from ...output_config.models import OutputConfig
from .base import LayerPreset, SubtitleStyleConfig


class VerticalPreset(LayerPreset):
    """縦型動画プリセット（9:16）"""

    @property
    def name(self) -> str:
        return "vertical"

    def get_output_config(self, output_path: str = "output.mp4") -> OutputConfig:
        return OutputConfig(
            path=output_path,
            width=1080,
            height=1920,
            fps=30,
            codec="libx264",
        )

    def get_subtitle_style(self) -> SubtitleStyleConfig:
        return SubtitleStyleConfig(
            font_size="xl",
            font_color="white",
            google_font="Noto Sans JP",
            font_weight="bold",
            stroke_width="base",
            stroke_color="black",
            appearance="background",
            position="center",
        )

    def get_image_effects(self) -> list[AnimationEffect]:
        return [AnimationEffect(type="kenBurns", duration=1.0)]

    def get_video_effects(self) -> list[AnimationEffect]:
        return []

    def get_transition(self) -> TransitionConfig | None:
        return TransitionConfig(type="crossfade", duration=0.3)
