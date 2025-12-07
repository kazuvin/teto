"""動画・画像処理プロセッサー"""

from pathlib import Path
from moviepy import (
    VideoFileClip,
    ImageClip,
    CompositeVideoClip,
    concatenate_videoclips,
    ColorClip,
)
from moviepy.video.fx import CrossFadeIn, CrossFadeOut
from ..models import VideoLayer, ImageLayer, StampLayer, PositionPreset
from ...effect.processors import EffectProcessor
from ...core import ProcessorBase
from typing import Union


def calc_contain_size(
    clip_size: tuple[int, int], target_size: tuple[int, int]
) -> tuple[int, int]:
    """
    アスペクト比を保ったまま収まるサイズを計算（object-fit: contain）

    Args:
        clip_size: 元のサイズ (width, height)
        target_size: 目標サイズ (width, height)

    Returns:
        リサイズ後のサイズ (width, height)
    """
    target_width, target_height = target_size
    clip_width, clip_height = clip_size

    target_aspect = target_width / target_height
    clip_aspect = clip_width / clip_height

    if clip_aspect > target_aspect:
        # クリップが横長 -> 幅を基準にリサイズ
        new_width = target_width
        new_height = int(target_width / clip_aspect)
    else:
        # クリップが縦長 -> 高さを基準にリサイズ
        new_height = target_height
        new_width = int(target_height * clip_aspect)

    return (new_width, new_height)


def resize_contain_only(clip, target_size: tuple[int, int]):
    """
    アスペクト比を保ったままクリップをリサイズ（パディングなし）

    Args:
        clip: リサイズするクリップ
        target_size: 目標サイズ (width, height)

    Returns:
        リサイズされたクリップ
    """
    new_size = calc_contain_size(clip.size, target_size)
    return clip.resized(new_size)


def add_background_padding(clip, target_size: tuple[int, int], bg_color=(0, 0, 0)):
    """
    クリップに背景を追加して中央配置

    Args:
        clip: 配置するクリップ
        target_size: 目標サイズ (width, height)
        bg_color: 背景色 (R, G, B)

    Returns:
        背景付きのクリップ
    """
    target_width, target_height = target_size
    clip_width, clip_height = clip.size

    # 背景クリップを作成
    bg_clip = ColorClip(size=target_size, color=bg_color, duration=clip.duration)

    # 中央配置
    x_center = (target_width - clip_width) // 2
    y_center = (target_height - clip_height) // 2

    # 合成
    final_clip = CompositeVideoClip(
        [bg_clip, clip.with_position((x_center, y_center))], size=target_size
    )

    return final_clip


def resize_with_padding(clip, target_size: tuple[int, int], bg_color=(0, 0, 0)):
    """
    アスペクト比を保ったままクリップをリサイズし、余白を追加（object-fit: contain）

    Args:
        clip: リサイズするクリップ
        target_size: 目標サイズ (width, height)
        bg_color: 背景色 (R, G, B)

    Returns:
        リサイズされたクリップ
    """
    resized_clip = resize_contain_only(clip, target_size)
    return add_background_padding(resized_clip, target_size, bg_color)


def resize_with_cover(clip, target_size: tuple[int, int]):
    """
    アスペクト比を保ったままクリップをリサイズし、画面を埋める（object-fit: cover）
    はみ出た部分は中央でトリミングされる

    Args:
        clip: リサイズするクリップ
        target_size: 目標サイズ (width, height)

    Returns:
        リサイズ＆クロップされたクリップ
    """
    target_width, target_height = target_size
    clip_width, clip_height = clip.size

    # アスペクト比を計算
    target_aspect = target_width / target_height
    clip_aspect = clip_width / clip_height

    # coverの場合は画面を埋めるように大きい方に合わせる
    if clip_aspect > target_aspect:
        # クリップが横長 -> 高さを基準にリサイズ
        new_height = target_height
        new_width = int(target_height * clip_aspect)
    else:
        # クリップが縦長 -> 幅を基準にリサイズ
        new_width = target_width
        new_height = int(target_width / clip_aspect)

    # リサイズ
    resized_clip = clip.resized((new_width, new_height))

    # 中央でクロップ
    x_center = (new_width - target_width) // 2
    y_center = (new_height - target_height) // 2

    cropped_clip = resized_clip.cropped(
        x1=x_center, y1=y_center, width=target_width, height=target_height
    )

    return cropped_clip


