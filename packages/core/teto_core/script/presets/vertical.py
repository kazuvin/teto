"""Vertical video scene preset"""

from ...effect.models import AnimationEffect, TransitionConfig
from .base import ScenePreset


class VerticalScenePreset(ScenePreset):
    """縦型動画プリセット（Ken Burns + crossfade）

    Note:
        出力解像度（1080x1920など）は Script.output で指定してください。
        このプリセットはエフェクト・トランジションのみを定義します。
    """

    @property
    def name(self) -> str:
        return "vertical"

    def get_image_effects(self) -> list[AnimationEffect]:
        return [AnimationEffect(type="kenBurns", duration=1.0)]

    def get_video_effects(self) -> list[AnimationEffect]:
        return []

    def get_transition(self) -> TransitionConfig | None:
        return TransitionConfig(type="crossfade", duration=0.3)


# 後方互換性のためのエイリアス
VerticalPreset = VerticalScenePreset
