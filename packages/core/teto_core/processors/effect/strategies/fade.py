"""フェードエフェクト"""

import numpy as np
from moviepy import VideoClip, ImageClip
from .base import EffectStrategy
from ..utils import get_easing_function
from ....models.effects import AnimationEffect


class FadeInEffect(EffectStrategy):
    """フェードインエフェクト（透明度ベース）"""

    def apply(
        self,
        clip: VideoClip | ImageClip,
        effect: AnimationEffect,
        video_size: tuple[int, int]
    ) -> VideoClip | ImageClip:
        """フェードインを適用"""
        easing_fn = get_easing_function(effect.easing)

        def fadein_transform(get_frame, t):
            frame = get_frame(t)
            if t > effect.duration:
                return frame

            progress = min(t / effect.duration, 1.0)
            eased_progress = easing_fn(progress)

            # フレームのコピーを作成して乗算
            frame = frame.copy().astype(np.float32)
            frame = (frame * eased_progress).astype(np.uint8)

            return frame

        return clip.transform(fadein_transform)


class FadeOutEffect(EffectStrategy):
    """フェードアウトエフェクト（透明度ベース）"""

    def apply(
        self,
        clip: VideoClip | ImageClip,
        effect: AnimationEffect,
        video_size: tuple[int, int]
    ) -> VideoClip | ImageClip:
        """フェードアウトを適用"""
        easing_fn = get_easing_function(effect.easing)

        def fadeout_transform(get_frame, t):
            frame = get_frame(t)
            time_from_end = clip.duration - t
            if time_from_end > effect.duration:
                return frame

            progress = 1 - min(time_from_end / effect.duration, 1.0)
            eased_progress = easing_fn(progress)
            opacity = 1.0 - eased_progress

            # フレームのコピーを作成して乗算
            frame = frame.copy().astype(np.float32)
            frame = (frame * opacity).astype(np.uint8)

            return frame

        return clip.transform(fadeout_transform)
