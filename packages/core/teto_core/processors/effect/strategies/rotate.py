"""回転エフェクト"""

from scipy.ndimage import rotate
from moviepy import VideoClip, ImageClip
from .base import EffectStrategy
from ..utils import get_easing_function
from ....models.effects import AnimationEffect


class RotateEffect(EffectStrategy):
    """回転効果"""

    def apply(
        self,
        clip: VideoClip | ImageClip,
        effect: AnimationEffect,
        video_size: tuple[int, int]
    ) -> VideoClip | ImageClip:
        """回転を適用"""
        rotation_angle = effect.rotation_angle or 360
        easing_fn = get_easing_function(effect.easing)

        def rotate_frame(get_frame, t):
            frame = get_frame(t)
            progress = min(t / clip.duration, 1.0) if clip.duration > 0 else 0
            eased_progress = easing_fn(progress)

            angle = rotation_angle * eased_progress
            return rotate(frame, angle, reshape=False, order=1)

        return clip.transform(rotate_frame)
