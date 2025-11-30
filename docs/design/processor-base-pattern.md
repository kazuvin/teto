# ProcessorBase - Template Method パターンの実装

## 概要

`ProcessorBase` は、すべてのプロセッサークラスの基底クラスです。Template Method パターンを使用して、共通の処理フローを定義し、各サブクラスは具体的な処理のみを実装します。

## 設計パターン

### Template Method パターン

Template Method パターンは、アルゴリズムの骨格を定義し、いくつかのステップをサブクラスに委譲するデザインパターンです。

```python
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar("T")  # 入力データの型
R = TypeVar("R")  # 出力データの型


class ProcessorBase(ABC, Generic[T, R]):
    """プロセッサーの基底クラス"""

    def execute(self, data: T, **kwargs) -> R:
        """処理を実行（Template Method）"""
        # 1. バリデーション
        if not self.validate(data, **kwargs):
            raise ValueError(f"Validation failed for {type(data).__name__}")

        # 2. 前処理
        data = self.preprocess(data, **kwargs)

        # 3. メイン処理（サブクラスで実装）
        result = self.process(data, **kwargs)

        # 4. 後処理
        result = self.postprocess(result, **kwargs)

        return result

    @abstractmethod
    def process(self, data: T, **kwargs) -> R:
        """メイン処理（サブクラスで実装）"""
        pass

    def validate(self, data: T, **kwargs) -> bool:
        """データのバリデーション（オプション）"""
        return True

    def preprocess(self, data: T, **kwargs) -> T:
        """前処理（オプション）"""
        return data

    def postprocess(self, result: R, **kwargs) -> R:
        """後処理（オプション）"""
        return result
```

## 処理フロー

`execute()` メソッドは以下の順序で処理を実行します：

1. **バリデーション** (`validate`)

   - 入力データの妥当性をチェック
   - 失敗した場合は `ValueError` を投げる

2. **前処理** (`preprocess`)

   - データの正規化や変換を行う

3. **メイン処理** (`process`)

   - 実際の処理ロジック（サブクラスで必ず実装）

4. **後処理** (`postprocess`)
   - 結果の整形や追加処理を行う

## 実装例

### 動画レイヤープロセッサー

```python
from pathlib import Path
from moviepy import VideoFileClip
from teto_core.processors.base import ProcessorBase
from teto_core.models.layers import VideoLayer


class VideoLayerProcessor(ProcessorBase[VideoLayer, VideoFileClip]):
    """動画レイヤー処理プロセッサー"""

    def __init__(self, effect_processor=None):
        self.effect_processor = effect_processor or EffectProcessor()

    def validate(self, layer: VideoLayer, **kwargs) -> bool:
        """動画ファイルの存在チェック"""
        if not Path(layer.path).exists():
            print(f"Warning: Video file not found: {layer.path}")
            return False
        return True

    def process(self, layer: VideoLayer, **kwargs) -> VideoFileClip:
        """動画レイヤーを読み込む"""
        output_size = kwargs.get('output_size')
        clip = VideoFileClip(layer.path)

        # 音量調整
        if clip.audio and layer.volume != 1.0:
            clip = clip.with_volume_scaled(layer.volume)

        # 継続時間の調整
        if layer.duration is not None:
            clip = clip.subclipped(0, min(layer.duration, clip.duration))

        # エフェクトを適用
        if layer.effects and output_size:
            clip = self.effect_processor.apply_effects(
                clip, layer.effects, output_size
            )

        # 開始時間の設定
        clip = clip.with_start(layer.start_time)

        return clip
```

### カスタムバリデーション

```python
class StrictVideoProcessor(VideoLayerProcessor):
    """厳格なバリデーションを持つ動画プロセッサー"""

    def validate(self, layer: VideoLayer, **kwargs) -> bool:
        # 親クラスのバリデーション
        if not super().validate(layer, **kwargs):
            return False

        # 追加のバリデーション
        if layer.duration and layer.duration > 300:
            print("Warning: Video is longer than 5 minutes")
            return False

        return True
```

