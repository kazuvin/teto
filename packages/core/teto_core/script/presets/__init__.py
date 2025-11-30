"""Layer presets - Style configurations for video generation"""

from .base import LayerPreset, SubtitleStyleConfig
from .registry import LayerPresetRegistry
from .default import DefaultLayerPreset
from .bold_subtitle import BoldSubtitlePreset
from .minimal import MinimalPreset
from .vertical import VerticalPreset

__all__ = [
    "LayerPreset",
    "SubtitleStyleConfig",
    "LayerPresetRegistry",
    "DefaultLayerPreset",
    "BoldSubtitlePreset",
    "MinimalPreset",
    "VerticalPreset",
]
