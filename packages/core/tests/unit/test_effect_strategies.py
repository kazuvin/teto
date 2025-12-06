"""Tests for effect strategies module."""

import pytest
import numpy as np
from unittest.mock import Mock, MagicMock

from teto_core.effect.models import AnimationEffect
from teto_core.effect.strategies.fade import FadeInEffect, FadeOutEffect
from teto_core.effect.strategies.zoom import ZoomEffect, KenBurnsEffect
from teto_core.effect.strategies.blur import BlurEffect
from teto_core.effect.strategies.slide import SlideInEffect, SlideOutEffect


@pytest.fixture
def simple_frame():
    """Create a simple RGB frame for testing."""
    return np.full((100, 100, 3), 128, dtype=np.uint8)


@pytest.fixture
def simple_frame_rgba():
    """Create a simple RGBA frame for testing."""
    frame = np.full((100, 100, 4), 128, dtype=np.uint8)
    frame[:, :, 3] = 255  # Full opacity
    return frame


class TransformableClip:
    """A helper class that captures transform functions for testing."""

    def __init__(self, duration: float = 5.0):
        self.duration = duration
        self._transform_fn = None

    def transform(self, fn):
        new_clip = TransformableClip(self.duration)
        new_clip._transform_fn = fn
        return new_clip


@pytest.fixture
def mock_clip():
    """Create a mock video clip."""
    return TransformableClip(duration=5.0)


@pytest.fixture
def video_size():
    """Standard video size for testing."""
    return (1920, 1080)


@pytest.mark.unit
class TestFadeInEffect:
    """Test suite for FadeInEffect."""

    def test_apply_returns_clip(self, mock_clip):
        """Test that apply returns a clip."""
        effect = AnimationEffect(type="fadein", duration=1.0)
        fade_in = FadeInEffect()
        video_size = (1920, 1080)

        result = fade_in.apply(mock_clip, effect, video_size)
        assert result is not None
        assert hasattr(result, "_transform_fn")

    def test_fadein_at_start_is_black(self, simple_frame, mock_clip):
        """Test that fade in starts with black (opacity 0)."""
        effect = AnimationEffect(type="fadein", duration=1.0, easing="linear")
        fade_in = FadeInEffect()

        result_clip = fade_in.apply(mock_clip, effect, (1920, 1080))

        # Get the transform function
        transform_fn = result_clip._transform_fn

        # At t=0, frame should be all zeros (fully transparent)
        result = transform_fn(lambda t: simple_frame.copy(), 0.0)
        assert np.all(result == 0)

    def test_fadein_at_end_is_full(self, simple_frame, mock_clip):
        """Test that fade in ends with full opacity."""
        effect = AnimationEffect(type="fadein", duration=1.0, easing="linear")
        fade_in = FadeInEffect()

        result_clip = fade_in.apply(mock_clip, effect, (1920, 1080))
        transform_fn = result_clip._transform_fn

        # At t=duration, frame should be at full brightness
        result = transform_fn(lambda t: simple_frame.copy(), 1.0)
        assert np.allclose(result, simple_frame, atol=1)

    def test_fadein_after_duration_is_unchanged(self, simple_frame, mock_clip):
        """Test that after duration, frame is unchanged."""
        effect = AnimationEffect(type="fadein", duration=1.0)
        fade_in = FadeInEffect()

        result_clip = fade_in.apply(mock_clip, effect, (1920, 1080))
        transform_fn = result_clip._transform_fn

        # At t > duration, frame should be unchanged
        result = transform_fn(lambda t: simple_frame.copy(), 2.0)
        assert np.array_equal(result, simple_frame)


@pytest.mark.unit
class TestFadeOutEffect:
    """Test suite for FadeOutEffect."""

    def test_apply_returns_clip(self, mock_clip):
        """Test that apply returns a clip."""
        effect = AnimationEffect(type="fadeout", duration=1.0)
        fade_out = FadeOutEffect()
        video_size = (1920, 1080)

        result = fade_out.apply(mock_clip, effect, video_size)
        assert result is not None
        assert hasattr(result, "_transform_fn")

    def test_fadeout_before_end_is_full(self, simple_frame, mock_clip):
        """Test that before fadeout starts, frame is full brightness."""
        effect = AnimationEffect(type="fadeout", duration=1.0, easing="linear")
        fade_out = FadeOutEffect()

        result_clip = fade_out.apply(mock_clip, effect, (1920, 1080))
        transform_fn = result_clip._transform_fn

        # At t=0 (well before end), frame should be unchanged
        result = transform_fn(lambda t: simple_frame.copy(), 0.0)
        assert np.array_equal(result, simple_frame)

    def test_fadeout_at_end_is_black(self, simple_frame, mock_clip):
        """Test that at the end, frame is black."""
        effect = AnimationEffect(type="fadeout", duration=1.0, easing="linear")
        fade_out = FadeOutEffect()

        result_clip = fade_out.apply(mock_clip, effect, (1920, 1080))
        transform_fn = result_clip._transform_fn

        # At t=5.0 (exact end), frame should be all zeros
        result = transform_fn(lambda t: simple_frame.copy(), 5.0)
        assert np.all(result == 0)


