"""Scene presets - Style configurations for video generation"""

from .base import ScenePreset, LayerPreset, SubtitleStyleConfig
from .registry import ScenePresetRegistry, LayerPresetRegistry
from .default import DefaultScenePreset, DefaultLayerPreset
from .dramatic import DramaticScenePreset, DramaticPreset
from .slideshow import SlideshowScenePreset, SlideshowPreset
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
from .composite import PresetConfig, PresetRegistry

# library は遅延インポートする（循環インポート回避）

__all__ = [
    # 新しい名前（エフェクトプリセット）
    "ScenePreset",
    "ScenePresetRegistry",
    "DefaultScenePreset",
    "DramaticScenePreset",
    "SlideshowScenePreset",
    # Ken Burns プリセット
    "KenBurnsLeftToRightPreset",
    "KenBurnsRightToLeftPreset",
    "KenBurnsTopToBottomPreset",
    "KenBurnsBottomToTopPreset",
    "KenBurnsZoomInPreset",
    "KenBurnsZoomOutPreset",
    "KenBurnsDiagonalLeftTopPreset",
    "KenBurnsDiagonalRightTopPreset",
    # 複合プリセット
    "PresetConfig",
    "PresetRegistry",
    # 後方互換性のためのエイリアス
    "LayerPreset",
    "LayerPresetRegistry",
    "DefaultLayerPreset",
    "DramaticPreset",
    "SlideshowPreset",
    # 共通
    "SubtitleStyleConfig",
]
