"""カラーエフェクト"""

import numpy as np
from moviepy import VideoClip, ImageClip
from .base import EffectStrategy
from ....models.effects import AnimationEffect


class ColorGradeEffect(EffectStrategy):
    """シネマティックなカラーグレーディング"""

    def apply(
        self,
        clip: VideoClip | ImageClip,
        effect: AnimationEffect,
        video_size: tuple[int, int]
    ) -> VideoClip | ImageClip:
        """カラーグレーディングを適用"""
        color_temp = effect.color_temp or 0.0
        saturation = effect.saturation or 1.0
        contrast = effect.contrast or 1.0
        brightness = effect.brightness or 1.0

        def color_grade_frame(get_frame, t):
            frame = get_frame(t).astype(float) / 255.0

            frame = (frame - 0.5) * contrast + 0.5
            frame = frame * brightness

            if color_temp != 0:
                if color_temp > 0:
                    frame[:, :, 0] *= (1 + color_temp * 0.3)
                    frame[:, :, 2] *= (1 - color_temp * 0.3)
                else:
                    frame[:, :, 0] *= (1 + color_temp * 0.3)
                    frame[:, :, 2] *= (1 - color_temp * 0.3)

            if saturation != 1.0:
                gray = np.dot(frame[..., :3], [0.299, 0.587, 0.114])
                frame[:, :, :3] = gray[..., np.newaxis] * (1 - saturation) + frame[:, :, :3] * saturation

            return np.clip(frame * 255, 0, 255).astype(np.uint8)

        return clip.transform(color_grade_frame)


class VignetteEffect(EffectStrategy):
    """ビネット効果（周辺減光）"""

    def apply(
        self,
        clip: VideoClip | ImageClip,
        effect: AnimationEffect,
        video_size: tuple[int, int]
    ) -> VideoClip | ImageClip:
        """ビネットを適用"""
        vignette_amount = effect.vignette_amount or 0.5

        def vignette_frame(get_frame, t):
            frame = get_frame(t)
            h, w = frame.shape[:2]

            y, x = np.ogrid[:h, :w]
            cx, cy = w / 2, h / 2
            distance = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            max_distance = np.sqrt(cx ** 2 + cy ** 2)
            vignette_mask = 1 - (distance / max_distance) * vignette_amount

            if len(frame.shape) == 3:
                vignette_mask = vignette_mask[:, :, np.newaxis]

            return np.clip(frame * vignette_mask, 0, 255).astype(np.uint8)

        return clip.transform(vignette_frame)
