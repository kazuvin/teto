"""Tests for models.layers module."""

import pytest
from pydantic import ValidationError
from teto_core.models import (
    VideoLayer,
    ImageLayer,
    AudioLayer,
    SubtitleLayer,
    SubtitleItem,
)


@pytest.mark.unit
class TestVideoLayer:
    """Test suite for VideoLayer model."""

    def test_video_layer_creation(self):
        """Test creating a basic video layer."""
        layer = VideoLayer(path="/path/to/video.mp4")
        assert layer.type == "video"
        assert layer.path == "/path/to/video.mp4"
        assert layer.start_time == 0.0
        assert layer.volume == 1.0
        assert layer.duration is None
        assert layer.effects == []

    def test_video_layer_with_all_fields(self):
        """Test creating a video layer with all fields."""
        layer = VideoLayer(
            path="/path/to/video.mp4",
            start_time=5.0,
            duration=10.0,
            volume=0.5,
        )
        assert layer.start_time == 5.0
        assert layer.duration == 10.0
        assert layer.volume == 0.5

    def test_video_layer_volume_validation(self):
        """Test that volume is validated to be between 0 and 1."""
        # Valid volumes
        VideoLayer(path="/test.mp4", volume=0.0)
        VideoLayer(path="/test.mp4", volume=0.5)
        VideoLayer(path="/test.mp4", volume=1.0)

        # Invalid volumes
        with pytest.raises(ValidationError):
            VideoLayer(path="/test.mp4", volume=-0.1)

        with pytest.raises(ValidationError):
            VideoLayer(path="/test.mp4", volume=1.1)

    def test_video_layer_start_time_validation(self):
        """Test that start_time must be non-negative."""
        VideoLayer(path="/test.mp4", start_time=0.0)
        VideoLayer(path="/test.mp4", start_time=10.0)

        with pytest.raises(ValidationError):
            VideoLayer(path="/test.mp4", start_time=-1.0)


@pytest.mark.unit
class TestImageLayer:
    """Test suite for ImageLayer model."""

    def test_image_layer_creation(self):
        """Test creating a basic image layer."""
        layer = ImageLayer(path="/path/to/image.png", duration=5.0)
        assert layer.type == "image"
        assert layer.path == "/path/to/image.png"
        assert layer.duration == 5.0
        assert layer.start_time == 0.0
        assert layer.effects == []

    def test_image_layer_requires_duration(self):
        """Test that image layer requires duration."""
        with pytest.raises(ValidationError):
            ImageLayer(path="/test.png")

    def test_image_layer_duration_must_be_positive(self):
        """Test that duration must be positive."""
        ImageLayer(path="/test.png", duration=0.1)
        ImageLayer(path="/test.png", duration=10.0)

        with pytest.raises(ValidationError):
            ImageLayer(path="/test.png", duration=0.0)

        with pytest.raises(ValidationError):
            ImageLayer(path="/test.png", duration=-1.0)


@pytest.mark.unit
class TestAudioLayer:
    """Test suite for AudioLayer model."""

    def test_audio_layer_creation(self):
        """Test creating a basic audio layer."""
        layer = AudioLayer(path="/path/to/audio.mp3")
        assert layer.type == "audio"
        assert layer.path == "/path/to/audio.mp3"
        assert layer.start_time == 0.0
        assert layer.volume == 1.0
        assert layer.duration is None

    def test_audio_layer_with_volume(self):
        """Test creating audio layer with custom volume."""
        layer = AudioLayer(path="/test.mp3", volume=0.7)
        assert layer.volume == 0.7

    def test_audio_layer_volume_validation(self):
        """Test that volume is validated."""
        with pytest.raises(ValidationError):
            AudioLayer(path="/test.mp3", volume=1.5)


