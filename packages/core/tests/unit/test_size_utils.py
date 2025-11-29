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
    BASE_HEIGHT,
    BASE_FONT_SIZE,
    BASE_BORDER_WIDTH,
    BASE_PADDING,
    BASE_MARGIN,
)


@pytest.mark.unit
class TestGetScaleFactor:
    """Test suite for get_scale_factor function."""

    def test_scale_factor_1080p(self):
        """Test scale factor for 1080p (base resolution)."""
        result = get_scale_factor(1080)
        assert result == 1.0

    def test_scale_factor_4k(self):
        """Test scale factor for 4K (2160p)."""
        result = get_scale_factor(2160)
        assert result == 2.0

    def test_scale_factor_720p(self):
        """Test scale factor for 720p."""
        result = get_scale_factor(720)
        assert result == pytest.approx(720 / 1080)

    def test_scale_factor_480p(self):
        """Test scale factor for 480p."""
        result = get_scale_factor(480)
        assert result == pytest.approx(480 / 1080)

    def test_scale_factor_8k(self):
        """Test scale factor for 8K (4320p)."""
        result = get_scale_factor(4320)
        assert result == 4.0


@pytest.mark.unit
class TestGetResponsiveConstants:
    """Test suite for get_responsive_constants function."""

    def test_responsive_constants_1080p(self):
        """Test responsive constants for 1080p."""
        result = get_responsive_constants(1080)
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
        result = get_responsive_constants(1080)
        assert all(isinstance(v, int) for v in result.values())

    def test_responsive_constants_scale_with_resolution(self):
        """Test that constants scale properly with resolution."""
        result_1080 = get_responsive_constants(1080)
        result_2160 = get_responsive_constants(2160)

        # 4K values should be roughly 2x the 1080p values
        assert result_2160["LINE_SPACING"] == result_1080["LINE_SPACING"] * 2
        assert result_2160["TEXT_PADDING"] == result_1080["TEXT_PADDING"] * 2


@pytest.mark.unit
class TestCalculateSize:
    """Test suite for calculate_size function."""

    def test_calculate_size_with_int(self):
        """Test that integer values are returned as-is."""
        result = calculate_size(48, 1080)
        assert result == 48

    def test_calculate_size_with_base_size(self):
        """Test calculation with 'base' responsive size."""
        result = calculate_size("base", 1080, BASE_FONT_SIZE)
        assert result == BASE_FONT_SIZE

    def test_calculate_size_with_base_size_4k(self):
        """Test calculation with 'base' size at 4K resolution."""
        result = calculate_size("base", 2160, BASE_FONT_SIZE)
        assert result == BASE_FONT_SIZE * 2

    def test_calculate_size_with_lg_size(self):
        """Test calculation with 'lg' size (1.5x scale)."""
        result = calculate_size("lg", 1080, BASE_FONT_SIZE)
        assert result == int(BASE_FONT_SIZE * 1.5)

    def test_calculate_size_with_xl_size(self):
        """Test calculation with 'xl' size (2.0x scale)."""
        result = calculate_size("xl", 1080, BASE_FONT_SIZE)
        assert result == BASE_FONT_SIZE * 2

    def test_calculate_size_with_sm_size(self):
        """Test calculation with 'sm' size (0.75x scale)."""
        result = calculate_size("sm", 1080, BASE_FONT_SIZE)
        assert result == int(BASE_FONT_SIZE * 0.75)

    def test_calculate_size_with_xs_size(self):
        """Test calculation with 'xs' size (0.5x scale)."""
        result = calculate_size("xs", 1080, BASE_FONT_SIZE)
        assert result == int(BASE_FONT_SIZE * 0.5)

    def test_calculate_size_with_2xl_size(self):
        """Test calculation with '2xl' size (3.0x scale)."""
        result = calculate_size("2xl", 1080, BASE_FONT_SIZE)
        assert result == BASE_FONT_SIZE * 3


@pytest.mark.unit
class TestCalculateFontSize:
    """Test suite for calculate_font_size function."""

    def test_calculate_font_size_with_int(self):
        """Test font size calculation with integer."""
        result = calculate_font_size(60, 1080)
        assert result == 60

    def test_calculate_font_size_with_base(self):
        """Test font size calculation with 'base' size."""
        result = calculate_font_size("base", 1080)
        assert result == BASE_FONT_SIZE

    def test_calculate_font_size_scales_with_resolution(self):
        """Test that font size scales with resolution."""
        result_1080 = calculate_font_size("base", 1080)
        result_2160 = calculate_font_size("base", 2160)
        assert result_2160 == result_1080 * 2


@pytest.mark.unit
class TestCalculateStrokeWidth:
    """Test suite for calculate_stroke_width function."""

    def test_calculate_stroke_width_with_int(self):
        """Test stroke width calculation with integer."""
        result = calculate_stroke_width(5, 1080)
        assert result == 5

    def test_calculate_stroke_width_with_base(self):
        """Test stroke width calculation with 'base' size."""
        result = calculate_stroke_width("base", 1080)
        assert result == BASE_BORDER_WIDTH


@pytest.mark.unit
class TestCalculatePadding:
    """Test suite for calculate_padding function."""

    def test_calculate_padding_with_int(self):
        """Test padding calculation with integer."""
        result = calculate_padding(10, 1080)
        assert result == 10

    def test_calculate_padding_with_base(self):
        """Test padding calculation with 'base' size."""
        result = calculate_padding("base", 1080)
        assert result == BASE_PADDING


@pytest.mark.unit
class TestCalculateMargin:
    """Test suite for calculate_margin function."""

    def test_calculate_margin_with_int(self):
        """Test margin calculation with integer."""
        result = calculate_margin(30, 1080)
        assert result == 30

    def test_calculate_margin_with_base(self):
        """Test margin calculation with 'base' size."""
        result = calculate_margin("base", 1080)
        assert result == BASE_MARGIN
