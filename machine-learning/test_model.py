#!/usr/bin/env python3
"""
Quick test script to verify the MotionClassifier model works correctly.
"""

import torch
import numpy as np
from model_training import MotionClassifier, decode_combined_label

def test_model():
    """Test that the model architecture works correctly."""

    print("=" * 60)
    print("Testing MotionClassifier with 8-class output")
    print("=" * 60)

    # Model parameters
    input_dim = 20  # Number of features
    batch_size = 5

    # Create model
    model = MotionClassifier(input_dim=input_dim, num_classes=8)
    print(f"\n✓ Model created successfully")
    print(f"  Architecture: {input_dim} → 64 → 32 → 8")

    # Create dummy input data
    dummy_input = torch.randn(batch_size, input_dim)
    print(f"\n✓ Created dummy input: shape {dummy_input.shape}")

    # Forward pass
    output = model(dummy_input)
    print(f"\n✓ Forward pass successful")
    print(f"  Output shape: {output.shape} (expected: [{batch_size}, 8])")

    # Check output shape
    assert output.shape == (batch_size, 8), f"Expected shape ({batch_size}, 8), got {output.shape}"

    # Apply softmax to get probabilities
    probabilities = torch.softmax(output, dim=1)
    print(f"\n✓ Softmax applied")
    print(f"  Probabilities shape: {probabilities.shape}")

    # Check probabilities sum to 1
    prob_sums = probabilities.sum(dim=1)
    print(f"  Probability sums: {prob_sums.numpy()}")
    assert torch.allclose(prob_sums, torch.ones(batch_size)), "Probabilities don't sum to 1!"
    print(f"  ✓ All probabilities sum to 1.0")

    # Get predictions
    predicted_labels = torch.argmax(probabilities, dim=1)
    print(f"\n✓ Predictions generated")
    print(f"  Predicted labels: {predicted_labels.numpy()}")

    # Decode predictions
    print(f"\n✓ Decoding predictions:")
    for i, label in enumerate(predicted_labels):
        terrain, has_anomaly = decode_combined_label(label.item())
        terrain_names = ['IDLE', 'TERRESTRIAL', 'MARITIME', 'LIFT']
        anomaly_str = 'WITH anomaly' if has_anomaly else 'NO anomaly'
        print(f"  Sample {i}: Label {label.item()} → {terrain_names[terrain]}, {anomaly_str}")

    # Show example probabilities
    print(f"\n✓ Example probability distribution (sample 0):")
    class_names = [
        'IDLE', 'TERRESTRIAL', 'MARITIME', 'LIFT',
        'IDLE_ANOM', 'TERRESTRIAL_ANOM', 'MARITIME_ANOM', 'LIFT_ANOM'
    ]
    for i, (name, prob) in enumerate(zip(class_names, probabilities[0])):
        print(f"  {name:20s}: {prob.item():.4f}")

    print("\n" + "=" * 60)
    print("✓ All tests passed! Model is working correctly.")
    print("=" * 60)

if __name__ == '__main__':
    test_model()
