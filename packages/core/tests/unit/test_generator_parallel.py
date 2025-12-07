"""Tests for parallel video generation."""

import pytest
from unittest.mock import Mock, patch
from concurrent.futures import ThreadPoolExecutor
from teto_core import VideoGenerator
from teto_core.models import Project
from teto_core.output_config.models import OutputConfig


@pytest.mark.unit
class TestGenerateMultiParallel:
    """Test suite for generate_multi_parallel method."""

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
        project.output.object_fit = "cover"
        project.timeline = Mock()
        project.timeline.video_layers = []
        project.timeline.audio_layers = []
        project.timeline.subtitle_layers = []
        project.model_dump = Mock(
            return_value={
                "output": {
                    "path": "/tmp/output.mp4",
                    "width": 1920,
                    "height": 1080,
                },
                "timeline": {
                    "video_layers": [],
                    "audio_layers": [],
                    "subtitle_layers": [],
                },
            }
        )
        return project

    @pytest.fixture
    def output_configs(self, temp_dir):
        """Create test output configs."""
        return [
            OutputConfig(path=str(temp_dir / "youtube.mp4"), width=1920, height=1080),
            OutputConfig(path=str(temp_dir / "tiktok.mp4"), width=1080, height=1920),
            OutputConfig(path=str(temp_dir / "instagram.mp4"), width=1080, height=1080),
        ]

    def test_generate_multi_parallel_returns_all_paths(
        self, mock_project, output_configs
    ):
        """Test that all output paths are returned."""
        generator = VideoGenerator(mock_project)

        with patch(
            "teto_core.generator.parallel._create_generator_and_run"
        ) as mock_create:
            # Mock to return the path from output_config (with verbose parameter)
            mock_create.side_effect = lambda p, c, v: c["path"]

            result = generator.generate_multi_parallel(
                output_configs, _executor_class=ThreadPoolExecutor
            )

            assert len(result) == len(output_configs)
            for i, config in enumerate(output_configs):
                assert result[i] == config.path

    def test_generate_multi_parallel_respects_max_workers(
        self, mock_project, output_configs
    ):
        """Test that max_workers parameter is used."""
        generator = VideoGenerator(mock_project)
        max_workers = 2

        with patch(
            "teto_core.generator.parallel._create_generator_and_run"
        ) as mock_create:
            mock_create.side_effect = lambda p, c, v: c["path"]

            result = generator.generate_multi_parallel(
                output_configs,
                max_workers=max_workers,
                _executor_class=ThreadPoolExecutor,
            )

            assert len(result) == len(output_configs)

    def test_generate_multi_parallel_calls_progress_callback(
        self, mock_project, output_configs
    ):
        """Test that progress callback is called for each completed output."""
        generator = VideoGenerator(mock_project)
        progress_callback = Mock()

        with patch(
            "teto_core.generator.parallel._create_generator_and_run"
        ) as mock_create:
            mock_create.side_effect = lambda p, c, v: c["path"]

            generator.generate_multi_parallel(
                output_configs,
                progress_callback=progress_callback,
                _executor_class=ThreadPoolExecutor,
            )

            # Progress callback should be called for start + each completion
            # 1 for start + 3 for completions = 4 calls
            assert progress_callback.call_count == 1 + len(output_configs)

    def test_generate_multi_parallel_executes_pre_hooks(
        self, mock_project, output_configs
    ):
        """Test that pre-hooks are executed before parallel generation."""
        generator = VideoGenerator(mock_project)
        pre_hook = Mock()
        generator.register_pre_hook(pre_hook)

        with patch(
            "teto_core.generator.parallel._create_generator_and_run"
        ) as mock_create:
            mock_create.side_effect = lambda p, c, v: c["path"]

            generator.generate_multi_parallel(
                output_configs, _executor_class=ThreadPoolExecutor
            )

            pre_hook.assert_called_once_with(mock_project)

    def test_generate_multi_parallel_executes_post_hooks(
        self, mock_project, output_configs
    ):
        """Test that post-hooks are executed for each completed output."""
        generator = VideoGenerator(mock_project)
        post_hook = Mock()
        generator.register_post_hook(post_hook)

        with patch(
            "teto_core.generator.parallel._create_generator_and_run"
        ) as mock_create:
            mock_create.side_effect = lambda p, c, v: c["path"]

            generator.generate_multi_parallel(
                output_configs, _executor_class=ThreadPoolExecutor
            )

            # Post hook should be called for each output
            assert post_hook.call_count == len(output_configs)

    def test_generate_multi_parallel_handles_dict_configs(self, mock_project, temp_dir):
        """Test that dict configs are converted to OutputConfig."""
        generator = VideoGenerator(mock_project)

        dict_configs = [
            {"path": str(temp_dir / "output1.mp4"), "width": 1920, "height": 1080},
            {"path": str(temp_dir / "output2.mp4"), "width": 1080, "height": 1920},
        ]

        with patch(
            "teto_core.generator.parallel._create_generator_and_run"
        ) as mock_create:
            mock_create.side_effect = lambda p, c, v: c["path"]

            result = generator.generate_multi_parallel(
                dict_configs, _executor_class=ThreadPoolExecutor
            )

            assert len(result) == len(dict_configs)
            assert result[0] == dict_configs[0]["path"]
            assert result[1] == dict_configs[1]["path"]

    def test_generate_multi_parallel_raises_on_failure(
        self, mock_project, output_configs
    ):
        """Test that RuntimeError is raised when generation fails."""
        generator = VideoGenerator(mock_project)

        with patch(
            "teto_core.generator.parallel._create_generator_and_run"
        ) as mock_create:
            # Second call fails
            def side_effect(p, c, v):
                if "tiktok" in c["path"]:
                    raise Exception("Encoding failed")
                return c["path"]

            mock_create.side_effect = side_effect

            with pytest.raises(RuntimeError) as exc_info:
                generator.generate_multi_parallel(
                    output_configs, _executor_class=ThreadPoolExecutor
                )

            assert "Failed to generate" in str(exc_info.value)

    def test_generate_multi_parallel_maintains_order(
        self, mock_project, output_configs
    ):
        """Test that output paths maintain input order even with parallel execution."""
        generator = VideoGenerator(mock_project)

        with patch(
            "teto_core.generator.parallel._create_generator_and_run"
        ) as mock_create:
            mock_create.side_effect = lambda p, c, v: c["path"]

            result = generator.generate_multi_parallel(
                output_configs, _executor_class=ThreadPoolExecutor
            )

            # Results should be in original order
            assert result[0] == output_configs[0].path
            assert result[1] == output_configs[1].path
            assert result[2] == output_configs[2].path


