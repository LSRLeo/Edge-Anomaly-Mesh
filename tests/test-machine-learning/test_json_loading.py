"""
Tests for json_events_to_numpy and load_json_data fallback logic.

Covers:
  - Nested JSON format (accel_mss, gyro_rads)
  - Flat JSON format (accel_x, gyro_x)
  - Mixed format events
  - Missing keys and default/fallback behavior
  - Data shape and dtype correctness
  - Multiple events and batch handling
  - Integration with load_json_data (file loading, label parsing)
  - Unknown keys and robustness to extra fields
  - Dtype checks (float32)
  - Empty event list handling
  - Error handling for invalid input types
"""

import sys
from pathlib import Path
import numpy as np
import pytest

ML_DIR = Path(__file__).parent.parent.parent / "ml"
sys.path.insert(0, str(ML_DIR))

from data_pipeline import json_events_to_numpy, load_json_data  # noqa: E402

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestJsonLoadingFallback:
    def test_nested_format(self):
        """Handles nested accel_mss and gyro_rads keys."""
        events = [
            {"accel_mss": {"x": 1, "y": 2, "z": 3}, "gyro_rads": {"x": 4, "y": 5, "z": 6}}
        ]
        data = json_events_to_numpy(events)
        assert np.allclose(data["accel_x"], [1])
        assert np.allclose(data["gyro_z"], [6])

    def test_flat_format(self):
        """Handles flat accel_x and gyro_x keys."""
        events = [
            {"accel_x": 7, "accel_y": 8, "accel_z": 9, "gyro_x": 10, "gyro_y": 11, "gyro_z": 12}
        ]
        data = json_events_to_numpy(events)
        assert np.allclose(data["accel_y"], [8])
        assert np.allclose(data["gyro_x"], [10])

    def test_mixed_format(self):
        """Handles mixed nested and flat keys."""
        events = [
            {"accel_mss": {"x": 1, "y": 2, "z": 3}, "gyro_x": 4, "gyro_y": 5, "gyro_z": 6}
        ]
        data = json_events_to_numpy(events)
        assert np.allclose(data["accel_x"], [1])
        assert np.allclose(data["gyro_z"], [6])

    def test_missing_keys(self):
        """Missing keys default to 0."""
        events = [{}]
        data = json_events_to_numpy(events)
        assert np.allclose(data["accel_x"], [0])
        assert np.allclose(data["gyro_y"], [0])

    def test_multiple_events(self):
        """Handles multiple events and correct shapes."""
        events = [
            {"accel_x": 1, "accel_y": 2, "accel_z": 3, "gyro_x": 4, "gyro_y": 5, "gyro_z": 6},
            {"accel_mss": {"x": 7, "y": 8, "z": 9}, "gyro_rads": {"x": 10, "y": 11, "z": 12}}
        ]
        data = json_events_to_numpy(events)
        assert data["accel_x"].shape == (2,)
        assert np.allclose(data["accel_x"], [1, 7])
        assert np.allclose(data["gyro_z"], [6, 12])

    def test_dtype_is_float32(self):
        """All returned arrays are float32 dtype."""
        events = [{"accel_x": 1, "accel_y": 2, "accel_z": 3, "gyro_x": 4, "gyro_y": 5, "gyro_z": 6}]
        data = json_events_to_numpy(events)
        for arr in data.values():
            assert arr.dtype == np.float32

    def test_empty_event_list(self):
        """Handles empty event list gracefully."""
        events = []
        data = json_events_to_numpy(events)
        for arr in data.values():
            assert arr.shape == (0,)

    def test_extra_keys_ignored(self):
        """Ignores unknown keys and extra fields."""
        events = [{"accel_x": 1, "gyro_x": 2, "extra": 99}]
        data = json_events_to_numpy(events)
        assert np.allclose(data["accel_x"], [1])
        assert np.allclose(data["gyro_x"], [2])

    def test_invalid_input_type_raises(self):
        """Raises TypeError or ValueError for invalid input types."""
        with pytest.raises(Exception):
            json_events_to_numpy("not a list")

    def test_load_json_data_integration(self, tmp_path):
        """Integration: load_json_data parses file and labels."""
        # Create a temporary JSON file
        events = [
            {"accel_x": 1, "accel_y": 2, "accel_z": 3, "gyro_x": 4, "gyro_y": 5, "gyro_z": 6,
             "meta": {"sim_mode": "IDLE", "anomaly": "true"}}
        ]
        file = tmp_path / "test.json"
        import json
        with open(file, "w") as f:
            json.dump(events, f)
        data, labels = load_json_data(file)
        assert np.allclose(data["accel_x"], [1])
        assert labels.shape == (1,)
        assert labels[0] == 4  # IDLE + anomaly

    def test_malformed_json_file_raises(self, tmp_path):
        """Raises ValueError for malformed JSON file."""
        file = tmp_path / "bad.json"
        file.write_text("{not: valid, json}")  # Invalid JSON
        from data_pipeline import load_json_data
        with pytest.raises(Exception):
            load_json_data(file)

    def test_partial_nested_keys(self):
        """Handles events with some axes nested, others flat."""
        events = [
            {"accel_mss": {"x": 1}, "accel_y": 2, "accel_z": 3, "gyro_rads": {"y": 5}, "gyro_x": 4, "gyro_z": 6}
        ]
        data = json_events_to_numpy(events)
        assert np.allclose(data["accel_x"], [1])
        assert np.allclose(data["accel_y"], [2])
        assert np.allclose(data["gyro_y"], [5])
        assert np.allclose(data["gyro_x"], [4])

    def test_non_numeric_values(self):
        """Handles non-numeric sensor values gracefully (defaults to 0)."""
        events = [
            {"accel_x": "bad", "accel_y": None, "accel_z": 3, "gyro_x": 4, "gyro_y": "NaN", "gyro_z": 6}
        ]
        data = json_events_to_numpy(events)
        assert data["accel_x"][0] == 0
        assert data["accel_y"][0] == 0
        assert data["accel_z"][0] == 3
        assert data["gyro_y"][0] == 0

    def test_large_batch_performance(self):
        """Handles large batch of events."""
        events = [{"accel_x": i, "accel_y": i+1, "accel_z": i+2, "gyro_x": i+3, "gyro_y": i+4, "gyro_z": i+5} for i in range(10000)]
        data = json_events_to_numpy(events)
        assert data["accel_x"].shape == (10000,)
        assert np.allclose(data["gyro_z"][:3], [5, 6, 7])

    def test_label_edge_cases(self, tmp_path):
        """Raises ValueError for unknown terrain/anomaly values."""
        events = [
            {"accel_x": 1, "accel_y": 2, "accel_z": 3, "gyro_x": 4, "gyro_y": 5, "gyro_z": 6},  # No label/meta
            {"accel_x": 7, "accel_y": 8, "accel_z": 9, "gyro_x": 10, "gyro_y": 11, "gyro_z": 12,
            "meta": {"sim_mode": "UNKNOWN", "anomaly": "false"}}
        ]
        file = tmp_path / "label_edge.json"
        import json
        with open(file, "w") as f:
            json.dump(events, f)
        from data_pipeline import load_json_data
        with pytest.raises(ValueError):
            load_json_data(file)