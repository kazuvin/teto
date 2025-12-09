"""Slideshow effect preset"""

from ...effect.models import AnimationEffect
from .base import EffectPreset


class SlideshowEffectPreset(EffectPreset):
    """スライドショープリセット（slideIn）

    スライドショー形式の演出向けプリセット。
    プレゼンテーションや写真スライドショーに適しています。
    """

    @property
    def name(self) -> str:
        return "slideshow"

    def get_image_effects(self) -> list[AnimationEffect]:
        return [
            AnimationEffect(
                type="slideIn",
                direction="right",
                duration=0.5,
                easing="easeOut",
            ),
        ]

    def get_video_effects(self) -> list[AnimationEffect]:
        return [
            AnimationEffect(
                type="slideIn",
                direction="right",
                duration=0.5,
                easing="easeOut",
            ),
        ]


# 後方互換性のためのエイリアス
SlideshowScenePreset = SlideshowEffectPreset
SlideshowPreset = SlideshowEffectPreset
