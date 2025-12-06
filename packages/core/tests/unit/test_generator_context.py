"""Tests for generator context module."""

import pytest
from unittest.mock import MagicMock, Mock

from teto_core.generator.context import ProcessingContext


@pytest.fixture
def mock_project():
    """Create a mock project for testing."""
    project = MagicMock()
    project.output = MagicMock()
    project.output.path = "/tmp/output.mp4"
    project.output.fps = 30
    return project


@pytest.mark.unit
class TestProcessingContext:
    """Test suite for ProcessingContext."""

    def test_create_with_project(self, mock_project):
        """Test creating context with project."""
        context = ProcessingContext(project=mock_project)

        assert context.project is mock_project
        assert context.video_clip is None
        assert context.audio_clip is None
        assert context.output_size is None
        assert context.progress_callback is None

    def test_set_video_clip(self, mock_project):
        """Test setting video clip."""
        context = ProcessingContext(project=mock_project)
        mock_clip = MagicMock()

        context.video_clip = mock_clip

        assert context.video_clip is mock_clip

    def test_set_audio_clip(self, mock_project):
        """Test setting audio clip."""
        context = ProcessingContext(project=mock_project)
        mock_clip = MagicMock()

        context.audio_clip = mock_clip

        assert context.audio_clip is mock_clip

    def test_set_output_size(self, mock_project):
        """Test setting output size."""
        context = ProcessingContext(project=mock_project)

        context.output_size = (1920, 1080)

        assert context.output_size == (1920, 1080)

    def test_report_progress_with_callback(self, mock_project):
        """Test report_progress calls callback."""
        callback = Mock()
        context = ProcessingContext(
            project=mock_project, progress_callback=callback
        )

        context.report_progress("Processing step 1...")

        callback.assert_called_once_with("Processing step 1...")

    def test_report_progress_without_callback(self, mock_project):
        """Test report_progress without callback doesn't raise."""
        context = ProcessingContext(project=mock_project)

        # Should not raise
        context.report_progress("Processing step 1...")

    def test_report_progress_multiple_calls(self, mock_project):
        """Test report_progress can be called multiple times."""
        callback = Mock()
        context = ProcessingContext(
            project=mock_project, progress_callback=callback
        )

        context.report_progress("Step 1")
        context.report_progress("Step 2")
        context.report_progress("Step 3")

        assert callback.call_count == 3
        callback.assert_any_call("Step 1")
        callback.assert_any_call("Step 2")
        callback.assert_any_call("Step 3")

    def test_create_with_all_attributes(self, mock_project):
        """Test creating context with all attributes."""
        mock_video = MagicMock()
        mock_audio = MagicMock()
        callback = Mock()

        context = ProcessingContext(
            project=mock_project,
            video_clip=mock_video,
            audio_clip=mock_audio,
            output_size=(1280, 720),
            progress_callback=callback,
        )

        assert context.project is mock_project
        assert context.video_clip is mock_video
        assert context.audio_clip is mock_audio
        assert context.output_size == (1280, 720)
        assert context.progress_callback is callback
