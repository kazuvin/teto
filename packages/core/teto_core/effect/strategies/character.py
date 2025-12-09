"""キャラクターアニメーションエフェクト"""

import numpy as np
from moviepy import VideoClip, ImageClip

from ...layer.models import CharacterAnimationConfig, CharacterAnimationType


def apply_character_animation(
    clip: VideoClip | ImageClip,
    animation: CharacterAnimationConfig,
    video_size: tuple[int, int],
    base_position: tuple[int, int] = (0, 0),
) -> VideoClip | ImageClip:
    """キャラクターアニメーションを適用

    Args:
        clip: 元のクリップ（キャラクター画像）
        animation: アニメーション設定
        video_size: 動画サイズ (width, height)
        base_position: 基準位置 (x, y)

    Returns:
        アニメーションを適用したクリップ
    """
    if animation.type == CharacterAnimationType.NONE:
        return clip

    intensity = animation.intensity
    speed = animation.speed

    # アニメーションタイプに応じた処理
    if animation.type == CharacterAnimationType.BOUNCE:
        return _apply_bounce(clip, intensity, speed, base_position)
    elif animation.type == CharacterAnimationType.SHAKE:
        return _apply_shake(clip, intensity, speed, base_position)
    elif animation.type == CharacterAnimationType.NOD:
        return _apply_nod(clip, intensity, speed, base_position)
    elif animation.type == CharacterAnimationType.SWAY:
        return _apply_sway(clip, intensity, speed, base_position)
    elif animation.type == CharacterAnimationType.BREATHE:
        return _apply_breathe(clip, intensity, speed)
    elif animation.type == CharacterAnimationType.FLOAT:
        return _apply_float(clip, intensity, speed, base_position)
    elif animation.type == CharacterAnimationType.PULSE:
        return _apply_pulse(clip, intensity, speed)

    return clip


def _apply_bounce(
    clip: VideoClip | ImageClip,
    intensity: float,
    speed: float,
    base_position: tuple[int, int],
) -> VideoClip | ImageClip:
    """バウンドアニメーション（上下に弾む）

    位置を動的に変更することで、透明度を保持したままアニメーション。
    """
    max_offset = int(20 * intensity)  # 最大オフセット（ピクセル）
    frequency = 3.0 * speed  # 1秒あたりの回数
    base_x, base_y = base_position

    def position_func(t):
        # バウンス計算（絶対値を取ることで常に上方向への移動）
        bounce = abs(np.sin(t * frequency * np.pi * 2))
        offset = int(max_offset * bounce)
        return (base_x, base_y - offset)

    return clip.with_position(position_func)


def _apply_shake(
    clip: VideoClip | ImageClip,
    intensity: float,
    speed: float,
    base_position: tuple[int, int],
) -> VideoClip | ImageClip:
    """揺れアニメーション（左右に小刻みに揺れる）"""
    max_offset = int(8 * intensity)  # 最大オフセット（ピクセル）
    frequency = 8.0 * speed  # 高速な振動
    base_x, base_y = base_position

    def position_func(t):
        shake = np.sin(t * frequency * np.pi * 2)
        offset = int(max_offset * shake)
        return (base_x + offset, base_y)

    return clip.with_position(position_func)


def _apply_nod(
    clip: VideoClip | ImageClip,
    intensity: float,
    speed: float,
    base_position: tuple[int, int],
) -> VideoClip | ImageClip:
    """頷きアニメーション（上下に小さく動く）"""
    max_offset = int(10 * intensity)  # 最大オフセット（ピクセル）
    frequency = 2.0 * speed  # ゆっくりとした動き
    base_x, base_y = base_position

    def position_func(t):
        nod = np.sin(t * frequency * np.pi * 2)
        offset = int(max_offset * nod)
        return (base_x, base_y + offset)

    return clip.with_position(position_func)


def _apply_sway(
    clip: VideoClip | ImageClip,
    intensity: float,
    speed: float,
    base_position: tuple[int, int],
) -> VideoClip | ImageClip:
    """揺らぎアニメーション（ゆっくり左右に揺れる）"""
    max_offset = int(15 * intensity)  # 最大オフセット（ピクセル）
    frequency = 0.5 * speed  # とてもゆっくり
    base_x, base_y = base_position

    def position_func(t):
        sway = np.sin(t * frequency * np.pi * 2)
        offset = int(max_offset * sway)
        return (base_x + offset, base_y)

    return clip.with_position(position_func)


def _apply_breathe(
    clip: VideoClip | ImageClip, intensity: float, speed: float
) -> VideoClip | ImageClip:
    """呼吸アニメーション（拡大縮小）

    スケール変化のみ。位置は CharacterLayerProcessor で設定される。
    """
    scale_range = 0.03 * intensity  # スケール変化の範囲
    frequency = 0.8 * speed  # 呼吸のリズム

    def resize_func(t):
        breathe = np.sin(t * frequency * np.pi * 2)
        scale = 1.0 + scale_range * breathe
        return scale

    return clip.resized(resize_func)


def _apply_float(
    clip: VideoClip | ImageClip,
    intensity: float,
    speed: float,
    base_position: tuple[int, int],
) -> VideoClip | ImageClip:
    """浮遊アニメーション（上下にゆっくり動く）"""
    max_offset = int(12 * intensity)  # 最大オフセット（ピクセル）
    frequency = 0.4 * speed  # とてもゆっくり
    base_x, base_y = base_position

    def position_func(t):
        float_val = np.sin(t * frequency * np.pi * 2)
        offset = int(max_offset * float_val)
        return (base_x, base_y + offset)

    return clip.with_position(position_func)


def _apply_pulse(
    clip: VideoClip | ImageClip, intensity: float, speed: float
) -> VideoClip | ImageClip:
    """脈動アニメーション（リズミカルに拡大縮小）

    スケール変化のみ。位置は CharacterLayerProcessor で設定される。
    """
    scale_range = 0.05 * intensity  # スケール変化の範囲
    frequency = 1.5 * speed  # やや早いリズム

    def resize_func(t):
        pulse = abs(np.sin(t * frequency * np.pi * 2))
        scale = 1.0 + scale_range * pulse
        return scale

    return clip.resized(resize_func)
