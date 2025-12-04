"""TTS キャッシュマネージャー（後方互換性のためのラッパー）

NOTE: このモジュールは後方互換性のために残されています。
新しいコードでは teto_core.cache モジュールを直接使用してください。
"""

# 新しいキャッシュモジュールから再エクスポート
from ..cache.base import CacheInfo
from ..cache.tts import (
    TTSCacheManager,
    get_tts_cache_manager as get_cache_manager,
    clear_tts_cache as clear_cache,
    get_tts_cache_info as get_cache_info,
)

# 後方互換性のためのデフォルトキャッシュディレクトリ
from ..cache.base import DEFAULT_BASE_CACHE_DIR

DEFAULT_CACHE_DIR = DEFAULT_BASE_CACHE_DIR / "tts"

__all__ = [
    "CacheInfo",
    "TTSCacheManager",
    "get_cache_manager",
    "clear_cache",
    "get_cache_info",
    "DEFAULT_CACHE_DIR",
]
