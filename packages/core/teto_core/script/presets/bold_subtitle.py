"""Bold subtitle layer preset"""

from ...effect.models import AnimationEffect, TransitionConfig
from ...output_config.models import OutputConfig
from .base import LayerPreset, SubtitleStyleConfig


class BoldSubtitlePreset(LayerPreset):
    """太字字幕プリセット（目立つ字幕）"""

    @property
    def name(self) -> str:
        return "bold_subtitle"

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
            font_size="xl",
            font_color="yellow",
            google_font="Noto Sans JP",
            font_weight="bold",
            stroke_width="base",
            stroke_color="black",
            appearance="drop-shadow",
            position="center",
        )

    def get_image_effects(self) -> list[AnimationEffect]:
        return [
            AnimationEffect(type="zoom", start_scale=1.0, end_scale=1.1, duration=1.0)
        ]

    def get_video_effects(self) -> list[AnimationEffect]:
        return []

    def get_transition(self) -> TransitionConfig | None:
        return TransitionConfig(type="crossfade", duration=0.3)
