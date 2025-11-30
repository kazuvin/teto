from typing import Literal, Union
from .models import (
    VideoLayer,
    ImageLayer,
    AudioLayer,
    SubtitleLayer,
    SubtitleItem,
    StampLayer,
)
from ..effect.models import AnimationEffect, TransitionConfig
from ..core.types import ResponsiveSize


class VideoLayerBuilder:
    """動画レイヤーのビルダー"""

    def __init__(self, path: str):
        self._path = path
        self._duration = None
        self._volume = 1.0
        self._effects: list[AnimationEffect] = []
        self._transition: TransitionConfig | None = None

    def for_duration(self, duration: float) -> "VideoLayerBuilder":
        """継続時間を設定"""
        self._duration = duration
        return self

    def with_volume(self, volume: float) -> "VideoLayerBuilder":
        """音量を設定"""
        self._volume = volume
        return self

    def fade_in(
        self,
        duration: float = 1.0,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut",
    ) -> "VideoLayerBuilder":
        """フェードインエフェクトを追加"""
        effect = AnimationEffect(type="fadein", duration=duration, easing=easing)
        self._effects.append(effect)
        return self

    def fade_out(
        self,
        duration: float = 1.0,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut",
    ) -> "VideoLayerBuilder":
        """フェードアウトエフェクトを追加"""
        effect = AnimationEffect(type="fadeout", duration=duration, easing=easing)
        self._effects.append(effect)
        return self

    def slide_in(
        self,
        direction: Literal["left", "right", "top", "bottom"] = "left",
        duration: float = 1.0,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut",
    ) -> "VideoLayerBuilder":
        """スライドインエフェクトを追加"""
        effect = AnimationEffect(
            type="slideIn", duration=duration, direction=direction, easing=easing
        )
        self._effects.append(effect)
        return self

    def slide_out(
        self,
        direction: Literal["left", "right", "top", "bottom"] = "left",
        duration: float = 1.0,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut",
    ) -> "VideoLayerBuilder":
        """スライドアウトエフェクトを追加"""
        effect = AnimationEffect(
            type="slideOut", duration=duration, direction=direction, easing=easing
        )
        self._effects.append(effect)
        return self

    def zoom(
        self,
        start_scale: float = 1.0,
        end_scale: float = 1.2,
        duration: float = 1.0,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut",
    ) -> "VideoLayerBuilder":
        """ズームエフェクトを追加"""
        effect = AnimationEffect(
            type="zoom",
            duration=duration,
            start_scale=start_scale,
            end_scale=end_scale,
            easing=easing,
        )
        self._effects.append(effect)
        return self

    def blur(
        self,
        amount: float = 5.0,
        duration: float = 1.0,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut",
    ) -> "VideoLayerBuilder":
        """ブラーエフェクトを追加"""
        effect = AnimationEffect(
            type="blur", duration=duration, blur_amount=amount, easing=easing
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
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut",
    ) -> "VideoLayerBuilder":
        """カラーグレーディングエフェクトを追加"""
        effect = AnimationEffect(
            type="colorGrade",
            duration=duration,
            color_temp=color_temp,
            saturation=saturation,
            contrast=contrast,
            brightness=brightness,
            easing=easing,
        )
        self._effects.append(effect)
        return self

    def vignette(
        self,
        amount: float = 0.5,
        duration: float = 1.0,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut",
    ) -> "VideoLayerBuilder":
        """ビネットエフェクトを追加"""
        effect = AnimationEffect(
            type="vignette", duration=duration, vignette_amount=amount, easing=easing
        )
        self._effects.append(effect)
        return self

    def glitch(
        self,
        intensity: float = 0.5,
        duration: float = 1.0,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut",
    ) -> "VideoLayerBuilder":
        """グリッチエフェクトを追加"""
        effect = AnimationEffect(
            type="glitch", duration=duration, glitch_intensity=intensity, easing=easing
        )
        self._effects.append(effect)
        return self

    def rotate(
        self,
        angle: float,
        duration: float = 1.0,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut",
    ) -> "VideoLayerBuilder":
        """回転エフェクトを追加"""
        effect = AnimationEffect(
            type="rotate", duration=duration, rotation_angle=angle, easing=easing
        )
        self._effects.append(effect)
        return self

    def crossfade(self, duration: float = 0.5) -> "VideoLayerBuilder":
        """次のクリップへのクロスフェードトランジションを設定"""
        self._transition = TransitionConfig(type="crossfade", duration=duration)
        return self

    def build(self) -> VideoLayer:
        """VideoLayer を構築"""
        return VideoLayer(
            path=self._path,
            duration=self._duration,
            volume=self._volume,
            effects=self._effects,
            transition=self._transition,
        )


