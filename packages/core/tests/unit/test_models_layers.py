"""Tests for models.layers module."""

import pytest
from pydantic import ValidationError
from teto_core.models import (
    VideoLayer,
    ImageLayer,
    AudioLayer,
    SubtitleLayer,
    SubtitleItem,
    StampLayer,
)
from teto_core.layer.models import PositionPreset


@pytest.mark.unit
class TestVideoLayer:
    """Test suite for VideoLayer model."""

    def test_video_layer_creation(self):
        """Test creating a basic video layer."""
        layer = VideoLayer(path="/path/to/video.mp4")
        assert layer.type == "video"
        assert layer.path == "/path/to/video.mp4"
        assert layer.volume == 1.0
        assert layer.duration is None
        assert layer.effects == []
        assert layer.transition is None

    def test_video_layer_with_all_fields(self):
        """Test creating a video layer with all fields."""
        layer = VideoLayer(
            path="/path/to/video.mp4",
            duration=10.0,
            volume=0.5,
        )
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


@pytest.mark.unit
class TestImageLayer:
    """Test suite for ImageLayer model."""

    def test_image_layer_creation(self):
        """Test creating a basic image layer."""
        layer = ImageLayer(path="/path/to/image.png", duration=5.0)
        assert layer.type == "image"
        assert layer.path == "/path/to/image.png"
        assert layer.duration == 5.0
        assert layer.effects == []
        assert layer.transition is None

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
        item = SubtitleItem(text="Hello World", start_time=0.0, end_time=2.0)
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
            font_color="red", stroke_color="white", bg_color="black@0.8"
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
        layer = SubtitleLayer(stroke_width=5, outer_stroke_width=10)
        assert layer.stroke_width == 5
        assert layer.outer_stroke_width == 10

        # Test with responsive sizes
        layer2 = SubtitleLayer(stroke_width="sm", outer_stroke_width="lg")
        assert layer2.stroke_width == "sm"
        assert layer2.outer_stroke_width == "lg"


@pytest.mark.unit
class TestStampLayer:
    """Test suite for StampLayer model."""

    def test_stamp_layer_creation(self):
        """Test creating a basic stamp layer."""
        layer = StampLayer(path="/path/to/stamp.png", duration=5.0)
        assert layer.type == "stamp"
        assert layer.path == "/path/to/stamp.png"
        assert layer.duration == 5.0
        assert layer.position_x == 0
        assert layer.position_y == 0
        assert layer.scale == 1.0
        assert layer.opacity == 1.0
        assert layer.position_preset is None
        assert layer.margin == 20
        assert layer.effects == []

    def test_stamp_layer_with_all_fields(self):
        """Test creating a stamp layer with all fields."""
        layer = StampLayer(
            path="/path/to/stamp.png",
            duration=10.0,
            position_x=100,
            position_y=200,
            scale=0.5,
            opacity=0.7,
            position_preset=PositionPreset.TOP_RIGHT,
            margin=30,
            start_time=2.0,
        )
        assert layer.duration == 10.0
        assert layer.position_x == 100
        assert layer.position_y == 200
        assert layer.scale == 0.5
        assert layer.opacity == 0.7
        assert layer.position_preset == PositionPreset.TOP_RIGHT
        assert layer.margin == 30
        assert layer.start_time == 2.0

    def test_stamp_layer_requires_duration(self):
        """Test that stamp layer requires duration."""
        with pytest.raises(ValidationError):
            StampLayer(path="/test.png")

    def test_stamp_layer_duration_must_be_positive(self):
        """Test that duration must be positive."""
        StampLayer(path="/test.png", duration=0.1)
        StampLayer(path="/test.png", duration=10.0)

        with pytest.raises(ValidationError):
            StampLayer(path="/test.png", duration=0.0)

        with pytest.raises(ValidationError):
            StampLayer(path="/test.png", duration=-1.0)

    def test_stamp_layer_opacity_validation(self):
        """Test that opacity is validated to be between 0.0 and 1.0."""
        # Valid opacity values
        StampLayer(path="/test.png", duration=1.0, opacity=0.0)
        StampLayer(path="/test.png", duration=1.0, opacity=0.5)
        StampLayer(path="/test.png", duration=1.0, opacity=1.0)

        # Invalid opacity values
        with pytest.raises(ValidationError):
            StampLayer(path="/test.png", duration=1.0, opacity=-0.1)

        with pytest.raises(ValidationError):
            StampLayer(path="/test.png", duration=1.0, opacity=1.1)

    def test_stamp_layer_scale_must_be_positive(self):
        """Test that scale must be positive."""
        StampLayer(path="/test.png", duration=1.0, scale=0.1)
        StampLayer(path="/test.png", duration=1.0, scale=2.0)

        with pytest.raises(ValidationError):
            StampLayer(path="/test.png", duration=1.0, scale=0.0)

        with pytest.raises(ValidationError):
            StampLayer(path="/test.png", duration=1.0, scale=-1.0)

    def test_stamp_layer_margin_must_be_non_negative(self):
        """Test that margin must be non-negative."""
        StampLayer(path="/test.png", duration=1.0, margin=0)
        StampLayer(path="/test.png", duration=1.0, margin=50)

        with pytest.raises(ValidationError):
            StampLayer(path="/test.png", duration=1.0, margin=-10)

    def test_stamp_layer_position_preset_options(self):
        """Test all position preset options."""
        StampLayer(
            path="/test.png", duration=1.0, position_preset=PositionPreset.TOP_LEFT
        )
        StampLayer(
            path="/test.png", duration=1.0, position_preset=PositionPreset.TOP_RIGHT
        )
        StampLayer(
            path="/test.png", duration=1.0, position_preset=PositionPreset.BOTTOM_LEFT
        )
        StampLayer(
            path="/test.png", duration=1.0, position_preset=PositionPreset.BOTTOM_RIGHT
        )
        StampLayer(
            path="/test.png", duration=1.0, position_preset=PositionPreset.CUSTOM
        )
        StampLayer(path="/test.png", duration=1.0, position_preset=None)

    def test_stamp_layer_position_preset_from_string(self):
        """Test that position preset can be set from string."""
        layer = StampLayer(path="/test.png", duration=1.0, position_preset="top-left")
        assert layer.position_preset == PositionPreset.TOP_LEFT

        layer = StampLayer(
            path="/test.png", duration=1.0, position_preset="bottom-right"
        )
        assert layer.position_preset == PositionPreset.BOTTOM_RIGHT
