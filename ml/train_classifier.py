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
    # Run with defaults
    python train_classifier.py
    
    # Custom training settings
    python train_classifier.py --epochs 200 --batch-size 64 --learning-rate 0.0005
    
    # Specify data and output locations
    python train_classifier.py --data-dir data/generated_data --model-output models/my_model.pt

Requirements:
    pip install torch numpy scikit-learn
"""

import argparse
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

<<<<<<< HEAD:ml/train_classifier.py

# ============================================================================
# ARGUMENT PARSING
# ============================================================================

def parse_args():
    """
    Parse command-line arguments for training configuration.
    
    This allows users to experiment with different hyperparameters
    without editing code.
    
    Returns:
        argparse.Namespace with all arguments as attributes
    """
    parser = argparse.ArgumentParser(
        description='Train motion classifier on sensor data',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Data arguments
    parser.add_argument('--data-dir', type=str, default='data/generated_data',
                        help='Directory containing training data')
    
    parser.add_argument('--features-file', type=str, default=None,
                        help='Pre-extracted features file (.npz). If provided, skip extraction.')
    
    # Training hyperparameters
    parser.add_argument('--epochs', type=int, default=100,
                        help='Maximum number of training epochs')
    
    parser.add_argument('--batch-size', type=int, default=32,
                        help='Number of samples per training batch')
    
    parser.add_argument('--learning-rate', type=float, default=0.001,
                        help='Learning rate for Adam optimizer')
    
    parser.add_argument('--patience', type=int, default=10,
                        help='Early stopping patience (epochs without improvement)')
    
    parser.add_argument('--dropout', type=float, default=0.3,
                        help='Dropout probability for regularization')
    
    # Model architecture
    parser.add_argument('--hidden-dims', type=int, nargs='+', default=[64, 32],
                        help='Hidden layer dimensions (e.g., --hidden-dims 64 32)')
    
    # Feature extraction (if not using pre-extracted)
    parser.add_argument('--window-size', type=int, default=100,
                        help='Window size for feature extraction')
    
    parser.add_argument('--overlap', type=float, default=0.5,
                        help='Window overlap for feature extraction')
    
    # Output arguments
    parser.add_argument('--model-output', type=str, default='models/motion_classifier.pt',
                        help='Path to save trained model')
    
    parser.add_argument('--history-output', type=str, default='models/training_history.json',
                        help='Path to save training history')
    
    # Runtime options
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed for reproducibility')
    
    parser.add_argument('--no-cuda', action='store_true',
                        help='Disable CUDA even if available')
    
    parser.add_argument('--verbose', action='store_true',
                        help='Print detailed training progress')
    
    return parser.parse_args()


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

def load_all_data(data_dir, window_size=100, overlap=0.5):
    """
    Load and process data from all motion types.
    
    Args:
        data_dir: Path to data/generated_data directory
        window_size: Window size for feature extraction
        overlap: Window overlap for feature extraction
    
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


=======
>>>>>>> 997c19f (Committing Initial File Split):machine-learning/train_classifier.py
# ============================================================================
# MAIN TRAINING SCRIPT
# ============================================================================

def main():
    """
    Main training function.
    
    Uses command-line arguments to configure training.
    
    Steps:
        1. Parse arguments
        2. Set random seeds for reproducibility
        3. Load and preprocess data
        4. Create train/val/test splits
        5. Initialize model, optimizer, loss function
        6. Training loop with early stopping
        7. Evaluate on test set
        8. Save model and results
    """
    # Parse arguments
    args = parse_args()
    
    # Set random seeds for reproducibility
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    
    # Determine device
    if args.no_cuda:
        device = torch.device('cpu')
    else:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Class names for reporting
    CLASS_NAMES = ['IDLE', 'TERRESTRIAL', 'MARITIME', 'LIFT']
    
    if args.verbose:
        print("=" * 60)
        print("Motion Classifier Training")
        print("=" * 60)
        print(f"  Device:         {device}")
        print(f"  Data directory: {args.data_dir}")
        print(f"  Epochs:         {args.epochs}")
        print(f"  Batch size:     {args.batch_size}")
        print(f"  Learning rate:  {args.learning_rate}")
        print(f"  Hidden dims:    {args.hidden_dims}")
        print(f"  Dropout:        {args.dropout}")
        print(f"  Patience:       {args.patience}")
        print(f"  Model output:   {args.model_output}")
        print("=" * 60)
    
    # Create output directory
    Path(args.model_output).parent.mkdir(parents=True, exist_ok=True)
    
    # =========================================================================
    # TODO: Implement the rest of main()
    # =========================================================================
    #
    # 1. Load data:
    #    X, y, extractor = load_all_data(args.data_dir, args.window_size, args.overlap)
    #    X_normalized, scaler = normalize_features(X)
    #
    # 2. Create dataset and split:
    #    dataset = MotionDataset(X_normalized, y)
    #    train_set, val_set, test_set = random_split(dataset, [0.7, 0.15, 0.15])
    #
    # 3. Create dataloaders:
    #    train_loader = DataLoader(train_set, batch_size=args.batch_size, shuffle=True)
    #    val_loader = DataLoader(val_set, batch_size=args.batch_size)
    #    test_loader = DataLoader(test_set, batch_size=args.batch_size)
    #
    # 4. Initialize model:
    #    model = MotionClassifier(
    #        input_dim=extractor.n_features,
    #        hidden_dims=tuple(args.hidden_dims),
    #        dropout=args.dropout
    #    ).to(device)
    #    criterion = nn.CrossEntropyLoss()
    #    optimizer = optim.Adam(model.parameters(), lr=args.learning_rate)
    #
    # 5. Training loop with early stopping:
    #    best_val_acc = 0
    #    patience_counter = 0
    #    history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}
    #
    #    for epoch in range(args.epochs):
    #        train_loss, train_acc = train_epoch(...)
    #        val_loss, val_acc, _, _ = evaluate(...)
    #
    #        # Early stopping check
    #        if val_acc > best_val_acc:
    #            best_val_acc = val_acc
    #            patience_counter = 0
    #            # Save best model
    #        else:
    #            patience_counter += 1
    #            if patience_counter >= args.patience:
    #                print("Early stopping!")
    #                break
    #
    # 6. Evaluate on test set and print results
    #
    # 7. Save model and training history
    #
    pass  # TODO: Implement


if __name__ == '__main__':
    main()
