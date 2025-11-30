"""モーションエフェクト"""

import numpy as np
from moviepy import VideoClip, ImageClip
from .base import EffectStrategy
from ..utils import get_easing_function
from ..models import AnimationEffect


class ParallaxEffect(EffectStrategy):
    """パララックス効果（立体的な動き）"""

    def apply(
        self,
        clip: VideoClip | ImageClip,
        effect: AnimationEffect,
        video_size: tuple[int, int],
    ) -> VideoClip | ImageClip:
        """パララックスを適用"""
        direction = effect.direction or "right"
        easing_fn = get_easing_function(effect.easing)

        def parallax_frame(get_frame, t):
            frame = get_frame(t)
            progress = min(t / clip.duration, 1.0) if clip.duration > 0 else 0
            eased_progress = easing_fn(progress)

            h, w = frame.shape[:2]
            max_shift = int(w * 0.05)
            shift = int(max_shift * eased_progress)

            if direction == "right":
                shift_x = shift
            elif direction == "left":
                shift_x = -shift
            else:
                shift_x = 0

            result = np.zeros_like(frame)
            if shift_x > 0:
                result[:, shift_x:] = frame[:, : w - shift_x]
            elif shift_x < 0:
                result[:, : w + shift_x] = frame[:, -shift_x:]
            else:
                result = frame

            return result

        return clip.transform(parallax_frame)


class BounceEffect(EffectStrategy):
    """バウンス効果（弾むような動き）"""

    def apply(
        self,
        clip: VideoClip | ImageClip,
        effect: AnimationEffect,
        video_size: tuple[int, int],
    ) -> VideoClip | ImageClip:
        """バウンスを適用"""
        direction = effect.direction or "bottom"

        def bounce_frame(get_frame, t):
            frame = get_frame(t)
            progress = min(t / effect.duration, 1.0)

            bounce_curve = abs(np.sin(progress * np.pi))
            h, w = frame.shape[:2]

            result = np.zeros_like(frame)

            if direction == "bottom":
                offset = int(h * 0.3 * (1 - bounce_curve))
                if offset < h:
                    result[offset:] = frame[: h - offset]
            elif direction == "top":
                offset = int(h * 0.3 * (1 - bounce_curve))
                if offset < h:
                    result[: h - offset] = frame[offset:]

            return result

        return clip.transform(bounce_frame)
