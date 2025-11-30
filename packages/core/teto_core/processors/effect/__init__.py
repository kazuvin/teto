"""エフェクト処理モジュール

MoviePy のエフェクトシステムを拡張した、柔軟で拡張可能なエフェクトプロセッサー。
Strategy パターンにより、カスタムエフェクトの追加が容易。
"""

from .processor import EffectProcessor, AnimationProcessor
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

__all__ = [
    # Main processor
    "EffectProcessor",
    "AnimationProcessor",  # 後方互換性のため
    # Base class
    "EffectStrategy",
    # Effect strategies
    "FadeInEffect",
    "FadeOutEffect",
    "SlideInEffect",
    "SlideOutEffect",
    "ZoomEffect",
    "KenBurnsEffect",
    "BlurEffect",
    "ColorGradeEffect",
    "VignetteEffect",
    "GlitchEffect",
    "ParallaxEffect",
    "BounceEffect",
    "RotateEffect",
]
