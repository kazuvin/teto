"""Tests for size_utils module."""

import pytest
from teto_core.utils.size_utils import (
    get_scale_factor,
    get_responsive_constants,
    calculate_size,
    calculate_font_size,
    calculate_stroke_width,
    calculate_padding,
    calculate_margin,
)
from teto_core.constants import (
    BASE_FONT_SIZE,
    BASE_BORDER_WIDTH,
    BASE_PADDING,
    BASE_MARGIN,
)


@pytest.mark.unit
class TestGetScaleFactor:
    """Test suite for get_scale_factor function (width-based)."""

    def test_scale_factor_1080p(self):
        """Test scale factor for 1080p 16:9 (base resolution)."""
        result = get_scale_factor(1920)  # 16:9の幅
        assert result == 1.0

    def test_scale_factor_4k(self):
        """Test scale factor for 4K 16:9 (square root)."""
        import math

        result = get_scale_factor(3840)  # 16:9の幅
        # sqrt(3840/1920) = sqrt(2) ≈ 1.414
        assert result == pytest.approx(math.sqrt(2))

    def test_scale_factor_720p(self):
        """Test scale factor for 720p 16:9."""
        import math

        result = get_scale_factor(1280)  # 16:9の幅
        assert result == pytest.approx(math.sqrt(1280 / 1920))

    def test_scale_factor_portrait(self):
        """Test scale factor for 9:16 portrait."""
        import math

        result = get_scale_factor(1080)  # 9:16の幅
        expected = math.sqrt(1080 / 1920)  # ≈ 0.75
        assert result == pytest.approx(expected)

    def test_scale_factor_8k(self):
        """Test scale factor for 8K 16:9 (square root)."""
        result = get_scale_factor(7680)  # 16:9の幅
        # sqrt(7680/1920) = sqrt(4) = 2.0
        assert result == 2.0


@pytest.mark.unit
class TestGetResponsiveConstants:
    """Test suite for get_responsive_constants function."""

    def test_responsive_constants_1080p(self):
        """Test responsive constants for 1080p 16:9."""
        result = get_responsive_constants(1920)  # 16:9の幅
        assert isinstance(result, dict)
        assert "LINE_SPACING" in result
        assert "TEXT_PADDING" in result
        assert "BG_PADDING_X" in result
        assert "BG_PADDING_Y" in result
        assert "BG_RADIUS" in result
        assert "MARGIN_BOTTOM" in result
        assert "MARGIN_TOP" in result
        assert "MAX_TEXT_WIDTH_OFFSET" in result

    def test_responsive_constants_values_are_integers(self):
        """Test that all values are integers."""
        result = get_responsive_constants(1920)  # 16:9の幅
        assert all(isinstance(v, int) for v in result.values())

    def test_responsive_constants_scale_with_resolution(self):
        """Test that constants scale properly with resolution (square root)."""
        import math

        result_1080 = get_responsive_constants(1920)  # 16:9 FHD の幅
        result_2160 = get_responsive_constants(3840)  # 16:9 4K の幅

        # 4K values should be sqrt(2) times (≈1.41x) the 1080p values with square root scaling
        # But since 3840 = 1920 * 2, sqrt(2) = approx 1.41, which rounds to 2x for integers
        scale_ratio = math.sqrt(3840 / 1920)  # = sqrt(2) ≈ 1.41
        expected_line_spacing = int(result_1080["LINE_SPACING"] * scale_ratio)
        expected_text_padding = int(result_1080["TEXT_PADDING"] * scale_ratio)

        assert result_2160["LINE_SPACING"] == pytest.approx(
            expected_line_spacing, abs=1
        )
        assert result_2160["TEXT_PADDING"] == pytest.approx(
            expected_text_padding, abs=1
        )


