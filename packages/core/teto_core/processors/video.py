"""動画・画像処理プロセッサー"""

from pathlib import Path
from moviepy import (
    VideoFileClip,
    ImageClip,
    concatenate_videoclips,
    CompositeVideoClip,
)
from ..models.layers import VideoLayer, ImageLayer, StampLayer
from .effect import EffectProcessor
from .base import ProcessorBase
from typing import Union


class VideoLayerProcessor(ProcessorBase[VideoLayer, VideoFileClip]):
    """動画レイヤー処理プロセッサー"""

    def __init__(self, effect_processor: EffectProcessor = None):
        self.effect_processor = effect_processor or EffectProcessor()

    def validate(self, layer: VideoLayer, **kwargs) -> bool:
        """動画ファイルの存在チェック"""
        if not Path(layer.path).exists():
            print(f"Warning: Video file not found: {layer.path}")
            return False
        return True

    def process(self, layer: VideoLayer, **kwargs) -> VideoFileClip:
        """動画レイヤーを読み込む"""
        output_size = kwargs.get('output_size')

        # 動画を読み込む
        clip = VideoFileClip(layer.path)

        # 音量調整
        if clip.audio and layer.volume != 1.0:
            clip = clip.with_volume_scaled(layer.volume)

        # 継続時間の調整
        if layer.duration is not None:
            clip = clip.subclipped(0, min(layer.duration, clip.duration))

        # エフェクトを適用
        if layer.effects and output_size:
            clip = self.effect_processor.apply_effects(clip, layer.effects, output_size)

        # 開始時間の設定
        clip = clip.with_start(layer.start_time)

        return clip


class ImageLayerProcessor(ProcessorBase[ImageLayer, ImageClip]):
    """画像レイヤー処理プロセッサー"""

    def __init__(self, effect_processor: EffectProcessor = None):
        self.effect_processor = effect_processor or EffectProcessor()

    def validate(self, layer: ImageLayer, **kwargs) -> bool:
        """画像ファイルの存在チェック"""
        if not Path(layer.path).exists():
            print(f"Warning: Image file not found: {layer.path}")
            return False

        target_size = kwargs.get('target_size')
        if not target_size:
            print("Warning: target_size is required for ImageLayer")
            return False

        return True

    def process(self, layer: ImageLayer, **kwargs) -> ImageClip:
        """画像レイヤーを読み込む"""
        target_size = kwargs['target_size']

        clip = ImageClip(layer.path, duration=layer.duration)

        # リサイズして中央配置
        clip = clip.resized(height=target_size[1])
        if clip.w > target_size[0]:
            clip = clip.resized(width=target_size[0])

        # エフェクトを適用
        if layer.effects:
            clip = self.effect_processor.apply_effects(clip, layer.effects, target_size)

        # 開始時間の設定
        clip = clip.with_start(layer.start_time)

        return clip


class StampLayerProcessor(ProcessorBase[StampLayer, ImageClip]):
    """スタンプレイヤー処理プロセッサー"""

    def __init__(self, effect_processor: EffectProcessor = None):
        self.effect_processor = effect_processor or EffectProcessor()

    def validate(self, layer: StampLayer, **kwargs) -> bool:
        """スタンプファイルの存在チェック"""
        if not Path(layer.path).exists():
            print(f"Warning: Stamp file not found: {layer.path}")
            return False
        return True

    def process(self, layer: StampLayer, **kwargs) -> ImageClip:
        """スタンプレイヤーを読み込む"""
        clip = ImageClip(layer.path, duration=layer.duration)

        # スケールを適用
        if layer.scale != 1.0:
            clip = clip.resized(layer.scale)

        # 位置を設定
        clip = clip.with_position((layer.position_x, layer.position_y))

        # エフェクトを適用
        if layer.effects:
            # スタンプのサイズを取得（スケール適用後）
            stamp_size = (int(clip.w), int(clip.h))
            clip = self.effect_processor.apply_effects(clip, layer.effects, stamp_size)

        # 開始時間の設定
        clip = clip.with_start(layer.start_time)

        return clip


class VideoProcessor(ProcessorBase[list[Union[VideoLayer, ImageLayer]], VideoFileClip]):
    """動画タイムライン処理プロセッサー"""

    def __init__(
        self,
        video_processor: VideoLayerProcessor = None,
        image_processor: ImageLayerProcessor = None
    ):
        self.video_processor = video_processor or VideoLayerProcessor()
        self.image_processor = image_processor or ImageLayerProcessor()

    def validate(self, layers: list, **kwargs) -> bool:
        """レイヤーリストのバリデーション"""
        if not layers:
            print("Error: At least one video or image layer is required")
            return False

        output_size = kwargs.get('output_size')
        if not output_size:
            print("Error: output_size is required")
            return False

        return True

    def process(
        self,
        layers: list[Union[VideoLayer, ImageLayer]],
        **kwargs
    ) -> VideoFileClip:
        """動画・画像レイヤーをタイムライン順に処理"""
        output_size = kwargs['output_size']
        clips = []

        for layer in layers:
            if isinstance(layer, VideoLayer):
                clip = self.video_processor.execute(
                    layer,
                    output_size=output_size
                )
            elif isinstance(layer, ImageLayer):
                clip = self.image_processor.execute(
                    layer,
                    target_size=output_size
                )
            else:
                continue

            clips.append(clip)

        # すべてのクリップを連結
        final_clip = concatenate_videoclips(clips, method="compose")

        # 出力サイズにリサイズ
        final_clip = final_clip.resized(output_size)

        return final_clip