@pytest.mark.unit
class TestBlurEffect:
    """Test suite for BlurEffect."""

    def test_apply_returns_clip(self, mock_clip):
        """Test that apply returns a clip."""
        effect = AnimationEffect(type="blur", duration=1.0, blur_amount=3.0)
        blur = BlurEffect()

        result = blur.apply(mock_clip, effect, (1920, 1080))
        assert result is not None
        assert hasattr(result, "_transform_fn")

    def test_blur_applies_gaussian(self, mock_clip):
        """Test that blur applies gaussian filter."""
        effect = AnimationEffect(type="blur", duration=1.0, blur_amount=5.0)
        blur = BlurEffect()

        result_clip = blur.apply(mock_clip, effect, (1920, 1080))
        transform_fn = result_clip._transform_fn

        # Create a frame with a sharp edge
        sharp_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        sharp_frame[:, 50:, :] = 255

        result = transform_fn(lambda t: sharp_frame, 0.0)

        # After blur, the edge should be smoothed
        # The center column should have intermediate values
        center_values = result[50, 50, 0]
        assert 0 < center_values < 255

    def test_blur_handles_grayscale(self, mock_clip):
        """Test that blur handles grayscale images."""
        effect = AnimationEffect(type="blur", duration=1.0, blur_amount=3.0)
        blur = BlurEffect()

        result_clip = blur.apply(mock_clip, effect, (1920, 1080))
        transform_fn = result_clip._transform_fn

        grayscale_frame = np.full((100, 100), 128, dtype=np.uint8)
        result = transform_fn(lambda t: grayscale_frame, 0.0)

        assert result.shape == (100, 100)

    def test_blur_default_amount(self, simple_frame, mock_clip):
        """Test blur with default amount."""
        effect = AnimationEffect(type="blur", duration=1.0)  # No blur_amount
        blur = BlurEffect()

        result_clip = blur.apply(mock_clip, effect, (1920, 1080))
        transform_fn = result_clip._transform_fn

        # Should not raise error with default blur amount
        result = transform_fn(lambda t: simple_frame.copy(), 0.0)
        assert result.shape == simple_frame.shape


@pytest.mark.unit
class TestZoomEffect:
    """Test suite for ZoomEffect."""

    def test_apply_returns_clip(self, mock_clip):
        """Test that apply returns a clip."""
        effect = AnimationEffect(
            type="zoom", duration=1.0, start_scale=1.0, end_scale=1.5
        )
        zoom = ZoomEffect()

        result = zoom.apply(mock_clip, effect, (1920, 1080))
        assert result is not None
        assert hasattr(result, "_transform_fn")

    def test_zoom_at_start_has_start_scale(self, simple_frame, mock_clip):
        """Test that zoom at t=0 uses start_scale."""
        effect = AnimationEffect(
            type="zoom", duration=5.0, start_scale=1.0, end_scale=2.0, easing="linear"
        )
        zoom = ZoomEffect()

        result_clip = zoom.apply(mock_clip, effect, (1920, 1080))
        transform_fn = result_clip._transform_fn

        # At t=0, scale should be 1.0, so output shape should match input
        result = transform_fn(lambda t: simple_frame.copy(), 0.0)
        assert result.shape[:2] == simple_frame.shape[:2]

    def test_zoom_default_scales(self, simple_frame, mock_clip):
        """Test zoom with default scale values."""
        effect = AnimationEffect(type="zoom", duration=1.0)  # No scale specified
        zoom = ZoomEffect()

        result_clip = zoom.apply(mock_clip, effect, (1920, 1080))
        transform_fn = result_clip._transform_fn

        # Should not raise error with default scales
        result = transform_fn(lambda t: simple_frame.copy(), 0.0)
        assert result.shape[:2] == simple_frame.shape[:2]


