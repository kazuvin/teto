"""動画生成エンジン"""

from pathlib import Path
from .models import Project
from .processors import VideoProcessor, AudioProcessor, SubtitleProcessor


class VideoGenerator:
    """動画生成のメインエンジン"""

    def __init__(self, project: Project):
        self.project = project

    def generate(self, progress_callback=None) -> str:
        """
        プロジェクトから動画を生成

        Args:
            progress_callback: 進捗コールバック関数（オプション）

        Returns:
            出力ファイルパス
        """
        output_config = self.project.output
        timeline = self.project.timeline

        # 出力サイズ
        output_size = (output_config.width, output_config.height)

        if progress_callback:
            progress_callback("動画・画像レイヤーを処理中...")

        # 1. 動画・画像レイヤーを処理
        video_clip = VideoProcessor.process_video_timeline(
            timeline.video_layers, output_size
        )

        if progress_callback:
            progress_callback("音声レイヤーを処理中...")

        # 2. 音声レイヤーを処理
        audio_clip = AudioProcessor.process_audio_timeline(timeline.audio_layers)

        # 3. 既存の動画音声と追加音声を合成
        if audio_clip is not None:
            if video_clip.audio is not None:
                # 動画の音声と追加音声を合成
                from moviepy import CompositeAudioClip

                final_audio = CompositeAudioClip([video_clip.audio, audio_clip])
                video_clip = video_clip.with_audio(final_audio)
            else:
                # 追加音声のみ
                video_clip = video_clip.with_audio(audio_clip)

        if progress_callback:
            progress_callback("字幕を処理中...")

        # 4. 字幕処理
        subtitle_mode = output_config.subtitle_mode

        if subtitle_mode == "burn":
            # 字幕を動画に焼き込む
            video_clip = SubtitleProcessor.burn_subtitles(
                video_clip, timeline.subtitle_layers
            )
        elif subtitle_mode in ["srt", "vtt"]:
            # 字幕ファイルを別途出力
            subtitle_path = Path(output_config.path).with_suffix(
                f".{subtitle_mode}"
            )
            if subtitle_mode == "srt":
                SubtitleProcessor.export_srt(timeline.subtitle_layers, str(subtitle_path))
            else:
                SubtitleProcessor.export_vtt(timeline.subtitle_layers, str(subtitle_path))

        if progress_callback:
            progress_callback("動画を出力中...")

        # 5. 動画を出力
        output_path = output_config.path
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        video_clip.write_videofile(
            output_path,
            fps=output_config.fps,
            codec=output_config.codec,
            audio_codec=output_config.audio_codec,
            bitrate=output_config.bitrate,
        )

        # クリーンアップ
        video_clip.close()
        if audio_clip is not None:
            audio_clip.close()

        if progress_callback:
            progress_callback("完了！")

        return output_path

    @classmethod
    def from_json(cls, json_path: str) -> "VideoGenerator":
        """JSONファイルから生成"""
        project = Project.from_json_file(json_path)
        return cls(project)
