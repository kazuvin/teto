"""Tests for constants module."""

import pytest
from teto_core.constants import (
    BASE_HEIGHT,
    SIZE_SCALE_MAP,
    BASE_FONT_SIZE,
    COLOR_MAP,
    PUNCTUATION_CHARS,
)


@pytest.mark.unit
class TestConstants:
    """Test suite for constants module."""

    def test_base_height(self):
        """Test base height constant."""
        assert BASE_HEIGHT == 1080
        assert isinstance(BASE_HEIGHT, int)

    def test_size_scale_map(self):
        """Test size scale map has expected keys and values."""
        expected_sizes = ["xs", "sm", "base", "lg", "xl", "2xl"]
        assert all(size in SIZE_SCALE_MAP for size in expected_sizes)

        # Verify scale values are positive
        assert all(scale > 0 for scale in SIZE_SCALE_MAP.values())

        # Verify base scale is 1.0
        assert SIZE_SCALE_MAP["base"] == 1.0

    def test_base_font_size(self):
        """Test base font size is positive."""
        assert BASE_FONT_SIZE > 0
        assert isinstance(BASE_FONT_SIZE, int)

    def test_color_map(self):
        """Test color map contains valid RGB tuples."""
        for color_name, rgb in COLOR_MAP.items():
            assert isinstance(rgb, tuple)
            assert len(rgb) == 3
            assert all(0 <= val <= 255 for val in rgb)

    def test_punctuation_chars(self):
        """Test punctuation characters string."""
        assert isinstance(PUNCTUATION_CHARS, str)
        assert len(PUNCTUATION_CHARS) > 0
