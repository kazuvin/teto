"""キャラクターレイヤー処理ステップ"""

from ..pipeline import ProcessingStep
from ..context import ProcessingContext
from ...layer.processors.character import CharacterLayerProcessor


class CharacterLayerProcessingStep(ProcessingStep):
    """キャラクターレイヤー処理ステップ

    キャラクターレイヤーを処理し、ベース動画に合成する。
    キャラクターは字幕より下、スタンプより上のレイヤーに配置される。
    """

    def __init__(
        self,
        character_processor: CharacterLayerProcessor = None,
        next_step: ProcessingStep = None,
    ):
        """初期化

        Args:
            character_processor: キャラクタープロセッサー（オプション）
            next_step: 次の処理ステップ（オプション）
        """
        super().__init__(next_step)
        self.character_processor = character_processor or CharacterLayerProcessor()

    def process(self, context: ProcessingContext) -> ProcessingContext:
        """キャラクターレイヤーを処理

        Args:
            context: 処理コンテキスト

        Returns:
            更新されたコンテキスト
        """
        timeline = context.project.timeline

        if not timeline.character_layers:
            return context

        context.report_progress("キャラクターを処理中...")

        from moviepy import CompositeVideoClip

        character_clips = []
        for character_layer in timeline.character_layers:
            if self.character_processor.validate(
                character_layer, output_size=context.output_size
            ):
                character_clip = self.character_processor.process(
                    character_layer, output_size=context.output_size
                )
                character_clips.append(character_clip)

        if character_clips:
            # ベース動画とキャラクターを合成
            context.video_clip = CompositeVideoClip(
                [context.video_clip] + character_clips, size=context.output_size
            )

        return context
