"""キャラクターレイヤー処理プロセッサー"""

from pathlib import Path
from moviepy import ImageClip
from ..models import CharacterLayer, CharacterPositionPreset
from ...effect.strategies.character import apply_character_animation
from ...core import ProcessorBase


class CharacterLayerProcessor(ProcessorBase[CharacterLayer, ImageClip]):
    """キャラクターレイヤー処理プロセッサー"""

    def validate(self, layer: CharacterLayer, **kwargs) -> bool:
        """キャラクター画像ファイルの存在チェック"""
        if not Path(layer.path).exists():
            print(f"Warning: Character image not found: {layer.path}")
            return False

        output_size = kwargs.get("output_size")
        if not output_size:
            print("Warning: output_size is required for CharacterLayer")
            return False

        return True

    def _calculate_position(
        self,
        video_size: tuple[int, int],
        char_size: tuple[int, int],
        position: CharacterPositionPreset,
        custom_position: tuple[int, int] | None,
        margin: int = 20,
    ) -> tuple[int, int]:
        """キャラクターの配置位置を計算

        Args:
            video_size: 動画サイズ (width, height)
            char_size: キャラクターサイズ (width, height)
            position: 配置位置プリセット
            custom_position: カスタム位置（指定時はこれを優先）
            margin: 端からの余白（ピクセル）

        Returns:
            配置位置 (x, y)
        """
        if custom_position:
            return custom_position

        video_w, video_h = video_size
        char_w, char_h = char_size

        # 位置計算
        positions = {
            CharacterPositionPreset.BOTTOM_LEFT: (
                margin,
                video_h - char_h - margin,
            ),
            CharacterPositionPreset.BOTTOM_RIGHT: (
                video_w - char_w - margin,
                video_h - char_h - margin,
            ),
            CharacterPositionPreset.BOTTOM_CENTER: (
                (video_w - char_w) // 2,
                video_h - char_h - margin,
            ),
            CharacterPositionPreset.LEFT: (
                margin,
                (video_h - char_h) // 2,
            ),
            CharacterPositionPreset.RIGHT: (
                video_w - char_w - margin,
                (video_h - char_h) // 2,
            ),
            CharacterPositionPreset.CENTER: (
                (video_w - char_w) // 2,
                (video_h - char_h) // 2,
            ),
        }

        return positions.get(position, (0, 0))

    def process(self, layer: CharacterLayer, **kwargs) -> ImageClip:
        """キャラクターレイヤーを処理

        Args:
            layer: キャラクターレイヤー
            **kwargs:
                output_size: 出力動画サイズ (width, height)

        Returns:
            処理済みの ImageClip
        """
        output_size = kwargs["output_size"]
        duration = layer.end_time - layer.start_time

        # 画像を読み込み
        clip = ImageClip(layer.path, duration=duration)

        # スケールを適用
        if layer.scale != 1.0:
            clip = clip.resized(layer.scale)

        # 透明度を適用
        if layer.opacity < 1.0:
            clip = clip.with_opacity(layer.opacity)

        # 位置を計算（アニメーション適用前にサイズを取得）
        char_size = (int(clip.w), int(clip.h))
        position = self._calculate_position(
            output_size,
            char_size,
            layer.position,
            layer.custom_position,
        )

        # アニメーションを適用（位置情報を渡す）
        clip = apply_character_animation(clip, layer.animation, output_size, position)

        # アニメーションが位置を設定しない場合（breathe, pulse）は位置を設定
        from ...layer.models import CharacterAnimationType

        if layer.animation.type in (
            CharacterAnimationType.NONE,
            CharacterAnimationType.BREATHE,
            CharacterAnimationType.PULSE,
        ):
            clip = clip.with_position(position)

        # 開始時間を設定
        clip = clip.with_start(layer.start_time)

        return clip


class CharacterProcessor(ProcessorBase[list[CharacterLayer], list[ImageClip]]):
    """キャラクタータイムライン処理プロセッサー

    複数のキャラクターレイヤーを処理し、合成用のクリップリストを返す。
    """

    def __init__(self, layer_processor: CharacterLayerProcessor | None = None):
        self.layer_processor = layer_processor or CharacterLayerProcessor()

    def validate(self, layers: list[CharacterLayer], **kwargs) -> bool:
        """レイヤーリストのバリデーション"""
        output_size = kwargs.get("output_size")
        if not output_size:
            print("Error: output_size is required")
            return False

        return True

    def process(self, layers: list[CharacterLayer], **kwargs) -> list[ImageClip]:
        """キャラクターレイヤーを処理してクリップリストを返す

        Args:
            layers: キャラクターレイヤーのリスト
            **kwargs:
                output_size: 出力動画サイズ (width, height)

        Returns:
            処理済みクリップのリスト（CompositeVideoClip で合成可能）
        """
        output_size = kwargs["output_size"]
        clips = []

        for layer in layers:
            if self.layer_processor.validate(layer, output_size=output_size):
                clip = self.layer_processor.process(layer, output_size=output_size)
                clips.append(clip)

        return clips
