# ProcessorBase の統合 - Template Method パターンの活用

## 概要
現在、`ProcessorBase` クラスは定義されていますが、実際の Processor クラス（VideoProcessor, AudioProcessor, SubtitleProcessor）では使用されていません。すべてが static メソッドのみで構成されています。ProcessorBase を活用した一貫性のある設計に変更します。

## 現在の問題点

**場所**:
- `packages/core/teto_core/processors/base.py` - 未使用の基底クラス
- `packages/core/teto_core/processors/video.py` - static メソッドのみ
- `packages/core/teto_core/processors/audio.py` - static メソッドのみ
- `packages/core/teto_core/processors/subtitle.py` - static メソッドのみ

### 問題
- ProcessorBase が定義されているが活用されていない
- 各 Processor が static メソッドのみで、オブジェクト指向の利点を活かせていない
- バリデーション、前処理、後処理のフックが使えない
- テスト時にモックやスタブの注入が困難
- プロセッサーの状態管理ができない（設定の保持など）

## 目標設計

### Template Method パターンの適用

```python
# processors/base.py
from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic

T = TypeVar("T")
R = TypeVar("R")


class ProcessorBase(ABC, Generic[T, R]):
    """プロセッサーの基底クラス

    Template Method パターンを使用して、共通の処理フローを定義。
    各サブクラスは具体的な処理のみを実装する。
    """

    def execute(self, data: T, **kwargs) -> R:
        """処理を実行（Template Method）

        Args:
            data: 処理対象のデータ
            **kwargs: 追加のパラメータ

        Returns:
            処理結果
        """
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
        """メイン処理（サブクラスで実装）

        Args:
            data: 処理対象のデータ
            **kwargs: 追加のパラメータ

        Returns:
            処理結果
        """
        pass

    def validate(self, data: T, **kwargs) -> bool:
        """データのバリデーション（オプション）

        Args:
            data: 検証対象のデータ
            **kwargs: 追加のパラメータ

        Returns:
            バリデーション結果
        """
        return True

    def preprocess(self, data: T, **kwargs) -> T:
        """前処理（オプション）

        Args:
            data: 前処理対象のデータ
            **kwargs: 追加のパラメータ

        Returns:
            前処理されたデータ
        """
        return data

    def postprocess(self, result: R, **kwargs) -> R:
        """後処理（オプション）

        Args:
            result: 後処理対象の結果
            **kwargs: 追加のパラメータ

        Returns:
            後処理された結果
        """
        return result
```

### VideoProcessor の実装例

