"""Effect presets - Animation effect configurations for scenes"""

from .base import EffectPreset
from .registry import EffectPresetRegistry
from .default import DefaultEffectPreset
from .dramatic import DramaticEffectPreset
from .slideshow import SlideshowEffectPreset
from .kenburns import (
    KenBurnsLeftToRightPreset,
    KenBurnsRightToLeftPreset,
    KenBurnsTopToBottomPreset,
    KenBurnsBottomToTopPreset,
    KenBurnsZoomInPreset,
    KenBurnsZoomOutPreset,
    KenBurnsDiagonalLeftTopPreset,
    KenBurnsDiagonalRightTopPreset,
)

# 後方互換性のためのエイリアス（presets/ からの移行）
ScenePreset = EffectPreset
ScenePresetRegistry = EffectPresetRegistry
DefaultScenePreset = DefaultEffectPreset
DramaticScenePreset = DramaticEffectPreset
SlideshowScenePreset = SlideshowEffectPreset

# さらに古いエイリアス
LayerPreset = EffectPreset
LayerPresetRegistry = EffectPresetRegistry
DefaultLayerPreset = DefaultEffectPreset
DramaticPreset = DramaticEffectPreset
SlideshowPreset = SlideshowEffectPreset

__all__ = [
    # 新しい名前（エフェクトプリセット）
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
    "DefaultScenePreset",
    "DramaticScenePreset",
    "SlideshowScenePreset",
    "LayerPreset",
    "LayerPresetRegistry",
    "DefaultLayerPreset",
    "DramaticPreset",
    "SlideshowPreset",
]
