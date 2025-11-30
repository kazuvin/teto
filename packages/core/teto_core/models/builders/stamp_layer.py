from typing import Literal, Union
from ..layers import StampLayer
from ..effects import AnimationEffect


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

    def at(self, start_time: float) -> 'StampLayerBuilder':
        """開始時間を設定"""
        self._start_time = start_time
        return self

    def position(self, x: Union[int, float], y: Union[int, float]) -> 'StampLayerBuilder':
        """位置を設定（ピクセルまたは0-1の割合）"""
        self._position_x = x
        self._position_y = y
        return self

    def with_scale(self, scale: float) -> 'StampLayerBuilder':
        """スケールを設定"""
        self._scale = scale
        return self

    def fade_in(
        self,
        duration: float = 1.0,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut"
    ) -> 'StampLayerBuilder':
        """フェードインエフェクトを追加"""
        effect = AnimationEffect(type="fadein", duration=duration, easing=easing)
        self._effects.append(effect)
        return self

    def fade_out(
        self,
        duration: float = 1.0,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut"
    ) -> 'StampLayerBuilder':
        """フェードアウトエフェクトを追加"""
        effect = AnimationEffect(type="fadeout", duration=duration, easing=easing)
        self._effects.append(effect)
        return self

    def bounce(
        self,
        duration: float = 1.0,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut"
    ) -> 'StampLayerBuilder':
        """バウンスエフェクトを追加"""
        effect = AnimationEffect(type="bounce", duration=duration, easing=easing)
        self._effects.append(effect)
        return self

    def rotate(
        self,
        angle: float,
        duration: float | None = None,
        easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeInOut"
    ) -> 'StampLayerBuilder':
        """回転エフェクトを追加"""
        effect = AnimationEffect(
            type="rotate",
            duration=duration or self._duration,
            rotation_angle=angle,
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
    ) -> 'StampLayerBuilder':
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
