"""動画生成エンジン"""

from pathlib import Path
from typing import Callable, Any
from .models import Project
from .processors import VideoProcessor, AudioProcessor, SubtitleProcessor


class VideoGenerator:
    """動画生成のメインエンジン

    プラグインシステムにより、カスタム処理を追加可能
    """

    def __init__(self, project: Project):
        self.project = project
        self._pre_hooks: list[Callable[[Project], Any]] = []
        self._post_hooks: list[Callable[[str, Project], Any]] = []
        self._custom_processors: dict[str, Any] = {}

    def register_pre_hook(self, hook: Callable[[Project], Any]) -> None:
        """生成前に実行されるフックを登録

        Args:
            hook: プロジェクトを引数に取る関数
        """
        self._pre_hooks.append(hook)

    def register_post_hook(self, hook: Callable[[str, Project], Any]) -> None:
        """生成後に実行されるフックを登録

        Args:
            hook: 出力パスとプロジェクトを引数に取る関数
        """
        self._post_hooks.append(hook)

    def register_processor(self, name: str, processor: Any) -> None:
        """カスタムプロセッサーを登録

        Args:
            name: プロセッサー名
            processor: プロセッサーインスタンス
        """
        self._custom_processors[name] = processor

    def get_processor(self, name: str) -> Any:
        """登録されたプロセッサーを取得

        Args:
            name: プロセッサー名

        Returns:
            プロセッサーインスタンス（存在しない場合はNone）
        """
        return self._custom_processors.get(name)

    def generate(self, progress_callback=None) -> str:
        """
        プロジェクトから動画を生成

        Args:
            progress_callback: 進捗コールバック関数（オプション）

        Returns:
            出力ファイルパス
        """
        # 前処理フックを実行
        for hook in self._pre_hooks:
            hook(self.project)

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

        # 後処理フックを実行
        for hook in self._post_hooks:
            hook(output_path, self.project)

        return output_path

    @classmethod
    def from_json(cls, json_path: str) -> "VideoGenerator":
        """JSONファイルから生成"""
        project = Project.from_json_file(json_path)
        return cls(project)
