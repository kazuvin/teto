"""Bold subtitle scene preset"""

from ...effect.models import AnimationEffect, TransitionConfig
from .base import ScenePreset


class BoldSubtitleScenePreset(ScenePreset):
    """太字字幕プリセット（zoom + crossfade）"""

    @property
    def name(self) -> str:
        return "bold_subtitle"

    def get_image_effects(self) -> list[AnimationEffect]:
        return [
            AnimationEffect(type="zoom", start_scale=1.0, end_scale=1.1, duration=1.0)
        ]

    def get_video_effects(self) -> list[AnimationEffect]:
        return []

    def get_transition(self) -> TransitionConfig | None:
        return TransitionConfig(type="crossfade", duration=0.3)


# 後方互換性のためのエイリアス
BoldSubtitlePreset = BoldSubtitleScenePreset