class ImageLayerBuilder:
    """画像レイヤーのビルダー"""

    def __init__(self, path: str, duration: float):
        self._path = path
        self._duration = duration
        self._effects: list[AnimationEffect] = []
        self._transition: TransitionConfig | None = None

    def fade_in(
        self,
        duration: float = 1.0,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut",
    ) -> "ImageLayerBuilder":
        """フェードインエフェクトを追加"""
        effect = AnimationEffect(type="fadein", duration=duration, easing=easing)
        self._effects.append(effect)
        return self

    def fade_out(
        self,
        duration: float = 1.0,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut",
    ) -> "ImageLayerBuilder":
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
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut",
    ) -> "ImageLayerBuilder":
        """Ken Burns エフェクトを追加"""
        effect = AnimationEffect(
            type="kenBurns",
            duration=duration or self._duration,
            start_scale=start_scale,
            end_scale=end_scale,
            pan_start=pan_start,
            pan_end=pan_end,
            easing=easing,
        )
        self._effects.append(effect)
        return self

    def zoom(
        self,
        start_scale: float = 1.0,
        end_scale: float = 1.2,
        duration: float | None = None,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut",
    ) -> "ImageLayerBuilder":
        """ズームエフェクトを追加"""
        effect = AnimationEffect(
            type="zoom",
            duration=duration or self._duration,
            start_scale=start_scale,
            end_scale=end_scale,
            easing=easing,
        )
        self._effects.append(effect)
        return self

    def slide_in(
        self,
        direction: Literal["left", "right", "top", "bottom"] = "left",
        duration: float = 1.0,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut",
    ) -> "ImageLayerBuilder":
        """スライドインエフェクトを追加"""
        effect = AnimationEffect(
            type="slideIn", duration=duration, direction=direction, easing=easing
        )
        self._effects.append(effect)
        return self

    def blur(
        self,
        amount: float = 5.0,
        duration: float = 1.0,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut",
    ) -> "ImageLayerBuilder":
        """ブラーエフェクトを追加"""
        effect = AnimationEffect(
            type="blur", duration=duration, blur_amount=amount, easing=easing
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
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut",
    ) -> "ImageLayerBuilder":
        """カラーグレーディングエフェクトを追加"""
        effect = AnimationEffect(
            type="colorGrade",
            duration=duration or self._duration,
            color_temp=color_temp,
            saturation=saturation,
            contrast=contrast,
            brightness=brightness,
            easing=easing,
        )
        self._effects.append(effect)
        return self

    def vignette(
        self,
        amount: float = 0.5,
        duration: float | None = None,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut",
    ) -> "ImageLayerBuilder":
        """ビネットエフェクトを追加"""
        effect = AnimationEffect(
            type="vignette",
            duration=duration or self._duration,
            vignette_amount=amount,
            easing=easing,
        )
        self._effects.append(effect)
        return self

    def rotate(
        self,
        angle: float,
        duration: float | None = None,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut",
    ) -> "ImageLayerBuilder":
        """回転エフェクトを追加"""
        effect = AnimationEffect(
            type="rotate",
            duration=duration or self._duration,
            rotation_angle=angle,
            easing=easing,
        )
        self._effects.append(effect)
        return self

    def crossfade(self, duration: float = 0.5) -> "ImageLayerBuilder":
        """次のクリップへのクロスフェードトランジションを設定"""
        self._transition = TransitionConfig(type="crossfade", duration=duration)
        return self

    def build(self) -> ImageLayer:
        """ImageLayer を構築"""
        return ImageLayer(
            path=self._path,
            duration=self._duration,
            effects=self._effects,
            transition=self._transition,
        )


class AudioLayerBuilder:
    """音声レイヤーのビルダー"""

    def __init__(self, path: str):
        self._path = path
        self._start_time = 0.0
        self._duration = None
        self._volume = 1.0

    def at(self, start_time: float) -> "AudioLayerBuilder":
        """開始時間を設定"""
        self._start_time = start_time
        return self

    def for_duration(self, duration: float) -> "AudioLayerBuilder":
        """継続時間を設定"""
        self._duration = duration
        return self

    def with_volume(self, volume: float) -> "AudioLayerBuilder":
        """音量を設定"""
        self._volume = volume
        return self

    def build(self) -> AudioLayer:
        """AudioLayer を構築"""
        return AudioLayer(
            path=self._path,
            start_time=self._start_time,
            duration=self._duration,
            volume=self._volume,
        )


class SubtitleItemBuilder:
    """字幕アイテムのビルダー"""

    def __init__(self, text: str, start_time: float, end_time: float):
        self._text = text
        self._start_time = start_time
        self._end_time = end_time

    def build(self) -> SubtitleItem:
        """SubtitleItem を構築"""
        return SubtitleItem(
            text=self._text,
            start_time=self._start_time,
            end_time=self._end_time,
        )


