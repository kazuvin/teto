"""音声合成ステップ"""

from ..pipeline import ProcessingStep
from ..context import ProcessingContext


class AudioMergingStep(ProcessingStep):
    """音声合成ステップ

    動画の既存音声と追加音声を合成する
    """

    def process(self, context: ProcessingContext) -> ProcessingContext:
        """音声を合成

        Args:
            context: 処理コンテキスト

        Returns:
            更新されたコンテキスト
        """
        if context.audio_clip is None:
            return context

        from moviepy import CompositeAudioClip

        if context.video_clip.audio is not None:
            # 動画の音声と追加音声を合成
            final_audio = CompositeAudioClip(
                [context.video_clip.audio, context.audio_clip]
            )
            context.video_clip = context.video_clip.with_audio(final_audio)
        else:
            # 追加音声のみ
            context.video_clip = context.video_clip.with_audio(context.audio_clip)

        return context
