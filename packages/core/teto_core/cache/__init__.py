"""Cache module - Asset caching for TTS, images, and videos"""

from .base import AssetCacheManager, CacheInfo
from .tts import (
    TTSCacheManager,
    get_tts_cache_manager,
    clear_tts_cache,
    get_tts_cache_info,
)
from .image import ImageCacheManager, get_image_cache_manager
from .video import VideoCacheManager, get_video_cache_manager
from .manager import (
    CacheManager,
    get_cache_manager,
    clear_all_cache,
    get_all_cache_info,
)

__all__ = [
    # Base
    "AssetCacheManager",
    "CacheInfo",
    # TTS
    "TTSCacheManager",
    "get_tts_cache_manager",
    "clear_tts_cache",
    "get_tts_cache_info",
    # Image
    "ImageCacheManager",
    "get_image_cache_manager",
    # Video
    "VideoCacheManager",
    "get_video_cache_manager",
    # Unified manager
    "CacheManager",
    "get_cache_manager",
    "clear_all_cache",
    "get_all_cache_info",
]
