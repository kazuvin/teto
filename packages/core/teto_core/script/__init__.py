"""Script module - Script to Project conversion"""

from .models import (
    Script,
    Scene,
    NarrationSegment,
    Visual,
    AssetType,
    TimingConfig,
    BGMConfig,
    VoiceConfig,
    SoundEffect,
)
from .compiler import (
    ScriptCompiler,
    CompileResult,
    CompileMetadata,
    SceneTiming,
    SegmentTiming,
)
from .builders import (
    ScriptBuilder,
    SceneBuilder,
    NarrationSegmentBuilder,
)
from .cache import (
    TTSCacheManager,
    CacheInfo,
    get_cache_manager,
    clear_cache,
    get_cache_info,
)

__all__ = [
    # Models
    "Script",
    "Scene",
    "NarrationSegment",
    "Visual",
    "AssetType",
    "TimingConfig",
    "BGMConfig",
    "VoiceConfig",
    "SoundEffect",
    # Compiler
    "ScriptCompiler",
    "CompileResult",
    "CompileMetadata",
    "SceneTiming",
    "SegmentTiming",
    # Builders
    "ScriptBuilder",
    "SceneBuilder",
    "NarrationSegmentBuilder",
    # Cache
    "TTSCacheManager",
    "CacheInfo",
    "get_cache_manager",
    "clear_cache",
    "get_cache_info",
]
