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
