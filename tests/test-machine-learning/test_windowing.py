"""
Tests for windowing logic in create_windows().

Covers:
  - Empty windows for small sample sizes
  - Exact window sizing
  - Multiple windows with/without overlap
  - Step size and overlap edge cases
  - Negative/invalid window size and overlap handling
  - Missing axis error
  - Majority and tie-breaking label logic
  - Window shape and label shape correctness
  - Non-integer and float label support
  - Large data handling
  - Random data windowing
"""

import sys
from pathlib import Path
import numpy as np
import pytest

ML_DIR = Path(__file__).parent.parent.parent / "ml"
sys.path.insert(0, str(ML_DIR))

from data_pipeline import create_windows  # noqa: E402

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestWindowingEdgeCases:
    def test_small_sample_returns_empty(self):
        """Returns empty if sample size < window_size."""
        data = {k: np.arange(10) for k in ['accel_x','accel_y','accel_z','gyro_x','gyro_y','gyro_z']}
        windows = create_windows(data, window_size=100, overlap=0.0)
        assert windows.shape[0] == 0

    def test_exact_window(self):
        """Returns one window if sample size == window_size."""
        data = {k: np.arange(100) for k in ['accel_x','accel_y','accel_z','gyro_x','gyro_y','gyro_z']}
        windows = create_windows(data, window_size=100, overlap=0.0)
        assert windows.shape[0] == 1

    def test_multiple_windows_no_overlap(self):
        """Returns multiple windows with no overlap."""
        data = {k: np.arange(200) for k in ['accel_x','accel_y','accel_z','gyro_x','gyro_y','gyro_z']}
        windows = create_windows(data, window_size=100, overlap=0.0)
        assert windows.shape[0] == 2

    def test_multiple_windows_with_overlap(self):
        """Returns correct number of windows with overlap."""
        data = {k: np.arange(150) for k in ['accel_x','accel_y','accel_z','gyro_x','gyro_y','gyro_z']}
        windows = create_windows(data, window_size=100, overlap=0.5)
        assert windows.shape[0] == 2

    def test_overlap_99_percent(self):
        """Raises ValueError for overlap causing step < 1."""
        data = {k: np.arange(200) for k in ['accel_x','accel_y','accel_z','gyro_x','gyro_y','gyro_z']}
        with pytest.raises(ValueError):
            create_windows(data, window_size=50, overlap=0.99)

    def test_negative_window_size_raises(self):
        """Raises ValueError for negative window_size."""
        data = {k: np.arange(100) for k in ['accel_x','accel_y','accel_z','gyro_x','gyro_y','gyro_z']}
        with pytest.raises(ValueError):
            create_windows(data, window_size=-10, overlap=0.0)

    def test_invalid_overlap_raises(self):
        """Raises ValueError for overlap >= 1 or < 0."""
        data = {k: np.arange(100) for k in ['accel_x','accel_y','accel_z','gyro_x','gyro_y','gyro_z']}
        with pytest.raises(ValueError):
            create_windows(data, window_size=50, overlap=1.5)

    def test_missing_axis_raises(self):
        """Raises KeyError if a sensor axis is missing."""
        data = {k: np.arange(100) for k in ['accel_x','accel_y','accel_z','gyro_x','gyro_y']}
        with pytest.raises(KeyError):
            create_windows(data, window_size=50, overlap=0.0)

    def test_labels_majority(self):
        """Majority label logic works."""
        data = {k: np.arange(100) for k in ['accel_x','accel_y','accel_z','gyro_x','gyro_y','gyro_z']}
        labels = np.array([1]*60 + [2]*40)
        windows, window_labels = create_windows(data, window_size=100, overlap=0.0, labels=labels)
        assert window_labels.shape[0] == windows.shape[0]
        assert window_labels[0] == 1

    def test_labels_tie_breaking(self):
        """Tie-breaking for labels works (either value allowed)."""
        data = {k: np.arange(100) for k in ['accel_x','accel_y','accel_z','gyro_x','gyro_y','gyro_z']}
        labels = np.array([1]*50 + [2]*50)
        windows, window_labels = create_windows(data, window_size=100, overlap=0.0, labels=labels)
        assert window_labels.shape[0] == windows.shape[0]
        assert window_labels[0] in [1,2]

    def test_multiple_windows_with_labels(self):
        """Labels are correct for multiple windows."""
        data = {k: np.arange(200) for k in ['accel_x','accel_y','accel_z','gyro_x','gyro_y','gyro_z']}
        labels = np.array([0]*100 + [1]*100)
        windows, window_labels = create_windows(data, window_size=100, overlap=0.0, labels=labels)
        assert window_labels.shape[0] == 2
        assert window_labels[0] == 0
        assert window_labels[1] == 1

    def test_window_shape(self):
        """Window shape is correct."""
        data = {k: np.arange(120) for k in ['accel_x','accel_y','accel_z','gyro_x','gyro_y','gyro_z']}
        windows = create_windows(data, window_size=60, overlap=0.0)
        assert windows.shape == (2, 60, 6)

    def test_window_shape_with_labels(self):
        """Window and label shapes are correct."""
        data = {k: np.arange(120) for k in ['accel_x','accel_y','accel_z','gyro_x','gyro_y','gyro_z']}
        labels = np.array([0]*60 + [1]*60)
        windows, window_labels = create_windows(data, window_size=60, overlap=0.0, labels=labels)
        assert windows.shape == (2, 60, 6)
        assert window_labels.shape == (2,)

    def test_non_integer_labels(self):
        """Supports non-integer labels."""
        data = {k: np.arange(100) for k in ['accel_x','accel_y','accel_z','gyro_x','gyro_y','gyro_z']}
        labels = np.array(['a']*100)
        windows, window_labels = create_windows(data, window_size=100, overlap=0.0, labels=labels)
        assert window_labels[0] == 'a'

    def test_float_labels(self):
        """Supports float labels."""
        data = {k: np.arange(100) for k in ['accel_x','accel_y','accel_z','gyro_x','gyro_y','gyro_z']}
        labels = np.array([1.5]*100)
        windows, window_labels = create_windows(data, window_size=100, overlap=0.0, labels=labels)
        assert window_labels[0] == 1.5

    def test_large_data(self):
        """Handles large data arrays."""
        data = {k: np.arange(10000) for k in ['accel_x','accel_y','accel_z','gyro_x','gyro_y','gyro_z']}
        windows = create_windows(data, window_size=100, overlap=0.5)
        assert windows.shape[0] > 0

    def test_zero_overlap(self):
        """Returns correct window count for zero overlap."""
        data = {k: np.arange(300) for k in ['accel_x','accel_y','accel_z','gyro_x','gyro_y','gyro_z']}
        windows = create_windows(data, window_size=100, overlap=0.0)
        assert windows.shape[0] == 3

    def test_full_overlap(self):
        """Raises ValueError for overlap >= 1.0."""
        data = {k: np.arange(100) for k in ['accel_x','accel_y','accel_z','gyro_x','gyro_y','gyro_z']}
        with pytest.raises(ValueError):
            create_windows(data, window_size=100, overlap=1.0)

    def test_windowing_with_random_data(self):
        """Windowing works with random data."""
        rng = np.random.default_rng(42)
        data = {k: rng.random(100) for k in ['accel_x','accel_y','accel_z','gyro_x','gyro_y','gyro_z']}
        windows = create_windows(data, window_size=50, overlap=0.5)
        assert windows.shape[0] > 0

    def test_windowing_with_negative_overlap(self):
        """Raises ValueError for negative overlap."""
        data = {k: np.arange(100) for k in ['accel_x','accel_y','accel_z','gyro_x','gyro_y','gyro_z']}
        with pytest.raises(ValueError):
            create_windows(data, window_size=50, overlap=-0.1)