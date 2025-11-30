"""字幕処理ステップ"""

from pathlib import Path

from ..pipeline import ProcessingStep
from ..context import ProcessingContext
from ...processors import SubtitleBurnProcessor, SubtitleExportProcessor


class SubtitleProcessingStep(ProcessingStep):
    """字幕処理ステップ"""

    def __init__(
        self,
        subtitle_burn_processor: SubtitleBurnProcessor = None,
        subtitle_export_processor: SubtitleExportProcessor = None,
        next_step: ProcessingStep = None,
    ):
        """初期化

        Args:
            subtitle_burn_processor: 字幕焼き込みプロセッサー（オプション）
            subtitle_export_processor: 字幕エクスポートプロセッサー（オプション）
            next_step: 次の処理ステップ（オプション）
        """
        super().__init__(next_step)
        self.subtitle_burn_processor = subtitle_burn_processor or SubtitleBurnProcessor()
        self.subtitle_export_processor = subtitle_export_processor

    def process(self, context: ProcessingContext) -> ProcessingContext:
        """字幕を処理

        Args:
            context: 処理コンテキスト

        Returns:
            更新されたコンテキスト
        """
        context.report_progress("字幕を処理中...")

        output_config = context.project.output
        timeline = context.project.timeline
        subtitle_mode = output_config.subtitle_mode

        if subtitle_mode == "burn":
            # 字幕を動画に焼き込む
            context.video_clip = self.subtitle_burn_processor.execute(
                (context.video_clip, timeline.subtitle_layers)
            )
        elif subtitle_mode in ["srt", "vtt"]:
            # 字幕ファイルを別途出力
            subtitle_path = Path(output_config.path).with_suffix(f".{subtitle_mode}")
            export_processor = SubtitleExportProcessor(format=subtitle_mode)
            export_processor.execute(timeline.subtitle_layers, output_path=str(subtitle_path))

        return context
