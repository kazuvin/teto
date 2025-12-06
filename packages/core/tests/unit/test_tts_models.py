"""Tests for TTS models module."""

import pytest
from pathlib import Path
from pydantic import ValidationError

from teto_core.tts.models import (
    ElevenLabsVoiceConfig,
    GeminiTTSVoiceConfig,
    GoogleTTSVoiceConfig,
    GoogleTTSAudioConfig,
    TTSRequest,
    TTSResult,
    TTSSegment,
)


@pytest.mark.unit
class TestElevenLabsVoiceConfig:
    """Test suite for ElevenLabsVoiceConfig."""

    def test_default_values(self):
        """Test default values."""
        config = ElevenLabsVoiceConfig()
        assert config.voice_id == "JBFqnCBsd6RMkjVDRZzb"
        assert config.model_id == "eleven_multilingual_v2"
        assert config.output_format == "mp3_44100_128"

    def test_custom_values(self):
        """Test custom values."""
        config = ElevenLabsVoiceConfig(
            voice_id="custom_voice",
            model_id="eleven_turbo_v2_5",
            output_format="pcm_22050",
        )
        assert config.voice_id == "custom_voice"
        assert config.model_id == "eleven_turbo_v2_5"
        assert config.output_format == "pcm_22050"


@pytest.mark.unit
class TestGeminiTTSVoiceConfig:
    """Test suite for GeminiTTSVoiceConfig."""

    def test_default_values(self):
        """Test default values."""
        config = GeminiTTSVoiceConfig()
        assert config.voice_name == "Kore"
        assert config.model_id == "gemini-2.5-flash-preview-tts"
        assert config.style_prompt is None

    def test_custom_values(self):
        """Test custom values."""
        config = GeminiTTSVoiceConfig(
            voice_name="Puck",
            model_id="gemini-pro-tts",
            style_prompt="Speak cheerfully",
        )
        assert config.voice_name == "Puck"
        assert config.model_id == "gemini-pro-tts"
        assert config.style_prompt == "Speak cheerfully"


@pytest.mark.unit
class TestGoogleTTSVoiceConfig:
    """Test suite for GoogleTTSVoiceConfig."""

    def test_default_values(self):
        """Test default values."""
        config = GoogleTTSVoiceConfig()
        assert config.language_code == "ja-JP"
        assert config.voice_name == "ja-JP-Wavenet-A"
        assert config.ssml_gender == "FEMALE"

    def test_custom_values(self):
        """Test custom values."""
        config = GoogleTTSVoiceConfig(
            language_code="en-US",
            voice_name="en-US-Neural2-A",
            ssml_gender="MALE",
        )
        assert config.language_code == "en-US"
        assert config.voice_name == "en-US-Neural2-A"
        assert config.ssml_gender == "MALE"

    def test_ssml_gender_validation(self):
        """Test ssml_gender accepts valid values."""
        for gender in ["NEUTRAL", "MALE", "FEMALE"]:
            config = GoogleTTSVoiceConfig(ssml_gender=gender)
            assert config.ssml_gender == gender


@pytest.mark.unit
class TestGoogleTTSAudioConfig:
    """Test suite for GoogleTTSAudioConfig."""

    def test_default_values(self):
        """Test default values."""
        config = GoogleTTSAudioConfig()
        assert config.audio_encoding == "MP3"
        assert config.speaking_rate == 1.0
        assert config.pitch == 0.0
        assert config.volume_gain_db == 0.0
        assert config.sample_rate_hertz == 24000
        assert config.effects_profile_id == []

    def test_speaking_rate_valid_range(self):
        """Test speaking_rate accepts valid range."""
        config = GoogleTTSAudioConfig(speaking_rate=0.25)
        assert config.speaking_rate == 0.25

        config = GoogleTTSAudioConfig(speaking_rate=4.0)
        assert config.speaking_rate == 4.0

    def test_speaking_rate_invalid_range(self):
        """Test speaking_rate rejects invalid range."""
        with pytest.raises(ValidationError):
            GoogleTTSAudioConfig(speaking_rate=0.1)

        with pytest.raises(ValidationError):
            GoogleTTSAudioConfig(speaking_rate=5.0)

    def test_pitch_valid_range(self):
        """Test pitch accepts valid range."""
        config = GoogleTTSAudioConfig(pitch=-20.0)
        assert config.pitch == -20.0

        config = GoogleTTSAudioConfig(pitch=20.0)
        assert config.pitch == 20.0

    def test_pitch_invalid_range(self):
        """Test pitch rejects invalid range."""
        with pytest.raises(ValidationError):
            GoogleTTSAudioConfig(pitch=-25.0)

        with pytest.raises(ValidationError):
            GoogleTTSAudioConfig(pitch=25.0)

    def test_volume_gain_db_valid_range(self):
        """Test volume_gain_db accepts valid range."""
        config = GoogleTTSAudioConfig(volume_gain_db=-96.0)
        assert config.volume_gain_db == -96.0

        config = GoogleTTSAudioConfig(volume_gain_db=16.0)
        assert config.volume_gain_db == 16.0

    def test_audio_encoding_options(self):
        """Test audio_encoding accepts valid options."""
        for encoding in ["MP3", "LINEAR16", "OGG_OPUS"]:
            config = GoogleTTSAudioConfig(audio_encoding=encoding)
            assert config.audio_encoding == encoding

    def test_effects_profile_id(self):
        """Test effects_profile_id accepts list."""
        config = GoogleTTSAudioConfig(
            effects_profile_id=["headphone-class-device", "wearable-class-device"]
        )
        assert len(config.effects_profile_id) == 2


