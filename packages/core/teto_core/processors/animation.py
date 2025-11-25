"""アニメーション処理プロセッサー"""

from moviepy import VideoClip, ImageClip, vfx
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

        return clip

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
        """スライドイン効果（moviepy の vfx を使用）"""
        direction = effect.direction or "left"
        # moviepy の SlideIn は side パラメータを使用
        return clip.with_effects([vfx.SlideIn(duration=effect.duration, side=direction)])

    @staticmethod
    def _apply_slide_out(
        clip: VideoClip | ImageClip, effect: AnimationEffect, video_size: tuple[int, int]
    ) -> VideoClip | ImageClip:
        """スライドアウト効果（moviepy の vfx を使用）"""
        direction = effect.direction or "left"
        return clip.with_effects([vfx.SlideOut(duration=effect.duration, side=direction)])

    @staticmethod
    def _apply_zoom(clip: VideoClip | ImageClip, effect: AnimationEffect) -> VideoClip | ImageClip:
        """ズーム効果（Resize vfx を使用）"""
        start_scale = effect.start_scale or 0.8
        end_scale = effect.end_scale or 1.0

        # ズームイン: 小さいサイズから元のサイズへ
        # まず縮小してから元のサイズに戻す
        if start_scale < end_scale:
            # 最初に縮小
            clip = clip.resized(start_scale)
            # アニメーションで拡大（Resize vfx は静的なので、シンプルなフェードで代用）
            # TODO: より高度なズームアニメーションは将来実装

        return clip
