"""Tests for cache module."""

import pytest
from pathlib import Path

from teto_core.cache.base import AssetCacheManager, CacheInfo


class ConcreteAssetCacheManager(AssetCacheManager):
    """テスト用の具象キャッシュマネージャー"""

    ASSET_TYPE = "test"
    DEFAULT_CACHE_SUBDIR = "test_cache"

    def _compute_cache_key(self, data: dict) -> str:
        return self.compute_hash(data)


@pytest.mark.unit
class TestCacheInfo:
    """Test suite for CacheInfo dataclass."""

    def test_cache_info_creation(self, temp_dir):
        """Test CacheInfo creation with basic values."""
        info = CacheInfo(
            total_files=10,
            total_size_bytes=1024 * 1024,
            cache_dir=temp_dir,
            asset_type="test",
        )
        assert info.total_files == 10
        assert info.total_size_bytes == 1024 * 1024
        assert info.cache_dir == temp_dir
        assert info.asset_type == "test"

    def test_cache_info_total_size_mb(self):
        """Test total_size_mb property."""
        info = CacheInfo(
            total_files=5,
            total_size_bytes=2 * 1024 * 1024,  # 2MB
            cache_dir=Path("/tmp"),
            asset_type="test",
        )
        assert info.total_size_mb == 2.0

    def test_cache_info_total_size_mb_fractional(self):
        """Test total_size_mb with fractional values."""
        info = CacheInfo(
            total_files=1,
            total_size_bytes=512 * 1024,  # 0.5MB
            cache_dir=Path("/tmp"),
            asset_type="test",
        )
        assert info.total_size_mb == 0.5

    def test_cache_info_str(self):
        """Test string representation."""
        info = CacheInfo(
            total_files=3,
            total_size_bytes=1024 * 1024,
            cache_dir=Path("/tmp/cache"),
            asset_type="image",
        )
        result = str(info)
        assert "image" in result
        assert "3 files" in result
        assert "1.00 MB" in result


@pytest.mark.unit
class TestAssetCacheManager:
    """Test suite for AssetCacheManager base class."""

    def test_init_with_default_cache_dir(self, temp_dir, monkeypatch):
        """Test initialization with default cache directory."""
        # Monkeypatch home directory
        monkeypatch.setattr(Path, "home", lambda: temp_dir)
        manager = ConcreteAssetCacheManager()
        assert manager.cache_dir.exists()
        assert "test_cache" in str(manager.cache_dir)

    def test_init_with_custom_cache_dir(self, temp_dir):
        """Test initialization with custom cache directory."""
        custom_dir = temp_dir / "custom_cache"
        manager = ConcreteAssetCacheManager(cache_dir=custom_dir)
        assert manager.cache_dir == custom_dir
        assert custom_dir.exists()

    def test_init_with_string_path(self, temp_dir):
        """Test initialization with string path."""
        custom_dir = str(temp_dir / "string_cache")
        manager = ConcreteAssetCacheManager(cache_dir=custom_dir)
        assert manager.cache_dir == Path(custom_dir)

    def test_compute_hash_consistent(self):
        """Test that compute_hash produces consistent results."""
        data = {"key": "value", "number": 42}
        hash1 = AssetCacheManager.compute_hash(data)
        hash2 = AssetCacheManager.compute_hash(data)
        assert hash1 == hash2
        assert len(hash1) == 16

    def test_compute_hash_different_for_different_data(self):
        """Test that different data produces different hashes."""
        data1 = {"key": "value1"}
        data2 = {"key": "value2"}
        hash1 = AssetCacheManager.compute_hash(data1)
        hash2 = AssetCacheManager.compute_hash(data2)
        assert hash1 != hash2

    def test_compute_hash_order_independent(self):
        """Test that key order doesn't affect hash."""
        data1 = {"a": 1, "b": 2}
        data2 = {"b": 2, "a": 1}
        hash1 = AssetCacheManager.compute_hash(data1)
        hash2 = AssetCacheManager.compute_hash(data2)
        assert hash1 == hash2

    def test_put_and_get_by_key(self, temp_dir):
        """Test putting and getting data by cache key."""
        manager = ConcreteAssetCacheManager(cache_dir=temp_dir)
        cache_key = "testkey123456"
        ext = ".txt"
        data = b"test data content"

        # Put data
        cache_path = manager.put_by_key(cache_key, ext, data)
        assert cache_path.exists()

        # Get data
        retrieved = manager.get_by_key(cache_key, ext)
        assert retrieved == data

    def test_get_by_key_returns_none_for_missing(self, temp_dir):
        """Test that get_by_key returns None for missing cache."""
        manager = ConcreteAssetCacheManager(cache_dir=temp_dir)
        result = manager.get_by_key("nonexistent", ".txt")
        assert result is None

    def test_has_by_key_exists(self, temp_dir):
        """Test has_by_key returns True when cache exists."""
        manager = ConcreteAssetCacheManager(cache_dir=temp_dir)
        cache_key = "existingkey12"
        ext = ".bin"
        manager.put_by_key(cache_key, ext, b"data")

        assert manager.has_by_key(cache_key, ext) is True

    def test_has_by_key_not_exists(self, temp_dir):
        """Test has_by_key returns False when cache doesn't exist."""
        manager = ConcreteAssetCacheManager(cache_dir=temp_dir)
        assert manager.has_by_key("missing", ".bin") is False

    def test_cache_path_creates_subdirectory(self, temp_dir):
        """Test that cache path creates subdirectory based on key prefix."""
        manager = ConcreteAssetCacheManager(cache_dir=temp_dir)
        cache_key = "abcdef123456"
        ext = ".data"

        cache_path = manager.put_by_key(cache_key, ext, b"data")

        # Should create subdirectory based on first 2 chars
        assert cache_path.parent.name == "ab"

    def test_clear_removes_all_files(self, temp_dir):
        """Test that clear removes all cached files."""
        manager = ConcreteAssetCacheManager(cache_dir=temp_dir)

        # Create multiple cache files
        for i in range(5):
            manager.put_by_key(f"key{i:012d}", ".txt", f"data{i}".encode())

        count = manager.clear()
        assert count == 5

        # Verify files are gone
        for i in range(5):
            assert manager.has_by_key(f"key{i:012d}", ".txt") is False

    def test_clear_empty_cache(self, temp_dir):
        """Test that clear works on empty cache."""
        manager = ConcreteAssetCacheManager(cache_dir=temp_dir)
        count = manager.clear()
        assert count == 0

    def test_get_info_empty_cache(self, temp_dir):
        """Test get_info on empty cache."""
        manager = ConcreteAssetCacheManager(cache_dir=temp_dir)
        info = manager.get_info()

        assert info.total_files == 0
        assert info.total_size_bytes == 0
        assert info.asset_type == "test"

    def test_get_info_with_files(self, temp_dir):
        """Test get_info with cached files."""
        manager = ConcreteAssetCacheManager(cache_dir=temp_dir)

        # Create cache files with known sizes
        manager.put_by_key("key1abc12345", ".txt", b"a" * 100)
        manager.put_by_key("key2def12345", ".txt", b"b" * 200)

        info = manager.get_info()

        assert info.total_files == 2
        assert info.total_size_bytes == 300
        assert info.cache_dir == temp_dir
