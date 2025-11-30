"""エフェクト処理プロセッサー（Strategy パターン実装）"""

from moviepy import VideoClip, ImageClip
from .models import AnimationEffect
from .strategies import (
    EffectStrategy,
    FadeInEffect,
    FadeOutEffect,
    SlideInEffect,
    SlideOutEffect,
    ZoomEffect,
    KenBurnsEffect,
    BlurEffect,
    ColorGradeEffect,
    VignetteEffect,
    GlitchEffect,
    ParallaxEffect,
    BounceEffect,
    RotateEffect,
)


class EffectProcessor:
    """エフェクト処理を担当するプロセッサー

    Strategy パターンを使用して、各エフェクトを独立したクラスとして実装。
    新しいエフェクトの追加は register_effect() で可能。
    """

    # エフェクト戦略のレジストリ
    _effect_strategies: dict[str, EffectStrategy] = {
        "fadein": FadeInEffect(),
        "fadeout": FadeOutEffect(),
        "slideIn": SlideInEffect(),
        "slideOut": SlideOutEffect(),
        "zoom": ZoomEffect(),
        "kenBurns": KenBurnsEffect(),
        "blur": BlurEffect(),
        "colorGrade": ColorGradeEffect(),
        "vignette": VignetteEffect(),
        "glitch": GlitchEffect(),
        "parallax": ParallaxEffect(),
        "bounce": BounceEffect(),
        "rotate": RotateEffect(),
    }

    @classmethod
    def register_effect(cls, name: str, strategy: EffectStrategy) -> None:
        """カスタムエフェクトを登録

        Args:
            name: エフェクト名
            strategy: エフェクト戦略インスタンス

        Example:
            >>> class CustomEffect(EffectStrategy):
            ...     def apply(self, clip, effect, video_size):
            ...         # カスタム処理
            ...         return clip
            >>> EffectProcessor.register_effect("custom", CustomEffect())
        """
        cls._effect_strategies[name] = strategy

    @classmethod
    def unregister_effect(cls, name: str) -> bool:
        """エフェクトの登録を解除

        Args:
            name: エフェクト名

        Returns:
            解除に成功した場合 True
        """
        if name in cls._effect_strategies:
            del cls._effect_strategies[name]
            return True
        return False

    @classmethod
    def list_effects(cls) -> list[str]:
        """登録されているすべてのエフェクト名を取得

        Returns:
            エフェクト名のリスト
        """
        return list(cls._effect_strategies.keys())

    @staticmethod
    def apply_effects(
        clip: VideoClip | ImageClip,
        effects: list[AnimationEffect],
        video_size: tuple[int, int],
    ) -> VideoClip | ImageClip:
        """クリップにエフェクトを適用

        Args:
            clip: 元のクリップ
            effects: 適用する効果のリスト
            video_size: 動画サイズ（スライド計算用）

        Returns:
            効果を適用したクリップ
        """
        for effect in effects:
            strategy = EffectProcessor._effect_strategies.get(effect.type)
            if strategy:
                clip = strategy.apply(clip, effect, video_size)
            else:
                print(f"Warning: Unknown effect type '{effect.type}'. Skipping.")

        return clip
