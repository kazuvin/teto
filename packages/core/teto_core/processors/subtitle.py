"""字幕処理プロセッサー"""

from pathlib import Path
from moviepy import VideoClip, CompositeVideoClip, ImageClip
from ..models.layers import SubtitleLayer, SubtitleItem
from ..utils.font_utils import find_system_font, download_google_font
from ..utils.time_utils import format_srt_time, format_vtt_time
from ..utils.size_utils import get_responsive_constants
from .subtitle_renderers import (
    SubtitleStyleRenderer,
    PlainStyleRenderer,
    BackgroundStyleRenderer,
    ShadowStyleRenderer,
    DropShadowStyleRenderer,
)


class SubtitleProcessor:
    """字幕処理を担当するプロセッサー"""

    # Style Renderer のマッピング
    _style_renderers: dict[str, SubtitleStyleRenderer] = {
        "plain": PlainStyleRenderer(),
        "background": BackgroundStyleRenderer(),
        "shadow": ShadowStyleRenderer(),
        "drop-shadow": DropShadowStyleRenderer(),
        # 将来の拡張用:
        # "3d": ThreeDStyleRenderer(),
    }

    @staticmethod
    def _calculate_position(layer: SubtitleLayer, clip_height: int, video_size: tuple[int, int]) -> tuple:
        """レイヤー設定に基づいてクリップの位置を計算する

        Args:
            layer: 字幕レイヤー
            clip_height: クリップの高さ
            video_size: 動画のサイズ (幅, 高さ)

        Returns:
            位置のタプル
        """
        # レスポンシブな定数を取得
        constants = get_responsive_constants(video_size[1])

        if layer.position == "bottom":
            return ("center", video_size[1] - clip_height - constants["MARGIN_BOTTOM"])
        elif layer.position == "top":
            return ("center", constants["MARGIN_TOP"])
        else:  # center
            return ("center", "center")

    @staticmethod
    def create_subtitle_clip(
        item: SubtitleItem, layer: SubtitleLayer, video_size: tuple[int, int]
    ) -> VideoClip:
        """字幕アイテムからテキストクリップを作成"""
        duration = item.end_time - item.start_time

        # フォントを決定（優先順位: google_font > システムフォント）
        font_path = None
        if layer.google_font:
            font_path = download_google_font(layer.google_font, layer.font_weight)
        if not font_path:
            font_path = find_system_font(layer.font_weight)

        # appearanceに基づいて適切なレンダラーを取得
        renderer = SubtitleProcessor._style_renderers.get(
            layer.appearance, SubtitleProcessor._style_renderers["plain"]
        )

        # レンダラーを使ってクリップを作成
        clip, clip_height = renderer.render(item, layer, video_size, font_path, duration)

        # 位置の計算
        position = SubtitleProcessor._calculate_position(layer, clip_height, video_size)
        return clip.with_position(position).with_start(item.start_time).with_duration(duration)

    @staticmethod
    def burn_subtitles(
        video: VideoClip, subtitle_layers: list[SubtitleLayer]
    ) -> VideoClip:
        """動画に字幕を焼き込む"""
        if not subtitle_layers:
            return video

        subtitle_clips = []

        for layer in subtitle_layers:
            for item in layer.items:
                try:
                    clip = SubtitleProcessor.create_subtitle_clip(
                        item, layer, (video.w, video.h)
                    )
                    subtitle_clips.append(clip)
                except Exception as e:
                    print(f"Warning: Failed to create subtitle clip: {e}")
                    continue

        if subtitle_clips:
            return CompositeVideoClip([video] + subtitle_clips, size=(video.w, video.h))
        else:
            return video

    @staticmethod
    def export_srt(subtitle_layers: list[SubtitleLayer], output_path: str) -> None:
        """SRT形式で字幕をエクスポート"""
        if not subtitle_layers:
            return

        with open(output_path, "w", encoding="utf-8") as f:
            index = 1
            for layer in subtitle_layers:
                for item in layer.items:
                    start = format_srt_time(item.start_time)
                    end = format_srt_time(item.end_time)

                    f.write(f"{index}\n")
                    f.write(f"{start} --> {end}\n")
                    f.write(f"{item.text}\n\n")

                    index += 1

    @staticmethod
    def export_vtt(subtitle_layers: list[SubtitleLayer], output_path: str) -> None:
        """VTT形式で字幕をエクスポート"""
        if not subtitle_layers:
            return

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("WEBVTT\n\n")

            for layer in subtitle_layers:
                for item in layer.items:
                    start = format_vtt_time(item.start_time)
                    end = format_vtt_time(item.end_time)

                    f.write(f"{start} --> {end}\n")
                    f.write(f"{item.text}\n\n")
