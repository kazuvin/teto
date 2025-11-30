from typing import Literal, Union
from ..layers import SubtitleLayer, SubtitleItem
from ...types import ResponsiveSize


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
        self._appearance: Literal["plain", "background", "shadow", "drop-shadow"] = "background"

    def add_item(self, text: str, start_time: float, end_time: float) -> 'SubtitleLayerBuilder':
        """字幕アイテムを追加"""
        item = SubtitleItem(text=text, start_time=start_time, end_time=end_time)
        self._items.append(item)
        return self

    def font(
        self,
        size: Union[int, ResponsiveSize] = "base",
        color: str = "white",
        google_font: str | None = None,
        weight: Literal["normal", "bold"] = "normal"
    ) -> 'SubtitleLayerBuilder':
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
        outer_color: str = "white"
    ) -> 'SubtitleLayerBuilder':
        """縁取り設定"""
        self._stroke_width = width
        self._stroke_color = color
        self._outer_stroke_width = outer_width
        self._outer_stroke_color = outer_color
        return self

    def style(
        self,
        position: Literal["bottom", "top", "center"] = "bottom",
        appearance: Literal["plain", "background", "shadow", "drop-shadow"] = "background",
        bg_color: str | None = "black@0.5"
    ) -> 'SubtitleLayerBuilder':
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
