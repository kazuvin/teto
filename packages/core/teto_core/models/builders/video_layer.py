from typing import Literal
from ..layers import VideoLayer
from ..effects import AnimationEffect


class VideoLayerBuilder:
    """動画レイヤーのビルダー"""

    def __init__(self, path: str):
        self._path = path
        self._start_time = 0.0
        self._duration = None
        self._volume = 1.0
        self._effects: list[AnimationEffect] = []

    def at(self, start_time: float) -> 'VideoLayerBuilder':
        """開始時間を設定"""
        self._start_time = start_time
        return self

    def for_duration(self, duration: float) -> 'VideoLayerBuilder':
        """継続時間を設定"""
        self._duration = duration
        return self

    def with_volume(self, volume: float) -> 'VideoLayerBuilder':
        """音量を設定"""
        self._volume = volume
        return self

    def fade_in(self, duration: float = 1.0, easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut") -> 'VideoLayerBuilder':
        """フェードインエフェクトを追加"""
        effect = AnimationEffect(type="fadein", duration=duration, easing=easing)
        self._effects.append(effect)
        return self

    def fade_out(self, duration: float = 1.0, easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut") -> 'VideoLayerBuilder':
        """フェードアウトエフェクトを追加"""
        effect = AnimationEffect(type="fadeout", duration=duration, easing=easing)
        self._effects.append(effect)
        return self

    def slide_in(
        self,
        direction: Literal["left", "right", "top", "bottom"] = "left",
        duration: float = 1.0,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut"
    ) -> 'VideoLayerBuilder':
        """スライドインエフェクトを追加"""
        effect = AnimationEffect(
            type="slideIn",
            duration=duration,
            direction=direction,
            easing=easing
        )
        self._effects.append(effect)
        return self

    def slide_out(
        self,
        direction: Literal["left", "right", "top", "bottom"] = "left",
        duration: float = 1.0,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut"
    ) -> 'VideoLayerBuilder':
        """スライドアウトエフェクトを追加"""
        effect = AnimationEffect(
            type="slideOut",
            duration=duration,
            direction=direction,
            easing=easing
        )
        self._effects.append(effect)
        return self

    def zoom(
        self,
        start_scale: float = 1.0,
        end_scale: float = 1.2,
        duration: float = 1.0,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut"
    ) -> 'VideoLayerBuilder':
        """ズームエフェクトを追加"""
        effect = AnimationEffect(
            type="zoom",
            duration=duration,
            start_scale=start_scale,
            end_scale=end_scale,
            easing=easing
        )
        self._effects.append(effect)
        return self

    def blur(
        self,
        amount: float = 5.0,
        duration: float = 1.0,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut"
    ) -> 'VideoLayerBuilder':
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
        duration: float = 1.0,
        color_temp: float | None = None,
        saturation: float | None = None,
        contrast: float | None = None,
        brightness: float | None = None,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut"
    ) -> 'VideoLayerBuilder':
        """カラーグレーディングエフェクトを追加"""
        effect = AnimationEffect(
            type="colorGrade",
            duration=duration,
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
        duration: float = 1.0,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut"
    ) -> 'VideoLayerBuilder':
        """ビネットエフェクトを追加"""
        effect = AnimationEffect(
            type="vignette",
            duration=duration,
            vignette_amount=amount,
            easing=easing
        )
        self._effects.append(effect)
        return self

    def glitch(
        self,
        intensity: float = 0.5,
        duration: float = 1.0,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut"
    ) -> 'VideoLayerBuilder':
        """グリッチエフェクトを追加"""
        effect = AnimationEffect(
            type="glitch",
            duration=duration,
            glitch_intensity=intensity,
            easing=easing
        )
        self._effects.append(effect)
        return self

    def rotate(
        self,
        angle: float,
        duration: float = 1.0,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut"
    ) -> 'VideoLayerBuilder':
        """回転エフェクトを追加"""
        effect = AnimationEffect(
            type="rotate",
            duration=duration,
            rotation_angle=angle,
            easing=easing
        )
        self._effects.append(effect)
        return self

    def build(self) -> VideoLayer:
        """VideoLayer を構築"""
        return VideoLayer(
            path=self._path,
            start_time=self._start_time,
            duration=self._duration,
            volume=self._volume,
            effects=self._effects,
        )
