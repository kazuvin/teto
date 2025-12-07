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

        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # 一時音声ファイルを出力ファイルと同じディレクトリに作成
        temp_audio_file = str(output_dir / f"temp_audio_{Path(output_path).stem}.mp4")

        context.video_clip.write_videofile(
            output_path,
            fps=output_config.fps,
            codec=output_config.codec,
            audio_codec=output_config.audio_codec,
            bitrate=output_config.bitrate,
            preset=output_config.preset,
            temp_audiofile=temp_audio_file,
        )

        return context
