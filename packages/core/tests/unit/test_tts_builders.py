"""Tests for TTS builders module."""

import pytest
from pathlib import Path

from teto_core.tts.builders import TTSBuilder
from teto_core.tts.models import TTSRequest


@pytest.mark.unit
class TestTTSBuilder:
    """Test suite for TTSBuilder."""

    def test_builder_requires_text(self):
        """Test that build fails without text."""
        builder = TTSBuilder()
        with pytest.raises(ValueError, match="Text is required"):
            builder.build()

    def test_minimal_build(self):
        """Test minimal build with just text."""
        request = TTSBuilder().text("Hello, World!").build()

        assert isinstance(request, TTSRequest)
        assert request.text == "Hello, World!"

    def test_builder_text(self):
        """Test setting text."""
        builder = TTSBuilder().text("Test text")
        request = builder.build()
        assert request.text == "Test text"

    def test_builder_voice(self):
        """Test setting voice."""
        request = TTSBuilder().text("Hello").voice("en-US-Wavenet-A").build()

        assert request.voice_config.voice_name == "en-US-Wavenet-A"
        assert request.voice_config.language_code == "en-US"

    def test_builder_voice_infers_language_code(self):
        """Test that voice setting infers language code."""
        request = TTSBuilder().text("Hello").voice("ja-JP-Neural2-B").build()

        assert request.voice_config.voice_name == "ja-JP-Neural2-B"
        assert request.voice_config.language_code == "ja-JP"

    def test_builder_voice_without_dash(self):
        """Test voice setting without dash."""
        request = TTSBuilder().text("Hello").voice("custom_voice").build()

        assert request.voice_config.voice_name == "custom_voice"

    def test_builder_language(self):
        """Test setting language."""
        request = TTSBuilder().text("Hello").language("fr-FR").build()

        assert request.voice_config.language_code == "fr-FR"

    def test_builder_speed(self):
        """Test setting speed."""
        request = TTSBuilder().text("Hello").speed(1.5).build()

        assert request.audio_config.speaking_rate == 1.5

    def test_builder_pitch(self):
        """Test setting pitch."""
        request = TTSBuilder().text("Hello").pitch(5.0).build()

        assert request.audio_config.pitch == 5.0

    def test_builder_volume(self):
        """Test setting volume."""
        request = TTSBuilder().text("Hello").volume(3.0).build()

        assert request.audio_config.volume_gain_db == 3.0

    def test_builder_sample_rate(self):
        """Test setting sample rate."""
        request = TTSBuilder().text("Hello").sample_rate(44100).build()

        assert request.audio_config.sample_rate_hertz == 44100

    def test_builder_output_format_mp3(self):
        """Test setting output format to MP3."""
        request = TTSBuilder().text("Hello").output_format("mp3").build()

        assert request.audio_config.audio_encoding == "MP3"

    def test_builder_output_format_wav(self):
        """Test setting output format to WAV."""
        request = TTSBuilder().text("Hello").output_format("wav").build()

        assert request.audio_config.audio_encoding == "LINEAR16"

    def test_builder_output_format_ogg(self):
        """Test setting output format to OGG."""
        request = TTSBuilder().text("Hello").output_format("ogg").build()

        assert request.audio_config.audio_encoding == "OGG_OPUS"

    def test_builder_output_format_unknown(self):
        """Test setting unknown output format defaults to MP3."""
        request = TTSBuilder().text("Hello").output_format("unknown").build()

        assert request.audio_config.audio_encoding == "MP3"

    def test_builder_output_path_string(self):
        """Test setting output path as string."""
        request = TTSBuilder().text("Hello").output_path("/tmp/audio.mp3").build()

        assert request.output_path == Path("/tmp/audio.mp3")

    def test_builder_output_path_path(self):
        """Test setting output path as Path."""
        path = Path("/tmp/audio.mp3")
        request = TTSBuilder().text("Hello").output_path(path).build()

        assert request.output_path == path

    def test_builder_effects_profile(self):
        """Test setting effects profile."""
        request = (
            TTSBuilder()
            .text("Hello")
            .effects_profile(["headphone-class-device"])
            .build()
        )

        assert request.audio_config.effects_profile_id == ["headphone-class-device"]

    def test_builder_ssml_enabled(self):
        """Test enabling SSML."""
        request = TTSBuilder().text("<speak>Hello</speak>").ssml(True).build()

        assert request.use_ssml is True

    def test_builder_ssml_disabled(self):
        """Test disabling SSML."""
        request = TTSBuilder().text("Hello").ssml(False).build()

        assert request.use_ssml is False

    def test_builder_ssml_default_true(self):
        """Test ssml() with no argument defaults to True."""
        request = TTSBuilder().text("<speak>Hello</speak>").ssml().build()

        assert request.use_ssml is True

    def test_builder_chaining(self):
        """Test chaining multiple builder methods."""
        request = (
            TTSBuilder()
            .text("Hello, World!")
            .voice("en-US-Wavenet-B")
            .speed(1.2)
            .pitch(2.0)
            .volume(1.0)
            .sample_rate(22050)
            .output_format("wav")
            .output_path("/tmp/test.wav")
            .effects_profile(["wearable-class-device"])
            .ssml(False)
            .build()
        )

        assert request.text == "Hello, World!"
        assert request.voice_config.voice_name == "en-US-Wavenet-B"
        assert request.voice_config.language_code == "en-US"
        assert request.audio_config.speaking_rate == 1.2
        assert request.audio_config.pitch == 2.0
        assert request.audio_config.volume_gain_db == 1.0
        assert request.audio_config.sample_rate_hertz == 22050
        assert request.audio_config.audio_encoding == "LINEAR16"
        assert request.output_path == Path("/tmp/test.wav")
        assert request.audio_config.effects_profile_id == ["wearable-class-device"]
        assert request.use_ssml is False

    def test_builder_returns_self(self):
        """Test that each builder method returns self for chaining."""
        builder = TTSBuilder()

        assert builder.text("Hello") is builder
        assert builder.voice("ja-JP-Wavenet-A") is builder
        assert builder.language("ja-JP") is builder
        assert builder.speed(1.0) is builder
        assert builder.pitch(0.0) is builder
        assert builder.volume(0.0) is builder
        assert builder.sample_rate(24000) is builder
        assert builder.output_format("mp3") is builder
        assert builder.output_path("/tmp/test.mp3") is builder
        assert builder.effects_profile([]) is builder
        assert builder.ssml(False) is builder

    def test_builder_multiple_builds(self):
        """Test that same builder can build multiple requests."""
        builder = TTSBuilder().text("Hello")

        request1 = builder.build()
        request2 = builder.build()

        assert request1.text == "Hello"
        assert request2.text == "Hello"

    def test_builder_override_values(self):
        """Test that later calls override earlier values."""
        request = TTSBuilder().text("First").text("Second").build()

        assert request.text == "Second"