class SubtitleLayerBuilder:
    """字幕レイヤーのビルダー"""

    def __init__(self):
        self._items: list[SubtitleItem] = []
        self._font_size: Union[int, ResponsiveSize] = "base"
        self._font_color = "white"
        self._google_font = None
        self._font_weight: Literal["normal", "bold"] = "normal"
        self._stroke_width: Union[int, ResponsiveSize] = 0
        self._stroke_color = "black"
        self._outer_stroke_width: Union[int, ResponsiveSize] = 0
        self._outer_stroke_color = "white"
        self._bg_color = "black@0.5"
        self._position: Literal["bottom", "top", "center"] = "bottom"
        self._appearance: Literal["plain", "background", "shadow", "drop-shadow"] = (
            "background"
        )

    def add_item(
        self, text: str, start_time: float, end_time: float
    ) -> "SubtitleLayerBuilder":
        """字幕アイテムを追加"""
        item = SubtitleItem(text=text, start_time=start_time, end_time=end_time)
        self._items.append(item)
        return self

    def font(
        self,
        size: Union[int, ResponsiveSize] = "base",
        color: str = "white",
        google_font: str | None = None,
        weight: Literal["normal", "bold"] = "normal",
    ) -> "SubtitleLayerBuilder":
        """フォント設定"""
        self._font_size = size
        self._font_color = color
        self._google_font = google_font
        self._font_weight = weight
        return self

    def stroke(
        self,
        width: Union[int, ResponsiveSize] = 0,
        color: str = "black",
        outer_width: Union[int, ResponsiveSize] = 0,
        outer_color: str = "white",
    ) -> "SubtitleLayerBuilder":
        """縁取り設定"""
        self._stroke_width = width
        self._stroke_color = color
        self._outer_stroke_width = outer_width
        self._outer_stroke_color = outer_color
        return self

    def style(
        self,
        position: Literal["bottom", "top", "center"] = "bottom",
        appearance: Literal[
            "plain", "background", "shadow", "drop-shadow"
        ] = "background",
        bg_color: str | None = "black@0.5",
    ) -> "SubtitleLayerBuilder":
        """スタイル設定"""
        self._position = position
        self._appearance = appearance
        self._bg_color = bg_color
        return self

    def build(self) -> SubtitleLayer:
        """SubtitleLayer を構築"""
        return SubtitleLayer(
            items=self._items,
            font_size=self._font_size,
            font_color=self._font_color,
            google_font=self._google_font,
            font_weight=self._font_weight,
            stroke_width=self._stroke_width,
            stroke_color=self._stroke_color,
            outer_stroke_width=self._outer_stroke_width,
            outer_stroke_color=self._outer_stroke_color,
            bg_color=self._bg_color,
            position=self._position,
            appearance=self._appearance,
        )


class StampLayerBuilder:
    """スタンプレイヤーのビルダー"""

    def __init__(self, path: str, duration: float):
        self._path = path
        self._duration = duration
        self._start_time = 0.0
        self._position_x: Union[int, float] = 0
        self._position_y: Union[int, float] = 0
        self._scale = 1.0
        self._effects: list[AnimationEffect] = []

    def at(self, start_time: float) -> "StampLayerBuilder":
        """開始時間を設定"""
        self._start_time = start_time
        return self

    def position(
        self, x: Union[int, float], y: Union[int, float]
    ) -> "StampLayerBuilder":
        """位置を設定（ピクセルまたは0-1の割合）"""
        self._position_x = x
        self._position_y = y
        return self

    def with_scale(self, scale: float) -> "StampLayerBuilder":
        """スケールを設定"""
        self._scale = scale
        return self

    def fade_in(
        self,
        duration: float = 1.0,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut",
    ) -> "StampLayerBuilder":
        """フェードインエフェクトを追加"""
        effect = AnimationEffect(type="fadein", duration=duration, easing=easing)
        self._effects.append(effect)
        return self

    def fade_out(
        self,
        duration: float = 1.0,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut",
    ) -> "StampLayerBuilder":
        """フェードアウトエフェクトを追加"""
        effect = AnimationEffect(type="fadeout", duration=duration, easing=easing)
        self._effects.append(effect)
        return self

    def bounce(
        self,
        duration: float = 1.0,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut",
    ) -> "StampLayerBuilder":
        """バウンスエフェクトを追加"""
        effect = AnimationEffect(type="bounce", duration=duration, easing=easing)
        self._effects.append(effect)
        return self

    def rotate(
        self,
        angle: float,
        duration: float | None = None,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut",
    ) -> "StampLayerBuilder":
        """回転エフェクトを追加"""
        effect = AnimationEffect(
            type="rotate",
            duration=duration or self._duration,
            rotation_angle=angle,
            easing=easing,
        )
        self._effects.append(effect)
        return self

    def zoom(
        self,
        start_scale: float = 1.0,
        end_scale: float = 1.2,
        duration: float | None = None,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut",
    ) -> "StampLayerBuilder":
        """ズームエフェクトを追加"""
        effect = AnimationEffect(
            type="zoom",
            duration=duration or self._duration,
            start_scale=start_scale,
            end_scale=end_scale,
            easing=easing,
        )
        self._effects.append(effect)
        return self

    def build(self) -> StampLayer:
        """StampLayer を構築"""
        return StampLayer(
            path=self._path,
            duration=self._duration,
            start_time=self._start_time,
            position_x=self._position_x,
            position_y=self._position_y,
            scale=self._scale,
            effects=self._effects,
        )
