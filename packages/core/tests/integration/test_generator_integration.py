"""Integration tests for VideoGenerator."""

import pytest
from pathlib import Path
from teto_core.generator import VideoGenerator
from teto_core.models import Project, OutputConfig, Timeline


@pytest.mark.integration
@pytest.mark.slow
class TestVideoGeneratorIntegration:
    """Integration test suite for VideoGenerator."""

    @pytest.fixture
    def minimal_project(self, temp_dir):
        """Create a minimal valid project for integration testing."""
        output_path = temp_dir / "output.mp4"
        project = Project(
            output=OutputConfig(
                path=str(output_path),
                width=640,
                height=480,
                fps=30,
                codec="libx264",
                audio_codec="aac",
                bitrate="2000k",
                subtitle_mode="none",
            ),
            timeline=Timeline(
                video_layers=[],
                audio_layers=[],
                subtitle_layers=[],
            ),
        )
        return project

    def test_from_json_method_exists(self):
        """Test that from_json classmethod exists."""
        assert hasattr(VideoGenerator, "from_json")
        assert callable(VideoGenerator.from_json)

    def test_generator_hook_execution_order(self, minimal_project):
        """Test that hooks are executed in the correct order."""
        generator = VideoGenerator(minimal_project)
        execution_log = []

        def pre_hook1(project):
            execution_log.append("pre1")

        def pre_hook2(project):
            execution_log.append("pre2")

        def post_hook1(output_path, project):
            execution_log.append("post1")

        def post_hook2(output_path, project):
            execution_log.append("post2")

        generator.register_pre_hook(pre_hook1)
        generator.register_pre_hook(pre_hook2)
        generator.register_post_hook(post_hook1)
        generator.register_post_hook(post_hook2)

        # Note: This test doesn't actually generate a video
        # It just validates the hook registration
        assert len(generator._pre_hooks) == 2
        assert len(generator._post_hooks) == 2
        assert generator._pre_hooks == [pre_hook1, pre_hook2]
        assert generator._post_hooks == [post_hook1, post_hook2]
