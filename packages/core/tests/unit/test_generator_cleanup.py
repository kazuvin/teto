"""Tests for generator cleanup step module."""

import pytest
from unittest.mock import MagicMock, Mock

from teto_core.generator.steps.cleanup import CleanupStep
from teto_core.generator.context import ProcessingContext


@pytest.fixture
def mock_project():
    """Create a mock project for testing."""
    project = MagicMock()
    return project


@pytest.fixture
def mock_video_clip():
    """Create a mock video clip for testing."""
    clip = MagicMock()
    clip.close = Mock()
    return clip


@pytest.fixture
def mock_audio_clip():
    """Create a mock audio clip for testing."""
    clip = MagicMock()
    clip.close = Mock()
    return clip


@pytest.mark.unit
class TestCleanupStep:
    """Test suite for CleanupStep."""

    def test_cleanup_closes_video_clip(self, mock_project, mock_video_clip):
        """Test that cleanup closes video clip."""
        context = ProcessingContext(
            project=mock_project, video_clip=mock_video_clip
        )
        step = CleanupStep()

        step.process(context)

        mock_video_clip.close.assert_called_once()

    def test_cleanup_closes_audio_clip(self, mock_project, mock_audio_clip):
        """Test that cleanup closes audio clip."""
        context = ProcessingContext(
            project=mock_project, audio_clip=mock_audio_clip
        )
        step = CleanupStep()

        step.process(context)

        mock_audio_clip.close.assert_called_once()

    def test_cleanup_closes_both_clips(
        self, mock_project, mock_video_clip, mock_audio_clip
    ):
        """Test that cleanup closes both clips."""
        context = ProcessingContext(
            project=mock_project,
            video_clip=mock_video_clip,
            audio_clip=mock_audio_clip,
        )
        step = CleanupStep()

        step.process(context)

        mock_video_clip.close.assert_called_once()
        mock_audio_clip.close.assert_called_once()

    def test_cleanup_without_clips(self, mock_project):
        """Test that cleanup works without clips."""
        context = ProcessingContext(project=mock_project)
        step = CleanupStep()

        # Should not raise
        result = step.process(context)

        assert result is context

    def test_cleanup_returns_context(
        self, mock_project, mock_video_clip, mock_audio_clip
    ):
        """Test that cleanup returns context."""
        context = ProcessingContext(
            project=mock_project,
            video_clip=mock_video_clip,
            audio_clip=mock_audio_clip,
        )
        step = CleanupStep()

        result = step.process(context)

        assert result is context

    def test_cleanup_reports_progress(self, mock_project):
        """Test that cleanup reports progress."""
        callback = Mock()
        context = ProcessingContext(
            project=mock_project, progress_callback=callback
        )
        step = CleanupStep()

        step.process(context)

        callback.assert_called_with("完了！")

    def test_cleanup_with_only_video(self, mock_project, mock_video_clip):
        """Test cleanup with only video clip."""
        context = ProcessingContext(
            project=mock_project, video_clip=mock_video_clip
        )
        step = CleanupStep()

        step.process(context)

        mock_video_clip.close.assert_called_once()

    def test_cleanup_with_only_audio(self, mock_project, mock_audio_clip):
        """Test cleanup with only audio clip."""
        context = ProcessingContext(
            project=mock_project, audio_clip=mock_audio_clip
        )
        step = CleanupStep()

        step.process(context)

        mock_audio_clip.close.assert_called_once()
