"""レイヤードキャラクターレイヤー処理ステップ"""

from ..pipeline import ProcessingStep
from ..context import ProcessingContext
from ...layer.processors.layered_character import LayeredCharacterProcessor


class LayeredCharacterLayerProcessingStep(ProcessingStep):
    """レイヤードキャラクターレイヤー処理ステップ

    レイヤードキャラクターレイヤーを処理し、ベース動画に合成する。
    """

    def __init__(
        self,
        processor: LayeredCharacterProcessor = None,
        next_step: ProcessingStep = None,
    ):
        """初期化

        Args:
            processor: レイヤードキャラクタープロセッサー（オプション）
            next_step: 次の処理ステップ（オプション）
        """
        super().__init__(next_step)
        self.processor = processor

    def process(self, context: ProcessingContext) -> ProcessingContext:
        """レイヤードキャラクターレイヤーを処理

        Args:
            context: 処理コンテキスト

        Returns:
            更新されたコンテキスト
        """
        timeline = context.project.timeline

        if not timeline.layered_character_layers:
            return context

        context.report_progress("レイヤードキャラクターを処理中...")

        # 出力サイズを取得
        video_size = context.output_size

        # プロセッサーを初期化
        if not self.processor:
            self.processor = LayeredCharacterProcessor(video_size=video_size)

        from moviepy import CompositeVideoClip

        # 各レイヤーを処理
        layered_character_clips = []
        for layer in timeline.layered_character_layers:
            clip = self.processor.process_layer(layer)
            layered_character_clips.append(clip)

        if layered_character_clips:
            # ベース動画とレイヤードキャラクターを合成
            context.video_clip = CompositeVideoClip(
                [context.video_clip] + layered_character_clips, size=video_size
            )

        return context
