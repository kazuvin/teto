"""TTS (Text-to-Speech) domain - TTS models, builders, and processors"""

from .models import (
    ElevenLabsVoiceConfig,
    GeminiTTSVoiceConfig,
    GoogleTTSVoiceConfig,
    GoogleTTSAudioConfig,
    TTSRequest,
    TTSResult,
    TTSSegment,
)
from .builders import TTSBuilder
from .google_tts import GoogleTTSClient
from .elevenlabs_tts import ElevenLabsTTSClient
from .gemini_tts import GeminiTTSClient

__all__ = [
    "ElevenLabsVoiceConfig",
    "ElevenLabsTTSClient",
    "GeminiTTSVoiceConfig",
    "GeminiTTSClient",
    "GoogleTTSVoiceConfig",
    "GoogleTTSAudioConfig",
    "TTSRequest",
    "TTSResult",
    "TTSSegment",
    "TTSBuilder",
    "GoogleTTSClient",
]
