"""Dramatic scene preset"""

from ...effect.models import AnimationEffect
from .base import ScenePreset


class DramaticScenePreset(ScenePreset):
    """ドラマティックプリセット（glitch + colorGrade）

    インパクトのある演出向けプリセット。
    緊張感のあるシーンやインパクトを与えたい場面に適しています。
    """

    @property
    def name(self) -> str:
        return "dramatic"

    def get_image_effects(self) -> list[AnimationEffect]:
        return [
            AnimationEffect(type="glitch", glitch_intensity=0.2, duration=0.1),
            AnimationEffect(
                type="colorGrade",
                contrast=1.3,
                saturation=0.8,
                brightness=0.9,
                duration=0.5,
            ),
        ]

    def get_video_effects(self) -> list[AnimationEffect]:
        return [
            AnimationEffect(type="glitch", glitch_intensity=0.15, duration=0.1),
            AnimationEffect(
                type="colorGrade",
                contrast=1.2,
                saturation=0.85,
                brightness=0.95,
                duration=0.5,
            ),
        ]


# 後方互換性のためのエイリアス
DramaticPreset = DramaticScenePreset
