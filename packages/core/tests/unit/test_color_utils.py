"""Tests for color_utils module."""

import pytest
from teto_core.utils.color_utils import parse_color, parse_background_color


@pytest.mark.unit
class TestParseColor:
    """Test suite for parse_color function."""

    def test_parse_named_color_white(self):
        """Test parsing named color 'white'."""
        result = parse_color("white")
        assert result == (255, 255, 255)

    def test_parse_named_color_black(self):
        """Test parsing named color 'black'."""
        result = parse_color("black")
        assert result == (0, 0, 0)

    def test_parse_named_color_red(self):
        """Test parsing named color 'red'."""
        result = parse_color("red")
        assert result == (255, 0, 0)

    def test_parse_named_color_case_insensitive(self):
        """Test that color names are case insensitive."""
        assert parse_color("WHITE") == (255, 255, 255)
        assert parse_color("White") == (255, 255, 255)
        assert parse_color("wHiTe") == (255, 255, 255)

    def test_parse_hex_color_6_digits(self):
        """Test parsing 6-digit hex color."""
        assert parse_color("#DADADA") == (218, 218, 218)
        assert parse_color("#FF0000") == (255, 0, 0)
        assert parse_color("#00FF00") == (0, 255, 0)
        assert parse_color("#0000FF") == (0, 0, 255)

    def test_parse_hex_color_3_digits(self):
        """Test parsing 3-digit hex color (expands to 6)."""
        assert parse_color("#FFF") == (255, 255, 255)
        assert parse_color("#000") == (0, 0, 0)
        assert parse_color("#F00") == (255, 0, 0)
        assert parse_color("#0F0") == (0, 255, 0)
        assert parse_color("#00F") == (0, 0, 255)

    def test_parse_hex_color_lowercase(self):
        """Test parsing hex color with lowercase letters."""
        assert parse_color("#dadada") == (218, 218, 218)
        assert parse_color("#abc") == (170, 187, 204)

    def test_parse_unknown_color_returns_white(self):
        """Test that unknown color names return white."""
        result = parse_color("unknown_color")
        assert result == (255, 255, 255)

    def test_parse_invalid_hex_returns_white(self):
        """Test that invalid hex values return white."""
        assert parse_color("#GGGGGG") == (255, 255, 255)
        assert parse_color("#XYZ") == (255, 255, 255)
        assert parse_color("#12") == (255, 255, 255)
        assert parse_color("#1234567") == (255, 255, 255)


@pytest.mark.unit
class TestParseBackgroundColor:
    """Test suite for parse_background_color function."""

    def test_parse_background_color_with_opacity(self):
        """Test parsing background color with opacity."""
        color, opacity = parse_background_color("black@0.5")
        assert color == (0, 0, 0)
        assert opacity == 0.5

    def test_parse_background_color_different_opacity(self):
        """Test parsing with different opacity values."""
        color, opacity = parse_background_color("red@0.8")
        assert color == (255, 0, 0)
        assert opacity == 0.8

    def test_parse_background_color_hex_with_opacity(self):
        """Test parsing hex color with opacity."""
        color, opacity = parse_background_color("#FF0000@0.3")
        assert color == (255, 0, 0)
        assert opacity == 0.3

    def test_parse_background_color_without_opacity(self):
        """Test parsing background color without opacity (defaults to 0.5)."""
        color, opacity = parse_background_color("white")
        assert color == (255, 255, 255)
        assert opacity == 0.5

    def test_parse_background_color_none(self):
        """Test parsing None returns default black with 0.5 opacity."""
        color, opacity = parse_background_color(None)
        assert color == (0, 0, 0)
        assert opacity == 0.5

    def test_parse_background_color_full_opacity(self):
        """Test parsing with full opacity."""
        color, opacity = parse_background_color("blue@1.0")
        assert color == (0, 0, 255)
        assert opacity == 1.0

    def test_parse_background_color_zero_opacity(self):
        """Test parsing with zero opacity."""
        color, opacity = parse_background_color("green@0.0")
        assert color == (0, 255, 0)
        assert opacity == 0.0