```python
# processors/video.py
from pathlib import Path
from moviepy import VideoFileClip, ImageClip
from .base import ProcessorBase
from ..models.layers import VideoLayer, ImageLayer
from .animation import AnimationProcessor
from typing import Union

class VideoLayerProcessor(ProcessorBase[VideoLayer, VideoFileClip]):
    """動画レイヤー処理プロセッサー"""

    def __init__(self, animation_processor: AnimationProcessor = None):
        self.animation_processor = animation_processor or AnimationProcessor()

    def validate(self, layer: VideoLayer, **kwargs) -> bool:
        """動画ファイルの存在チェック"""
        if not Path(layer.path).exists():
            print(f"Warning: Video file not found: {layer.path}")
            return False
        return True

    def process(self, layer: VideoLayer, **kwargs) -> VideoFileClip:
        """動画レイヤーを読み込む"""
        output_size = kwargs.get('output_size')

        # 動画を読み込む
        clip = VideoFileClip(layer.path)

        # 音量調整
        if clip.audio and layer.volume != 1.0:
            clip = clip.with_volume_scaled(layer.volume)

        # 継続時間の調整
        if layer.duration is not None:
            clip = clip.subclipped(0, min(layer.duration, clip.duration))

        # アニメーション効果を適用
        if layer.effects and output_size:
            clip = self.animation_processor.apply_effects(
                clip, layer.effects, output_size
            )

        # 開始時間の設定
        clip = clip.with_start(layer.start_time)

        return clip


class ImageLayerProcessor(ProcessorBase[ImageLayer, ImageClip]):
    """画像レイヤー処理プロセッサー"""

    def __init__(self, animation_processor: AnimationProcessor = None):
        self.animation_processor = animation_processor or AnimationProcessor()

    def validate(self, layer: ImageLayer, **kwargs) -> bool:
        """画像ファイルの存在チェック"""
        if not Path(layer.path).exists():
            print(f"Warning: Image file not found: {layer.path}")
            return False

        target_size = kwargs.get('target_size')
        if not target_size:
            print("Warning: target_size is required for ImageLayer")
            return False

        return True

    def process(self, layer: ImageLayer, **kwargs) -> ImageClip:
        """画像レイヤーを読み込む"""
        target_size = kwargs['target_size']

        clip = ImageClip(layer.path, duration=layer.duration)

        # リサイズして中央配置
        clip = clip.resized(height=target_size[1])
        if clip.w > target_size[0]:
            clip = clip.resized(width=target_size[0])

        # アニメーション効果を適用
        if layer.effects:
            clip = self.animation_processor.apply_effects(
                clip, layer.effects, target_size
            )

        # 開始時間の設定
        clip = clip.with_start(layer.start_time)

        return clip


class VideoTimelineProcessor(ProcessorBase[list[Union[VideoLayer, ImageLayer]], VideoFileClip]):
    """動画タイムライン処理プロセッサー"""

    def __init__(
        self,
        video_processor: VideoLayerProcessor = None,
        image_processor: ImageLayerProcessor = None
    ):
        self.video_processor = video_processor or VideoLayerProcessor()
        self.image_processor = image_processor or ImageLayerProcessor()

    def validate(self, layers: list, **kwargs) -> bool:
        """レイヤーリストのバリデーション"""
        if not layers:
            print("Error: At least one video or image layer is required")
            return False

        output_size = kwargs.get('output_size')
        if not output_size:
            print("Error: output_size is required")
            return False

        return True

    def process(
        self,
        layers: list[Union[VideoLayer, ImageLayer]],
        **kwargs
    ) -> VideoFileClip:
        """動画・画像レイヤーをタイムライン順に処理"""
        from moviepy import concatenate_videoclips

        output_size = kwargs['output_size']
        clips = []

        for layer in layers:
            if isinstance(layer, VideoLayer):
                clip = self.video_processor.execute(
                    layer,
                    output_size=output_size
                )
            elif isinstance(layer, ImageLayer):
                clip = self.image_processor.execute(
                    layer,
                    target_size=output_size
                )
            else:
                continue

            clips.append(clip)

        # すべてのクリップを連結
        final_clip = concatenate_videoclips(clips, method="compose")

        # 出力サイズにリサイズ
        final_clip = final_clip.resized(output_size)

        return final_clip


# 後方互換性のための static メソッド（非推奨）
class VideoProcessor:
    """動画処理を担当するプロセッサー（後方互換性用）"""

    _video_processor = VideoLayerProcessor()
    _image_processor = ImageLayerProcessor()
    _timeline_processor = VideoTimelineProcessor()

    @staticmethod
    def load_video_layer(layer: VideoLayer, output_size: tuple[int, int] = None) -> VideoFileClip:
        """動画レイヤーを読み込む（非推奨: VideoLayerProcessor を使用してください）"""
        return VideoProcessor._video_processor.execute(
            layer,
            output_size=output_size
        )

    @staticmethod
    def load_image_layer(layer: ImageLayer, target_size: tuple[int, int]) -> ImageClip:
        """画像レイヤーを読み込む（非推奨: ImageLayerProcessor を使用してください）"""
        return VideoProcessor._image_processor.execute(
            layer,
            target_size=target_size
        )

    @staticmethod
    def process_video_timeline(
        layers: list[Union[VideoLayer, ImageLayer]],
        output_size: tuple[int, int],
    ) -> VideoFileClip:
        """動画タイムラインを処理（非推奨: VideoTimelineProcessor を使用してください）"""
        return VideoProcessor._timeline_processor.execute(
            layers,
            output_size=output_size
        )
```

