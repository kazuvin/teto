"""処理パイプラインのコンテキスト"""

from dataclasses import dataclass
from typing import Callable
from moviepy import VideoClip, AudioClip

from ..project import Project


@dataclass
class ProcessingContext:
    """処理パイプライン全体で共有されるコンテキスト"""

    project: Project
    video_clip: VideoClip | None = None
    audio_clip: AudioClip | None = None
    output_size: tuple[int, int] | None = None
    progress_callback: Callable[[str], None] | None = None

    def report_progress(self, message: str) -> None:
        """進捗を報告

        Args:
            message: 進捗メッセージ
        """
        if self.progress_callback:
            self.progress_callback(message)
