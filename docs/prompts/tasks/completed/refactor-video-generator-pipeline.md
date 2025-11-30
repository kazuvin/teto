# VideoGenerator のリファクタリング - Pipeline パターンへの変更

## 概要
現在の `VideoGenerator.generate()` メソッドは約100行の巨大なメソッドで、複数の責任を持っています。Pipeline パターン（Chain of Responsibility の変形）を導入して、各処理ステップを独立したクラスとして実装します。

## 現在の問題点

**場所**: `packages/core/teto_core/generator.py:57-166`

### 問題
- 1つのメソッドに複数の責任が集中（動画処理、音声処理、スタンプ処理、字幕処理、出力）
- 処理フローの変更が困難
- 特定のステップだけをテストするのが困難
- 進捗コールバックのメッセージが処理ロジックと混在
- 新しい処理ステップの追加が難しい

## 目標設計

### Pipeline パターンによる実装

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Any
from moviepy import VideoClip, AudioClip

@dataclass
class ProcessingContext:
    """処理パイプライン全体で共有されるコンテキスト"""
    project: Project
    video_clip: VideoClip | None = None
    audio_clip: AudioClip | None = None
    output_size: tuple[int, int] = None
    progress_callback: Callable[[str], None] | None = None

    def report_progress(self, message: str) -> None:
        """進捗を報告"""
        if self.progress_callback:
            self.progress_callback(message)


class ProcessingStep(ABC):
    """処理ステップの基底クラス"""

    def __init__(self, next_step: 'ProcessingStep' = None):
        self._next = next_step

    @abstractmethod
    def process(self, context: ProcessingContext) -> ProcessingContext:
        """このステップの処理を実行

        Args:
            context: 処理コンテキスト

        Returns:
            更新されたコンテキスト
        """
        pass

    def execute(self, context: ProcessingContext) -> ProcessingContext:
        """このステップと次のステップを実行

        Args:
            context: 処理コンテキスト

        Returns:
            最終的なコンテキスト
        """
        context = self.process(context)

        if self._next:
            return self._next.execute(context)

        return context

    def then(self, next_step: 'ProcessingStep') -> 'ProcessingStep':
        """次のステップをチェーンに追加（Fluent Interface）

        Args:
            next_step: 次の処理ステップ

        Returns:
            次のステップ（チェーン可能）
        """
        self._next = next_step
        return next_step


class VideoLayerProcessingStep(ProcessingStep):
    """動画・画像レイヤー処理ステップ"""

    def process(self, context: ProcessingContext) -> ProcessingContext:
        context.report_progress("動画・画像レイヤーを処理中...")

        timeline = context.project.timeline
        context.output_size = (
            context.project.output.width,
            context.project.output.height
        )

        context.video_clip = VideoProcessor.process_video_timeline(
            timeline.video_layers,
            context.output_size
        )

        return context


class AudioLayerProcessingStep(ProcessingStep):
    """音声レイヤー処理ステップ"""

    def process(self, context: ProcessingContext) -> ProcessingContext:
        context.report_progress("音声レイヤーを処理中...")

        timeline = context.project.timeline
        context.audio_clip = AudioProcessor.process_audio_timeline(
            timeline.audio_layers
        )

        return context


class AudioMergingStep(ProcessingStep):
    """音声合成ステップ"""

    def process(self, context: ProcessingContext) -> ProcessingContext:
        if context.audio_clip is None:
            return context

        from moviepy import CompositeAudioClip

        if context.video_clip.audio is not None:
            # 動画の音声と追加音声を合成
            final_audio = CompositeAudioClip([
                context.video_clip.audio,
                context.audio_clip
            ])
            context.video_clip = context.video_clip.with_audio(final_audio)
        else:
            # 追加音声のみ
            context.video_clip = context.video_clip.with_audio(context.audio_clip)

        return context


class StampLayerProcessingStep(ProcessingStep):
    """スタンプレイヤー処理ステップ"""

    def process(self, context: ProcessingContext) -> ProcessingContext:
        timeline = context.project.timeline

        if not timeline.stamp_layers:
            return context

        context.report_progress("スタンプを処理中...")

        from moviepy import CompositeVideoClip

        stamp_clips = []
        for stamp_layer in timeline.stamp_layers:
            stamp_clip = VideoProcessor.load_stamp_layer(stamp_layer)
            stamp_clips.append(stamp_clip)

        # ベース動画とスタンプを合成
        context.video_clip = CompositeVideoClip(
            [context.video_clip] + stamp_clips,
            size=context.output_size
        )

        return context


class SubtitleProcessingStep(ProcessingStep):
    """字幕処理ステップ"""

    def process(self, context: ProcessingContext) -> ProcessingContext:
        context.report_progress("字幕を処理中...")

        output_config = context.project.output
        timeline = context.project.timeline
        subtitle_mode = output_config.subtitle_mode

        if subtitle_mode == "burn":
            # 字幕を動画に焼き込む
            context.video_clip = SubtitleProcessor.burn_subtitles(
                context.video_clip,
                timeline.subtitle_layers
            )
        elif subtitle_mode in ["srt", "vtt"]:
            # 字幕ファイルを別途出力
            from pathlib import Path
            subtitle_path = Path(output_config.path).with_suffix(
                f".{subtitle_mode}"
            )
            if subtitle_mode == "srt":
                SubtitleProcessor.export_srt(
                    timeline.subtitle_layers,
                    str(subtitle_path)
                )
            else:
                SubtitleProcessor.export_vtt(
                    timeline.subtitle_layers,
                    str(subtitle_path)
                )

        return context


