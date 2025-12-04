"""Script providers - Strategy implementations for TTS and Asset resolution"""

from .tts import (
    TTSProvider,
    TTSResult,
    GoogleTTSProvider,
    ElevenLabsTTSProvider,
    GeminiTTSProvider,
    MockTTSProvider,
)
from .assets import (
    AssetResolver,
    LocalAssetResolver,
    AIImageResolver,
    CompositeAssetResolver,
)

__all__ = [
    "TTSProvider",
    "TTSResult",
    "GoogleTTSProvider",
    "ElevenLabsTTSProvider",
    "GeminiTTSProvider",
    "MockTTSProvider",
    "AssetResolver",
    "LocalAssetResolver",
    "AIImageResolver",
    "CompositeAssetResolver",
]
