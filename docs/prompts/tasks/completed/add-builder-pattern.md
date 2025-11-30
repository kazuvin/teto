# Builder パターンの導入 - プロジェクト構築の簡略化

## 概要
現在、`Project` オブジェクトの構築は Pydantic モデルの直接的なインスタンス化に依存しており、複雑なプロジェクトを作成する際にコードが冗長になります。Builder パターンを導入して、より直感的で読みやすい API を提供します。

## 現在の問題点

### 現在の使い方
```python
from teto_core.models import Project, Timeline, VideoLayer, SubtitleLayer, SubtitleItem, OutputConfig

# プロジェクトの作成が冗長
project = Project(
    version="1.0",
    output=OutputConfig(
        path="output.mp4",
        width=1920,
        height=1080,
        fps=30,
    ),
    timeline=Timeline(
        video_layers=[
            VideoLayer(
                type="video",
                path="intro.mp4",
                start_time=0.0,
                volume=1.0,
            ),
            VideoLayer(
                type="video",
                path="main.mp4",
                start_time=5.0,
                volume=0.8,
            ),
        ],
        subtitle_layers=[
            SubtitleLayer(
                type="subtitle",
                items=[
                    SubtitleItem(text="Hello", start_time=0.0, end_time=2.0),
                    SubtitleItem(text="World", start_time=2.0, end_time=4.0),
                ],
                font_size="lg",
                font_color="white",
            )
        ]
    )
)
```

### 問題
- ネストが深く、読みにくい
- デフォルト値を何度も指定する必要がある
- タイポやフィールド名の間違いに気づきにくい
- 複雑なプロジェクトでは可読性が著しく低下
- Fluent Interface がないため、段階的な構築が困難

## 目標設計

### Builder パターンによる実装

```python
# models/builders.py
from typing import Literal
from ..models import (
    Project, Timeline, VideoLayer, ImageLayer, AudioLayer,
    SubtitleLayer, SubtitleItem, StampLayer, OutputConfig,
    AnimationEffect
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
        self._font_size = "base"
        self._font_color = "white"
        self._google_font = None
        self._font_weight = "normal"
        self._stroke_width = 0
        self._stroke_color = "black"
        self._outer_stroke_width = 0
        self._outer_stroke_color = "white"
        self._bg_color = "black@0.5"
        self._position = "bottom"
        self._appearance = "background"

    def add_item(self, text: str, start_time: float, end_time: float) -> 'SubtitleLayerBuilder':
        """字幕アイテムを追加"""
        item = SubtitleItem(text=text, start_time=start_time, end_time=end_time)
        self._items.append(item)
        return self

    def font(
        self,
        size="base",
        color="white",
        google_font=None,
        weight="normal"
    ) -> 'SubtitleLayerBuilder':
        """フォント設定"""
        self._font_size = size
        self._font_color = color
        self._google_font = google_font
        self._font_weight = weight
        return self

    def stroke(
        self,
        width=0,
        color="black",
        outer_width=0,
        outer_color="white"
    ) -> 'SubtitleLayerBuilder':
        """縁取り設定"""
        self._stroke_width = width
        self._stroke_color = color
        self._outer_stroke_width = outer_width
        self._outer_stroke_color = outer_color
        return self

    def style(
        self,
        position="bottom",
        appearance="background",
        bg_color="black@0.5"
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

    def fade_in(self, duration: float = 1.0, easing="easeInOut") -> 'VideoLayerBuilder':
        """フェードインエフェクトを追加"""
        effect = AnimationEffect(type="fadein", duration=duration, easing=easing)
        self._effects.append(effect)
        return self

    def fade_out(self, duration: float = 1.0, easing="easeInOut") -> 'VideoLayerBuilder':
        """フェードアウトエフェクトを追加"""
        effect = AnimationEffect(type="fadeout", duration=duration, easing=easing)
        self._effects.append(effect)
        return self

    def slide_in(
        self,
        direction: Literal["left", "right", "top", "bottom"] = "left",
        duration: float = 1.0,
        easing="easeInOut"
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

    def zoom(
        self,
        start_scale: float = 1.0,
        end_scale: float = 1.2,
        duration: float = None,
        easing="easeInOut"
    ) -> 'VideoLayerBuilder':
        """ズームエフェクトを追加"""
        effect = AnimationEffect(
            type="zoom",
            duration=duration or 1.0,
            start_scale=start_scale,
            end_scale=end_scale,
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

    def fade_in(self, duration: float = 1.0) -> 'ImageLayerBuilder':
        """フェードインエフェクトを追加"""
        effect = AnimationEffect(type="fadein", duration=duration)
        self._effects.append(effect)
        return self

    def ken_burns(
        self,
        start_scale: float = 1.0,
        end_scale: float = 1.3,
        pan_start: tuple[float, float] = (0.0, 0.0),
        pan_end: tuple[float, float] = (0.1, 0.1),
        duration: float = None,
    ) -> 'ImageLayerBuilder':
        """Ken Burns エフェクトを追加"""
        effect = AnimationEffect(
            type="kenBurns",
            duration=duration or self._duration,
            start_scale=start_scale,
            end_scale=end_scale,
            pan_start=pan_start,
            pan_end=pan_end,
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


class AudioLayerBuilder:
    """音声レイヤーのビルダー"""

    def __init__(self, path: str):
        self._path = path
        self._start_time = 0.0
        self._duration = None
        self._volume = 1.0

    def at(self, start_time: float) -> 'AudioLayerBuilder':
        """開始時間を設定"""
        self._start_time = start_time
        return self

    def for_duration(self, duration: float) -> 'AudioLayerBuilder':
        """継続時間を設定"""
        self._duration = duration
        return self

    def with_volume(self, volume: float) -> 'AudioLayerBuilder':
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


class ProjectBuilder:
    """プロジェクトのビルダー"""

    def __init__(self, output_path: str = "output.mp4"):
        self._output = OutputConfig(path=output_path)
        self._video_layers = []
        self._audio_layers = []
        self._subtitle_layers = []
        self._stamp_layers = []

    def output(
        self,
        path: str = None,
        width: int = 1920,
        height: int = 1080,
        fps: int = 30,
        codec: str = "libx264",
        audio_codec: str = "aac",
        bitrate: str = "5000k",
        subtitle_mode: Literal["burn", "srt", "vtt", "none"] = "burn"
    ) -> 'ProjectBuilder':
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
            return layer
        builder.build = auto_build
        return builder

    def add_image(self, path: str, duration: float) -> ImageLayerBuilder:
        """画像レイヤーを追加（ビルダーを返す）"""
        builder = ImageLayerBuilder(path, duration)
        original_build = builder.build
        def auto_build():
            layer = original_build()
            self._video_layers.append(layer)
            return layer
        builder.build = auto_build
        return builder

    def add_audio(self, path: str) -> AudioLayerBuilder:
        """音声レイヤーを追加（ビルダーを返す）"""
        builder = AudioLayerBuilder(path)
        original_build = builder.build
        def auto_build():
            layer = original_build()
            self._audio_layers.append(layer)
            return layer
        builder.build = auto_build
        return builder

    def add_subtitle_layer(self) -> SubtitleLayerBuilder:
        """字幕レイヤーを追加（ビルダーを返す）"""
        builder = SubtitleLayerBuilder()
        original_build = builder.build
        def auto_build():
            layer = original_build()
            self._subtitle_layers.append(layer)
            return layer
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
```

