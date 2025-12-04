"""Slideshow scene preset"""

from ...effect.models import AnimationEffect, TransitionConfig
from .base import ScenePreset


class SlideshowScenePreset(ScenePreset):
    """スライドショープリセット（slideIn + fadeout）

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

    def get_transition(self) -> TransitionConfig | None:
        return TransitionConfig(type="crossfade", duration=0.4)


# 後方互換性のためのエイリアス
SlideshowPreset = SlideshowScenePreset
