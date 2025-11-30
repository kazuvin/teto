"""動画生成エンジン"""

from pathlib import Path
from typing import Callable, Any
from .models import Project
from .processors import (
    VideoProcessor,
    AudioProcessor,
    StampLayerProcessor,
    SubtitleBurnProcessor,
    SubtitleExportProcessor,
)


class VideoGenerator:
    """動画生成のメインエンジン

    プラグインシステムにより、カスタム処理を追加可能
    """

    def __init__(
        self,
        project: Project,
        video_processor: VideoProcessor = None,
        audio_processor: AudioProcessor = None,
        stamp_processor: StampLayerProcessor = None,
        subtitle_burn_processor: SubtitleBurnProcessor = None,
        subtitle_export_processor: SubtitleExportProcessor = None,
    ):
        self.project = project
        self._pre_hooks: list[Callable[[Project], Any]] = []
        self._post_hooks: list[Callable[[str, Project], Any]] = []
        self._custom_processors: dict[str, Any] = {}

        # プロセッサーの初期化（依存性注入）
        self.video_processor = video_processor or VideoProcessor()
        self.audio_processor = audio_processor or AudioProcessor()
        self.stamp_processor = stamp_processor or StampLayerProcessor()
        self.subtitle_burn_processor = subtitle_burn_processor or SubtitleBurnProcessor()
        self.subtitle_export_processor = subtitle_export_processor or SubtitleExportProcessor()

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
        video_clip = self.video_processor.execute(
            timeline.video_layers, output_size=output_size
        )

        if progress_callback:
            progress_callback("音声レイヤーを処理中...")

        # 2. 音声レイヤーを処理
        audio_clip = self.audio_processor.execute(timeline.audio_layers)

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
            progress_callback("スタンプを処理中...")

        # 3.5. スタンプレイヤーを処理
        if timeline.stamp_layers:
            from moviepy import CompositeVideoClip

            stamp_clips = []
            for stamp_layer in timeline.stamp_layers:
                stamp_clip = self.stamp_processor.execute(stamp_layer)
                stamp_clips.append(stamp_clip)

            # ベース動画とスタンプを合成
            video_clip = CompositeVideoClip([video_clip] + stamp_clips, size=output_size)

        if progress_callback:
            progress_callback("字幕を処理中...")

        # 4. 字幕処理
        subtitle_mode = output_config.subtitle_mode

        if subtitle_mode == "burn":
            # 字幕を動画に焼き込む
            video_clip = self.subtitle_burn_processor.execute(
                (video_clip, timeline.subtitle_layers)
            )
        elif subtitle_mode in ["srt", "vtt"]:
            # 字幕ファイルを別途出力
            subtitle_path = Path(output_config.path).with_suffix(
                f".{subtitle_mode}"
            )
            export_processor = SubtitleExportProcessor(format=subtitle_mode)
            export_processor.execute(timeline.subtitle_layers, output_path=str(subtitle_path))

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
