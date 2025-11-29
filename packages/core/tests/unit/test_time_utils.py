"""Tests for time_utils module."""

import pytest
from teto_core.utils.time_utils import format_srt_time, format_vtt_time


@pytest.mark.unit
class TestFormatSrtTime:
    """Test suite for format_srt_time function."""

    def test_format_srt_time_basic(self):
        """Test basic SRT time formatting."""
        result = format_srt_time(0)
        assert result == "00:00:00,000"

    def test_format_srt_time_with_seconds(self):
        """Test SRT time formatting with seconds."""
        result = format_srt_time(30.5)
        assert result == "00:00:30,500"

    def test_format_srt_time_with_minutes(self):
        """Test SRT time formatting with minutes."""
        result = format_srt_time(90)
        assert result == "00:01:30,000"

    def test_format_srt_time_with_hours(self):
        """Test SRT time formatting with hours."""
        result = format_srt_time(3661.5)
        assert result == "01:01:01,500"

    def test_format_srt_time_full_example(self):
        """Test SRT time formatting with complex time."""
        result = format_srt_time(7384.125)
        # 7384.125 seconds = 2 hours, 3 minutes, 4 seconds, 125 milliseconds
        assert result == "02:03:04,125"

    def test_format_srt_time_milliseconds_precision(self):
        """Test that milliseconds are formatted with 3 digits."""
        result = format_srt_time(1.001)
        assert result == "00:00:01,001"

        result = format_srt_time(1.010)
        assert result == "00:00:01,010"

        result = format_srt_time(1.100)
        assert result == "00:00:01,100"

    def test_format_srt_time_edge_cases(self):
        """Test edge cases for SRT time formatting."""
        # Just under 1 second
        result = format_srt_time(0.999)
        assert result == "00:00:00,999"

        # Exactly 1 hour
        result = format_srt_time(3600)
        assert result == "01:00:00,000"


@pytest.mark.unit
class TestFormatVttTime:
    """Test suite for format_vtt_time function."""

    def test_format_vtt_time_basic(self):
        """Test basic VTT time formatting."""
        result = format_vtt_time(0)
        assert result == "00:00:00.000"

    def test_format_vtt_time_with_seconds(self):
        """Test VTT time formatting with seconds."""
        result = format_vtt_time(30.5)
        assert result == "00:00:30.500"

    def test_format_vtt_time_with_minutes(self):
        """Test VTT time formatting with minutes."""
        result = format_vtt_time(90)
        assert result == "00:01:30.000"

    def test_format_vtt_time_with_hours(self):
        """Test VTT time formatting with hours."""
        result = format_vtt_time(3661.5)
        assert result == "01:01:01.500"

    def test_format_vtt_time_full_example(self):
        """Test VTT time formatting with complex time."""
        result = format_vtt_time(7384.125)
        # 7384.125 seconds = 2 hours, 3 minutes, 4 seconds, 125 milliseconds
        assert result == "02:03:04.125"

    def test_format_vtt_time_uses_period_separator(self):
        """Test that VTT uses period instead of comma for milliseconds."""
        result = format_vtt_time(1.5)
        assert "." in result
        assert "," not in result
        assert result == "00:00:01.500"

    def test_format_vtt_time_milliseconds_precision(self):
        """Test that milliseconds are formatted with 3 digits."""
        result = format_vtt_time(1.001)
        assert result == "00:00:01.001"

        result = format_vtt_time(1.010)
        assert result == "00:00:01.010"

        result = format_vtt_time(1.100)
        assert result == "00:00:01.100"

    def test_format_vtt_time_edge_cases(self):
        """Test edge cases for VTT time formatting."""
        # Just under 1 second
        result = format_vtt_time(0.999)
        assert result == "00:00:00.999"

        # Exactly 1 hour
        result = format_vtt_time(3600)
        assert result == "01:00:00.000"


@pytest.mark.unit
class TestTimeFormatComparison:
    """Test suite comparing SRT and VTT formats."""

    def test_srt_vs_vtt_separator_difference(self):
        """Test that SRT uses comma and VTT uses period for milliseconds."""
        time = 12.345
        srt_result = format_srt_time(time)
        vtt_result = format_vtt_time(time)

        # Both should have same basic structure
        assert srt_result[:8] == vtt_result[:8]  # "00:00:12"

        # But different separators
        assert "," in srt_result
        assert "." in vtt_result
        assert "," not in vtt_result
        assert "." not in srt_result.replace(":", "")
