"""Tests for StampLayerProcessor."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from teto_core.layer.processors.video import StampLayerProcessor
from teto_core.layer.models import StampLayer, PositionPreset


@pytest.mark.unit
class TestStampLayerProcessorPositionCalculation:
    """Test suite for StampLayerProcessor position calculation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.processor = StampLayerProcessor()

    def test_calculate_position_top_left(self):
        """Test position calculation for top-left preset."""
        video_size = (1920, 1080)
        stamp_size = (100, 50)
        margin = 20

        position = self.processor._calculate_position_from_preset(
            video_size, stamp_size, PositionPreset.TOP_LEFT, margin
        )

        assert position == (20, 20)

    def test_calculate_position_top_right(self):
        """Test position calculation for top-right preset."""
        video_size = (1920, 1080)
        stamp_size = (100, 50)
        margin = 20

        position = self.processor._calculate_position_from_preset(
            video_size, stamp_size, PositionPreset.TOP_RIGHT, margin
        )

        # video_w - stamp_w - margin = 1920 - 100 - 20 = 1800
        assert position == (1800, 20)

    def test_calculate_position_bottom_left(self):
        """Test position calculation for bottom-left preset."""
        video_size = (1920, 1080)
        stamp_size = (100, 50)
        margin = 20

        position = self.processor._calculate_position_from_preset(
            video_size, stamp_size, PositionPreset.BOTTOM_LEFT, margin
        )

        # (margin, video_h - stamp_h - margin) = (20, 1080 - 50 - 20) = (20, 1010)
        assert position == (20, 1010)

    def test_calculate_position_bottom_right(self):
        """Test position calculation for bottom-right preset."""
        video_size = (1920, 1080)
        stamp_size = (100, 50)
        margin = 20

        position = self.processor._calculate_position_from_preset(
            video_size, stamp_size, PositionPreset.BOTTOM_RIGHT, margin
        )

        # (video_w - stamp_w - margin, video_h - stamp_h - margin)
        # = (1920 - 100 - 20, 1080 - 50 - 20) = (1800, 1010)
        assert position == (1800, 1010)

    def test_calculate_position_custom_margin(self):
        """Test position calculation with custom margin."""
        video_size = (1920, 1080)
        stamp_size = (200, 100)
        margin = 50

        position = self.processor._calculate_position_from_preset(
            video_size, stamp_size, PositionPreset.TOP_LEFT, margin
        )

        assert position == (50, 50)

        position = self.processor._calculate_position_from_preset(
            video_size, stamp_size, PositionPreset.BOTTOM_RIGHT, margin
        )

        # (1920 - 200 - 50, 1080 - 100 - 50) = (1670, 930)
        assert position == (1670, 930)

    def test_calculate_position_unknown_preset_returns_origin(self):
        """Test that unknown preset returns (0, 0)."""
        video_size = (1920, 1080)
        stamp_size = (100, 50)
        margin = 20

        # Using CUSTOM preset should return (0, 0) as fallback
        position = self.processor._calculate_position_from_preset(
            video_size, stamp_size, PositionPreset.CUSTOM, margin
        )

        assert position == (0, 0)


@pytest.mark.unit
class TestStampLayerProcessorOpacity:
    """Test suite for StampLayerProcessor opacity handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.processor = StampLayerProcessor()

    def test_apply_opacity_full(self):
        """Test that full opacity (1.0) does not modify clip."""
        mock_clip = Mock()
        result = self.processor._apply_opacity(mock_clip, 1.0)

        # Should return the same clip without calling with_opacity
        assert result is mock_clip
        mock_clip.with_opacity.assert_not_called()

    def test_apply_opacity_partial(self):
        """Test that partial opacity calls with_opacity."""
        mock_clip = Mock()
        mock_clip.with_opacity.return_value = Mock()

        result = self.processor._apply_opacity(mock_clip, 0.5)

        mock_clip.with_opacity.assert_called_once_with(0.5)
        assert result is mock_clip.with_opacity.return_value

    def test_apply_opacity_zero(self):
        """Test that zero opacity calls with_opacity."""
        mock_clip = Mock()
        mock_clip.with_opacity.return_value = Mock()

        self.processor._apply_opacity(mock_clip, 0.0)

        mock_clip.with_opacity.assert_called_once_with(0.0)


@pytest.mark.unit
class TestStampLayerProcessorValidation:
    """Test suite for StampLayerProcessor validation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.processor = StampLayerProcessor()

    def test_validate_missing_file(self, tmp_path):
        """Test validation fails for missing file."""
        layer = StampLayer(
            path="/nonexistent/file.png",
            duration=5.0,
        )

        result = self.processor.validate(layer)

        assert result is False

    def test_validate_existing_file(self, sample_image_path):
        """Test validation passes for existing file."""
        layer = StampLayer(
            path=str(sample_image_path),
            duration=5.0,
        )

        result = self.processor.validate(layer)

        assert result is True

    def test_validate_preset_without_output_size(self, sample_image_path):
        """Test validation fails when using preset without output_size."""
        layer = StampLayer(
            path=str(sample_image_path),
            duration=5.0,
            position_preset=PositionPreset.TOP_RIGHT,
        )

        result = self.processor.validate(layer)

        assert result is False

    def test_validate_preset_with_output_size(self, sample_image_path):
        """Test validation passes when using preset with output_size."""
        layer = StampLayer(
            path=str(sample_image_path),
            duration=5.0,
            position_preset=PositionPreset.TOP_RIGHT,
        )

        result = self.processor.validate(layer, output_size=(1920, 1080))

        assert result is True

    def test_validate_custom_preset_without_output_size(self, sample_image_path):
        """Test validation passes for CUSTOM preset without output_size."""
        layer = StampLayer(
            path=str(sample_image_path),
            duration=5.0,
            position_preset=PositionPreset.CUSTOM,
        )

        result = self.processor.validate(layer)

        assert result is True


