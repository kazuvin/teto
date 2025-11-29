"""アニメーション処理プロセッサー"""

import numpy as np
from moviepy import VideoClip, ImageClip, vfx
from scipy.ndimage import gaussian_filter
from ..models.effects import AnimationEffect


class AnimationProcessor:
    """アニメーション処理を担当するプロセッサー"""

    @staticmethod
    def apply_effects(clip: VideoClip | ImageClip, effects: list[AnimationEffect], video_size: tuple[int, int]) -> VideoClip | ImageClip:
        """
        クリップにアニメーション効果を適用

        Args:
            clip: 元のクリップ
            effects: 適用する効果のリスト
            video_size: 動画サイズ（スライド計算用）

        Returns:
            効果を適用したクリップ
        """
        for effect in effects:
            if effect.type == "fadein":
                clip = AnimationProcessor._apply_fadein(clip, effect)
            elif effect.type == "fadeout":
                clip = AnimationProcessor._apply_fadeout(clip, effect)
            elif effect.type == "slideIn":
                clip = AnimationProcessor._apply_slide_in(clip, effect, video_size)
            elif effect.type == "slideOut":
                clip = AnimationProcessor._apply_slide_out(clip, effect, video_size)
            elif effect.type == "zoom":
                clip = AnimationProcessor._apply_zoom(clip, effect)
            elif effect.type == "kenBurns":
                clip = AnimationProcessor._apply_ken_burns(clip, effect)
            elif effect.type == "blur":
                clip = AnimationProcessor._apply_blur(clip, effect)
            elif effect.type == "colorGrade":
                clip = AnimationProcessor._apply_color_grade(clip, effect)
            elif effect.type == "vignette":
                clip = AnimationProcessor._apply_vignette(clip, effect)
            elif effect.type == "glitch":
                clip = AnimationProcessor._apply_glitch(clip, effect)
            elif effect.type == "parallax":
                clip = AnimationProcessor._apply_parallax(clip, effect)
            elif effect.type == "bounce":
                clip = AnimationProcessor._apply_bounce(clip, effect)
            elif effect.type == "rotate":
                clip = AnimationProcessor._apply_rotate(clip, effect)

        return clip

    @staticmethod
    def _get_easing_function(easing: str | None):
        """イージング関数を取得"""
        if easing == "easeIn":
            return lambda t: t * t
        elif easing == "easeOut":
            return lambda t: t * (2 - t)
        elif easing == "easeInOut":
            return lambda t: t * t * (3 - 2 * t)
        else:  # linear
            return lambda t: t

    @staticmethod
    def _apply_fadein(clip: VideoClip | ImageClip, effect: AnimationEffect) -> VideoClip | ImageClip:
        """フェードイン効果（moviepy の vfx を使用）"""
        return clip.with_effects([vfx.FadeIn(duration=effect.duration)])

    @staticmethod
    def _apply_fadeout(clip: VideoClip | ImageClip, effect: AnimationEffect) -> VideoClip | ImageClip:
        """フェードアウト効果（moviepy の vfx を使用）"""
        return clip.with_effects([vfx.FadeOut(duration=effect.duration)])

    @staticmethod
    def _apply_slide_in(
        clip: VideoClip | ImageClip, effect: AnimationEffect, video_size: tuple[int, int]
    ) -> VideoClip | ImageClip:
        """スライドイン効果（カスタム実装）"""
        direction = effect.direction or "left"
        easing_fn = AnimationProcessor._get_easing_function(effect.easing)
        video_w, video_h = video_size

        def slide_in_frame(get_frame, t):
            frame = get_frame(t)
            # duration内のみアニメーション
            if t > effect.duration:
                # アニメーション完了後は元のフレームを返す
                h, w = frame.shape[:2]
                result = np.zeros((video_h, video_w, frame.shape[2]) if len(frame.shape) == 3 else (video_h, video_w), dtype=frame.dtype)
                # 中央配置
                y_offset = (video_h - h) // 2
                x_offset = (video_w - w) // 2
                result[y_offset:y_offset+h, x_offset:x_offset+w] = frame
                return result

            progress = min(t / effect.duration, 1.0)
            eased_progress = easing_fn(progress)

            h, w = frame.shape[:2]
            result = np.zeros((video_h, video_w, frame.shape[2]) if len(frame.shape) == 3 else (video_h, video_w), dtype=frame.dtype)

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
                result[dst_y1:dst_y2, dst_x1:dst_x2] = frame[src_y1:src_y2, src_x1:src_x2]

            return result

        return clip.transform(slide_in_frame)

    @staticmethod
    def _apply_slide_out(
        clip: VideoClip | ImageClip, effect: AnimationEffect, video_size: tuple[int, int]
    ) -> VideoClip | ImageClip:
        """スライドアウト効果（カスタム実装）"""
        direction = effect.direction or "left"
        easing_fn = AnimationProcessor._get_easing_function(effect.easing)
        video_w, video_h = video_size

        def slide_out_frame(get_frame, t):
            frame = get_frame(t)
            # クリップの最後のduration秒間のみアニメーション
            time_from_end = clip.duration - t
            if time_from_end > effect.duration:
                # アニメーション開始前は元のフレームを中央配置
                h, w = frame.shape[:2]
                result = np.zeros((video_h, video_w, frame.shape[2]) if len(frame.shape) == 3 else (video_h, video_w), dtype=frame.dtype)
                y_offset = (video_h - h) // 2
                x_offset = (video_w - w) // 2
                result[y_offset:y_offset+h, x_offset:x_offset+w] = frame
                return result

            progress = 1 - min(time_from_end / effect.duration, 1.0)
            eased_progress = easing_fn(progress)

            h, w = frame.shape[:2]
            result = np.zeros((video_h, video_w, frame.shape[2]) if len(frame.shape) == 3 else (video_h, video_w), dtype=frame.dtype)

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
                result[dst_y1:dst_y2, dst_x1:dst_x2] = frame[src_y1:src_y2, src_x1:src_x2]

            return result

        return clip.transform(slide_out_frame)

    @staticmethod
    def _apply_zoom(clip: VideoClip | ImageClip, effect: AnimationEffect) -> VideoClip | ImageClip:
        """スムーズズーム効果（イージング付き）"""
        start_scale = effect.start_scale or 1.0
        end_scale = effect.end_scale or 1.2
        easing_fn = AnimationProcessor._get_easing_function(effect.easing)

        def zoom_frame(get_frame, t):
            frame = get_frame(t)
            progress = min(t / clip.duration, 1.0) if clip.duration > 0 else 0
            eased_progress = easing_fn(progress)

            current_scale = start_scale + (end_scale - start_scale) * eased_progress

            h, w = frame.shape[:2]
            new_h, new_w = int(h * current_scale), int(w * current_scale)

            from scipy.ndimage import zoom as scipy_zoom
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
                result = np.zeros_like(frame)
                y_offset = (h - zh) // 2
                x_offset = (w - zw) // 2
                result[y_offset:y_offset + zh, x_offset:x_offset + zw] = zoomed
                return result

        return clip.transform(zoom_frame)

    @staticmethod
    def _apply_ken_burns(clip: VideoClip | ImageClip, effect: AnimationEffect) -> VideoClip | ImageClip:
        """Ken Burns効果（パン＋ズーム）"""
        start_scale = effect.start_scale or 1.0
        end_scale = effect.end_scale or 1.3
        pan_start = effect.pan_start or (0.0, 0.0)
        pan_end = effect.pan_end or (0.1, 0.1)
        easing_fn = AnimationProcessor._get_easing_function(effect.easing)

        def ken_burns_frame(get_frame, t):
            frame = get_frame(t)
            progress = min(t / clip.duration, 1.0) if clip.duration > 0 else 0
            eased_progress = easing_fn(progress)

            current_scale = start_scale + (end_scale - start_scale) * eased_progress
            pan_x = pan_start[0] + (pan_end[0] - pan_start[0]) * eased_progress
            pan_y = pan_start[1] + (pan_end[1] - pan_start[1]) * eased_progress

            h, w = frame.shape[:2]

            from scipy.ndimage import zoom as scipy_zoom
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

    @staticmethod
    def _apply_blur(clip: VideoClip | ImageClip, effect: AnimationEffect) -> VideoClip | ImageClip:
        """ブラー効果（被写界深度風）"""
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

    @staticmethod
    def _apply_color_grade(clip: VideoClip | ImageClip, effect: AnimationEffect) -> VideoClip | ImageClip:
        """シネマティックなカラーグレーディング"""
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

    @staticmethod
    def _apply_vignette(clip: VideoClip | ImageClip, effect: AnimationEffect) -> VideoClip | ImageClip:
        """ビネット効果（周辺減光）"""
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

    @staticmethod
    def _apply_glitch(clip: VideoClip | ImageClip, effect: AnimationEffect) -> VideoClip | ImageClip:
        """デジタルグリッチ効果"""
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

    @staticmethod
    def _apply_parallax(clip: VideoClip | ImageClip, effect: AnimationEffect) -> VideoClip | ImageClip:
        """パララックス効果（立体的な動き）"""
        direction = effect.direction or "right"
        easing_fn = AnimationProcessor._get_easing_function(effect.easing)

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
                result[:, shift_x:] = frame[:, :w - shift_x]
            elif shift_x < 0:
                result[:, :w + shift_x] = frame[:, -shift_x:]
            else:
                result = frame

            return result

        return clip.transform(parallax_frame)

    @staticmethod
    def _apply_bounce(clip: VideoClip | ImageClip, effect: AnimationEffect) -> VideoClip | ImageClip:
        """バウンス効果（弾むような動き）"""
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
                    result[offset:] = frame[:h - offset]
            elif direction == "top":
                offset = int(h * 0.3 * (1 - bounce_curve))
                if offset < h:
                    result[:h - offset] = frame[offset:]

            return result

        return clip.transform(bounce_frame)

    @staticmethod
    def _apply_rotate(clip: VideoClip | ImageClip, effect: AnimationEffect) -> VideoClip | ImageClip:
        """回転効果"""
        rotation_angle = effect.rotation_angle or 360
        easing_fn = AnimationProcessor._get_easing_function(effect.easing)

        def rotate_frame(get_frame, t):
            frame = get_frame(t)
            progress = min(t / clip.duration, 1.0) if clip.duration > 0 else 0
            eased_progress = easing_fn(progress)

            angle = rotation_angle * eased_progress
            from scipy.ndimage import rotate
            return rotate(frame, angle, reshape=False, order=1)

        return clip.transform(rotate_frame)
