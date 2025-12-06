"""Tests for video cache module."""

import pytest

from teto_core.cache.video import (
    VideoGenerationConfig,
    VideoCacheManager,
    get_video_cache_manager,
    get_video_cache_info,
)


@pytest.mark.unit
class TestVideoGenerationConfig:
    """Test suite for VideoGenerationConfig dataclass."""

    def test_default_values(self):
        """Test VideoGenerationConfig with default values."""
        config = VideoGenerationConfig(
            provider="runway",
            model="gen3",
            prompt="a person walking",
        )
        assert config.provider == "runway"
        assert config.model == "gen3"
        assert config.prompt == "a person walking"
        assert config.negative_prompt is None
        assert config.width == 1920
        assert config.height == 1080
        assert config.fps == 24
        assert config.duration == 4.0
        assert config.seed is None
        assert config.style is None
        assert config.motion_bucket_id is None
        assert config.image_ref is None

    def test_custom_values(self):
        """Test VideoGenerationConfig with custom values."""
        config = VideoGenerationConfig(
            provider="pika",
            model="v2",
            prompt="ocean waves",
            negative_prompt="static, still",
            width=1280,
            height=720,
            fps=30,
            duration=5.0,
            seed=42,
            style="cinematic",
            motion_bucket_id=150,
            image_ref="/path/to/image.png",
        )
        assert config.width == 1280
        assert config.height == 720
        assert config.fps == 30
        assert config.duration == 5.0
        assert config.seed == 42
        assert config.motion_bucket_id == 150
        assert config.image_ref == "/path/to/image.png"

    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = VideoGenerationConfig(
            provider="sora",
            model="v1",
            prompt="futuristic city",
            seed=123,
        )
        result = config.to_dict()

        assert isinstance(result, dict)
        assert result["provider"] == "sora"
        assert result["model"] == "v1"
        assert result["prompt"] == "futuristic city"
        assert result["seed"] == 123
        assert result["fps"] == 24
        assert result["duration"] == 4.0

    def test_to_dict_includes_all_fields(self):
        """Test that to_dict includes all fields."""
        config = VideoGenerationConfig(
            provider="test",
            model="test",
            prompt="test",
        )
        result = config.to_dict()

        expected_keys = [
            "provider",
            "model",
            "prompt",
            "negative_prompt",
            "width",
            "height",
            "fps",
            "duration",
            "seed",
            "style",
            "motion_bucket_id",
            "image_ref",
        ]
        assert set(result.keys()) == set(expected_keys)


@pytest.mark.unit
class TestVideoCacheManager:
    """Test suite for VideoCacheManager class."""

    def test_asset_type(self, temp_dir):
        """Test that asset type is correctly set."""
        manager = VideoCacheManager(cache_dir=temp_dir)
        assert manager.ASSET_TYPE == "video"
        assert manager.DEFAULT_CACHE_SUBDIR == "videos"

    def test_compute_cache_key(self, temp_dir):
        """Test cache key computation."""
        manager = VideoCacheManager(cache_dir=temp_dir)
        config = VideoGenerationConfig(
            provider="runway",
            model="gen3",
            prompt="test prompt",
        )

        key = manager._compute_cache_key(config)
        assert isinstance(key, str)
        assert len(key) == 16

    def test_compute_cache_key_consistent(self, temp_dir):
        """Test that same config produces same key."""
        manager = VideoCacheManager(cache_dir=temp_dir)
        config1 = VideoGenerationConfig(
            provider="runway",
            model="gen3",
            prompt="test prompt",
            seed=42,
            duration=4.0,
        )
        config2 = VideoGenerationConfig(
            provider="runway",
            model="gen3",
            prompt="test prompt",
            seed=42,
            duration=4.0,
        )

        key1 = manager._compute_cache_key(config1)
        key2 = manager._compute_cache_key(config2)
        assert key1 == key2

    def test_compute_cache_key_different_for_different_config(self, temp_dir):
        """Test that different configs produce different keys."""
        manager = VideoCacheManager(cache_dir=temp_dir)
        config1 = VideoGenerationConfig(
            provider="runway",
            model="gen3",
            prompt="sunset timelapse",
        )
        config2 = VideoGenerationConfig(
            provider="runway",
            model="gen3",
            prompt="sunrise timelapse",
        )

        key1 = manager._compute_cache_key(config1)
        key2 = manager._compute_cache_key(config2)
        assert key1 != key2

    def test_put_and_get(self, temp_dir):
        """Test putting and getting video data."""
        manager = VideoCacheManager(cache_dir=temp_dir)
        config = VideoGenerationConfig(
            provider="test",
            model="test",
            prompt="test video",
        )
        video_data = (
            b"\x00\x00\x00\x1c\x66\x74\x79\x70" + b"\x00" * 100
        )  # Fake MP4 data

        # Put video
        cache_path = manager.put(config, video_data)
        assert cache_path.exists()
        assert cache_path.suffix == ".mp4"

        # Get video
        retrieved = manager.get(config)
        assert retrieved == video_data

    def test_put_and_get_with_custom_extension(self, temp_dir):
        """Test putting and getting with custom extension."""
        manager = VideoCacheManager(cache_dir=temp_dir)
        config = VideoGenerationConfig(
            provider="test",
            model="test",
            prompt="test",
        )
        video_data = b"WebM data"

        manager.put(config, video_data, ext=".webm")
        retrieved = manager.get(config, ext=".webm")
        assert retrieved == video_data

    def test_get_returns_none_for_missing(self, temp_dir):
        """Test that get returns None for missing cache."""
        manager = VideoCacheManager(cache_dir=temp_dir)
        config = VideoGenerationConfig(
            provider="test",
            model="test",
            prompt="nonexistent",
        )

        result = manager.get(config)
        assert result is None

    def test_has_exists(self, temp_dir):
        """Test has returns True when cache exists."""
        manager = VideoCacheManager(cache_dir=temp_dir)
        config = VideoGenerationConfig(
            provider="test",
            model="test",
            prompt="existing",
        )
        manager.put(config, b"video data")

        assert manager.has(config) is True

    def test_has_not_exists(self, temp_dir):
        """Test has returns False when cache doesn't exist."""
        manager = VideoCacheManager(cache_dir=temp_dir)
        config = VideoGenerationConfig(
            provider="test",
            model="test",
            prompt="missing",
        )

        assert manager.has(config) is False


@pytest.mark.unit
class TestVideoCacheGlobalFunctions:
    """Test suite for global video cache functions."""

    def test_get_video_cache_manager_returns_singleton(self):
        """Test that get_video_cache_manager returns a singleton."""
        # Reset global state
        import teto_core.cache.video as video_module

        video_module._default_video_cache_manager = None

        manager1 = get_video_cache_manager()
        manager2 = get_video_cache_manager()
        assert manager1 is manager2

    def test_get_video_cache_info(self):
        """Test get_video_cache_info function."""
        info = get_video_cache_info()
        assert info.asset_type == "video"
