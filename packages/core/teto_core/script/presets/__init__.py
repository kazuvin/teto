"""Composite presets - Scene-level style configurations (subtitle, timing, etc.)

Note:
    エフェクトプリセット（アニメーション設定）は effects/ モジュールを使用してください。
    このモジュールは複合プリセット（字幕スタイル、タイミング等の一括設定）を提供します。
"""

from .base import SubtitleStyleConfig
from .composite import PresetConfig, PresetRegistry

# library は遅延インポートする（循環インポート回避）

# 後方互換性のためのエイリアス（effects/ からも再エクスポート）
from ..effects import (
    # エフェクトプリセット基底クラス
    EffectPreset,
    EffectPresetRegistry,
    # 後方互換性のためのエイリアス
    ScenePreset,
    ScenePresetRegistry,
    LayerPreset,
    LayerPresetRegistry,
    # 具象プリセット
    DefaultEffectPreset,
    DefaultScenePreset,
    DefaultLayerPreset,
    DramaticEffectPreset,
    DramaticScenePreset,
    DramaticPreset,
    SlideshowEffectPreset,
    SlideshowScenePreset,
    SlideshowPreset,
    # Ken Burns プリセット
    KenBurnsLeftToRightPreset,
    KenBurnsRightToLeftPreset,
    KenBurnsTopToBottomPreset,
    KenBurnsBottomToTopPreset,
    KenBurnsZoomInPreset,
    KenBurnsZoomOutPreset,
    KenBurnsDiagonalLeftTopPreset,
    KenBurnsDiagonalRightTopPreset,
)

__all__ = [
    # 複合プリセット（このモジュールの主要機能）
    "PresetConfig",
    "PresetRegistry",
    "SubtitleStyleConfig",
    # エフェクトプリセット（後方互換性のため再エクスポート）
    "EffectPreset",
    "EffectPresetRegistry",
    "DefaultEffectPreset",
    "DramaticEffectPreset",
    "SlideshowEffectPreset",
    # Ken Burns プリセット
    "KenBurnsLeftToRightPreset",
    "KenBurnsRightToLeftPreset",
    "KenBurnsTopToBottomPreset",
    "KenBurnsBottomToTopPreset",
    "KenBurnsZoomInPreset",
    "KenBurnsZoomOutPreset",
    "KenBurnsDiagonalLeftTopPreset",
    "KenBurnsDiagonalRightTopPreset",
    # 後方互換性のためのエイリアス
    "ScenePreset",
    "ScenePresetRegistry",
    "LayerPreset",
    "LayerPresetRegistry",
    "DefaultScenePreset",
    "DefaultLayerPreset",
    "DramaticScenePreset",
    "DramaticPreset",
    "SlideshowScenePreset",
    "SlideshowPreset",
]