@pytest.mark.unit
class TestSubtitleItem:
    """Test suite for SubtitleItem model."""

    def test_subtitle_item_creation(self):
        """Test creating a subtitle item."""
        item = SubtitleItem(
            text="Hello World",
            start_time=0.0,
            end_time=2.0
        )
        assert item.text == "Hello World"
        assert item.start_time == 0.0
        assert item.end_time == 2.0

    def test_subtitle_item_time_validation(self):
        """Test that times must be non-negative."""
        SubtitleItem(text="Test", start_time=0.0, end_time=1.0)

        with pytest.raises(ValidationError):
            SubtitleItem(text="Test", start_time=-1.0, end_time=1.0)

        with pytest.raises(ValidationError):
            SubtitleItem(text="Test", start_time=0.0, end_time=-1.0)


@pytest.mark.unit
class TestSubtitleLayer:
    """Test suite for SubtitleLayer model."""

    def test_subtitle_layer_creation_empty(self):
        """Test creating an empty subtitle layer."""
        layer = SubtitleLayer()
        assert layer.type == "subtitle"
        assert layer.items == []
        assert layer.font_size == "base"
        assert layer.font_color == "white"
        assert layer.font_weight == "normal"
        assert layer.position == "bottom"
        assert layer.appearance == "background"

    def test_subtitle_layer_with_items(self):
        """Test creating subtitle layer with items."""
        items = [
            SubtitleItem(text="First", start_time=0.0, end_time=2.0),
            SubtitleItem(text="Second", start_time=2.0, end_time=4.0),
        ]
        layer = SubtitleLayer(items=items)
        assert len(layer.items) == 2
        assert layer.items[0].text == "First"
        assert layer.items[1].text == "Second"

    def test_subtitle_layer_font_size_int(self):
        """Test subtitle layer with integer font size."""
        layer = SubtitleLayer(font_size=60)
        assert layer.font_size == 60

    def test_subtitle_layer_font_size_responsive(self):
        """Test subtitle layer with responsive font size."""
        layer = SubtitleLayer(font_size="lg")
        assert layer.font_size == "lg"

    def test_subtitle_layer_custom_colors(self):
        """Test subtitle layer with custom colors."""
        layer = SubtitleLayer(
            font_color="red",
            stroke_color="white",
            bg_color="black@0.8"
        )
        assert layer.font_color == "red"
        assert layer.stroke_color == "white"
        assert layer.bg_color == "black@0.8"

    def test_subtitle_layer_position_options(self):
        """Test subtitle layer position options."""
        SubtitleLayer(position="bottom")
        SubtitleLayer(position="top")
        SubtitleLayer(position="center")

        with pytest.raises(ValidationError):
            SubtitleLayer(position="invalid")

    def test_subtitle_layer_appearance_options(self):
        """Test subtitle layer appearance options."""
        SubtitleLayer(appearance="plain")
        SubtitleLayer(appearance="background")
        SubtitleLayer(appearance="shadow")

        with pytest.raises(ValidationError):
            SubtitleLayer(appearance="invalid")

    def test_subtitle_layer_font_weight_options(self):
        """Test subtitle layer font weight options."""
        SubtitleLayer(font_weight="normal")
        SubtitleLayer(font_weight="bold")

        with pytest.raises(ValidationError):
            SubtitleLayer(font_weight="invalid")

    def test_subtitle_layer_google_font(self):
        """Test subtitle layer with Google Font."""
        layer = SubtitleLayer(google_font="Noto Sans JP")
        assert layer.google_font == "Noto Sans JP"

    def test_subtitle_layer_stroke_widths(self):
        """Test subtitle layer with stroke widths."""
        layer = SubtitleLayer(
            stroke_width=5,
            outer_stroke_width=10
        )
        assert layer.stroke_width == 5
        assert layer.outer_stroke_width == 10

        # Test with responsive sizes
        layer2 = SubtitleLayer(
            stroke_width="sm",
            outer_stroke_width="lg"
        )
        assert layer2.stroke_width == "sm"
        assert layer2.outer_stroke_width == "lg"
