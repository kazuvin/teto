"""TTS (Text-to-Speech) domain - TTS models, builders, and processors"""

from .models import (
    ElevenLabsVoiceConfig,
    GoogleTTSVoiceConfig,
    GoogleTTSAudioConfig,
    TTSRequest,
    TTSResult,
    TTSSegment,
)
from .builders import TTSBuilder
from .google_tts import GoogleTTSClient
from .elevenlabs_tts import ElevenLabsTTSClient

__all__ = [
    "ElevenLabsVoiceConfig",
    "ElevenLabsTTSClient",
    "GoogleTTSVoiceConfig",
    "GoogleTTSAudioConfig",
    "TTSRequest",
    "TTSResult",
    "TTSSegment",
    "TTSBuilder",
    "GoogleTTSClient",
]
