"""Tests for VideoGenerator class."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
from teto_core import VideoGenerator
from teto_core.models import Project


@pytest.mark.unit
class TestVideoGenerator:
    """Test suite for VideoGenerator class."""

    @pytest.fixture
    def mock_project(self):
        """Create a mock project for testing."""
        project = Mock(spec=Project)
        project.output = Mock()
        project.output.width = 1920
        project.output.height = 1080
        project.output.fps = 30
        project.output.codec = "libx264"
        project.output.audio_codec = "aac"
        project.output.bitrate = "5000k"
        project.output.path = "/tmp/output.mp4"
        project.output.subtitle_mode = "burn"
        project.timeline = Mock()
        project.timeline.video_layers = []
        project.timeline.audio_layers = []
        project.timeline.subtitle_layers = []
        return project

    def test_generator_initialization(self, mock_project):
        """Test VideoGenerator initialization."""
        generator = VideoGenerator(mock_project)
        assert generator.project == mock_project
        assert generator._pre_hooks == []
        assert generator._post_hooks == []
        assert generator._custom_processors == {}

    def test_register_pre_hook(self, mock_project):
        """Test registering pre-generation hooks."""
        generator = VideoGenerator(mock_project)
        hook_func = Mock()
        generator.register_pre_hook(hook_func)
        assert len(generator._pre_hooks) == 1
        assert generator._pre_hooks[0] == hook_func

    def test_register_post_hook(self, mock_project):
        """Test registering post-generation hooks."""
        generator = VideoGenerator(mock_project)
        hook_func = Mock()
        generator.register_post_hook(hook_func)
        assert len(generator._post_hooks) == 1
        assert generator._post_hooks[0] == hook_func

    def test_register_processor(self, mock_project):
        """Test registering custom processors."""
        generator = VideoGenerator(mock_project)
        custom_processor = Mock()
        generator.register_processor("custom", custom_processor)
        assert "custom" in generator._custom_processors
        assert generator._custom_processors["custom"] == custom_processor

    def test_get_processor(self, mock_project):
        """Test retrieving registered processors."""
        generator = VideoGenerator(mock_project)
        custom_processor = Mock()
        generator.register_processor("custom", custom_processor)

        # Get existing processor
        result = generator.get_processor("custom")
        assert result == custom_processor

        # Get non-existing processor
        result = generator.get_processor("nonexistent")
        assert result is None

    def test_multiple_hooks(self, mock_project):
        """Test registering multiple hooks."""
        generator = VideoGenerator(mock_project)
        pre_hook1 = Mock()
        pre_hook2 = Mock()
        post_hook1 = Mock()
        post_hook2 = Mock()

        generator.register_pre_hook(pre_hook1)
        generator.register_pre_hook(pre_hook2)
        generator.register_post_hook(post_hook1)
        generator.register_post_hook(post_hook2)

        assert len(generator._pre_hooks) == 2
        assert len(generator._post_hooks) == 2
