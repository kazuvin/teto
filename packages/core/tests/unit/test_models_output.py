"""Tests for models.output module."""

import pytest
from pydantic import ValidationError
from teto_core.models import OutputConfig


@pytest.mark.unit
class TestOutputConfig:
    """Test suite for OutputConfig model."""

    def test_output_config_minimal(self):
        """Test creating output config with minimal required fields."""
        config = OutputConfig(path="/output/video.mp4")
        assert config.path == "/output/video.mp4"
        assert config.width == 1920
        assert config.height == 1080
        assert config.fps == 30
        assert config.codec == "libx264"
        assert config.audio_codec == "aac"
        assert config.bitrate is None
        assert config.subtitle_mode == "burn"

    def test_output_config_custom_resolution(self):
        """Test output config with custom resolution."""
        config = OutputConfig(path="/output/video.mp4", width=1280, height=720)
        assert config.width == 1280
        assert config.height == 720

    def test_output_config_4k_resolution(self):
        """Test output config with 4K resolution."""
        config = OutputConfig(path="/output/video.mp4", width=3840, height=2160)
        assert config.width == 3840
        assert config.height == 2160

    def test_output_config_custom_fps(self):
        """Test output config with custom fps."""
        config = OutputConfig(path="/output/video.mp4", fps=60)
        assert config.fps == 60

    def test_output_config_custom_codecs(self):
        """Test output config with custom codecs."""
        config = OutputConfig(
            path="/output/video.mp4", codec="libx265", audio_codec="mp3"
        )
        assert config.codec == "libx265"
        assert config.audio_codec == "mp3"

    def test_output_config_with_bitrate(self):
        """Test output config with bitrate."""
        config = OutputConfig(path="/output/video.mp4", bitrate="5000k")
        assert config.bitrate == "5000k"

    def test_output_config_subtitle_mode_burn(self):
        """Test subtitle mode: burn."""
        config = OutputConfig(path="/output/video.mp4", subtitle_mode="burn")
        assert config.subtitle_mode == "burn"

    def test_output_config_subtitle_mode_srt(self):
        """Test subtitle mode: srt."""
        config = OutputConfig(path="/output/video.mp4", subtitle_mode="srt")
        assert config.subtitle_mode == "srt"

    def test_output_config_subtitle_mode_vtt(self):
        """Test subtitle mode: vtt."""
        config = OutputConfig(path="/output/video.mp4", subtitle_mode="vtt")
        assert config.subtitle_mode == "vtt"

    def test_output_config_subtitle_mode_none(self):
        """Test subtitle mode: none."""
        config = OutputConfig(path="/output/video.mp4", subtitle_mode="none")
        assert config.subtitle_mode == "none"

    def test_output_config_invalid_subtitle_mode(self):
        """Test that invalid subtitle mode raises validation error."""
        with pytest.raises(ValidationError):
            OutputConfig(path="/output/video.mp4", subtitle_mode="invalid")

    def test_output_config_width_must_be_positive(self):
        """Test that width must be positive."""
        with pytest.raises(ValidationError):
            OutputConfig(path="/output/video.mp4", width=0)

        with pytest.raises(ValidationError):
            OutputConfig(path="/output/video.mp4", width=-100)

    def test_output_config_height_must_be_positive(self):
        """Test that height must be positive."""
        with pytest.raises(ValidationError):
            OutputConfig(path="/output/video.mp4", height=0)

        with pytest.raises(ValidationError):
            OutputConfig(path="/output/video.mp4", height=-100)

    def test_output_config_fps_must_be_positive(self):
        """Test that fps must be positive."""
        with pytest.raises(ValidationError):
            OutputConfig(path="/output/video.mp4", fps=0)

        with pytest.raises(ValidationError):
            OutputConfig(path="/output/video.mp4", fps=-30)

    def test_output_config_path_required(self):
        """Test that path is required."""
        with pytest.raises(ValidationError):
            OutputConfig()

    def test_output_config_full_configuration(self):
        """Test output config with all fields specified."""
        config = OutputConfig(
            path="/output/video.mp4",
            width=1280,
            height=720,
            fps=24,
            codec="libx265",
            audio_codec="opus",
            bitrate="3000k",
            subtitle_mode="srt",
        )
        assert config.path == "/output/video.mp4"
        assert config.width == 1280
        assert config.height == 720
        assert config.fps == 24
        assert config.codec == "libx265"
        assert config.audio_codec == "opus"
        assert config.bitrate == "3000k"
        assert config.subtitle_mode == "srt"
