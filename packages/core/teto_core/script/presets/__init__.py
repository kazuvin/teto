"""Scene presets - Style configurations for video generation"""

from .base import ScenePreset, LayerPreset, SubtitleStyleConfig
from .registry import ScenePresetRegistry, LayerPresetRegistry
from .default import DefaultScenePreset, DefaultLayerPreset
from .dramatic import DramaticScenePreset, DramaticPreset
from .slideshow import SlideshowScenePreset, SlideshowPreset

__all__ = [
    # 新しい名前
    "ScenePreset",
    "ScenePresetRegistry",
    "DefaultScenePreset",
    "DramaticScenePreset",
    "SlideshowScenePreset",
    # 後方互換性のためのエイリアス
    "LayerPreset",
    "LayerPresetRegistry",
    "DefaultLayerPreset",
    "DramaticPreset",
    "SlideshowPreset",
    # 共通
    "SubtitleStyleConfig",
]