## タスク詳細

### Phase 1: ProcessorBase の改善
- [ ] `processors/base.py` の `ProcessorBase` を Template Method パターンに変更
- [ ] `execute()` メソッドを追加（process, validate, preprocess, postprocess を呼び出す）
- [ ] 型ヒントを改善（Generic[T, R] の活用）

### Phase 2: VideoProcessor のリファクタリング
- [ ] `VideoLayerProcessor` クラスを作成（VideoLayer → VideoFileClip）
- [ ] `ImageLayerProcessor` クラスを作成（ImageLayer → ImageClip）
- [ ] `StampLayerProcessor` クラスを作成（StampLayer → ImageClip）
- [ ] `VideoTimelineProcessor` クラスを作成（レイヤーリスト → VideoFileClip）
- [ ] 既存の `VideoProcessor` static メソッドを後方互換性のために残す

### Phase 3: AudioProcessor のリファクタリング
- [ ] `AudioLayerProcessor` クラスを作成（AudioLayer → AudioFileClip）
- [ ] `AudioTimelineProcessor` クラスを作成（レイヤーリスト → CompositeAudioClip）
- [ ] 既存の `AudioProcessor` static メソッドを後方互換性のために残す

### Phase 4: SubtitleProcessor のリファクタリング
- [ ] `SubtitleBurnProcessor` クラスを作成（字幕焼き込み）
- [ ] `SubtitleExportProcessor` クラスを作成（SRT/VTT エクスポート）
- [ ] 既存の `SubtitleProcessor` static メソッドを後方互換性のために残す

### Phase 5: 依存性注入の実装
- [ ] 各 Processor のコンストラクタで依存を注入できるようにする
- [ ] デフォルト値を提供して、既存コードとの互換性を保つ

### Phase 6: テストとドキュメント
- [ ] 各 Processor クラスの単体テストを作成
- [ ] バリデーション、前処理、後処理のテストを追加
- [ ] 新しい API の使用方法をドキュメント化
- [ ] 既存の static メソッドを非推奨としてマーク

## 期待される効果

### メリット
1. **一貫性**: すべての Processor が同じインターフェースを持つ
2. **拡張性**: バリデーション、前処理、後処理を簡単に追加可能
3. **テスタビリティ**: 依存性注入によりモック/スタブが使用可能
4. **再利用性**: Processor インスタンスを異なるコンテキストで再利用可能
5. **保守性**: 共通ロジックが基底クラスに集約される

### 使用例
```python
# 新しい API
video_processor = VideoLayerProcessor()
clip = video_processor.execute(video_layer, output_size=(1920, 1080))

# カスタムバリデーションの追加
class StrictVideoProcessor(VideoLayerProcessor):
    def validate(self, layer: VideoLayer, **kwargs) -> bool:
        if not super().validate(layer, **kwargs):
            return False
        # 追加のバリデーション
        if layer.duration and layer.duration > 300:
            print("Warning: Video is longer than 5 minutes")
            return False
        return True

# 依存性注入
custom_animation = CustomAnimationProcessor()
video_processor = VideoLayerProcessor(animation_processor=custom_animation)
```

## 後方互換性
- 既存の static メソッドは残し、内部で新しい Processor を使用
- 非推奨の警告を追加（将来のバージョンで削除予定）
- 既存のコードは変更なしで動作し続ける

## 検討事項
- エラーハンドリングの戦略（例外を投げる vs エラーを返す）
- ログ出力の統一
- キャッシュ機構の追加（同じファイルを複数回読み込まない）
- 非同期処理への対応（async/await）

## 参考
- Template Method パターン
- Strategy パターン（SubtitleProcessor で既に使用）
- Dependency Injection パターン