def resize_with_fill(clip, target_size: tuple[int, int]):
    """
    アスペクト比を無視してクリップをリサイズ（object-fit: fill）
    引き伸ばしまたは圧縮される

    Args:
        clip: リサイズするクリップ
        target_size: 目標サイズ (width, height)

    Returns:
        リサイズされたクリップ
    """
    return clip.resized(target_size)


class VideoLayerProcessor(ProcessorBase[VideoLayer, VideoFileClip]):
    """動画レイヤー処理プロセッサー"""

    def __init__(self, effect_processor: EffectProcessor = None):
        self.effect_processor = effect_processor or EffectProcessor()

    def _loop_clip(self, clip: VideoFileClip, target_duration: float) -> VideoFileClip:
        """動画をループして指定時間まで延長する"""
        clips = []
        total_duration = 0.0

        while total_duration < target_duration:
            remaining = target_duration - total_duration
            if remaining >= clip.duration:
                clips.append(clip)
                total_duration += clip.duration
            else:
                # 最後の部分は必要な長さだけカット
                clips.append(clip.subclipped(0, remaining))
                total_duration += remaining

        return concatenate_videoclips(clips, method="compose")

    def validate(self, layer: VideoLayer, **kwargs) -> bool:
        """動画ファイルの存在チェック"""
        if not Path(layer.path).exists():
            print(f"Warning: Video file not found: {layer.path}")
            return False
        return True

    def process(self, layer: VideoLayer, **kwargs) -> VideoFileClip:
        """動画レイヤーを読み込む"""
        output_size = kwargs.get("output_size")
        object_fit = kwargs.get("object_fit", "cover")

        # 動画を読み込む
        clip = VideoFileClip(layer.path)

        # 音量調整
        if clip.audio and layer.volume != 1.0:
            clip = clip.with_volume_scaled(layer.volume)

        # 継続時間の調整
        if layer.duration is not None:
            # loop が None または True の場合はループ有効
            should_loop = layer.loop is not False
            if should_loop and layer.duration > clip.duration:
                # ループ再生: 動画が短い場合は繰り返す
                clip = self._loop_clip(clip, layer.duration)
            else:
                clip = clip.subclipped(0, min(layer.duration, clip.duration))

        if output_size:
            if layer.effects:
                # エフェクトがある場合は object_fit に応じて処理を分ける
                if object_fit == "contain":
                    # contain モード: 動画全体を表示し、エフェクトは動画のみに適用
                    resized_clip = resize_contain_only(clip, output_size)
                    effect_size = resized_clip.size
                    effect_clip = self.effect_processor.apply_effects(
                        resized_clip, layer.effects, effect_size
                    )
                    clip = add_background_padding(effect_clip, output_size)
                elif object_fit == "fill":
                    resized_clip = resize_with_fill(clip, output_size)
                    clip = self.effect_processor.apply_effects(
                        resized_clip, layer.effects, output_size
                    )
                else:  # cover (default)
                    resized_clip = resize_with_cover(clip, output_size)
                    clip = self.effect_processor.apply_effects(
                        resized_clip, layer.effects, output_size
                    )
            else:
                # エフェクトがない場合は通常のリサイズ
                if object_fit == "contain":
                    clip = resize_with_padding(clip, output_size)
                elif object_fit == "fill":
                    clip = resize_with_fill(clip, output_size)
                else:  # cover (default)
                    clip = resize_with_cover(clip, output_size)

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

        target_size = kwargs.get("target_size")
        if not target_size:
            print("Warning: target_size is required for ImageLayer")
            return False

        return True

    def process(self, layer: ImageLayer, **kwargs) -> ImageClip:
        """画像レイヤーを読み込む"""
        target_size = kwargs["target_size"]
        object_fit = kwargs.get("object_fit", "cover")

        clip = ImageClip(layer.path, duration=layer.duration)

        if layer.effects:
            # エフェクトがある場合は object_fit に応じて処理を分ける
            if object_fit == "contain":
                # contain モード: 画像全体を表示し、エフェクトは画像のみに適用
                # 1. アスペクト比を保ってリサイズ（パディングなし）
                resized_clip = resize_contain_only(clip, target_size)
                # 2. エフェクトを適用（リサイズ後のサイズで）
                effect_size = resized_clip.size
                effect_clip = self.effect_processor.apply_effects(
                    resized_clip, layer.effects, effect_size
                )
                # 3. 背景を追加して中央配置（黒背景は静止したまま）
                clip = add_background_padding(effect_clip, target_size)
            elif object_fit == "fill":
                # fill モード: 引き伸ばしてからエフェクト適用
                resized_clip = resize_with_fill(clip, target_size)
                clip = self.effect_processor.apply_effects(
                    resized_clip, layer.effects, target_size
                )
            else:  # cover (default)
                # cover モード: トリミングしてからエフェクト適用
                resized_clip = resize_with_cover(clip, target_size)
                clip = self.effect_processor.apply_effects(
                    resized_clip, layer.effects, target_size
                )
        else:
            # エフェクトがない場合は通常のリサイズ
            if object_fit == "contain":
                clip = resize_with_padding(clip, target_size)
            elif object_fit == "fill":
                clip = resize_with_fill(clip, target_size)
            else:  # cover (default)
                clip = resize_with_cover(clip, target_size)

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

        # プリセット位置を使用する場合は output_size が必要
        if layer.position_preset and layer.position_preset != PositionPreset.CUSTOM:
            output_size = kwargs.get("output_size")
            if not output_size:
                print("Warning: output_size is required when using position_preset")
                return False

        return True

    def _calculate_position_from_preset(
        self,
        video_size: tuple[int, int],
        stamp_size: tuple[int, int],
        preset: PositionPreset,
        margin: int,
    ) -> tuple[int, int]:
        """プリセットから実際の座標を計算する"""
        video_w, video_h = video_size
        stamp_w, stamp_h = stamp_size

        positions = {
            PositionPreset.TOP_LEFT: (margin, margin),
            PositionPreset.TOP_RIGHT: (video_w - stamp_w - margin, margin),
            PositionPreset.BOTTOM_LEFT: (margin, video_h - stamp_h - margin),
            PositionPreset.BOTTOM_RIGHT: (
                video_w - stamp_w - margin,
                video_h - stamp_h - margin,
            ),
        }
        return positions.get(preset, (0, 0))

    def _apply_opacity(self, clip: ImageClip, opacity: float) -> ImageClip:
        """クリップに透明度を適用する"""
        if opacity < 1.0:
            return clip.with_opacity(opacity)
        return clip

    def process(self, layer: StampLayer, **kwargs) -> ImageClip:
        """スタンプレイヤーを読み込む"""
        output_size = kwargs.get("output_size")

        clip = ImageClip(layer.path, duration=layer.duration)

        # スケールを適用
        if layer.scale != 1.0:
            clip = clip.resized(layer.scale)

        # 透明度を適用
        clip = self._apply_opacity(clip, layer.opacity)

        # 位置を設定（プリセットがある場合はプリセットを優先）
        if layer.position_preset and layer.position_preset != PositionPreset.CUSTOM:
            if output_size:
                stamp_size = (int(clip.w), int(clip.h))
                position = self._calculate_position_from_preset(
                    output_size, stamp_size, layer.position_preset, layer.margin
                )
                clip = clip.with_position(position)
        else:
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
        image_processor: ImageLayerProcessor = None,
    ):
        self.video_processor = video_processor or VideoLayerProcessor()
        self.image_processor = image_processor or ImageLayerProcessor()

    def validate(self, layers: list, **kwargs) -> bool:
        """レイヤーリストのバリデーション"""
        if not layers:
            print("Error: At least one video or image layer is required")
            return False

        output_size = kwargs.get("output_size")
        if not output_size:
            print("Error: output_size is required")
            return False

        return True

    def process(
        self, layers: list[Union[VideoLayer, ImageLayer]], **kwargs
    ) -> VideoFileClip:
        """動画・画像レイヤーをタイムライン順に処理（トランジション対応）"""
        output_size = kwargs["output_size"]
        object_fit = kwargs.get("object_fit", "cover")

        # レイヤーとクリップのペアを作成
        layer_clips: list[tuple[Union[VideoLayer, ImageLayer], any]] = []

        for layer in layers:
            if isinstance(layer, VideoLayer):
                clip = self.video_processor.execute(
                    layer, output_size=output_size, object_fit=object_fit
                )
            elif isinstance(layer, ImageLayer):
                clip = self.image_processor.execute(
                    layer, target_size=output_size, object_fit=object_fit
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
            return final_clip

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
            overlap = (
                layer.transition.duration if (not is_last and layer.transition) else 0
            )
            current_time += clip.duration - overlap

        # CompositeVideoClip で合成
        final_clip = CompositeVideoClip(composite_clips, size=output_size)

        return final_clip
