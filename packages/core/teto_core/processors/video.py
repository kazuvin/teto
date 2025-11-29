"""動画・画像処理プロセッサー"""

from pathlib import Path
from moviepy import (
    VideoFileClip,
    ImageClip,
    concatenate_videoclips,
    CompositeVideoClip,
)
from ..models.layers import VideoLayer, ImageLayer, StampLayer
from .animation import AnimationProcessor
from typing import Union


class VideoProcessor:
    """動画・画像処理を担当するプロセッサー"""

    @staticmethod
    def load_video_layer(layer: VideoLayer, output_size: tuple[int, int] = None) -> VideoFileClip:
        """動画レイヤーを読み込む"""
        clip = VideoFileClip(layer.path)

        # 音量調整
        if clip.audio and layer.volume != 1.0:
            clip = clip.with_volume_scaled(layer.volume)

        # 継続時間の調整
        if layer.duration is not None:
            clip = clip.subclipped(0, min(layer.duration, clip.duration))

        # アニメーション効果を適用
        if layer.effects and output_size:
            clip = AnimationProcessor.apply_effects(clip, layer.effects, output_size)

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

        # アニメーション効果を適用
        if layer.effects:
            clip = AnimationProcessor.apply_effects(clip, layer.effects, target_size)

        # 開始時間の設定
        clip = clip.with_start(layer.start_time)

        return clip

    @staticmethod
    def load_stamp_layer(layer: StampLayer) -> ImageClip:
        """スタンプレイヤーを読み込む"""
        clip = ImageClip(layer.path, duration=layer.duration)

        # スケールを適用
        if layer.scale != 1.0:
            clip = clip.resized(layer.scale)

        # 位置を設定
        clip = clip.with_position((layer.position_x, layer.position_y))

        # アニメーション効果を適用
        if layer.effects:
            # スタンプのサイズを取得（スケール適用後）
            stamp_size = (int(clip.w), int(clip.h))
            clip = AnimationProcessor.apply_effects(clip, layer.effects, stamp_size)

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
                clip = VideoProcessor.load_video_layer(layer, output_size)
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