## 依存性注入

各プロセッサーは、コンストラクタで依存関係を注入できます。

```python
# デフォルトのプロセッサーを使用
processor = VideoLayerProcessor()

# カスタムプロセッサーを注入
custom_effect_processor = CustomEffectProcessor()
processor = VideoLayerProcessor(effect_processor=custom_effect_processor)
```

## 使用例

### 基本的な使い方

```python
from teto_core.processors import VideoLayerProcessor
from teto_core.models.layers import VideoLayer

# プロセッサーを作成
processor = VideoLayerProcessor()

# レイヤーを作成
layer = VideoLayer(
    path="path/to/video.mp4",
    start_time=0,
    duration=10,
    volume=0.8
)

# 処理を実行
clip = processor.execute(layer, output_size=(1920, 1080))
```

### タイムライン処理

```python
from teto_core.processors import VideoTimelineProcessor
from teto_core.models.layers import VideoLayer, ImageLayer

# タイムラインプロセッサーを作成
processor = VideoTimelineProcessor()

# レイヤーリストを作成
layers = [
    VideoLayer(path="intro.mp4", start_time=0),
    ImageLayer(path="slide.png", start_time=5, duration=3),
    VideoLayer(path="outro.mp4", start_time=8),
]

# タイムラインを処理
final_clip = processor.execute(layers, output_size=(1920, 1080))
```

### 依存性注入を使った拡張

```python
# カスタムエフェクトプロセッサーを作成
class MyEffectProcessor(EffectProcessor):
    def apply_effects(self, clip, effects, size):
        # カスタムエフェクト処理
        return super().apply_effects(clip, effects, size)

# カスタムプロセッサーを注入
effect_processor = MyEffectProcessor()
video_processor = VideoLayerProcessor(effect_processor=effect_processor)
image_processor = ImageLayerProcessor(effect_processor=effect_processor)

# タイムラインプロセッサーに注入
timeline_processor = VideoTimelineProcessor(
    video_processor=video_processor,
    image_processor=image_processor
)

# 処理を実行
clip = timeline_processor.execute(layers, output_size=(1920, 1080))
```

## 利点

1. **一貫性**: すべてのプロセッサーが同じインターフェースを持つ
2. **拡張性**: バリデーション、前処理、後処理を簡単に追加可能
3. **テスタビリティ**: 依存性注入によりモック/スタブが使用可能
4. **再利用性**: プロセッサーインスタンスを異なるコンテキストで再利用可能
5. **保守性**: 共通ロジックが基底クラスに集約される

## 後方互換性

既存の static メソッドは後方互換性のために残されていますが、新しいコードでは新しいプロセッサークラスを使用してください。

```python
# 古い API（非推奨）
from teto_core.processors import VideoProcessor

clip = VideoProcessor.load_video_layer(layer, output_size)

# 新しい API（推奨）
from teto_core.processors import VideoLayerProcessor

processor = VideoLayerProcessor()
clip = processor.execute(layer, output_size=output_size)
```

## 実装されたプロセッサー

### 動画処理

- `VideoLayerProcessor`: 動画レイヤーを処理
- `ImageLayerProcessor`: 画像レイヤーを処理
- `StampLayerProcessor`: スタンプレイヤーを処理
- `VideoProcessor`: 動画タイムラインを処理

### 音声処理

- `AudioLayerProcessor`: 音声レイヤーを処理
- `AudioProcessor`: 音声タイムラインを処理

### 字幕処理

- `SubtitleBurnProcessor`: 字幕を動画に焼き込む
- `SubtitleExportProcessor`: 字幕を SRT/VTT 形式でエクスポート

## テスト

各プロセッサーは、以下のテストケースを持ちます：

- バリデーションのテスト
- 前処理・後処理のテスト
- 依存性注入のテスト
- 後方互換性のテスト

詳細は `packages/core/tests/unit/test_processor_base.py` と `packages/core/tests/unit/test_processor_integration.py` を参照してください。