@pytest.mark.unit
class TestTTSRequest:
    """Test suite for TTSRequest."""

    def test_minimal_request(self):
        """Test minimal request with just text."""
        request = TTSRequest(text="Hello, World!")
        assert request.text == "Hello, World!"
        assert request.output_path is None
        assert request.use_ssml is False

    def test_text_with_whitespace_is_stripped(self):
        """Test text with whitespace is stripped."""
        request = TTSRequest(text="  Hello  ")
        assert request.text == "Hello"

    def test_empty_text_raises_error(self):
        """Test empty text raises error."""
        with pytest.raises(ValidationError):
            TTSRequest(text="")

    def test_whitespace_only_text_raises_error(self):
        """Test whitespace-only text raises error."""
        with pytest.raises(ValidationError):
            TTSRequest(text="   ")

    def test_text_max_length(self):
        """Test text max length."""
        # Should work with 5000 characters
        long_text = "a" * 5000
        request = TTSRequest(text=long_text)
        assert len(request.text) == 5000

        # Should fail with 5001 characters
        with pytest.raises(ValidationError):
            TTSRequest(text="a" * 5001)

    def test_with_output_path(self):
        """Test request with output path."""
        request = TTSRequest(text="Hello", output_path=Path("/tmp/audio.mp3"))
        assert request.output_path == Path("/tmp/audio.mp3")

    def test_with_ssml(self):
        """Test request with SSML."""
        request = TTSRequest(
            text="<speak>Hello</speak>",
            use_ssml=True,
        )
        assert request.use_ssml is True

    def test_with_voice_config(self):
        """Test request with custom voice config."""
        voice_config = GoogleTTSVoiceConfig(voice_name="en-US-Wavenet-B")
        request = TTSRequest(text="Hello", voice_config=voice_config)
        assert request.voice_config.voice_name == "en-US-Wavenet-B"

    def test_with_audio_config(self):
        """Test request with custom audio config."""
        audio_config = GoogleTTSAudioConfig(speaking_rate=1.5, pitch=2.0)
        request = TTSRequest(text="Hello", audio_config=audio_config)
        assert request.audio_config.speaking_rate == 1.5
        assert request.audio_config.pitch == 2.0


@pytest.mark.unit
class TestTTSResult:
    """Test suite for TTSResult."""

    def test_create_result(self):
        """Test creating a result."""
        result = TTSResult(
            audio_path=Path("/tmp/audio.mp3"),
            duration_seconds=5.5,
            text="Hello, World!",
            voice_config=GoogleTTSVoiceConfig(),
            audio_config=GoogleTTSAudioConfig(),
            character_count=13,
            estimated_cost_usd=0.0052,
        )
        assert result.audio_path == Path("/tmp/audio.mp3")
        assert result.duration_seconds == 5.5
        assert result.text == "Hello, World!"
        assert result.character_count == 13
        assert result.estimated_cost_usd == 0.0052


@pytest.mark.unit
class TestTTSSegment:
    """Test suite for TTSSegment."""

    def test_create_segment(self):
        """Test creating a segment."""
        segment = TTSSegment(
            text="Hello",
            start_time=0.0,
            end_time=1.5,
        )
        assert segment.text == "Hello"
        assert segment.start_time == 0.0
        assert segment.end_time == 1.5
        assert segment.audio_path is None

    def test_segment_with_audio_path(self):
        """Test segment with audio path."""
        segment = TTSSegment(
            text="Hello",
            start_time=0.0,
            end_time=1.5,
            audio_path=Path("/tmp/segment.mp3"),
        )
        assert segment.audio_path == Path("/tmp/segment.mp3")