@pytest.mark.unit
class TestKenBurnsEffect:
    """Test suite for KenBurnsEffect."""

    def test_apply_returns_clip(self, mock_clip):
        """Test that apply returns a clip."""
        effect = AnimationEffect(
            type="kenBurns",
            duration=1.0,
            start_scale=1.0,
            end_scale=1.3,
            pan_start=(0.0, 0.0),
            pan_end=(0.1, 0.1),
        )
        ken_burns = KenBurnsEffect()

        result = ken_burns.apply(mock_clip, effect, (1920, 1080))
        assert result is not None
        assert hasattr(result, "_transform_fn")

    def test_ken_burns_default_values(self, simple_frame, mock_clip):
        """Test Ken Burns with default values."""
        effect = AnimationEffect(type="kenBurns", duration=1.0)
        ken_burns = KenBurnsEffect()

        result_clip = ken_burns.apply(mock_clip, effect, (1920, 1080))
        transform_fn = result_clip._transform_fn

        # Should not raise error with default values
        result = transform_fn(lambda t: simple_frame.copy(), 0.0)
        assert result.shape[:2] == simple_frame.shape[:2]

    def test_ken_burns_preserves_shape(self, simple_frame, mock_clip):
        """Test that Ken Burns preserves frame shape."""
        effect = AnimationEffect(
            type="kenBurns",
            duration=5.0,
            start_scale=1.0,
            end_scale=1.3,
            pan_start=(0.0, 0.0),
            pan_end=(0.1, 0.1),
        )
        ken_burns = KenBurnsEffect()

        result_clip = ken_burns.apply(mock_clip, effect, (1920, 1080))
        transform_fn = result_clip._transform_fn

        for t in [0.0, 1.0, 2.5, 5.0]:
            result = transform_fn(lambda t: simple_frame.copy(), t)
            assert result.shape[:2] == simple_frame.shape[:2]


@pytest.mark.unit
class TestSlideInEffect:
    """Test suite for SlideInEffect."""

    def test_apply_returns_clip(self, mock_clip):
        """Test that apply returns a clip."""
        effect = AnimationEffect(type="slideIn", duration=1.0, direction="left")
        slide_in = SlideInEffect()

        result = slide_in.apply(mock_clip, effect, (1920, 1080))
        assert result is not None
        assert hasattr(result, "_transform_fn")

    def test_slide_in_directions(self, simple_frame, mock_clip):
        """Test slide in from all directions."""
        directions = ["left", "right", "top", "bottom"]

        for direction in directions:
            effect = AnimationEffect(
                type="slideIn", duration=1.0, direction=direction, easing="linear"
            )
            slide_in = SlideInEffect()

            result_clip = slide_in.apply(mock_clip, effect, (200, 200))
            transform_fn = result_clip._transform_fn

            # At t=0, frame should be off-screen
            result_start = transform_fn(lambda t: simple_frame.copy(), 0.0)
            # At t >= duration, frame should be centered
            result_end = transform_fn(lambda t: simple_frame.copy(), 1.0)

            assert result_start.shape == (200, 200, 3)
            assert result_end.shape == (200, 200, 3)

    def test_slide_in_default_direction(self, simple_frame, mock_clip):
        """Test slide in with default direction."""
        effect = AnimationEffect(type="slideIn", duration=1.0)  # No direction
        slide_in = SlideInEffect()

        result_clip = slide_in.apply(mock_clip, effect, (200, 200))
        transform_fn = result_clip._transform_fn

        # Should not raise error with default direction
        result = transform_fn(lambda t: simple_frame.copy(), 0.5)
        assert result.shape == (200, 200, 3)


@pytest.mark.unit
class TestSlideOutEffect:
    """Test suite for SlideOutEffect."""

    def test_apply_returns_clip(self, mock_clip):
        """Test that apply returns a clip."""
        effect = AnimationEffect(type="slideOut", duration=1.0, direction="right")
        slide_out = SlideOutEffect()

        result = slide_out.apply(mock_clip, effect, (1920, 1080))
        assert result is not None
        assert hasattr(result, "_transform_fn")

    def test_slide_out_directions(self, simple_frame, mock_clip):
        """Test slide out to all directions."""
        directions = ["left", "right", "top", "bottom"]

        for direction in directions:
            effect = AnimationEffect(
                type="slideOut", duration=1.0, direction=direction, easing="linear"
            )
            slide_out = SlideOutEffect()

            result_clip = slide_out.apply(mock_clip, effect, (200, 200))
            transform_fn = result_clip._transform_fn

            # At t=0 (before slideout starts), frame should be centered
            result_before = transform_fn(lambda t: simple_frame.copy(), 0.0)
            # At t=end, frame should be off-screen
            result_end = transform_fn(lambda t: simple_frame.copy(), 5.0)

            assert result_before.shape == (200, 200, 3)
            assert result_end.shape == (200, 200, 3)

    def test_slide_out_default_direction(self, simple_frame, mock_clip):
        """Test slide out with default direction."""
        effect = AnimationEffect(type="slideOut", duration=1.0)  # No direction
        slide_out = SlideOutEffect()

        result_clip = slide_out.apply(mock_clip, effect, (200, 200))
        transform_fn = result_clip._transform_fn

        # Should not raise error with default direction
        result = transform_fn(lambda t: simple_frame.copy(), 2.5)
        assert result.shape == (200, 200, 3)