@pytest.mark.unit
class TestGenerateSingleOutput:
    """Test suite for generate_single_output worker function."""

    def test_generate_single_output_creates_generator(self):
        """Test that worker function creates VideoGenerator correctly."""
        from teto_core.generator.parallel import generate_single_output

        project_dict = {
            "output": {
                "path": "/tmp/test.mp4",
                "width": 1920,
                "height": 1080,
                "fps": 30,
                "codec": "libx264",
                "audio_codec": "aac",
                "bitrate": None,
                "preset": "fast",
                "subtitle_mode": "burn",
                "object_fit": "cover",
            },
            "timeline": {
                "video_layers": [],
                "audio_layers": [],
                "subtitle_layers": [],
            },
        }

        output_config_dict = {
            "path": "/tmp/output.mp4",
            "width": 1920,
            "height": 1080,
            "fps": 30,
            "codec": "libx264",
            "audio_codec": "aac",
            "bitrate": None,
            "preset": "fast",
            "subtitle_mode": "burn",
            "object_fit": "cover",
        }

        with patch(
            "teto_core.generator.parallel._create_generator_and_run"
        ) as mock_create:
            mock_create.return_value = "/tmp/output.mp4"

            result = generate_single_output(project_dict, output_config_dict)

            # verbose defaults to True
            mock_create.assert_called_once_with(project_dict, output_config_dict, True)
            assert result == "/tmp/output.mp4"

    def test_generate_single_output_raises_on_error(self):
        """Test that worker function raises RuntimeError on failure."""
        from teto_core.generator.parallel import generate_single_output

        project_dict = {
            "output": {
                "path": "/tmp/test.mp4",
                "width": 1920,
                "height": 1080,
                "fps": 30,
                "codec": "libx264",
                "audio_codec": "aac",
                "bitrate": None,
                "preset": "fast",
                "subtitle_mode": "burn",
                "object_fit": "cover",
            },
            "timeline": {
                "video_layers": [],
                "audio_layers": [],
                "subtitle_layers": [],
            },
        }

        output_config_dict = {
            "path": "/tmp/output.mp4",
            "width": 1920,
            "height": 1080,
            "fps": 30,
            "codec": "libx264",
            "audio_codec": "aac",
            "bitrate": None,
            "preset": "fast",
            "subtitle_mode": "burn",
            "object_fit": "cover",
        }

        with patch(
            "teto_core.generator.parallel._create_generator_and_run"
        ) as mock_create:
            mock_create.side_effect = Exception("Encoding failed")

            with pytest.raises(RuntimeError) as exc_info:
                generate_single_output(project_dict, output_config_dict)

            assert "Failed to generate" in str(exc_info.value)
            assert "/tmp/output.mp4" in str(exc_info.value)
