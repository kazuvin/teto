"""TTS (Text-to-Speech) domain - TTS models, builders, and processors"""

from .models import (
    GoogleTTSVoiceConfig,
    GoogleTTSAudioConfig,
    TTSRequest,
    TTSResult,
    TTSSegment,
)
from .builders import TTSBuilder
from .google_tts import GoogleTTSClient

__all__ = [
    "GoogleTTSVoiceConfig",
    "GoogleTTSAudioConfig",
    "TTSRequest",
    "TTSResult",
    "TTSSegment",
    "TTSBuilder",
    "GoogleTTSClient",
]
