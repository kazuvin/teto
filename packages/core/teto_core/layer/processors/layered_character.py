"""Layered character processor for rendering character parts with animation"""

from PIL import Image
import numpy as np
from moviepy import VideoClip, CompositeVideoClip

from ..models import (
    LayeredCharacterLayer,
    CharacterPart,
    MouthKeyframe,
    EyeKeyframe,
    MouthShape,
    EyeState,
    CharacterPartType,
)


class LayeredCharacterProcessor:
    """レイヤードキャラクタープロセッサー

    パーツベースのキャラクターをレンダリングする。
    キーフレームに基づいてパーツを切り替え、リップシンクと瞬きを実現する。
    """

    def __init__(self, video_size: tuple[int, int]):
        """初期化

        Args:
            video_size: 動画サイズ (width, height)
        """
        self.video_size = video_size

    def process_layer(self, layer: LayeredCharacterLayer) -> CompositeVideoClip:
        """レイヤーを処理してクリップを生成

        Args:
            layer: レイヤードキャラクターレイヤー

        Returns:
            CompositeVideoClip: レンダリングされたクリップ
        """
        duration = layer.end_time - layer.start_time

        # パーツを読み込んでキャッシュ
        part_images = self._load_parts(layer.parts)

        # make_frame関数を作成
        def make_frame(t: float) -> np.ndarray:
            """フレームを生成

            Args:
                t: レイヤー開始からの相対時刻(秒)

            Returns:
                フレーム画像(numpy array)
            """
            absolute_time = layer.start_time + t

            # 現在の口の形状を取得
            mouth_shape = self._get_current_mouth_shape(
                absolute_time, layer.mouth_keyframes
            )

            # 現在の目の状態を取得
            eye_state = self._get_current_eye_state(absolute_time, layer.eye_keyframes)

            # パーツを合成
            composite_image = self._composite_parts(
                part_images, layer.parts, mouth_shape, eye_state
            )

            # numpy array に変換
            return np.array(composite_image)

        # VideoClip を作成
        # ベースパーツの画像サイズを取得
        base_part = layer.parts[0]
        base_image = part_images[base_part.path]
        clip_size = base_image.size  # (width, height)

        clip = VideoClip(make_frame, duration=duration)
        # サイズを手動設定（VideoClipにはw, h属性がないため）
        clip.size = clip_size

        # 開始時刻を設定
        clip = clip.with_start(layer.start_time)

        # スケール・不透明度を適用
        if layer.scale != 1.0:
            clip = clip.resized(layer.scale)
            # スケール後のサイズを手動計算（resizedはw, h属性を更新しない）
            scaled_size = (
                int(clip_size[0] * layer.scale),
                int(clip_size[1] * layer.scale),
            )
        else:
            # スケールなしの場合、clip.wとclip.hを使用できるように設定
            scaled_size = clip_size

        if layer.opacity != 1.0:
            clip = clip.with_opacity(layer.opacity)

        # 配置を計算
        position = self._calculate_position(layer, scaled_size)
        clip = clip.with_position(position)

        # アニメーション適用
        if layer.animation is not None:
            from ...effect.strategies.character import apply_character_animation

            # base_positionを取得（位置がタプルの場合のみアニメーション適用）
            if isinstance(position, tuple):
                clip = apply_character_animation(
                    clip, layer.animation, self.video_size, base_position=position
                )

        # フェードイン/アウト適用
        if layer.fade_in_duration is not None or layer.fade_out_duration is not None:

            def apply_fade(get_frame, t):
                frame = get_frame(t)
                alpha = 1.0

                # フェードイン
                if layer.fade_in_duration is not None and t < layer.fade_in_duration:
                    alpha = t / layer.fade_in_duration

                # フェードアウト
                if layer.fade_out_duration is not None:
                    time_from_end = duration - t
                    if time_from_end < layer.fade_out_duration:
                        fade_out_alpha = time_from_end / layer.fade_out_duration
                        alpha = min(alpha, fade_out_alpha)

                if alpha < 1.0:
                    frame = frame.copy().astype(np.float32)
                    frame = (frame * alpha).astype(np.uint8)

                return frame

            clip = clip.transform(apply_fade)

        return clip

    def _load_parts(self, parts: list[CharacterPart]) -> dict[str, Image.Image]:
        """パーツ画像を読み込む

        Args:
            parts: パーツリスト

        Returns:
            パスをキーとした画像辞書
        """
        part_images = {}
        for part in parts:
            if part.path not in part_images:
                try:
                    img = Image.open(part.path).convert("RGBA")
                    part_images[part.path] = img
                except Exception as e:
                    raise ValueError(
                        f"パーツ画像の読み込みに失敗しました: {part.path}"
                    ) from e
        return part_images

    def _get_current_mouth_shape(
        self, time: float, keyframes: list[MouthKeyframe]
    ) -> MouthShape | None:
        """現在の時刻における口の形状を取得

        Args:
            time: 現在時刻(秒)
            keyframes: 口のキーフレームリスト

        Returns:
            口の形状(キーフレームがない場合はNone)
        """
        if not keyframes:
            return None

        # 最も近い過去のキーフレームを取得
        current_shape = None
        for kf in keyframes:
            if kf.time <= time:
                current_shape = kf.shape
            else:
                break

        return current_shape

    def _get_current_eye_state(
        self, time: float, keyframes: list[EyeKeyframe]
    ) -> EyeState | None:
        """現在の時刻における目の状態を取得

        Args:
            time: 現在時刻(秒)
            keyframes: 目のキーフレームリスト

        Returns:
            目の状態(キーフレームがない場合はNone)
        """
        if not keyframes:
            return None

        # 最も近い過去のキーフレームを取得
        current_state = None
        for kf in keyframes:
            if kf.time <= time:
                current_state = kf.state
            else:
                break

        return current_state

    def _composite_parts(
        self,
        part_images: dict[str, Image.Image],
        parts: list[CharacterPart],
        mouth_shape: MouthShape | None,
        eye_state: EyeState | None,
    ) -> Image.Image:
        """パーツを合成して1枚の画像を生成

        Args:
            part_images: パーツ画像辞書
            parts: パーツリスト(Z-index順にソート済み)
            mouth_shape: 現在の口の形状
            eye_state: 現在の目の状態

        Returns:
            合成された画像
        """
        # ベース画像のサイズを取得
        base_part = parts[0]
        base_image = part_images[base_part.path]
        composite = Image.new("RGBA", base_image.size, (0, 0, 0, 0))

        # キーフレームがない場合に描画する最初のパーツを追跡
        first_eye_part_rendered = False
        first_mouth_part_rendered = False

        for part in parts:
            # パーツタイプによってフィルタリング
            should_render = True

            if part.type == CharacterPartType.MOUTH:
                # 口は現在の形状と一致する場合のみ描画
                if mouth_shape is None:
                    # キーフレームがない場合は、最初の口パーツのみ描画
                    if first_mouth_part_rendered:
                        should_render = False
                    else:
                        should_render = True
                        first_mouth_part_rendered = True
                else:
                    # パーツ名から形状を判定
                    # 例: "mouth_open" -> "open"
                    part_shape_str = part.name.replace("mouth_", "")
                    should_render = part_shape_str == mouth_shape.value

            elif part.type == CharacterPartType.EYES:
                # 目は現在の状態と一致する場合のみ描画
                if eye_state is None:
                    # キーフレームがない場合は、最初の目パーツのみ描画
                    if first_eye_part_rendered:
                        should_render = False
                    else:
                        should_render = True
                        first_eye_part_rendered = True
                else:
                    # パーツ名から状態を判定
                    # 例: "eyes_open" -> "open"
                    part_state_str = part.name.replace("eyes_", "")
                    should_render = part_state_str == eye_state.value

            if not should_render:
                continue

            # パーツ画像を取得
            part_img = part_images[part.path]

            # オフセットを適用して貼り付け
            position = (part.offset_x, part.offset_y)
            composite.paste(part_img, position, part_img)

        return composite

    def _calculate_position(
        self, layer: LayeredCharacterLayer, clip_size: tuple[int, int]
    ) -> tuple[int, int] | str:
        """キャラクターの配置位置を計算

        Args:
            layer: レイヤー
            clip_size: クリップサイズ (width, height)

        Returns:
            位置座標またはmoviepy位置文字列
        """
        # カスタム位置が指定されている場合
        if layer.custom_position:
            return layer.custom_position

        # プリセット位置の場合
        video_width, video_height = self.video_size
        clip_width, clip_height = clip_size

        position_str = layer.position.value
        if position_str == "bottom-right":
            return (video_width - clip_width, video_height - clip_height)
        elif position_str == "bottom-left":
            return (0, video_height - clip_height)
        elif position_str == "bottom-center":
            return ((video_width - clip_width) // 2, video_height - clip_height)
        elif position_str == "right":
            return (video_width - clip_width, (video_height - clip_height) // 2)
        elif position_str == "left":
            return (0, (video_height - clip_height) // 2)
        elif position_str == "center":
            return (
                (video_width - clip_width) // 2,
                (video_height - clip_height) // 2,
            )
        else:
            # デフォルトは右下
            return (video_width - clip_width, video_height - clip_height)
