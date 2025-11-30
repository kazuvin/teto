"""グリッチエフェクト"""

import numpy as np
from moviepy import VideoClip, ImageClip
from .base import EffectStrategy
from ....models.effects import AnimationEffect


class GlitchEffect(EffectStrategy):
    """デジタルグリッチ効果"""

    def apply(
        self,
        clip: VideoClip | ImageClip,
        effect: AnimationEffect,
        video_size: tuple[int, int]
    ) -> VideoClip | ImageClip:
        """グリッチを適用"""
        intensity = effect.glitch_intensity or 0.3

        def glitch_frame(get_frame, t):
            frame = get_frame(t).copy()

            if np.random.random() < intensity:
                h, w = frame.shape[:2]
                num_slices = np.random.randint(3, 10)

                for _ in range(num_slices):
                    y1 = np.random.randint(0, h - 10)
                    y2 = y1 + np.random.randint(5, 30)
                    shift = np.random.randint(-20, 20)

                    if shift > 0:
                        frame[y1:y2, shift:] = frame[y1:y2, :-shift]
                    elif shift < 0:
                        frame[y1:y2, :shift] = frame[y1:y2, -shift:]

                if np.random.random() < 0.5 and len(frame.shape) == 3:
                    channel = np.random.randint(0, 3)
                    frame[:, :, channel] = np.roll(frame[:, :, channel], np.random.randint(-5, 5), axis=1)

            return frame

        return clip.transform(glitch_frame)
