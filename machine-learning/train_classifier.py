#!/usr/bin/env python3
"""
train_classifier.py

Train a PyTorch motion classifier on extracted features.

NEURAL NETWORK OVERVIEW:
========================
We use a simple feedforward neural network (also called MLP - Multi-Layer Perceptron).

    Input (20 features)
         ↓
    Linear Layer (20 → 64 neurons)
         ↓
    ReLU Activation (adds non-linearity)
         ↓
    Dropout (randomly zeros 30% of neurons - prevents overfitting)
         ↓
    Linear Layer (64 → 32 neurons)
         ↓
    ReLU Activation
         ↓
    Linear Layer (32 → 8 outputs)
         ↓
    Softmax (converts to probabilities)
         ↓
    Output: [P(IDLE), P(TERR), P(MAR), P(LIFT), P(IDLE_A), P(TERR_A), P(MAR_A), P(LIFT_A)]

TRAINING PROCESS:
=================
1. Forward pass: Input → Network → Prediction
2. Compute loss: How wrong was the prediction?
3. Backward pass: Compute gradients (how to adjust weights)
4. Update weights: Move weights in direction that reduces loss
5. Repeat for many epochs until loss stops decreasing

Usage:
    python3 ml/train_classifier.py

Requirements:
    pip install torch numpy scikit-learn
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
from pathlib import Path
import json
from datetime import datetime

# Import from our feature extraction module
from ml.feature_extraction import FeatureExtractor
from ml.data_pipeline import load_json_data, create_windows

# ============================================================================
# MAIN TRAINING SCRIPT
# ============================================================================

def main():
    """
    Main training function.
    
    Steps:
        1. Configuration (hyperparameters, paths)
        2. Load and preprocess data
        3. Create train/val/test splits
        4. Initialize model, optimizer, loss function
        5. Training loop with early stopping
        6. Evaluate on test set
        7. Save model and results
    
    Key hyperparameters to set:
        - BATCH_SIZE: 32 (samples per gradient update)
        - LEARNING_RATE: 0.001 (step size for optimizer)
        - EPOCHS: 100 (maximum training iterations)
        - PATIENCE: 10 (early stopping patience)
    
    Early stopping:
        - Track validation accuracy each epoch
        - If it doesn't improve for PATIENCE epochs, stop training
        - Save the best model (highest validation accuracy)
    
    Implementation outline:
        
        # Setup
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load data
        X, y, extractor = load_all_data(DATA_DIR)
        X_normalized, scaler = normalize_features(X)
        
        # Create dataset and split
        dataset = MotionDataset(X_normalized, y)
        train_set, val_set, test_set = random_split(dataset, [0.7, 0.15, 0.15])
        
        # Create dataloaders
        train_loader = DataLoader(train_set, batch_size=32, shuffle=True)
        val_loader = DataLoader(val_set, batch_size=32)
        test_loader = DataLoader(test_set, batch_size=32)
        
        # Initialize model
        model = MotionClassifier(input_dim=extractor.n_features).to(device)
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001)
        
        # Training loop
        best_val_acc = 0
        patience_counter = 0
        
        for epoch in range(EPOCHS):
            train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
            val_loss, val_acc, _, _ = evaluate(model, val_loader, criterion, device)
            
            # Early stopping check
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                patience_counter = 0
                torch.save(model.state_dict(), 'best_model.pt')
            else:
                patience_counter += 1
                if patience_counter >= PATIENCE:
                    print("Early stopping!")
                    break
        
        # Load best model and evaluate on test set
        model.load_state_dict(torch.load('best_model.pt'))
        test_loss, test_acc, predictions, labels = evaluate(model, test_loader, criterion, device)
        
        # Print results
        conf_matrix = compute_confusion_matrix(predictions, labels)
        print_confusion_matrix(conf_matrix, CLASS_NAMES)
        print_classification_report(conf_matrix, CLASS_NAMES)
    """
    pass  # TODO: Implement


if __name__ == '__main__':
    main()
