"""音声レイヤー処理ステップ"""

from ..pipeline import ProcessingStep
from ..context import ProcessingContext
from ...layer.processors import AudioProcessor


class AudioLayerProcessingStep(ProcessingStep):
    """音声レイヤー処理ステップ"""

    def __init__(
        self, audio_processor: AudioProcessor = None, next_step: ProcessingStep = None
    ):
        """初期化

        Args:
            audio_processor: 音声プロセッサー（オプション）
            next_step: 次の処理ステップ（オプション）
        """
        super().__init__(next_step)
        self.audio_processor = audio_processor or AudioProcessor()

    def process(self, context: ProcessingContext) -> ProcessingContext:
        """音声レイヤーを処理

        Args:
            context: 処理コンテキスト

        Returns:
            更新されたコンテキスト
        """
        context.report_progress("音声レイヤーを処理中...")

        timeline = context.project.timeline
        context.audio_clip = self.audio_processor.execute(timeline.audio_layers)

        return context
