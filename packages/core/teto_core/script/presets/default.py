"""Default scene preset"""

from ...effect.models import AnimationEffect
from .base import ScenePreset


class DefaultScenePreset(ScenePreset):
    """デフォルトプリセット（静止画）"""

    @property
    def name(self) -> str:
        return "default"

    def get_image_effects(self) -> list[AnimationEffect]:
        return []  # 静止画

    def get_video_effects(self) -> list[AnimationEffect]:
        return []


# 後方互換性のためのエイリアス
DefaultLayerPreset = DefaultScenePreset
