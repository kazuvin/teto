"""Tests for models.project module."""

import pytest
import json
from pathlib import Path
from pydantic import ValidationError
from teto_core.models import Project, Timeline, OutputConfig, SubtitleItem


@pytest.mark.unit
class TestTimeline:
    """Test suite for Timeline model."""

    def test_timeline_creation_empty(self):
        """Test creating an empty timeline."""
        timeline = Timeline()
        assert timeline.video_layers == []
        assert timeline.audio_layers == []
        assert timeline.subtitle_layers == []

    def test_timeline_with_layers(self):
        """Test creating timeline with layers."""
        from teto_core.models import VideoLayer, AudioLayer, SubtitleLayer

        video_layer = VideoLayer(path="/video.mp4")
        audio_layer = AudioLayer(path="/audio.mp3")
        subtitle_layer = SubtitleLayer()

        timeline = Timeline(
            video_layers=[video_layer],
            audio_layers=[audio_layer],
            subtitle_layers=[subtitle_layer]
        )

        assert len(timeline.video_layers) == 1
        assert len(timeline.audio_layers) == 1
        assert len(timeline.subtitle_layers) == 1


@pytest.mark.unit
class TestProject:
    """Test suite for Project model."""

    def test_project_minimal_creation(self):
        """Test creating a minimal project."""
        output = OutputConfig(path="/output/video.mp4")
        project = Project(output=output)

        assert project.version == "1.0"
        assert project.output.path == "/output/video.mp4"
        assert isinstance(project.timeline, Timeline)

    def test_project_with_custom_version(self):
        """Test creating project with custom version."""
        output = OutputConfig(path="/output/video.mp4")
        project = Project(output=output, version="2.0")
        assert project.version == "2.0"

    def test_project_with_timeline(self):
        """Test creating project with custom timeline."""
        from teto_core.models import VideoLayer

        output = OutputConfig(path="/output/video.mp4")
        timeline = Timeline(
            video_layers=[VideoLayer(path="/test.mp4")]
        )
        project = Project(output=output, timeline=timeline)

        assert len(project.timeline.video_layers) == 1

    def test_project_output_required(self):
        """Test that output config is required."""
        with pytest.raises(ValidationError):
            Project()

    def test_project_to_json_file(self, temp_dir):
        """Test saving project to JSON file."""
        output = OutputConfig(path="/output/video.mp4")
        project = Project(output=output)

        json_path = temp_dir / "project.json"
        project.to_json_file(str(json_path))

        assert json_path.exists()

        # Verify content
        with open(json_path, "r") as f:
            data = json.load(f)

        assert data["version"] == "1.0"
        assert data["output"]["path"] == "/output/video.mp4"

    def test_project_from_json_file(self, temp_dir):
        """Test loading project from JSON file."""
        # Create a JSON file
        json_data = {
            "version": "1.0",
            "output": {
                "path": "/output/test.mp4",
                "width": 1920,
                "height": 1080,
                "fps": 30,
                "codec": "libx264",
                "audio_codec": "aac",
                "subtitle_mode": "burn"
            },
            "timeline": {
                "video_layers": [],
                "audio_layers": [],
                "subtitle_layers": []
            }
        }

        json_path = temp_dir / "project.json"
        with open(json_path, "w") as f:
            json.dump(json_data, f)

        # Load project
        project = Project.from_json_file(str(json_path))

        assert project.version == "1.0"
        assert project.output.path == "/output/test.mp4"
        assert project.output.width == 1920
        assert isinstance(project.timeline, Timeline)

    def test_project_round_trip(self, temp_dir):
        """Test saving and loading project produces same result."""
        from teto_core.models import VideoLayer, SubtitleLayer

        output = OutputConfig(
            path="/output/video.mp4",
            width=1280,
            height=720,
            fps=24
        )
        timeline = Timeline(
            video_layers=[VideoLayer(path="/test.mp4")],
            subtitle_layers=[SubtitleLayer()]
        )
        original_project = Project(
            version="1.5",
            output=output,
            timeline=timeline
        )

        # Save
        json_path = temp_dir / "project.json"
        original_project.to_json_file(str(json_path))

        # Load
        loaded_project = Project.from_json_file(str(json_path))

        # Compare
        assert loaded_project.version == original_project.version
        assert loaded_project.output.path == original_project.output.path
        assert loaded_project.output.width == original_project.output.width
        assert loaded_project.output.height == original_project.output.height
        assert loaded_project.output.fps == original_project.output.fps
        assert len(loaded_project.timeline.video_layers) == 1
        assert len(loaded_project.timeline.subtitle_layers) == 1

    def test_project_with_complex_timeline(self, temp_dir):
        """Test project with complex timeline serialization."""
        from teto_core.models import VideoLayer, AudioLayer, SubtitleLayer, ImageLayer

        output = OutputConfig(path="/output/video.mp4")
        timeline = Timeline(
            video_layers=[
                VideoLayer(path="/video1.mp4", start_time=0, volume=0.8),
                ImageLayer(path="/image1.png", duration=5.0, start_time=10)
            ],
            audio_layers=[
                AudioLayer(path="/audio1.mp3", volume=0.5)
            ],
            subtitle_layers=[
                SubtitleLayer(
                    items=[
                        SubtitleItem(text="Hello", start_time=0, end_time=2),
                        SubtitleItem(text="World", start_time=2, end_time=4)
                    ],
                    font_size="lg",
                    position="top"
                )
            ]
        )
        project = Project(output=output, timeline=timeline)

        # Save and load
        json_path = temp_dir / "complex_project.json"
        project.to_json_file(str(json_path))
        loaded = Project.from_json_file(str(json_path))

        # Verify structure
        assert len(loaded.timeline.video_layers) == 2
        assert len(loaded.timeline.audio_layers) == 1
        assert len(loaded.timeline.subtitle_layers) == 1
        assert len(loaded.timeline.subtitle_layers[0].items) == 2
