"""
Tests for confidence score computation in MotionClassifier.predict().

Covers:
  - predict() returns confidence in [0.0, 1.0]
  - confidence equals the maximum softmax probability
  - returned probabilities sum to 1.0 per sample
  - predicted class index equals argmax of probabilities
  - terrain-specific confidence derivation: P(terrain) + P(terrain_anomaly)
  - anomaly score in [0.0, 1.0]
  - predict() output shapes are correct
  - predict() is deterministic in eval mode
"""

import sys
from pathlib import Path

import torch
import pytest

ML_DIR = Path(__file__).parent.parent.parent / "ml"
sys.path.insert(0, str(ML_DIR))

from train_classifier import MotionClassifier  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def model():
    """Small MotionClassifier (8 classes) with dropout disabled for determinism."""
    return MotionClassifier(input_dim=20, num_classes=8, hidden_dims=(16, 8), dropout=0.0)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestMotionClassifierConfidence:

    def test_confidence_in_unit_interval(self, model):
        """predict() confidence values must lie in [0.0, 1.0]."""
        x = torch.randn(4, 20)
        _, confidence, _ = model.predict(x)
        assert (confidence >= 0.0).all(), "confidence below 0.0"
        assert (confidence <= 1.0).all(), "confidence above 1.0"

    def test_confidence_equals_max_softmax(self, model):
        """confidence must equal max(softmax(logits)) for each sample."""
        x = torch.randn(4, 20)
        with torch.no_grad():
            logits = model(x)
            probs = torch.softmax(logits, dim=1)
            expected = probs.max(dim=1).values
        _, confidence, _ = model.predict(x)
        assert torch.allclose(confidence, expected, atol=1e-6)

    def test_probabilities_sum_to_one(self, model):
        """Returned probability tensor must sum to 1.0 per sample."""
        x = torch.randn(4, 20)
        _, _, probs = model.predict(x)
        sums = probs.sum(dim=1)
        assert torch.allclose(sums, torch.ones(4), atol=1e-5)

    def test_predicted_class_matches_argmax(self, model):
        """Predicted class index must equal argmax of probabilities."""
        x = torch.randn(4, 20)
        predicted, _, probs = model.predict(x)
        expected = probs.argmax(dim=1)
        assert (predicted == expected).all()

    def test_terrain_confidence_in_unit_interval(self, model):
        """terrain_confidence = P(terrain) + P(terrain_anomaly) must be in [0, 1]."""
        x = torch.randn(8, 20)
        predicted, _, probs = model.predict(x)
        for i in range(x.shape[0]):
            terrain_idx = predicted[i].item() % 4
            terrain_conf = probs[i, terrain_idx].item() + probs[i, terrain_idx + 4].item()
            assert 0.0 <= terrain_conf <= 1.0 + 1e-6, (
                f"sample {i}: terrain_conf={terrain_conf:.6f} out of [0, 1]"
            )

    def test_anomaly_score_in_unit_interval(self, model):
        """anomaly_score = sum(P(anomaly classes 4-7)) must be in [0, 1]."""
        x = torch.randn(8, 20)
        _, _, probs = model.predict(x)
        anomaly_scores = probs[:, 4:].sum(dim=1)
        assert (anomaly_scores >= 0.0).all(), "anomaly_score below 0.0"
        assert (anomaly_scores <= 1.0 + 1e-5).all(), "anomaly_score above 1.0"

    def test_single_sample_output_shapes(self, model):
        """predict() with one sample must return (1,), (1,), (1, 8) shaped tensors."""
        x = torch.randn(1, 20)
        predicted, confidence, probs = model.predict(x)
        assert predicted.shape == (1,)
        assert confidence.shape == (1,)
        assert probs.shape == (1, 8)

    def test_batch_output_shapes(self, model):
        """predict() with a batch must return tensors with matching batch dimension."""
        batch_size = 6
        x = torch.randn(batch_size, 20)
        predicted, confidence, probs = model.predict(x)
        assert predicted.shape == (batch_size,)
        assert confidence.shape == (batch_size,)
        assert probs.shape == (batch_size, 8)

    def test_predict_deterministic_in_eval_mode(self, model):
        """Repeated calls to predict() must return identical results (eval mode)."""
        model.eval()
        x = torch.randn(2, 20)
        pred1, conf1, probs1 = model.predict(x)
        pred2, conf2, probs2 = model.predict(x)
        assert (pred1 == pred2).all()
        assert torch.allclose(conf1, conf2)
        assert torch.allclose(probs1, probs2)

    def test_confidence_values_are_finite(self, model):
        """predict() must not produce NaN or Inf in confidence or probabilities."""
        x = torch.randn(4, 20)
        _, confidence, probs = model.predict(x)
        assert torch.isfinite(confidence).all(), "NaN/Inf in confidence"
        assert torch.isfinite(probs).all(), "NaN/Inf in probabilities"
