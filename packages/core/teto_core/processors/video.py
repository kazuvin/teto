"""動画・画像処理プロセッサー"""

from pathlib import Path
from moviepy import (
    VideoFileClip,
    ImageClip,
    concatenate_videoclips,
    CompositeVideoClip,
)
from ..models.layers import VideoLayer, ImageLayer
from typing import Union


class VideoProcessor:
    """動画・画像処理を担当するプロセッサー"""

    @staticmethod
    def load_video_layer(layer: VideoLayer) -> VideoFileClip:
        """動画レイヤーを読み込む"""
        clip = VideoFileClip(layer.path)

        # 音量調整
        if clip.audio and layer.volume != 1.0:
            clip = clip.with_volume_scaled(layer.volume)

        # 継続時間の調整
        if layer.duration is not None:
            clip = clip.subclipped(0, min(layer.duration, clip.duration))

        # 開始時間の設定
        clip = clip.with_start(layer.start_time)

        return clip

    @staticmethod
    def load_image_layer(layer: ImageLayer, target_size: tuple[int, int]) -> ImageClip:
        """画像レイヤーを読み込む"""
        clip = ImageClip(layer.path, duration=layer.duration)

        # リサイズして中央配置
        clip = clip.resized(height=target_size[1])
        if clip.w > target_size[0]:
            clip = clip.resized(width=target_size[0])

        # 開始時間の設定
        clip = clip.with_start(layer.start_time)

        return clip

    @staticmethod
    def process_video_timeline(
        layers: list[Union[VideoLayer, ImageLayer]],
        output_size: tuple[int, int],
    ) -> VideoFileClip:
        """動画・画像レイヤーをタイムライン順に処理"""
        clips = []

        for layer in layers:
            if isinstance(layer, VideoLayer):
                clip = VideoProcessor.load_video_layer(layer)
            elif isinstance(layer, ImageLayer):
                clip = VideoProcessor.load_image_layer(layer, output_size)
            else:
                continue

            clips.append(clip)

        if not clips:
            raise ValueError("少なくとも1つの動画または画像レイヤーが必要です")

        # すべてのクリップを連結
        final_clip = concatenate_videoclips(clips, method="compose")

        # 出力サイズにリサイズ
        final_clip = final_clip.resized(output_size)

        return final_clip
