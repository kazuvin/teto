"""Default scene preset"""

from ...effect.models import AnimationEffect, TransitionConfig
from .base import ScenePreset


class DefaultScenePreset(ScenePreset):
    """デフォルトプリセット（Ken Burns + crossfade）"""

    @property
    def name(self) -> str:
        return "default"

    def get_image_effects(self) -> list[AnimationEffect]:
        # 画像には軽い Ken Burns エフェクト
        return [AnimationEffect(type="kenBurns", duration=1.0)]

    def get_video_effects(self) -> list[AnimationEffect]:
        return []

    def get_transition(self) -> TransitionConfig | None:
        return TransitionConfig(type="crossfade", duration=0.5)


# 後方互換性のためのエイリアス
DefaultLayerPreset = DefaultScenePreset
