"""Minimal scene preset"""

from ...effect.models import AnimationEffect, TransitionConfig
from .base import ScenePreset


class MinimalScenePreset(ScenePreset):
    """ミニマルプリセット（エフェクトなし、トランジションなし）"""

    @property
    def name(self) -> str:
        return "minimal"

    def get_image_effects(self) -> list[AnimationEffect]:
        return []  # エフェクトなし

    def get_video_effects(self) -> list[AnimationEffect]:
        return []

    def get_transition(self) -> TransitionConfig | None:
        return None  # カット（トランジションなし）


# 後方互換性のためのエイリアス
MinimalPreset = MinimalScenePreset
