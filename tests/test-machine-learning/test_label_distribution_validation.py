"""
Tests for validate_label_distribution() in train_classifier.py.

Covers class count printing and missing-class warnings for the 8-class label
space (4 terrain types × 2 anomaly states).

NOTE: y arrays in these tests are synthetic inputs used to exercise specific
behaviours of the function.  They do not represent real training data.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

# Make the ml/ package importable without an editable install
ML_DIR = Path(__file__).parent.parent.parent / "ml"
sys.path.insert(0, str(ML_DIR))

from train_classifier import validate_label_distribution  # noqa: E402


_CLASS_NAMES = [
    'IDLE', 'TERRESTRIAL', 'MARITIME', 'LIFT',
    'IDLE_ANOM', 'TERRESTRIAL_ANOM', 'MARITIME_ANOM', 'LIFT_ANOM',
]


class TestValidateLabelDistribution:

    def test_counts_match_actual_label_frequencies(self, capsys):
        """Returned counts equal the actual frequency of each class in y."""
        # One sample of each class — simplest way to verify all counts are correct
        y = np.arange(8)

        counts = validate_label_distribution(y)

        for idx, name in enumerate(_CLASS_NAMES):
            assert counts[name] == int(np.sum(y == idx))

    def test_all_classes_present_no_warning(self, capsys):
        """All 8 classes present → no warning is printed."""
        y = np.tile(np.arange(8), 25)  # 25 samples of each class

        validate_label_distribution(y)

        captured = capsys.readouterr()
        assert 'Warning' not in captured.out

    def test_missing_classes_prints_warning(self, capsys):
        """Classes with zero samples trigger a warning listing their names."""
        # Only classes 0 (IDLE) and 1 (TERRESTRIAL) present
        y = np.array([0, 1] * 50)

        validate_label_distribution(y)

        captured = capsys.readouterr()
        assert 'Warning' in captured.out
        assert 'MARITIME' in captured.out
        assert 'LIFT' in captured.out

    def test_prints_all_class_names(self, capsys):
        """Output includes each of the 8 expected class names."""
        y = np.zeros(100, dtype=int)  # only class 0 (IDLE)

        validate_label_distribution(y)

        captured = capsys.readouterr()
        for name in _CLASS_NAMES:
            assert name in captured.out

    def test_single_class_warns_seven_missing(self, capsys):
        """Only one class present → warning lists the other 7 missing classes."""
        y = np.full(100, fill_value=2, dtype=int)  # only class 2 (MARITIME)

        validate_label_distribution(y)

        captured = capsys.readouterr()
        assert 'Warning' in captured.out
        for name in _CLASS_NAMES:
            if name != 'MARITIME':
                assert name in captured.out

    def test_returns_dict_with_all_eight_keys(self):
        """Return value always contains all 8 class keys regardless of y content."""
        y = np.zeros(10, dtype=int)

        counts = validate_label_distribution(y)

        assert set(counts.keys()) == set(_CLASS_NAMES)
