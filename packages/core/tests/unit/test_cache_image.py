"""Tests for image cache module."""

import pytest
from pathlib import Path

from teto_core.cache.image import (
    ImageGenerationConfig,
    ImageCacheManager,
    get_image_cache_manager,
    clear_image_cache,
    get_image_cache_info,
)


@pytest.mark.unit
class TestImageGenerationConfig:
    """Test suite for ImageGenerationConfig dataclass."""

    def test_default_values(self):
        """Test ImageGenerationConfig with default values."""
        config = ImageGenerationConfig(
            provider="stable_diffusion",
            model="sdxl",
            prompt="a beautiful sunset",
        )
        assert config.provider == "stable_diffusion"
        assert config.model == "sdxl"
        assert config.prompt == "a beautiful sunset"
        assert config.negative_prompt is None
        assert config.width == 1024
        assert config.height == 1024
        assert config.seed is None
        assert config.style is None
        assert config.quality is None

    def test_custom_values(self):
        """Test ImageGenerationConfig with custom values."""
        config = ImageGenerationConfig(
            provider="dalle",
            model="dall-e-3",
            prompt="mountain landscape",
            negative_prompt="blurry, low quality",
            width=1920,
            height=1080,
            seed=42,
            style="photorealistic",
            quality="hd",
        )
        assert config.width == 1920
        assert config.height == 1080
        assert config.seed == 42
        assert config.negative_prompt == "blurry, low quality"

    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = ImageGenerationConfig(
            provider="midjourney",
            model="v6",
            prompt="cyberpunk city",
            seed=123,
        )
        result = config.to_dict()

        assert isinstance(result, dict)
        assert result["provider"] == "midjourney"
        assert result["model"] == "v6"
        assert result["prompt"] == "cyberpunk city"
        assert result["seed"] == 123
        assert result["width"] == 1024
        assert result["height"] == 1024

    def test_to_dict_includes_all_fields(self):
        """Test that to_dict includes all fields."""
        config = ImageGenerationConfig(
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
            "seed",
            "style",
            "quality",
        ]
        assert set(result.keys()) == set(expected_keys)


@pytest.mark.unit
class TestImageCacheManager:
    """Test suite for ImageCacheManager class."""

    def test_asset_type(self, temp_dir):
        """Test that asset type is correctly set."""
        manager = ImageCacheManager(cache_dir=temp_dir)
        assert manager.ASSET_TYPE == "image"
        assert manager.DEFAULT_CACHE_SUBDIR == "images"

    def test_compute_cache_key(self, temp_dir):
        """Test cache key computation."""
        manager = ImageCacheManager(cache_dir=temp_dir)
        config = ImageGenerationConfig(
            provider="dalle",
            model="dall-e-3",
            prompt="test prompt",
        )

        key = manager._compute_cache_key(config)
        assert isinstance(key, str)
        assert len(key) == 16

    def test_compute_cache_key_consistent(self, temp_dir):
        """Test that same config produces same key."""
        manager = ImageCacheManager(cache_dir=temp_dir)
        config1 = ImageGenerationConfig(
            provider="dalle",
            model="dall-e-3",
            prompt="test prompt",
            seed=42,
        )
        config2 = ImageGenerationConfig(
            provider="dalle",
            model="dall-e-3",
            prompt="test prompt",
            seed=42,
        )

        key1 = manager._compute_cache_key(config1)
        key2 = manager._compute_cache_key(config2)
        assert key1 == key2

    def test_compute_cache_key_different_for_different_config(self, temp_dir):
        """Test that different configs produce different keys."""
        manager = ImageCacheManager(cache_dir=temp_dir)
        config1 = ImageGenerationConfig(
            provider="dalle",
            model="dall-e-3",
            prompt="sunset",
        )
        config2 = ImageGenerationConfig(
            provider="dalle",
            model="dall-e-3",
            prompt="sunrise",
        )

        key1 = manager._compute_cache_key(config1)
        key2 = manager._compute_cache_key(config2)
        assert key1 != key2

    def test_put_and_get(self, temp_dir):
        """Test putting and getting image data."""
        manager = ImageCacheManager(cache_dir=temp_dir)
        config = ImageGenerationConfig(
            provider="test",
            model="test",
            prompt="test image",
        )
        image_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100  # Fake PNG data

        # Put image
        cache_path = manager.put(config, image_data)
        assert cache_path.exists()
        assert cache_path.suffix == ".png"

        # Get image
        retrieved = manager.get(config)
        assert retrieved == image_data

    def test_put_and_get_with_custom_extension(self, temp_dir):
        """Test putting and getting with custom extension."""
        manager = ImageCacheManager(cache_dir=temp_dir)
        config = ImageGenerationConfig(
            provider="test",
            model="test",
            prompt="test",
        )
        image_data = b"JPEG data"

        manager.put(config, image_data, ext=".jpg")
        retrieved = manager.get(config, ext=".jpg")
        assert retrieved == image_data

    def test_get_returns_none_for_missing(self, temp_dir):
        """Test that get returns None for missing cache."""
        manager = ImageCacheManager(cache_dir=temp_dir)
        config = ImageGenerationConfig(
            provider="test",
            model="test",
            prompt="nonexistent",
        )

        result = manager.get(config)
        assert result is None

    def test_has_exists(self, temp_dir):
        """Test has returns True when cache exists."""
        manager = ImageCacheManager(cache_dir=temp_dir)
        config = ImageGenerationConfig(
            provider="test",
            model="test",
            prompt="existing",
        )
        manager.put(config, b"image data")

        assert manager.has(config) is True

    def test_has_not_exists(self, temp_dir):
        """Test has returns False when cache doesn't exist."""
        manager = ImageCacheManager(cache_dir=temp_dir)
        config = ImageGenerationConfig(
            provider="test",
            model="test",
            prompt="missing",
        )

        assert manager.has(config) is False


@pytest.mark.unit
class TestImageCacheGlobalFunctions:
    """Test suite for global image cache functions."""

    def test_get_image_cache_manager_returns_singleton(self):
        """Test that get_image_cache_manager returns a singleton."""
        # Reset global state
        import teto_core.cache.image as image_module

        image_module._default_image_cache_manager = None

        manager1 = get_image_cache_manager()
        manager2 = get_image_cache_manager()
        assert manager1 is manager2

    def test_get_image_cache_info(self):
        """Test get_image_cache_info function."""
        info = get_image_cache_info()
        assert info.asset_type == "image"
