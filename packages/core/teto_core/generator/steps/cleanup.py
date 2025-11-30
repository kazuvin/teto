"""リソースクリーンアップステップ"""

from ..pipeline import ProcessingStep
from ..context import ProcessingContext


class CleanupStep(ProcessingStep):
    """リソースクリーンアップステップ"""

    def process(self, context: ProcessingContext) -> ProcessingContext:
        """リソースをクリーンアップ

        Args:
            context: 処理コンテキスト

        Returns:
            更新されたコンテキスト
        """
        # クリーンアップ
        if context.video_clip:
            context.video_clip.close()
        if context.audio_clip:
            context.audio_clip.close()

        context.report_progress("完了！")

        return context
