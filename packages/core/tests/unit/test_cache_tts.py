"""Tests for TTS cache module."""

import pytest

from teto_core.cache.tts import (
    TTSCacheManager,
    get_tts_cache_manager,
    clear_tts_cache,
    get_tts_cache_info,
)
from teto_core.script.models import VoiceConfig


@pytest.fixture
def voice_config():
    """Create a sample voice config for testing."""
    return VoiceConfig(
        provider="google",
        voice_id="ja-JP-Neural2-B",
        language_code="ja-JP",
        speed=1.0,
        pitch=0.0,
    )


@pytest.fixture
def elevenlabs_voice_config():
    """Create an ElevenLabs voice config for testing."""
    return VoiceConfig(
        provider="elevenlabs",
        voice_id="21m00Tcm4TlvDq8ikWAM",
        language_code="ja-JP",
        speed=1.0,
        pitch=0.0,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )


@pytest.fixture
def gemini_voice_config():
    """Create a Gemini voice config for testing."""
    return VoiceConfig(
        provider="gemini",
        language_code="ja-JP",
        speed=1.0,
        pitch=0.0,
        voice_name="Kore",
        gemini_model_id="gemini-2.5-flash-preview-tts",
        style_prompt="Speak calmly and clearly",
    )


@pytest.mark.unit
class TestTTSCacheManager:
    """Test suite for TTSCacheManager class."""

    def test_asset_type(self, temp_dir):
        """Test that asset type is correctly set."""
        manager = TTSCacheManager(cache_dir=temp_dir)
        assert manager.ASSET_TYPE == "tts"
        assert manager.DEFAULT_CACHE_SUBDIR == "tts"

    def test_compute_cache_key(self, temp_dir, voice_config):
        """Test cache key computation."""
        manager = TTSCacheManager(cache_dir=temp_dir)
        text = "こんにちは、世界"

        key = manager._compute_cache_key(text, voice_config)
        assert isinstance(key, str)
        assert len(key) == 16

    def test_compute_cache_key_consistent(self, temp_dir, voice_config):
        """Test that same text and config produces same key."""
        manager = TTSCacheManager(cache_dir=temp_dir)
        text = "同じテキスト"

        key1 = manager._compute_cache_key(text, voice_config)
        key2 = manager._compute_cache_key(text, voice_config)
        assert key1 == key2

    def test_compute_cache_key_different_for_different_text(
        self, temp_dir, voice_config
    ):
        """Test that different texts produce different keys."""
        manager = TTSCacheManager(cache_dir=temp_dir)

        key1 = manager._compute_cache_key("テキスト1", voice_config)
        key2 = manager._compute_cache_key("テキスト2", voice_config)
        assert key1 != key2

    def test_compute_cache_key_different_for_different_config(self, temp_dir):
        """Test that different configs produce different keys."""
        manager = TTSCacheManager(cache_dir=temp_dir)
        text = "同じテキスト"

        config1 = VoiceConfig(provider="google", speed=1.0)
        config2 = VoiceConfig(provider="google", speed=1.5)

        key1 = manager._compute_cache_key(text, config1)
        key2 = manager._compute_cache_key(text, config2)
        assert key1 != key2

    def test_compute_cache_key_includes_elevenlabs_fields(
        self, temp_dir, elevenlabs_voice_config
    ):
        """Test that ElevenLabs specific fields are included in cache key."""
        manager = TTSCacheManager(cache_dir=temp_dir)
        text = "テスト"

        # Create two configs with different model_id
        config1 = VoiceConfig(
            provider="elevenlabs",
            voice_id="test",
            model_id="eleven_multilingual_v1",
        )
        config2 = VoiceConfig(
            provider="elevenlabs",
            voice_id="test",
            model_id="eleven_multilingual_v2",
        )

        key1 = manager._compute_cache_key(text, config1)
        key2 = manager._compute_cache_key(text, config2)
        assert key1 != key2

    def test_compute_cache_key_includes_gemini_fields(
        self, temp_dir, gemini_voice_config
    ):
        """Test that Gemini specific fields are included in cache key."""
        manager = TTSCacheManager(cache_dir=temp_dir)
        text = "テスト"

        # Create two configs with different voice_name
        config1 = VoiceConfig(
            provider="gemini",
            voice_name="Kore",
        )
        config2 = VoiceConfig(
            provider="gemini",
            voice_name="Aoede",
        )

        key1 = manager._compute_cache_key(text, config1)
        key2 = manager._compute_cache_key(text, config2)
        assert key1 != key2

    def test_put_and_get(self, temp_dir, voice_config):
        """Test putting and getting audio data."""
        manager = TTSCacheManager(cache_dir=temp_dir)
        text = "テスト音声"
        audio_data = b"ID3" + b"\x00" * 100  # Fake MP3 data

        # Put audio
        cache_path = manager.put(text, voice_config, ".mp3", audio_data)
        assert cache_path.exists()
        assert cache_path.suffix == ".mp3"

        # Get audio
        retrieved = manager.get(text, voice_config, ".mp3")
        assert retrieved == audio_data

    def test_put_and_get_wav(self, temp_dir, voice_config):
        """Test putting and getting WAV audio data."""
        manager = TTSCacheManager(cache_dir=temp_dir)
        text = "WAVテスト"
        audio_data = b"RIFF" + b"\x00" * 100  # Fake WAV data

        manager.put(text, voice_config, ".wav", audio_data)
        retrieved = manager.get(text, voice_config, ".wav")
        assert retrieved == audio_data

    def test_get_returns_none_for_missing(self, temp_dir, voice_config):
        """Test that get returns None for missing cache."""
        manager = TTSCacheManager(cache_dir=temp_dir)

        result = manager.get("存在しないテキスト", voice_config, ".mp3")
        assert result is None

    def test_has_exists(self, temp_dir, voice_config):
        """Test has returns True when cache exists."""
        manager = TTSCacheManager(cache_dir=temp_dir)
        text = "存在するテキスト"
        manager.put(text, voice_config, ".mp3", b"audio data")

        assert manager.has(text, voice_config, ".mp3") is True

    def test_has_not_exists(self, temp_dir, voice_config):
        """Test has returns False when cache doesn't exist."""
        manager = TTSCacheManager(cache_dir=temp_dir)

        assert manager.has("存在しない", voice_config, ".mp3") is False

    def test_cache_key_with_unicode_text(self, temp_dir, voice_config):
        """Test cache key generation with various unicode characters."""
        manager = TTSCacheManager(cache_dir=temp_dir)

        # Test with various unicode characters
        texts = [
            "日本語テキスト",
            "中文文本",
            "한국어 텍스트",
            "Emoji 🎉🚀",
            "Mixed 日本語 and English",
        ]

        keys = set()
        for text in texts:
            key = manager._compute_cache_key(text, voice_config)
            keys.add(key)
            assert len(key) == 16

        # All keys should be unique
        assert len(keys) == len(texts)


@pytest.mark.unit
class TestTTSCacheGlobalFunctions:
    """Test suite for global TTS cache functions."""

    def test_get_tts_cache_manager_returns_singleton(self):
        """Test that get_tts_cache_manager returns a singleton."""
        # Reset global state
        import teto_core.cache.tts as tts_module

        tts_module._default_tts_cache_manager = None

        manager1 = get_tts_cache_manager()
        manager2 = get_tts_cache_manager()
        assert manager1 is manager2

    def test_get_tts_cache_info(self):
        """Test get_tts_cache_info function."""
        info = get_tts_cache_info()
        assert info.asset_type == "tts"
