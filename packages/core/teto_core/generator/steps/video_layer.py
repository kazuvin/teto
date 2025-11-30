"""動画・画像レイヤー処理ステップ"""

from ..pipeline import ProcessingStep
from ..context import ProcessingContext
from ...processors import VideoProcessor


class VideoLayerProcessingStep(ProcessingStep):
    """動画・画像レイヤー処理ステップ"""

    def __init__(self, video_processor: VideoProcessor = None, next_step: ProcessingStep = None):
        """初期化

        Args:
            video_processor: 動画プロセッサー（オプション）
            next_step: 次の処理ステップ（オプション）
        """
        super().__init__(next_step)
        self.video_processor = video_processor or VideoProcessor()

    def process(self, context: ProcessingContext) -> ProcessingContext:
        """動画・画像レイヤーを処理

        Args:
            context: 処理コンテキスト

        Returns:
            更新されたコンテキスト
        """
        context.report_progress("動画・画像レイヤーを処理中...")

        timeline = context.project.timeline
        context.output_size = (
            context.project.output.width,
            context.project.output.height,
        )

        context.video_clip = self.video_processor.execute(
            timeline.video_layers, output_size=context.output_size
        )

        return context
