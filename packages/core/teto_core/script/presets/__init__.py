"""Scene presets - Style configurations for video generation"""

from .base import ScenePreset, LayerPreset, SubtitleStyleConfig
from .registry import ScenePresetRegistry, LayerPresetRegistry
from .default import DefaultScenePreset, DefaultLayerPreset
from .bold_subtitle import BoldSubtitleScenePreset, BoldSubtitlePreset
from .minimal import MinimalScenePreset, MinimalPreset
from .vertical import VerticalScenePreset, VerticalPreset

__all__ = [
    # 新しい名前
    "ScenePreset",
    "ScenePresetRegistry",
    "DefaultScenePreset",
    "BoldSubtitleScenePreset",
    "MinimalScenePreset",
    "VerticalScenePreset",
    # 後方互換性のためのエイリアス
    "LayerPreset",
    "LayerPresetRegistry",
    "DefaultLayerPreset",
    "BoldSubtitlePreset",
    "MinimalPreset",
    "VerticalPreset",
    # 共通
    "SubtitleStyleConfig",
]
