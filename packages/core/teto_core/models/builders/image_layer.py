from typing import Literal
from ..layers import ImageLayer
from ..effects import AnimationEffect


class ImageLayerBuilder:
    """画像レイヤーのビルダー"""

    def __init__(self, path: str, duration: float):
        self._path = path
        self._duration = duration
        self._start_time = 0.0
        self._effects: list[AnimationEffect] = []

    def at(self, start_time: float) -> 'ImageLayerBuilder':
        """開始時間を設定"""
        self._start_time = start_time
        return self

    def fade_in(
        self,
        duration: float = 1.0,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut"
    ) -> 'ImageLayerBuilder':
        """フェードインエフェクトを追加"""
        effect = AnimationEffect(type="fadein", duration=duration, easing=easing)
        self._effects.append(effect)
        return self

    def fade_out(
        self,
        duration: float = 1.0,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut"
    ) -> 'ImageLayerBuilder':
        """フェードアウトエフェクトを追加"""
        effect = AnimationEffect(type="fadeout", duration=duration, easing=easing)
        self._effects.append(effect)
        return self

    def ken_burns(
        self,
        start_scale: float = 1.0,
        end_scale: float = 1.3,
        pan_start: tuple[float, float] = (0.0, 0.0),
        pan_end: tuple[float, float] = (0.1, 0.1),
        duration: float | None = None,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut"
    ) -> 'ImageLayerBuilder':
        """Ken Burns エフェクトを追加"""
        effect = AnimationEffect(
            type="kenBurns",
            duration=duration or self._duration,
            start_scale=start_scale,
            end_scale=end_scale,
            pan_start=pan_start,
            pan_end=pan_end,
            easing=easing
        )
        self._effects.append(effect)
        return self

    def zoom(
        self,
        start_scale: float = 1.0,
        end_scale: float = 1.2,
        duration: float | None = None,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut"
    ) -> 'ImageLayerBuilder':
        """ズームエフェクトを追加"""
        effect = AnimationEffect(
            type="zoom",
            duration=duration or self._duration,
            start_scale=start_scale,
            end_scale=end_scale,
            easing=easing
        )
        self._effects.append(effect)
        return self

    def slide_in(
        self,
        direction: Literal["left", "right", "top", "bottom"] = "left",
        duration: float = 1.0,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut"
    ) -> 'ImageLayerBuilder':
        """スライドインエフェクトを追加"""
        effect = AnimationEffect(
            type="slideIn",
            duration=duration,
            direction=direction,
            easing=easing
        )
        self._effects.append(effect)
        return self

    def blur(
        self,
        amount: float = 5.0,
        duration: float = 1.0,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut"
    ) -> 'ImageLayerBuilder':
        """ブラーエフェクトを追加"""
        effect = AnimationEffect(
            type="blur",
            duration=duration,
            blur_amount=amount,
            easing=easing
        )
        self._effects.append(effect)
        return self

    def color_grade(
        self,
        duration: float | None = None,
        color_temp: float | None = None,
        saturation: float | None = None,
        contrast: float | None = None,
        brightness: float | None = None,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut"
    ) -> 'ImageLayerBuilder':
        """カラーグレーディングエフェクトを追加"""
        effect = AnimationEffect(
            type="colorGrade",
            duration=duration or self._duration,
            color_temp=color_temp,
            saturation=saturation,
            contrast=contrast,
            brightness=brightness,
            easing=easing
        )
        self._effects.append(effect)
        return self

    def vignette(
        self,
        amount: float = 0.5,
        duration: float | None = None,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut"
    ) -> 'ImageLayerBuilder':
        """ビネットエフェクトを追加"""
        effect = AnimationEffect(
            type="vignette",
            duration=duration or self._duration,
            vignette_amount=amount,
            easing=easing
        )
        self._effects.append(effect)
        return self

    def rotate(
        self,
        angle: float,
        duration: float | None = None,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut"
    ) -> 'ImageLayerBuilder':
        """回転エフェクトを追加"""
        effect = AnimationEffect(
            type="rotate",
            duration=duration or self._duration,
            rotation_angle=angle,
            easing=easing
        )
        self._effects.append(effect)
        return self

    def build(self) -> ImageLayer:
        """ImageLayer を構築"""
        return ImageLayer(
            path=self._path,
            duration=self._duration,
            start_time=self._start_time,
            effects=self._effects,
        )
