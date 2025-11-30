"""ブラーエフェクト"""

import numpy as np
from scipy.ndimage import gaussian_filter
from moviepy import VideoClip, ImageClip
from .base import EffectStrategy
from ..models import AnimationEffect


class BlurEffect(EffectStrategy):
    """ブラー効果（被写界深度風）"""

    def apply(
        self,
        clip: VideoClip | ImageClip,
        effect: AnimationEffect,
        video_size: tuple[int, int]
    ) -> VideoClip | ImageClip:
        """ブラーを適用"""
        blur_amount = effect.blur_amount or 3.0

        def blur_frame(get_frame, t):
            frame = get_frame(t)
            if len(frame.shape) == 3:
                blurred = np.zeros_like(frame)
                for i in range(frame.shape[2]):
                    blurred[:, :, i] = gaussian_filter(frame[:, :, i], sigma=blur_amount)
                return blurred
            else:
                return gaussian_filter(frame, sigma=blur_amount)

        return clip.transform(blur_frame)
