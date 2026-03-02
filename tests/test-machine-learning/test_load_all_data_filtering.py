"""
Tests for None/NaN label filtering in load_all_data (train_classifier.py).

Covers the case where sensor events have missing or unrecognised sim_mode
values, which causes load_json_data to produce None labels.  load_all_data
must drop those windows and never pass None/NaN into the training loop.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pytest

# Make the ml/ package importable without an editable install
ML_DIR = Path(__file__).parent.parent.parent / "ml"
sys.path.insert(0, str(ML_DIR))

from train_classifier import load_all_data  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _event(mode, anomaly=False, seq=0):
    """Return a minimal sensor event dict with the given sim_mode."""
    return {
        "seq": seq,
        "accel_mss": {"x": 0.0, "y": 0.0, "z": 9.81},
        "gyro_rads": {"x": 0.0, "y": 0.0, "z": 0.0},
        "meta": {
            "sim_mode": mode,
            "sim_anomaly": anomaly,
        },
    }


def _events(mode, n=200, anomaly=False):
    return [_event(mode, anomaly=anomaly, seq=i) for i in range(n)]


def _write(path, events):
    path.write_text(json.dumps(events))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestLoadAllDataNoneNanFiltering:

    def test_clean_data_passes_through(self, tmp_path):
        """All valid labels → nothing is dropped, output is non-empty."""
        _write(tmp_path / "idle.json", _events("IDLE", n=200))

        X, y, _ = load_all_data(str(tmp_path), window_size=100, overlap=0.5)

        assert len(X) == len(y)
        assert len(X) > 0
        assert y.dtype in (np.int32, np.int64, np.intp, int)
        assert not np.any(np.isnan(y.astype(float)))

    def test_none_labels_are_dropped(self, tmp_path):
        """Windows whose majority label is None are silently dropped."""
        valid = _events("IDLE", n=150)

        # The last 50 events have no sim_mode → load_json_data assigns None label
        bad = []
        for i in range(50):
            e = _event("IDLE", seq=150 + i)
            del e["meta"]["sim_mode"]
            bad.append(e)

        _write(tmp_path / "mixed.json", valid + bad)

        X, y, _ = load_all_data(str(tmp_path), window_size=100, overlap=0.5)

        assert len(X) == len(y)
        assert len(X) > 0
        assert all(v is not None for v in y)
        assert not np.any(np.isnan(y.astype(float)))

    def test_nan_labels_are_dropped(self, tmp_path):
        """Windows with NaN labels (float) are dropped."""
        import data_pipeline as dp

        _write(tmp_path / "idle.json", _events("IDLE", n=200))

        original_load = dp.load_json_data

        def patched_load(filepath):
            data, labels = original_load(filepath)
            labels = labels.astype(float)
            labels[10:20] = np.nan  # inject NaN into a slice of sample labels
            return data, labels

        dp.load_json_data = patched_load
        try:
            X, y, _ = load_all_data(str(tmp_path), window_size=100, overlap=0.5)
        finally:
            dp.load_json_data = original_load

        assert len(X) == len(y)
        assert len(X) > 0
        assert not np.any(np.isnan(y.astype(float)))

    def test_all_none_labels_single_file_raises(self, tmp_path):
        """When every event in the only file has no valid label, raise ValueError."""
        bad = []
        for i in range(200):
            e = _event("IDLE", seq=i)
            del e["meta"]["sim_mode"]
            bad.append(e)

        _write(tmp_path / "all_bad.json", bad)

        with pytest.raises(ValueError, match="No valid training samples"):
            load_all_data(str(tmp_path), window_size=100, overlap=0.5)

    def test_mixed_files_bad_file_skipped(self, tmp_path):
        """Two files: one clean, one all-bad.  Only the clean file's windows survive."""
        _write(tmp_path / "clean.json", _events("TERRESTRIAL", n=200))

        bad = []
        for i in range(200):
            e = _event("IDLE", seq=i)
            del e["meta"]["sim_mode"]
            bad.append(e)
        _write(tmp_path / "bad.json", bad)

        X, y, _ = load_all_data(str(tmp_path), window_size=100, overlap=0.5)

        assert len(X) == len(y)
        assert len(X) > 0
        assert all(v is not None for v in y)
        assert not np.any(np.isnan(y.astype(float)))

    def test_labels_castable_to_int(self, tmp_path):
        """Returned y must be an integer array (required by torch.LongTensor)."""
        _write(tmp_path / "maritime.json", _events("MARITIME", n=200))

        _, y, _ = load_all_data(str(tmp_path), window_size=100, overlap=0.5)

        # This is the exact conversion MotionDataset does — must not raise
        import torch
        tensor = torch.LongTensor(y)
        assert tensor.dtype == torch.int64
