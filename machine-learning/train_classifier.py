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
    Linear Layer (32 → 4 outputs)
         ↓
    Softmax (converts to probabilities)
         ↓
    Output: [P(IDLE), P(TERRESTRIAL), P(MARITIME), P(LIFT)]

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
from feature_extraction import FeatureExtractor, create_windows, load_csv_data, normalize_features


# ============================================================================
# DATASET
# ============================================================================

class MotionDataset(Dataset):
    """
    PyTorch Dataset for motion classification.
    
    A Dataset is PyTorch's way of organizing data. It must implement:
        - __len__: Return total number of samples
        - __getitem__: Return one sample by index
    
    PyTorch's DataLoader then uses this to:
        - Batch samples together
        - Shuffle data each epoch
        - Load data in parallel
    """
    
    def __init__(self, features, labels):
        """
        Initialize the dataset.
        
        Args:
            features: numpy array of shape (n_samples, n_features)
            labels: numpy array of shape (n_samples,) with integer class labels
                    0=IDLE, 1=TERRESTRIAL, 2=MARITIME, 3=LIFT
        
        Implementation:
            - Convert numpy arrays to PyTorch tensors
            - features → torch.FloatTensor (32-bit float)
            - labels → torch.LongTensor (64-bit integer, required for CrossEntropyLoss)
        """
        pass  # TODO: Implement
    
    def __len__(self):
        """
        Return the total number of samples.
        
        Returns:
            int: Number of samples in dataset
        """
        pass  # TODO: Implement
    
    def __getitem__(self, idx):
        """
        Return one sample by index.
        
        Args:
            idx: integer index
        
        Returns:
            tuple: (features_tensor, label_tensor) for sample at idx
        """
        pass  # TODO: Implement


# ============================================================================
# MODEL
# ============================================================================

class MotionClassifier(nn.Module):
    """
    Simple feedforward neural network for motion classification.
    
    Architecture:
        Input → Linear → ReLU → Dropout → Linear → ReLU → Linear → Output
    
    All PyTorch models inherit from nn.Module and must implement:
        - __init__: Define the layers
        - forward: Define how data flows through layers
    """
    
    def __init__(self, input_dim, num_classes=4, hidden_dims=(64, 32), dropout=0.3):
        """
        Initialize the model layers.
        
        Args:
            input_dim: Number of input features (e.g., 20)
            num_classes: Number of output classes (4 for our motion types)
            hidden_dims: Tuple of hidden layer sizes (64, 32)
            dropout: Dropout probability (0.3 = drop 30% of neurons)
        
        Implementation:
            - Use nn.Linear(in_features, out_features) for fully connected layers
            - Use nn.ReLU() for activation
            - Use nn.Dropout(p) for regularization
            - Combine into nn.Sequential for clean code
        
        Example:
            self.network = nn.Sequential(
                nn.Linear(input_dim, 64),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(64, 32),
                nn.ReLU(),
                nn.Linear(32, num_classes)
            )
        """
        super().__init__()  # Always call parent __init__
        pass  # TODO: Implement
    
    def forward(self, x):
        """
        Define the forward pass.
        
        Args:
            x: Input tensor of shape (batch_size, input_dim)
        
        Returns:
            Output tensor of shape (batch_size, num_classes)
            These are "logits" (raw scores), not probabilities.
            CrossEntropyLoss applies softmax internally.
        
        Implementation:
            - Simply pass x through self.network
            - return self.network(x)
        """
        pass  # TODO: Implement
    
    def predict(self, x):
        """
        Make predictions with confidence scores.
        
        Args:
            x: Input tensor of shape (batch_size, input_dim)
        
        Returns:
            predicted: Tensor of predicted class indices
            confidence: Tensor of confidence scores (0-1)
        
        Implementation:
            - Use torch.no_grad() context (no need to track gradients)
            - Get logits from forward pass
            - Apply softmax to get probabilities
            - Use torch.max to get highest probability and its index
        """
        pass  # TODO: Implement


# ============================================================================
# TRAINING FUNCTIONS
# ============================================================================

