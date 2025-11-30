"""動画・画像処理プロセッサー"""

from pathlib import Path
from moviepy import (
    VideoFileClip,
    ImageClip,
    CompositeVideoClip,
    concatenate_videoclips,
)
from moviepy.video.fx import CrossFadeIn, CrossFadeOut
from ..models import VideoLayer, ImageLayer, StampLayer
from ...effect.processors import EffectProcessor
from ...core import ProcessorBase
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
        """動画・画像レイヤーをタイムライン順に処理（トランジション対応）"""
        output_size = kwargs['output_size']

        # レイヤーとクリップのペアを作成
        layer_clips: list[tuple[Union[VideoLayer, ImageLayer], any]] = []

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

            layer_clips.append((layer, clip))

        if not layer_clips:
            raise ValueError("No valid layers to process")

        # トランジションがない場合は単純に連結
        if not any(layer.transition for layer, _ in layer_clips[:-1]):
            clips = [clip for _, clip in layer_clips]
            final_clip = concatenate_videoclips(clips, method="compose")
            return final_clip.resized(output_size)

        # トランジションがある場合は CompositeVideoClip で合成
        composite_clips = []
        current_time = 0.0

        for i, (layer, clip) in enumerate(layer_clips):
            is_last = i == len(layer_clips) - 1
            prev_layer = layer_clips[i - 1][0] if i > 0 else None

            # 前のレイヤーからのトランジションがある場合、フェードインを適用
            if prev_layer and prev_layer.transition:
                clip = clip.with_effects([CrossFadeIn(prev_layer.transition.duration)])

            # 次のレイヤーへのトランジションがある場合、フェードアウトを適用
            if not is_last and layer.transition:
                clip = clip.with_effects([CrossFadeOut(layer.transition.duration)])

            # 開始時間を設定
            clip = clip.with_start(current_time)
            composite_clips.append(clip)

            # 次のクリップの開始時間を計算（トランジション分オーバーラップ）
            overlap = layer.transition.duration if (not is_last and layer.transition) else 0
            current_time += clip.duration - overlap

        # CompositeVideoClip で合成
        final_clip = CompositeVideoClip(composite_clips, size=output_size)

        return final_clip
