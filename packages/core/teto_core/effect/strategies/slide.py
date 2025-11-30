"""スライドエフェクト"""

import numpy as np
from moviepy import VideoClip, ImageClip
from .base import EffectStrategy
from ..utils import get_easing_function
from ..models import AnimationEffect


class SlideInEffect(EffectStrategy):
    """スライドインエフェクト（カスタム実装）"""

    def apply(
        self,
        clip: VideoClip | ImageClip,
        effect: AnimationEffect,
        video_size: tuple[int, int],
    ) -> VideoClip | ImageClip:
        """スライドインを適用"""
        direction = effect.direction or "left"
        easing_fn = get_easing_function(effect.easing)
        video_w, video_h = video_size

        def slide_in_frame(get_frame, t):
            frame = get_frame(t)
            # duration内のみアニメーション
            if t > effect.duration:
                # アニメーション完了後は元のフレームを返す
                h, w = frame.shape[:2]
                result = np.zeros(
                    (
                        (video_h, video_w, frame.shape[2])
                        if len(frame.shape) == 3
                        else (video_h, video_w)
                    ),
                    dtype=frame.dtype,
                )
                # 中央配置
                y_offset = (video_h - h) // 2
                x_offset = (video_w - w) // 2
                result[y_offset : y_offset + h, x_offset : x_offset + w] = frame
                return result

            progress = min(t / effect.duration, 1.0)
            eased_progress = easing_fn(progress)

            h, w = frame.shape[:2]
            result = np.zeros(
                (
                    (video_h, video_w, frame.shape[2])
                    if len(frame.shape) == 3
                    else (video_h, video_w)
                ),
                dtype=frame.dtype,
            )

            # 最終位置（中央）
            final_y = (video_h - h) // 2
            final_x = (video_w - w) // 2

            if direction == "left":
                # 左からスライドイン（画面外左 → 中央）
                x_pos = int(final_x - video_w * (1 - eased_progress))
                y_pos = final_y
            elif direction == "right":
                # 右からスライドイン（画面外右 → 中央）
                x_pos = int(final_x + video_w * (1 - eased_progress))
                y_pos = final_y
            elif direction == "top":
                # 上からスライドイン（画面外上 → 中央）
                x_pos = final_x
                y_pos = int(final_y - video_h * (1 - eased_progress))
            elif direction == "bottom":
                # 下からスライドイン（画面外下 → 中央）
                x_pos = final_x
                y_pos = int(final_y + video_h * (1 - eased_progress))
            else:
                x_pos = final_x
                y_pos = final_y

            # フレームを配置（はみ出し部分は切り取る）
            src_x1 = max(0, -x_pos)
            src_y1 = max(0, -y_pos)
            src_x2 = min(w, video_w - x_pos)
            src_y2 = min(h, video_h - y_pos)

            dst_x1 = max(0, x_pos)
            dst_y1 = max(0, y_pos)
            dst_x2 = dst_x1 + (src_x2 - src_x1)
            dst_y2 = dst_y1 + (src_y2 - src_y1)

            if src_x2 > src_x1 and src_y2 > src_y1:
                result[dst_y1:dst_y2, dst_x1:dst_x2] = frame[
                    src_y1:src_y2, src_x1:src_x2
                ]

            return result

        return clip.transform(slide_in_frame)


class SlideOutEffect(EffectStrategy):
    """スライドアウトエフェクト（カスタム実装）"""

    def apply(
        self,
        clip: VideoClip | ImageClip,
        effect: AnimationEffect,
        video_size: tuple[int, int],
    ) -> VideoClip | ImageClip:
        """スライドアウトを適用"""
        direction = effect.direction or "left"
        easing_fn = get_easing_function(effect.easing)
        video_w, video_h = video_size

        def slide_out_frame(get_frame, t):
            frame = get_frame(t)
            # クリップの最後のduration秒間のみアニメーション
            time_from_end = clip.duration - t
            if time_from_end > effect.duration:
                # アニメーション開始前は元のフレームを中央配置
                h, w = frame.shape[:2]
                result = np.zeros(
                    (
                        (video_h, video_w, frame.shape[2])
                        if len(frame.shape) == 3
                        else (video_h, video_w)
                    ),
                    dtype=frame.dtype,
                )
                y_offset = (video_h - h) // 2
                x_offset = (video_w - w) // 2
                result[y_offset : y_offset + h, x_offset : x_offset + w] = frame
                return result

            progress = 1 - min(time_from_end / effect.duration, 1.0)
            eased_progress = easing_fn(progress)

            h, w = frame.shape[:2]
            result = np.zeros(
                (
                    (video_h, video_w, frame.shape[2])
                    if len(frame.shape) == 3
                    else (video_h, video_w)
                ),
                dtype=frame.dtype,
            )

            # 開始位置（中央）
            start_y = (video_h - h) // 2
            start_x = (video_w - w) // 2

            if direction == "left":
                # 左へスライドアウト（中央 → 画面外左）
                x_pos = int(start_x - video_w * eased_progress)
                y_pos = start_y
            elif direction == "right":
                # 右へスライドアウト（中央 → 画面外右）
                x_pos = int(start_x + video_w * eased_progress)
                y_pos = start_y
            elif direction == "top":
                # 上へスライドアウト（中央 → 画面外上）
                x_pos = start_x
                y_pos = int(start_y - video_h * eased_progress)
            elif direction == "bottom":
                # 下へスライドアウト（中央 → 画面外下）
                x_pos = start_x
                y_pos = int(start_y + video_h * eased_progress)
            else:
                x_pos = start_x
                y_pos = start_y

            # フレームを配置（はみ出し部分は切り取る）
            src_x1 = max(0, -x_pos)
            src_y1 = max(0, -y_pos)
            src_x2 = min(w, video_w - x_pos)
            src_y2 = min(h, video_h - y_pos)

            dst_x1 = max(0, x_pos)
            dst_y1 = max(0, y_pos)
            dst_x2 = dst_x1 + (src_x2 - src_x1)
            dst_y2 = dst_y1 + (src_y2 - src_y1)

            if src_x2 > src_x1 and src_y2 > src_y1:
                result[dst_y1:dst_y2, dst_x1:dst_x2] = frame[
                    src_y1:src_y2, src_x1:src_x2
                ]

            return result

        return clip.transform(slide_out_frame)
