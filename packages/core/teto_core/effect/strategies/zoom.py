"""ズームエフェクト"""

import numpy as np
from scipy.ndimage import zoom as scipy_zoom
from moviepy import VideoClip, ImageClip
from .base import EffectStrategy
from ..utils import get_easing_function
from ..models import AnimationEffect


class ZoomEffect(EffectStrategy):
    """スムーズズーム効果（イージング付き、透明背景対応）"""

    def apply(
        self,
        clip: VideoClip | ImageClip,
        effect: AnimationEffect,
        video_size: tuple[int, int]
    ) -> VideoClip | ImageClip:
        """ズームを適用"""
        start_scale = effect.start_scale or 1.0
        end_scale = effect.end_scale or 1.2
        easing_fn = get_easing_function(effect.easing)

        def zoom_frame(get_frame, t):
            frame = get_frame(t)
            progress = min(t / clip.duration, 1.0) if clip.duration > 0 else 0
            eased_progress = easing_fn(progress)

            current_scale = start_scale + (end_scale - start_scale) * eased_progress

            h, w = frame.shape[:2]
            new_h, new_w = int(h * current_scale), int(w * current_scale)

            if len(frame.shape) == 3:
                zoomed = scipy_zoom(frame, (current_scale, current_scale, 1), order=1)
            else:
                zoomed = scipy_zoom(frame, (current_scale, current_scale), order=1)

            zh, zw = zoomed.shape[:2]
            y_start = (zh - h) // 2
            x_start = (zw - w) // 2

            if current_scale >= 1.0:
                return zoomed[y_start:y_start + h, x_start:x_start + w]
            else:
                # 透明背景を使用（RGBAの場合）
                if len(frame.shape) == 3:
                    if frame.shape[2] == 4:
                        # RGBA - アルファチャンネル付き透明背景
                        result = np.zeros((h, w, 4), dtype=frame.dtype)
                    elif frame.shape[2] == 3:
                        # RGB - アルファチャンネルを追加
                        result = np.zeros((h, w, 4), dtype=frame.dtype)
                        # ズーム後の画像にアルファチャンネルを追加
                        alpha = np.full((zh, zw, 1), 255, dtype=frame.dtype)
                        zoomed = np.concatenate([zoomed, alpha], axis=2)
                    else:
                        result = np.zeros_like(frame)
                else:
                    result = np.zeros_like(frame)

                y_offset = (h - zh) // 2
                x_offset = (w - zw) // 2
                result[y_offset:y_offset + zh, x_offset:x_offset + zw] = zoomed
                return result

        return clip.transform(zoom_frame)


class KenBurnsEffect(EffectStrategy):
    """Ken Burns効果（パン＋ズーム）"""

    def apply(
        self,
        clip: VideoClip | ImageClip,
        effect: AnimationEffect,
        video_size: tuple[int, int]
    ) -> VideoClip | ImageClip:
        """Ken Burns効果を適用"""
        start_scale = effect.start_scale or 1.0
        end_scale = effect.end_scale or 1.3
        pan_start = effect.pan_start or (0.0, 0.0)
        pan_end = effect.pan_end or (0.1, 0.1)
        easing_fn = get_easing_function(effect.easing)

        def ken_burns_frame(get_frame, t):
            frame = get_frame(t)
            progress = min(t / clip.duration, 1.0) if clip.duration > 0 else 0
            eased_progress = easing_fn(progress)

            current_scale = start_scale + (end_scale - start_scale) * eased_progress
            pan_x = pan_start[0] + (pan_end[0] - pan_start[0]) * eased_progress
            pan_y = pan_start[1] + (pan_end[1] - pan_start[1]) * eased_progress

            h, w = frame.shape[:2]

            if len(frame.shape) == 3:
                zoomed = scipy_zoom(frame, (current_scale, current_scale, 1), order=1)
            else:
                zoomed = scipy_zoom(frame, (current_scale, current_scale), order=1)

            zh, zw = zoomed.shape[:2]
            x_offset = int((zw - w) * (0.5 + pan_x))
            y_offset = int((zh - h) * (0.5 + pan_y))

            x_offset = max(0, min(x_offset, zw - w))
            y_offset = max(0, min(y_offset, zh - h))

            return zoomed[y_offset:y_offset + h, x_offset:x_offset + w]

        return clip.transform(ken_burns_frame)
