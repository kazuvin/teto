"""Default layer preset"""

from ...effect.models import AnimationEffect, TransitionConfig
from ...output_config.models import OutputConfig
from .base import LayerPreset, SubtitleStyleConfig


class DefaultLayerPreset(LayerPreset):
    """デフォルトプリセット（シンプルな設定）"""

    @property
    def name(self) -> str:
        return "default"

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
            font_size="lg",
            font_color="white",
            google_font="Noto Sans JP",
            stroke_width="sm",
            stroke_color="black",
            appearance="shadow",
            position="bottom",
        )

    def get_image_effects(self) -> list[AnimationEffect]:
        # 画像には軽い Ken Burns エフェクト
        return [AnimationEffect(type="kenBurns", duration=1.0)]

    def get_video_effects(self) -> list[AnimationEffect]:
        return []

    def get_transition(self) -> TransitionConfig | None:
        return TransitionConfig(type="crossfade", duration=0.5)