def train_epoch(model, dataloader, criterion, optimizer, device):
    """
    Train the model for one epoch.
    
    One epoch = one complete pass through all training data.
    
    Args:
        model: The neural network
        dataloader: DataLoader providing batches of (features, labels)
        criterion: Loss function (CrossEntropyLoss)
        optimizer: Optimizer (Adam)
        device: 'cuda' or 'cpu'
    
    Returns:
        avg_loss: Average loss over all batches
        accuracy: Fraction of correct predictions
    
    Implementation steps (for each batch):
        1. Move data to device: features, labels = features.to(device), labels.to(device)
        2. Zero gradients: optimizer.zero_grad()
        3. Forward pass: outputs = model(features)
        4. Compute loss: loss = criterion(outputs, labels)
        5. Backward pass: loss.backward()
        6. Update weights: optimizer.step()
        7. Track statistics (loss, correct predictions)
    
    Important:
        - Call model.train() at the start (enables dropout)
    """
    pass  # TODO: Implement


def evaluate(model, dataloader, criterion, device):
    """
    Evaluate the model on a dataset (validation or test).
    
    Args:
        model: The neural network
        dataloader: DataLoader for evaluation data
        criterion: Loss function
        device: 'cuda' or 'cpu'
    
    Returns:
        avg_loss: Average loss
        accuracy: Fraction correct
        predictions: numpy array of all predictions
        labels: numpy array of all true labels
    
    Implementation:
        - Call model.eval() at the start (disables dropout)
        - Use torch.no_grad() context (no gradient computation needed)
        - Otherwise similar to train_epoch but without backward/step
    
    Important:
        - Save all predictions and labels for confusion matrix later
    """
    pass  # TODO: Implement


# ============================================================================
# EVALUATION METRICS
# ============================================================================

def compute_confusion_matrix(predictions, labels, num_classes=4):
    """
    Compute confusion matrix from predictions and labels.
    
    A confusion matrix shows:
        - Rows: True class
        - Columns: Predicted class
        - Cell [i,j]: Count of samples with true class i predicted as class j
    
    Args:
        predictions: numpy array of predicted class indices
        labels: numpy array of true class indices
        num_classes: number of classes (4)
    
    Returns:
        numpy array of shape (num_classes, num_classes)
    
    Example for 2 classes:
        [[50, 5],      # 50 true-0 predicted as 0, 5 true-0 predicted as 1
         [3, 42]]      # 3 true-1 predicted as 0, 42 true-1 predicted as 1
    
    Implementation:
        - Initialize zeros matrix
        - Loop through predictions and labels
        - Increment matrix[true_label, predicted_label]
    """
    pass  # TODO: Implement


def print_confusion_matrix(matrix, class_names):
    """
    Pretty print the confusion matrix.
    
    Args:
        matrix: numpy array from compute_confusion_matrix
        class_names: list like ['IDLE', 'TERRESTRIAL', 'MARITIME', 'LIFT']
    
    Output format:
        Predicted ->      IDLE  TERRESTRIAL  MARITIME      LIFT
        IDLE              45           2         0         1
        TERRESTRIAL        1          38         3         2
        ...
    """
    pass  # TODO: Implement


def print_classification_report(matrix, class_names):
    """
    Print precision, recall, F1 score for each class.
    
    Definitions:
        - Precision: Of all predicted as class X, how many were correct?
                     precision = TP / (TP + FP)
        
        - Recall: Of all actual class X, how many did we find?
                  recall = TP / (TP + FN)
        
        - F1: Harmonic mean of precision and recall
              f1 = 2 * precision * recall / (precision + recall)
    
    Where:
        - TP (True Positive): Correctly predicted as class X
        - FP (False Positive): Incorrectly predicted as class X
        - FN (False Negative): Actually class X but predicted differently
    
    Args:
        matrix: confusion matrix
        class_names: list of class names
    
    Implementation hints:
        - TP for class i: matrix[i, i]
        - FP for class i: sum of column i minus TP
        - FN for class i: sum of row i minus TP
    """
    pass  # TODO: Implement


# ============================================================================
# DATA LOADING
# ============================================================================

def load_all_data(data_dir):
    """
    Load and process data from all motion types.
    
    Args:
        data_dir: Path to data/generated_data directory
    
    Returns:
        X: numpy array of features, shape (n_samples, n_features)
        y: numpy array of labels, shape (n_samples,)
        extractor: FeatureExtractor instance (for n_features info)
    
    Implementation:
        1. Create FeatureExtractor
        2. For each motion type (idle, terrestrial, maritime, lift):
            a. Load CSV data
            b. Create windows
            c. Extract features
            d. Add to lists with appropriate labels
        3. Stack all features and labels
    """
    pass  # TODO: Implement


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