class VideoOutputStep(ProcessingStep):
    """動画出力ステップ"""

    def process(self, context: ProcessingContext) -> ProcessingContext:
        context.report_progress("動画を出力中...")

        output_config = context.project.output
        output_path = output_config.path

        from pathlib import Path
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        context.video_clip.write_videofile(
            output_path,
            fps=output_config.fps,
            codec=output_config.codec,
            audio_codec=output_config.audio_codec,
            bitrate=output_config.bitrate,
        )

        return context


class CleanupStep(ProcessingStep):
    """リソースクリーンアップステップ"""

    def process(self, context: ProcessingContext) -> ProcessingContext:
        # クリーンアップ
        if context.video_clip:
            context.video_clip.close()
        if context.audio_clip:
            context.audio_clip.close()

        context.report_progress("完了！")

        return context


class VideoGenerator:
    """動画生成のメインエンジン"""

    def __init__(self, project: Project):
        self.project = project
        self._pre_hooks: list[Callable[[Project], Any]] = []
        self._post_hooks: list[Callable[[str, Project], Any]] = []
        self._custom_processors: dict[str, Any] = {}
        self._pipeline = self._build_default_pipeline()

    def _build_default_pipeline(self) -> ProcessingStep:
        """デフォルトの処理パイプラインを構築"""
        video_step = VideoLayerProcessingStep()
        video_step.then(AudioLayerProcessingStep()) \
                  .then(AudioMergingStep()) \
                  .then(StampLayerProcessingStep()) \
                  .then(SubtitleProcessingStep()) \
                  .then(VideoOutputStep()) \
                  .then(CleanupStep())

        return video_step

    def set_pipeline(self, pipeline: ProcessingStep) -> None:
        """カスタムパイプラインを設定

        Args:
            pipeline: カスタム処理パイプライン
        """
        self._pipeline = pipeline

    def generate(self, progress_callback=None) -> str:
        """プロジェクトから動画を生成

        Args:
            progress_callback: 進捗コールバック関数

        Returns:
            出力ファイルパス
        """
        # 前処理フックを実行
        for hook in self._pre_hooks:
            hook(self.project)

        # 処理コンテキストを作成
        context = ProcessingContext(
            project=self.project,
            progress_callback=progress_callback
        )

        # パイプラインを実行
        context = self._pipeline.execute(context)

        # 後処理フックを実行
        output_path = self.project.output.path
        for hook in self._post_hooks:
            hook(output_path, self.project)

        return output_path

    # 既存のメソッド（register_pre_hook等）は維持
```

## タスク詳細

### Phase 1: 基盤の作成
- [ ] `generator/` ディレクトリを作成
- [ ] `generator/context.py` に `ProcessingContext` を作成
- [ ] `generator/pipeline.py` に `ProcessingStep` 基底クラスを作成

### Phase 2: 処理ステップの実装
- [ ] `generator/steps/video_layer.py` - `VideoLayerProcessingStep`
- [ ] `generator/steps/audio_layer.py` - `AudioLayerProcessingStep`
- [ ] `generator/steps/audio_merge.py` - `AudioMergingStep`
- [ ] `generator/steps/stamp_layer.py` - `StampLayerProcessingStep`
- [ ] `generator/steps/subtitle.py` - `SubtitleProcessingStep`
- [ ] `generator/steps/output.py` - `VideoOutputStep`
- [ ] `generator/steps/cleanup.py` - `CleanupStep`

### Phase 3: VideoGenerator のリファクタリング
- [ ] `VideoGenerator` を新しい設計に変更
- [ ] `_build_default_pipeline()` メソッドの実装
- [ ] `set_pipeline()` メソッドの追加（カスタムパイプライン対応）
- [ ] 既存の `generate()` メソッドをリファクタリング

### Phase 4: 拡張機能の実装
- [ ] パイプラインステップの動的な追加/削除機能
- [ ] ステップのスキップ機能（条件付き実行）
- [ ] 並列処理可能なステップの識別と最適化

### Phase 5: テストとドキュメント
- [ ] 各ステップの単体テストを作成
- [ ] パイプライン全体の統合テストを作成
- [ ] カスタムパイプラインの作成方法をドキュメント化

## 期待される効果

### メリット
1. **可読性向上**: 各処理ステップが独立して理解しやすい
2. **テスタビリティ向上**: 各ステップを独立してテスト可能
3. **拡張性向上**: 新しいステップの追加や順序変更が容易
4. **再利用性向上**: ステップを他のプロジェクトでも利用可能
5. **デバッグ容易**: 各ステップでのコンテキスト状態を確認しやすい
6. **カスタマイズ性**: ユーザーが独自のパイプラインを構築可能

### 使用例
```python
# カスタムパイプラインの構築
custom_pipeline = VideoLayerProcessingStep()
custom_pipeline.then(MyCustomStep()) \
               .then(AudioLayerProcessingStep()) \
               .then(VideoOutputStep())

generator = VideoGenerator(project)
generator.set_pipeline(custom_pipeline)
generator.generate()
```

## 検討事項
- 一部のステップ（音声合成など）は条件付き実行が必要
- エラーハンドリングをどのレベルで行うか（各ステップ or パイプライン全体）
- ステップ間の依存関係の検証をどう実装するか
- 並列実行可能なステップの識別方法

## 参考
- Chain of Responsibility パターン
- Pipeline パターン（Unix のパイプラインの概念）
- Middleware パターン（Express.js などで使用）
