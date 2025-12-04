"""動画出力ステップ"""

from pathlib import Path

from ..pipeline import ProcessingStep
from ..context import ProcessingContext


class VideoOutputStep(ProcessingStep):
    """動画出力ステップ"""

    def process(self, context: ProcessingContext) -> ProcessingContext:
        """動画を出力

        Args:
            context: 処理コンテキスト

        Returns:
            更新されたコンテキスト
        """
        context.report_progress("動画を出力中...")

        output_config = context.project.output
        output_path = output_config.path

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        context.video_clip.write_videofile(
            output_path,
            fps=output_config.fps,
            codec=output_config.codec,
            audio_codec=output_config.audio_codec,
            bitrate=output_config.bitrate,
            preset=output_config.preset,
        )

        return context
