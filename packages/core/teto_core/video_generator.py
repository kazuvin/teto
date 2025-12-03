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

    @classmethod
    def from_json(cls, json_path: str) -> "VideoGenerator":
        """JSONファイルから生成"""
        project = Project.from_json_file(json_path)
        return cls(project)
