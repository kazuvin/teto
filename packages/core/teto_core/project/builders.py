from typing import Literal, Union
from .models import Project, Timeline
from ..layer.models import VideoLayer, ImageLayer, AudioLayer, SubtitleLayer, StampLayer
from ..output_config.models import OutputConfig
from ..layer.builders import (
    VideoLayerBuilder,
    ImageLayerBuilder,
    AudioLayerBuilder,
    SubtitleLayerBuilder,
    StampLayerBuilder,
)


class ProjectBuilder:
    """プロジェクトのビルダー"""

    def __init__(self, output_path: str = "output.mp4"):
        self._output = OutputConfig(path=output_path)
        self._video_layers: list[Union[VideoLayer, ImageLayer]] = []
        self._audio_layers: list[AudioLayer] = []
        self._subtitle_layers: list[SubtitleLayer] = []
        self._stamp_layers: list[StampLayer] = []

    def output(
        self,
        path: str | None = None,
        width: int = 1920,
        height: int = 1080,
        fps: int = 30,
        codec: str = "libx264",
        audio_codec: str = "aac",
        bitrate: str | None = None,
        subtitle_mode: Literal["burn", "srt", "vtt", "none"] = "burn",
    ) -> "ProjectBuilder":
        """出力設定"""
        if path:
            self._output.path = path
        self._output.width = width
        self._output.height = height
        self._output.fps = fps
        self._output.codec = codec
        self._output.audio_codec = audio_codec
        self._output.bitrate = bitrate
        self._output.subtitle_mode = subtitle_mode
        return self

    def add_video(self, path: str) -> VideoLayerBuilder:
        """動画レイヤーを追加（ビルダーを返す）"""
        builder = VideoLayerBuilder(path)
        # ビルダーの build() を自動的に呼び出して追加する仕組み
        original_build = builder.build

        def auto_build():
            layer = original_build()
            self._video_layers.append(layer)
            return self

        builder.build = auto_build
        return builder

    def add_image(self, path: str, duration: float) -> ImageLayerBuilder:
        """画像レイヤーを追加（ビルダーを返す）"""
        builder = ImageLayerBuilder(path, duration)
        original_build = builder.build

        def auto_build():
            layer = original_build()
            self._video_layers.append(layer)
            return self

        builder.build = auto_build
        return builder

    def add_audio(self, path: str) -> AudioLayerBuilder:
        """音声レイヤーを追加（ビルダーを返す）"""
        builder = AudioLayerBuilder(path)
        original_build = builder.build

        def auto_build():
            layer = original_build()
            self._audio_layers.append(layer)
            return self

        builder.build = auto_build
        return builder

    def add_subtitle_layer(self) -> SubtitleLayerBuilder:
        """字幕レイヤーを追加（ビルダーを返す）"""
        builder = SubtitleLayerBuilder()
        original_build = builder.build

        def auto_build():
            layer = original_build()
            self._subtitle_layers.append(layer)
            return self

        builder.build = auto_build
        return builder

    def add_stamp(self, path: str, duration: float) -> StampLayerBuilder:
        """スタンプレイヤーを追加（ビルダーを返す）"""
        builder = StampLayerBuilder(path, duration)
        original_build = builder.build

        def auto_build():
            layer = original_build()
            self._stamp_layers.append(layer)
            return self

        builder.build = auto_build
        return builder

    def build(self) -> Project:
        """Project を構築"""
        timeline = Timeline(
            video_layers=self._video_layers,
            audio_layers=self._audio_layers,
            subtitle_layers=self._subtitle_layers,
            stamp_layers=self._stamp_layers,
        )

        return Project(
            version="1.0",
            output=self._output,
            timeline=timeline,
        )
