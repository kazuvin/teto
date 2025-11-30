"""スタンプレイヤー処理ステップ"""

from ..pipeline import ProcessingStep
from ..context import ProcessingContext
from ...layer.processors.video import StampLayerProcessor


class StampLayerProcessingStep(ProcessingStep):
    """スタンプレイヤー処理ステップ"""

    def __init__(
        self,
        stamp_processor: StampLayerProcessor = None,
        next_step: ProcessingStep = None,
    ):
        """初期化

        Args:
            stamp_processor: スタンププロセッサー（オプション）
            next_step: 次の処理ステップ（オプション）
        """
        super().__init__(next_step)
        self.stamp_processor = stamp_processor or StampLayerProcessor()

    def process(self, context: ProcessingContext) -> ProcessingContext:
        """スタンプレイヤーを処理

        Args:
            context: 処理コンテキスト

        Returns:
            更新されたコンテキスト
        """
        timeline = context.project.timeline

        if not timeline.stamp_layers:
            return context

        context.report_progress("スタンプを処理中...")

        from moviepy import CompositeVideoClip

        stamp_clips = []
        for stamp_layer in timeline.stamp_layers:
            stamp_clip = self.stamp_processor.execute(stamp_layer)
            stamp_clips.append(stamp_clip)

        # ベース動画とスタンプを合成
        context.video_clip = CompositeVideoClip(
            [context.video_clip] + stamp_clips, size=context.output_size
        )

        return context
