"""Default effect preset"""

from ...effect.models import AnimationEffect
from .base import EffectPreset


class DefaultEffectPreset(EffectPreset):
    """デフォルトプリセット（静止画）"""

    @property
    def name(self) -> str:
        return "default"

    def get_image_effects(self) -> list[AnimationEffect]:
        return []  # 静止画

    def get_video_effects(self) -> list[AnimationEffect]:
        return []


# 後方互換性のためのエイリアス
DefaultScenePreset = DefaultEffectPreset
DefaultLayerPreset = DefaultEffectPreset
