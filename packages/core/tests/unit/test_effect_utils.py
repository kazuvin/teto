"""Tests for effect utilities module."""

import pytest
from teto_core.effect.utils import get_easing_function


@pytest.mark.unit
class TestGetEasingFunction:
    """Test suite for get_easing_function."""

    def test_linear_at_zero(self):
        """Test linear easing at t=0."""
        fn = get_easing_function("linear")
        assert fn(0.0) == 0.0

    def test_linear_at_one(self):
        """Test linear easing at t=1."""
        fn = get_easing_function("linear")
        assert fn(1.0) == 1.0

    def test_linear_at_midpoint(self):
        """Test linear easing at t=0.5."""
        fn = get_easing_function("linear")
        assert fn(0.5) == 0.5

    def test_linear_is_linear(self):
        """Test that linear easing is truly linear."""
        fn = get_easing_function("linear")
        for i in range(11):
            t = i / 10.0
            assert fn(t) == pytest.approx(t)

    def test_ease_in_at_zero(self):
        """Test easeIn at t=0."""
        fn = get_easing_function("easeIn")
        assert fn(0.0) == 0.0

    def test_ease_in_at_one(self):
        """Test easeIn at t=1."""
        fn = get_easing_function("easeIn")
        assert fn(1.0) == 1.0

    def test_ease_in_is_slower_at_start(self):
        """Test that easeIn is slower at the start."""
        fn = get_easing_function("easeIn")
        # At t=0.5, easeIn (t^2) should be 0.25, less than 0.5
        assert fn(0.5) < 0.5
        assert fn(0.5) == pytest.approx(0.25)

    def test_ease_out_at_zero(self):
        """Test easeOut at t=0."""
        fn = get_easing_function("easeOut")
        assert fn(0.0) == 0.0

    def test_ease_out_at_one(self):
        """Test easeOut at t=1."""
        fn = get_easing_function("easeOut")
        assert fn(1.0) == 1.0

    def test_ease_out_is_faster_at_start(self):
        """Test that easeOut is faster at the start."""
        fn = get_easing_function("easeOut")
        # At t=0.5, easeOut t*(2-t) should be 0.75, more than 0.5
        assert fn(0.5) > 0.5
        assert fn(0.5) == pytest.approx(0.75)

    def test_ease_in_out_at_zero(self):
        """Test easeInOut at t=0."""
        fn = get_easing_function("easeInOut")
        assert fn(0.0) == 0.0

    def test_ease_in_out_at_one(self):
        """Test easeInOut at t=1."""
        fn = get_easing_function("easeInOut")
        assert fn(1.0) == 1.0

    def test_ease_in_out_at_midpoint(self):
        """Test easeInOut at t=0.5 (inflection point)."""
        fn = get_easing_function("easeInOut")
        # t^2 * (3 - 2t) at t=0.5 should be 0.5
        assert fn(0.5) == pytest.approx(0.5)

    def test_ease_in_out_symmetry(self):
        """Test that easeInOut is symmetric around midpoint."""
        fn = get_easing_function("easeInOut")
        # f(t) + f(1-t) should equal 1 for smooth S-curve
        for t in [0.1, 0.2, 0.3, 0.4]:
            assert fn(t) + fn(1 - t) == pytest.approx(1.0)

    def test_none_defaults_to_linear(self):
        """Test that None defaults to linear easing."""
        fn = get_easing_function(None)
        assert fn(0.5) == 0.5
        assert fn(0.25) == 0.25

    def test_unknown_easing_defaults_to_linear(self):
        """Test that unknown easing type defaults to linear."""
        fn = get_easing_function("unknown")
        assert fn(0.5) == 0.5

    def test_all_easings_start_at_zero(self):
        """Test that all easing functions start at 0."""
        for easing in ["linear", "easeIn", "easeOut", "easeInOut", None]:
            fn = get_easing_function(easing)
            assert fn(0.0) == 0.0

    def test_all_easings_end_at_one(self):
        """Test that all easing functions end at 1."""
        for easing in ["linear", "easeIn", "easeOut", "easeInOut", None]:
            fn = get_easing_function(easing)
            assert fn(1.0) == 1.0

    def test_all_easings_are_monotonic(self):
        """Test that all easing functions are monotonically increasing."""
        for easing in ["linear", "easeIn", "easeOut", "easeInOut"]:
            fn = get_easing_function(easing)
            prev = 0.0
            for i in range(1, 21):
                t = i / 20.0
                current = fn(t)
                assert current >= prev, f"{easing} is not monotonic at t={t}"
                prev = current