@pytest.mark.unit
class TestStampLayerProcessorProcess:
    """Test suite for StampLayerProcessor process method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.processor = StampLayerProcessor()

    @patch("teto_core.layer.processors.video.ImageClip")
    def test_process_basic(self, mock_image_clip_class, sample_image_path):
        """Test basic processing without presets."""
        mock_clip = MagicMock()
        mock_clip.w = 100
        mock_clip.h = 50
        mock_image_clip_class.return_value = mock_clip

        layer = StampLayer(
            path=str(sample_image_path),
            duration=5.0,
            position_x=100,
            position_y=200,
        )

        self.processor.process(layer)

        mock_image_clip_class.assert_called_once_with(
            str(sample_image_path), duration=5.0
        )
        mock_clip.with_position.assert_called_with((100, 200))

    @patch("teto_core.layer.processors.video.ImageClip")
    def test_process_with_scale(self, mock_image_clip_class, sample_image_path):
        """Test processing with scale."""
        mock_clip = MagicMock()
        mock_clip.w = 100
        mock_clip.h = 50
        mock_clip.resized.return_value = mock_clip
        mock_image_clip_class.return_value = mock_clip

        layer = StampLayer(
            path=str(sample_image_path),
            duration=5.0,
            scale=0.5,
        )

        self.processor.process(layer)

        mock_clip.resized.assert_called_once_with(0.5)

    @patch("teto_core.layer.processors.video.ImageClip")
    def test_process_with_opacity(self, mock_image_clip_class, sample_image_path):
        """Test processing with opacity."""
        mock_clip = MagicMock()
        mock_clip.w = 100
        mock_clip.h = 50
        mock_clip.with_opacity.return_value = mock_clip
        mock_image_clip_class.return_value = mock_clip

        layer = StampLayer(
            path=str(sample_image_path),
            duration=5.0,
            opacity=0.7,
        )

        self.processor.process(layer)

        mock_clip.with_opacity.assert_called_once_with(0.7)

    @patch("teto_core.layer.processors.video.ImageClip")
    def test_process_with_position_preset(
        self, mock_image_clip_class, sample_image_path
    ):
        """Test processing with position preset."""
        mock_clip = MagicMock()
        mock_clip.w = 100
        mock_clip.h = 50
        mock_image_clip_class.return_value = mock_clip

        layer = StampLayer(
            path=str(sample_image_path),
            duration=5.0,
            position_preset=PositionPreset.BOTTOM_RIGHT,
            margin=20,
        )

        self.processor.process(layer, output_size=(1920, 1080))

        # Expected position: (1920-100-20, 1080-50-20) = (1800, 1010)
        mock_clip.with_position.assert_called_with((1800, 1010))

    @patch("teto_core.layer.processors.video.ImageClip")
    def test_process_custom_preset_uses_manual_position(
        self, mock_image_clip_class, sample_image_path
    ):
        """Test that CUSTOM preset uses manual position_x and position_y."""
        mock_clip = MagicMock()
        mock_clip.w = 100
        mock_clip.h = 50
        mock_image_clip_class.return_value = mock_clip

        layer = StampLayer(
            path=str(sample_image_path),
            duration=5.0,
            position_x=500,
            position_y=300,
            position_preset=PositionPreset.CUSTOM,
        )

        self.processor.process(layer, output_size=(1920, 1080))

        mock_clip.with_position.assert_called_with((500, 300))

    @patch("teto_core.layer.processors.video.ImageClip")
    def test_process_with_start_time(self, mock_image_clip_class, sample_image_path):
        """Test processing with start time."""
        mock_clip = MagicMock()
        mock_clip.w = 100
        mock_clip.h = 50
        # Ensure all chained methods return a MagicMock that tracks calls
        mock_clip.with_position.return_value = mock_clip
        mock_clip.with_start.return_value = mock_clip
        mock_image_clip_class.return_value = mock_clip

        layer = StampLayer(
            path=str(sample_image_path),
            duration=5.0,
            start_time=2.5,
        )

        self.processor.process(layer)

        mock_clip.with_start.assert_called_with(2.5)
