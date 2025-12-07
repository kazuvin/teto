"""動画生成エンジン"""

from typing import Callable, Any
from .project import Project
from .layer.processors import VideoProcessor, AudioProcessor
from .layer.processors.video import StampLayerProcessor
from .layer.processors.subtitle import SubtitleBurnProcessor, SubtitleExportProcessor
from .generator.pipeline import ProcessingStep
from .generator.context import ProcessingContext
from .generator.steps import (
    VideoLayerProcessingStep,
    AudioLayerProcessingStep,
    AudioMergingStep,
    StampLayerProcessingStep,
    SubtitleProcessingStep,
    VideoOutputStep,
    CleanupStep,
)


class VideoGenerator:
    """動画生成のメインエンジン

    Pipeline パターンにより、処理フローをカスタマイズ可能
    """

    def __init__(
        self,
        project: Project,
        video_processor: VideoProcessor = None,
        audio_processor: AudioProcessor = None,
        stamp_processor: StampLayerProcessor = None,
        subtitle_burn_processor: SubtitleBurnProcessor = None,
        subtitle_export_processor: SubtitleExportProcessor = None,
    ):
        self.project = project
        self._pre_hooks: list[Callable[[Project], Any]] = []
        self._post_hooks: list[Callable[[str, Project], Any]] = []
        self._custom_processors: dict[str, Any] = {}

        # プロセッサーの初期化（依存性注入）
        self.video_processor = video_processor or VideoProcessor()
        self.audio_processor = audio_processor or AudioProcessor()
        self.stamp_processor = stamp_processor or StampLayerProcessor()
        self.subtitle_burn_processor = (
            subtitle_burn_processor or SubtitleBurnProcessor()
        )
        self.subtitle_export_processor = (
            subtitle_export_processor or SubtitleExportProcessor()
        )

        # パイプラインを構築
        self._pipeline = self._build_default_pipeline()

    def register_pre_hook(self, hook: Callable[[Project], Any]) -> None:
        """生成前に実行されるフックを登録

        Args:
            hook: プロジェクトを引数に取る関数
        """
        self._pre_hooks.append(hook)

    def register_post_hook(self, hook: Callable[[str, Project], Any]) -> None:
        """生成後に実行されるフックを登録

        Args:
            hook: 出力パスとプロジェクトを引数に取る関数
        """
        self._post_hooks.append(hook)

    def register_processor(self, name: str, processor: Any) -> None:
        """カスタムプロセッサーを登録

        Args:
            name: プロセッサー名
            processor: プロセッサーインスタンス
        """
        self._custom_processors[name] = processor

    def get_processor(self, name: str) -> Any:
        """登録されたプロセッサーを取得

        Args:
            name: プロセッサー名

        Returns:
            プロセッサーインスタンス（存在しない場合はNone）
        """
        return self._custom_processors.get(name)

    def _build_default_pipeline(self) -> ProcessingStep:
        """デフォルトの処理パイプラインを構築

        Returns:
            処理パイプラインの先頭ステップ
        """
        video_step = VideoLayerProcessingStep(video_processor=self.video_processor)
        video_step.then(
            AudioLayerProcessingStep(audio_processor=self.audio_processor)
        ).then(AudioMergingStep()).then(
            StampLayerProcessingStep(stamp_processor=self.stamp_processor)
        ).then(
            SubtitleProcessingStep(
                subtitle_burn_processor=self.subtitle_burn_processor,
                subtitle_export_processor=self.subtitle_export_processor,
            )
        ).then(
            VideoOutputStep()
        ).then(
            CleanupStep()
        )

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
            progress_callback: 進捗コールバック関数（オプション）

        Returns:
            出力ファイルパス
        """
        # 前処理フックを実行
        for hook in self._pre_hooks:
            hook(self.project)

        # 処理コンテキストを作成
        context = ProcessingContext(
            project=self.project,
            progress_callback=progress_callback,
        )

        # パイプラインを実行
        context = self._pipeline.execute(context)

        # 後処理フックを実行
        output_path = self.project.output.path
        for hook in self._post_hooks:
            hook(output_path, self.project)

        return output_path

    def generate_multi(self, output_configs: list, progress_callback=None) -> list[str]:
        """複数のアスペクト比で動画を一度に生成

        各出力設定に対して別々にレイヤー処理を行い、object_fit などの設定を
        正しく適用します。

        Args:
            output_configs: 出力設定のリスト（OutputConfigまたはdict）
            progress_callback: 進捗コールバック関数（オプション）

        Returns:
            出力ファイルパスのリスト

        Example:
            >>> from teto_core.output_config import OutputConfig
            >>> configs = [
            ...     OutputConfig(path="youtube.mp4", aspect_ratio="16:9"),
            ...     OutputConfig(path="tiktok.mp4", aspect_ratio="9:16"),
            ... ]
            >>> generator.generate_multi(configs)
            ['youtube.mp4', 'tiktok.mp4']
        """
        from .output_config.models import OutputConfig
        from pathlib import Path

        # 前処理フックを実行
        for hook in self._pre_hooks:
            hook(self.project)

        # 元の output 設定を保存
        original_output = self.project.output

        # 複数の出力を生成
        output_paths = []
        for i, output_config in enumerate(output_configs):
            # dictの場合はOutputConfigに変換
            if isinstance(output_config, dict):
                output_config = OutputConfig(**output_config)

            if progress_callback:
                progress_callback(
                    f"出力中 ({i + 1}/{len(output_configs)}): {output_config.path}"
                )

            # 出力ディレクトリを作成
            Path(output_config.path).parent.mkdir(parents=True, exist_ok=True)

            # プロジェクトの output を一時的に変更
            self.project.output = output_config

            # 処理コンテキストを作成
            context = ProcessingContext(
                project=self.project,
                progress_callback=progress_callback,
            )

            # パイプラインを実行
            context = self._pipeline.execute(context)

            output_paths.append(output_config.path)

            # 後処理フックを実行
            for hook in self._post_hooks:
                hook(output_config.path, self.project)

            # クリーンアップ
            if context.video_clip:
                context.video_clip.close()
            if context.audio_clip:
                context.audio_clip.close()

        # 元の output 設定を復元
        self.project.output = original_output

        return output_paths

    @classmethod
    def from_json(cls, json_path: str) -> "VideoGenerator":
        """JSONファイルから生成"""
        project = Project.from_json_file(json_path)
        return cls(project)
