"""Pytest configuration and shared fixtures."""

import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_image_path(temp_dir):
    """Create a sample image for testing."""
    from PIL import Image

    img = Image.new("RGB", (100, 100), color="red")
    img_path = temp_dir / "test_image.png"
    img.save(img_path)
    return img_path


@pytest.fixture
def sample_output_path(temp_dir):
    """Provide a path for test output."""
    return temp_dir / "output.mp4"