### 使用例

```python
from teto_core.models.builders import ProjectBuilder

# Fluent Interface で直感的にプロジェクトを構築
project = ProjectBuilder("output.mp4") \
    .output(width=1920, height=1080, fps=30) \
    .add_video("intro.mp4").at(0.0).fade_in(1.0).build() \
    .add_video("main.mp4").at(5.0).with_volume(0.8).fade_out(1.0).build() \
    .add_image("cover.jpg", 3.0).ken_burns().build() \
    .add_audio("bgm.mp3").with_volume(0.3).build() \
    .add_subtitle_layer() \
        .add_item("Hello", 0.0, 2.0) \
        .add_item("World", 2.0, 4.0) \
        .font(size="lg", color="white") \
        .style(position="bottom", appearance="background") \
        .build() \
    .build()

# または、段階的に構築
builder = ProjectBuilder()
builder.output(path="my_video.mp4", width=1280, height=720)

video = builder.add_video("clip1.mp4")
video.at(0.0).fade_in(0.5).fade_out(0.5).build()

subtitles = builder.add_subtitle_layer()
subtitles.add_item("Introduction", 0, 3)
subtitles.add_item("Main content", 3, 10)
subtitles.font(size="xl", google_font="Noto Sans JP")
subtitles.build()

project = builder.build()
```

## タスク詳細

### Phase 1: 基盤の作成
- [ ] `models/builders/` ディレクトリを作成
- [ ] `models/builders/base.py` - 基底ビルダークラス
- [ ] `models/builders/__init__.py` - エクスポート設定

### Phase 2: レイヤービルダーの実装
- [ ] `models/builders/video_layer.py` - `VideoLayerBuilder`
- [ ] `models/builders/image_layer.py` - `ImageLayerBuilder`
- [ ] `models/builders/audio_layer.py` - `AudioLayerBuilder`
- [ ] `models/builders/subtitle_layer.py` - `SubtitleLayerBuilder`, `SubtitleItemBuilder`
- [ ] `models/builders/stamp_layer.py` - `StampLayerBuilder`

### Phase 3: プロジェクトビルダーの実装
- [ ] `models/builders/project.py` - `ProjectBuilder`
- [ ] Fluent Interface の実装
- [ ] 自動的な `build()` 呼び出しの仕組み

### Phase 4: エフェクトビルダーの実装
- [ ] 各レイヤービルダーにエフェクト追加メソッドを実装
- [ ] `fade_in()`, `fade_out()`, `slide_in()`, `zoom()`, `ken_burns()` など

### Phase 5: ドキュメントとサンプル
- [ ] Builder パターンの使用方法をドキュメント化
- [ ] サンプルプロジェクトを Builder で書き直す
- [ ] 既存の Pydantic ベースの API との互換性を確認

### Phase 6: ユーティリティメソッド
- [ ] よく使うパターンのヘルパーメソッド追加
- [ ] テンプレートビルダー（YouTubeショート向け、など）
- [ ] バリデーションとエラーメッセージの改善

## 期待される効果

### メリット
1. **可読性向上**: ネストが減り、コードが読みやすくなる
2. **タイプセーフ**: IDE の補完が効きやすい
3. **段階的構築**: 複雑なプロジェクトを段階的に構築可能
4. **デフォルト値管理**: ビルダーでデフォルト値を一元管理
5. **エラー削減**: Fluent Interface で設定漏れを防ぐ
6. **初心者フレンドリー**: より直感的な API

## 後方互換性
- 既存の Pydantic モデルベースの API は維持
- Builder は追加の便利機能として提供
- 内部的には同じ Pydantic モデルを使用

## 検討事項
- ビルダーの `build()` 呼び出しを自動化するか、明示的に呼ぶか
- バリデーションをビルダーレベルで行うか、Pydantic に任せるか
- テンプレートビルダーをどこまで提供するか

## 参考
- Builder パターン（GoF デザインパターン）
- Fluent Interface（Martin Fowler）
- Method Chaining パターン