@pytest.mark.unit
class TestCalculateSize:
    """Test suite for calculate_size function."""

    def test_calculate_size_with_int(self):
        """Test that integer values are returned as-is."""
        result = calculate_size(48, 1920)
        assert result == 48

    def test_calculate_size_with_base_size(self):
        """Test calculation with 'base' responsive size."""
        result = calculate_size("base", 1920, BASE_FONT_SIZE)  # 16:9の幅
        assert result == BASE_FONT_SIZE

    def test_calculate_size_with_base_size_4k(self):
        """Test calculation with 'base' size at 4K resolution (square root)."""
        import math

        result = calculate_size("base", 3840, BASE_FONT_SIZE)  # 16:9 4Kの幅
        # sqrt(3840/1920) = sqrt(2) ≈ 1.41
        expected = int(BASE_FONT_SIZE * math.sqrt(2))
        assert result == expected

    def test_calculate_size_with_lg_size(self):
        """Test calculation with 'lg' size (1.5x scale)."""
        result = calculate_size("lg", 1920, BASE_FONT_SIZE)  # 16:9の幅
        assert result == int(BASE_FONT_SIZE * 1.5)

    def test_calculate_size_with_xl_size(self):
        """Test calculation with 'xl' size (2.0x scale)."""
        result = calculate_size("xl", 1920, BASE_FONT_SIZE)  # 16:9の幅
        assert result == BASE_FONT_SIZE * 2

    def test_calculate_size_with_sm_size(self):
        """Test calculation with 'sm' size (0.75x scale)."""
        result = calculate_size("sm", 1920, BASE_FONT_SIZE)  # 16:9の幅
        assert result == int(BASE_FONT_SIZE * 0.75)

    def test_calculate_size_with_xs_size(self):
        """Test calculation with 'xs' size (0.5x scale)."""
        result = calculate_size("xs", 1920, BASE_FONT_SIZE)  # 16:9の幅
        assert result == int(BASE_FONT_SIZE * 0.5)

    def test_calculate_size_with_2xl_size(self):
        """Test calculation with '2xl' size (3.0x scale)."""
        result = calculate_size("2xl", 1920, BASE_FONT_SIZE)  # 16:9の幅
        assert result == BASE_FONT_SIZE * 3


@pytest.mark.unit
class TestCalculateFontSize:
    """Test suite for calculate_font_size function."""

    def test_calculate_font_size_with_int(self):
        """Test font size calculation with integer."""
        result = calculate_font_size(60, 1920)
        assert result == 60

    def test_calculate_font_size_with_base(self):
        """Test font size calculation with 'base' size."""
        result = calculate_font_size("base", 1920)  # 16:9の幅
        assert result == BASE_FONT_SIZE

    def test_calculate_font_size_scales_with_resolution(self):
        """Test that font size scales with resolution (square root)."""
        import math

        result_1080 = calculate_font_size("base", 1920)  # 16:9 FHDの幅
        result_2160 = calculate_font_size("base", 3840)  # 16:9 4Kの幅
        # sqrt(3840/1920) = sqrt(2) ≈ 1.41
        expected = int(result_1080 * math.sqrt(2))
        assert result_2160 == expected


@pytest.mark.unit
class TestCalculateStrokeWidth:
    """Test suite for calculate_stroke_width function."""

    def test_calculate_stroke_width_with_int(self):
        """Test stroke width calculation with integer."""
        result = calculate_stroke_width(5, 1920)
        assert result == 5

    def test_calculate_stroke_width_with_base(self):
        """Test stroke width calculation with 'base' size."""
        result = calculate_stroke_width("base", 1920)  # 16:9の幅
        assert result == BASE_BORDER_WIDTH


@pytest.mark.unit
class TestCalculatePadding:
    """Test suite for calculate_padding function."""

    def test_calculate_padding_with_int(self):
        """Test padding calculation with integer."""
        result = calculate_padding(10, 1920)
        assert result == 10

    def test_calculate_padding_with_base(self):
        """Test padding calculation with 'base' size."""
        result = calculate_padding("base", 1920)  # 16:9の幅
        assert result == BASE_PADDING


@pytest.mark.unit
class TestCalculateMargin:
    """Test suite for calculate_margin function."""

    def test_calculate_margin_with_int(self):
        """Test margin calculation with integer."""
        result = calculate_margin(30, 1920)
        assert result == 30

    def test_calculate_margin_with_base(self):
        """Test margin calculation with 'base' size."""
        result = calculate_margin("base", 1920)  # 16:9の幅
        assert result == BASE_MARGIN
