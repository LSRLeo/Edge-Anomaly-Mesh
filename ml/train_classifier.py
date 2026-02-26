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

# Clear model history
import gc
def clear_torch_session():
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()

clear_torch_session()

def load_json_strict(path):
    p = Path(path)

    if not p.exists():
        raise FileNotFoundError(f"JSON file not found: {p}")

    if p.stat().st_size == 0:
        raise ValueError(f"JSON file is empty: {p}")

    with open(p, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in file: {p}")

    if data is None or (isinstance(data, (dict, list)) and len(data) == 0):
        raise ValueError(f"JSON file contains no usable data: {p}")

    return data


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

    parser.add_argument('--results-output', type=str, default='models/inference_results.json',
                        help='Path to save inference results JSON for database team')
    
    # Runtime options
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed for reproducibility')
    
    parser.add_argument('--no-cuda', action='store_true',
                        help='Disable CUDA even if available')
    
    parser.add_argument('--verbose', default=True, action='store_true',
                        help='Print detailed training progress')
    
    parser.add_argument('--norm-stats-output', type=str,
                    default='ml/classifier/normalization_stats.json',
                    help='Path to save normalization mean/std stats as JSON')
    
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
                    0=IDLE, 1=TERRESTRIAL, 2=MARITIME, 3=LIFT,
                    4=IDLE_ANOM, 5=TERRESTRIAL_ANOM, 6=MARITIME_ANOM, 7=LIFT_ANOM

        Implementation:
            - Convert numpy arrays to PyTorch tensors
            - features → torch.FloatTensor (32-bit float)
            - labels → torch.LongTensor (64-bit integer, required for CrossEntropyLoss)
        """
        self.features = torch.FloatTensor(features)
        self.labels = torch.LongTensor(labels)

    def __len__(self):
        """
        Return the total number of samples.

        Returns:
            int: Number of samples in dataset
        """
        return len(self.features)

    def __getitem__(self, idx):
        """
        Return one sample by index.

        Args:
            idx: integer index

        Returns:
            tuple: (features_tensor, label_tensor) for sample at idx
        """
        return self.features[idx], self.labels[idx]


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
    
    def __init__(self, input_dim, num_classes=8, hidden_dims=(64, 32), dropout=0.3):
        """
        Initialize the model layers.

        Args:
            input_dim: Number of input features (e.g., 20)
            num_classes: Number of output classes (8 for terrain type + anomaly status)
                         Classes 0-3: IDLE, TERRESTRIAL, MARITIME, LIFT (no anomaly)
                         Classes 4-7: IDLE, TERRESTRIAL, MARITIME, LIFT (with anomaly)
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

        # Build the network architecture (supports any number of hidden layers)
        hidden_dims = list(hidden_dims)
        if len(hidden_dims) == 0:
            raise ValueError("hidden_dims must have at least 1 layer size")

        layers = []
        prev_dim = input_dim

        for h in hidden_dims:
            layers.append(nn.Linear(prev_dim, h))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout))
            prev_dim = h

        layers.append(nn.Linear(prev_dim, num_classes))
        self.network = nn.Sequential(*layers)

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
        return self.network(x)
    
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
        with torch.no_grad():
            # Get logits from forward pass
            logits = self.forward(x)

            # Apply softmax to convert logits to probabilities
            probabilities = torch.softmax(logits, dim=1)

            # Get the highest probability and its index
            confidence, predicted = torch.max(probabilities, dim=1)

            return predicted, confidence

# ============================================================================
# TRAINING FUNCTIONS
# ============================================================================

def save_normalization_stats(scaler, out_path: str):
    mean, std = scaler  # scaler is (mean, std) from feature_extraction.normalize_features

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    stats = {
        "mean": mean.tolist(),
        "std": std.tolist(),
        "std_zero_replaced_with_1": True
    }

    with open(out_path, "w") as f:
        json.dump(stats, f, indent=2)


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
    model.train()  # Enable dropout and batch normalization training mode

    total_loss = 0.0
    correct = 0
    total = 0

    for features, labels in dataloader:
        # 1. Move data to device
        features = features.to(device)
        labels = labels.to(device)

        # 2. Zero gradients from previous iteration
        optimizer.zero_grad()

        # 3. Forward pass
        outputs = model(features)

        # 4. Compute loss
        loss = criterion(outputs, labels)

        # 5. Backward pass (compute gradients)
        loss.backward()

        # 6. Update weights
        optimizer.step()

        # 7. Track statistics
        total_loss += loss.item() * features.size(0)  # Multiply by batch size for weighted average

        # Get predictions (class with highest score)
        _, predictions = torch.max(outputs, dim=1)
        correct += (predictions == labels).sum().item()
        total += labels.size(0)

    # Compute averages
    avg_loss = total_loss / total
    accuracy = correct / total

    return avg_loss, accuracy


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
    model.eval()  # Disables dropout / batchnorm updates

    total_loss = 0.0
    correct = 0
    total = 0

    all_predictions = []
    all_labels = []

    with torch.no_grad():  # No gradient computation during evaluation
        for inputs, labels in dataloader:
            inputs = inputs.to(device)
            labels = labels.to(device)

            outputs = model(inputs)
            loss = criterion(outputs, labels)

            total_loss += loss.item() * inputs.size(0)

            _, preds = torch.max(outputs, dim=1)

            correct += (preds == labels).sum().item()
            total += labels.size(0)

            all_predictions.append(preds.cpu())
            all_labels.append(labels.cpu())

    avg_loss = total_loss / total
    accuracy = correct / total

    predictions = torch.cat(all_predictions).numpy()
    labels = torch.cat(all_labels).numpy()

    return avg_loss, accuracy, predictions, labels


# ============================================================================
# LABEL UTILITIES
# ============================================================================

def decode_combined_label(label):
    """
    Decode a combined label (0-7) into terrain type and anomaly status.

    Args:
        label: integer from 0-7

    Returns:
        terrain_type: integer from 0-3 (IDLE, TERRESTRIAL, MARITIME, LIFT)
        has_anomaly: boolean (True if anomaly, False otherwise)

    Example:
        decode_combined_label(1) -> (1, False)  # TERRESTRIAL, no anomaly
        decode_combined_label(5) -> (1, True)   # TERRESTRIAL, with anomaly
    """
    terrain_type = label % 4
    has_anomaly = label >= 4
    return terrain_type, has_anomaly


def encode_combined_label(terrain_type, has_anomaly):
    """
    Encode terrain type and anomaly status into a single label (0-7).

    Args:
        terrain_type: integer from 0-3 (IDLE, TERRESTRIAL, MARITIME, LIFT)
        has_anomaly: boolean (True if anomaly, False otherwise)

    Returns:
        label: integer from 0-7

    Example:
        encode_combined_label(1, False) -> 1  # TERRESTRIAL, no anomaly
        encode_combined_label(1, True) -> 5   # TERRESTRIAL, with anomaly
    """
    return terrain_type + (4 if has_anomaly else 0)


def extract_terrain_predictions(predictions):
    """
    Extract just the terrain type predictions, ignoring anomaly status.

    Args:
        predictions: numpy array of combined labels (0-7)

    Returns:
        terrain_predictions: numpy array of terrain types (0-3)
    """
    return predictions % 4


def extract_anomaly_predictions(predictions):
    """
    Extract just the anomaly predictions, ignoring terrain type.

    Args:
        predictions: numpy array of combined labels (0-7)

    Returns:
        anomaly_predictions: numpy array of booleans
    """
    return predictions >= 4


def compute_separate_accuracies(predictions, labels):
    """
    Compute separate accuracies for terrain classification and anomaly detection.

    Args:
        predictions: numpy array of predicted combined labels (0-7)
        labels: numpy array of true combined labels (0-7)

    Returns:
        dict with keys:
            - 'joint_accuracy': Both terrain AND anomaly correct
            - 'terrain_accuracy': Terrain type correct (ignoring anomaly)
            - 'anomaly_accuracy': Anomaly status correct (ignoring terrain)
    """
    # Joint accuracy (both must be correct)
    joint_accuracy = (predictions == labels).mean()

    # Terrain accuracy (ignoring anomaly)
    pred_terrain = extract_terrain_predictions(predictions)
    true_terrain = extract_terrain_predictions(labels)
    terrain_accuracy = (pred_terrain == true_terrain).mean()

    # Anomaly accuracy (ignoring terrain)
    pred_anomaly = extract_anomaly_predictions(predictions)
    true_anomaly = extract_anomaly_predictions(labels)
    anomaly_accuracy = (pred_anomaly == true_anomaly).mean()

    return {
        'joint_accuracy': joint_accuracy,
        'terrain_accuracy': terrain_accuracy,
        'anomaly_accuracy': anomaly_accuracy
    }


# ============================================================================
# EVALUATION METRICS
# ============================================================================

def compute_confusion_matrix(predictions, labels, num_classes=8):
    """
    Compute confusion matrix from predictions and labels.

    A confusion matrix shows:
        - Rows: True class
        - Columns: Predicted class
        - Cell [i,j]: Count of samples with true class i predicted as class j

    Args:
        predictions: numpy array of predicted class indices
        labels: numpy array of true class indices
        num_classes: number of classes (8)

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
    # Initialize confusion matrix with zeros
    matrix = np.zeros((num_classes, num_classes), dtype=int)

    # Fill the matrix by counting predictions
    for true_label, predicted_label in zip(labels, predictions):
        matrix[true_label, predicted_label] += 1

    return matrix


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
    print("\nConfusion Matrix")
    print("=" * 80)

    # Print header row
    print(f"{'True \\ Pred':<20}", end="")
    for name in class_names:
        print(f"{name:>12}", end="")
    print()
    print("-" * 80)

    # Print each row
    for i, true_class in enumerate(class_names):
        print(f"{true_class:<20}", end="")
        for j in range(len(class_names)):
            print(f"{matrix[i, j]:>12}", end="")
        print()


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
    print("\nClassification Report")
    print("-" * 40)

    for i in range(len(class_names)):
        TP = matrix[i, i]
        FP = matrix[:, i].sum() - TP
        FN = matrix[i, :].sum() - TP

        if TP + FP > 0:
            precision = TP / (TP + FP)
        else:
            precision = 0.0

        if TP + FN > 0:
            recall = TP / (TP + FN)
        else:
            recall = 0.0

        if precision + recall > 0:
            f1 = 2 * precision * recall / (precision + recall)
        else:
            f1 = 0.0

        print(class_names[i])
        print("  Precision:", round(precision, 4))
        print("  Recall:   ", round(recall, 4))
        print("  F1 Score: ", round(f1, 4))
        print()


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
            a. Load JSON data
            b. Create windows
            c. Extract features
            d. Add to lists with appropriate labels
        3. Stack all features and labels
    """
    from pathlib import Path
    from data_pipeline import load_json_data, create_windows, windows_to_features

    # Create feature extractor
    extractor = FeatureExtractor(sample_rate=50)

    # Find all JSON files
    data_path = Path(data_dir)
    json_files = list(data_path.glob("**/*.json"))

    if not json_files:
        raise ValueError(f"No JSON files found in {data_dir}")

    all_features = []
    all_labels = []

    print(f"Loading data from {len(json_files)} files...")

    for json_file in json_files:
        print(f"  Processing: {json_file.name}")

        # Load data and labels
        data, labels = load_json_data(json_file)

        # Create windows
        windows, window_labels = create_windows(data, window_size=window_size, overlap=overlap, labels=labels)

        # Extract features
        features = windows_to_features(windows, sample_rate=50)

        # Add to lists
        all_features.append(features)
        all_labels.append(window_labels)

        print(f"    {len(features)} windows extracted")

    # Stack all data
    X = np.vstack(all_features)
    y = np.concatenate(all_labels)

    print(f"\nTotal samples: {len(X)}")
    print(f"Feature shape: {X.shape}")
    print(f"Unique labels: {np.unique(y)}")

    return X, y, extractor


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
    
    # Class names for reporting (8 classes: 4 terrain types × 2 anomaly states)
    CLASS_NAMES = [
        'IDLE', 'TERRESTRIAL', 'MARITIME', 'LIFT',           # No anomaly (0-3)
        'IDLE_ANOM', 'TERRESTRIAL_ANOM', 'MARITIME_ANOM', 'LIFT_ANOM'  # With anomaly (4-7)
    ]
    
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
    # 1. Load and preprocess data
    # =========================================================================
    print("\n" + "=" * 60)
    print("Loading and preprocessing data...")
    print("=" * 60)

    X, y, extractor = load_all_data(args.data_dir, args.window_size, args.overlap)
    X_normalized, scaler = normalize_features(X)
    save_normalization_stats(scaler, args.norm_stats_output)

    # =========================================================================
    # 2. Create dataset and split
    # =========================================================================
    print("\nCreating train/val/test splits...")
    dataset = MotionDataset(X_normalized, y)

    # Split: 70% train, 15% validation, 15% test
    train_size = int(0.7 * len(dataset))
    val_size = int(0.15 * len(dataset))
    test_size = len(dataset) - train_size - val_size

    train_set, val_set, test_set = random_split(
        dataset, [train_size, val_size, test_size],
        generator=torch.Generator().manual_seed(args.seed)
    )

    print(f"  Train set:      {len(train_set)} samples")
    print(f"  Validation set: {len(val_set)} samples")
    print(f"  Test set:       {len(test_set)} samples")

    # =========================================================================
    # 3. Create dataloaders
    # =========================================================================
    train_loader = DataLoader(train_set, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_set, batch_size=args.batch_size, shuffle=False)
    test_loader = DataLoader(test_set, batch_size=args.batch_size, shuffle=False)

    # =========================================================================
    # 4. Initialize model, criterion, optimizer
    # =========================================================================
    print("\nInitializing model...")
    model = MotionClassifier(
        input_dim=extractor.n_features,
        hidden_dims=tuple(args.hidden_dims),
        dropout=args.dropout
    ).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.learning_rate)

    print(f"  Model parameters: {sum(p.numel() for p in model.parameters())}")

    # =========================================================================
    # 5. Training loop with early stopping
    # =========================================================================
    print("\n" + "=" * 60)
    print("Training...")
    print("=" * 60)

    best_val_acc = 0
    patience_counter = 0
    history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}

    for epoch in range(args.epochs):
        # Train for one epoch
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)

        # Evaluate on validation set
        val_loss, val_acc, _, _ = evaluate(model, val_loader, criterion, device)

        # Record history
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)

        # Print progress
        print(f"Epoch {epoch+1}/{args.epochs}")
        print(f"  Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}")
        print(f"  Val Loss:   {val_loss:.4f}, Val Acc:   {val_acc:.4f}")

        # Early stopping check
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            patience_counter = 0
            # Save best model
            torch.save(model.state_dict(), args.model_output)
            print(f"  ✓ New best model saved (val_acc: {val_acc:.4f})")
        else:
            patience_counter += 1
            print(f"  No improvement ({patience_counter}/{args.patience})")

            if patience_counter >= args.patience:
                print(f"\nEarly stopping triggered after {epoch+1} epochs")
                break

    # =========================================================================
    # 6. Load best model and evaluate on test set
    # =========================================================================
    print("\n" + "=" * 60)
    print("Evaluating best model on test set...")
    print("=" * 60)

    model.load_state_dict(torch.load(args.model_output))
    test_loss, test_acc, predictions, labels = evaluate(model, test_loader, criterion, device)

    print(f"\nTest Loss: {test_loss:.4f}")
    print(f"Test Accuracy: {test_acc:.4f}")

    # Compute separate accuracies
    separate_accs = compute_separate_accuracies(predictions, labels)
    print(f"\nSeparate Accuracies:")
    print(f"  Joint (terrain + anomaly): {separate_accs['joint_accuracy']:.4f}")
    print(f"  Terrain only:              {separate_accs['terrain_accuracy']:.4f}")
    print(f"  Anomaly only:              {separate_accs['anomaly_accuracy']:.4f}")

    # Print confusion matrix and classification report
    conf_matrix = compute_confusion_matrix(predictions, labels)
    print_confusion_matrix(conf_matrix, CLASS_NAMES)
    print_classification_report(conf_matrix, CLASS_NAMES)

    # =========================================================================
    # 7. Save inference results to JSON (for database team)
    # =========================================================================
    print("\nExporting inference results to JSON...")

    model.eval()
    all_probabilities = []

    with torch.no_grad():
        for inputs, _ in test_loader:
            inputs = inputs.to(device)
            logits = model(inputs)
            probs = torch.softmax(logits, dim=1)
            all_probabilities.append(probs.cpu().numpy())

    all_probabilities = np.vstack(all_probabilities)

    inference_results = []
    for i in range(len(all_probabilities)):
        probs = all_probabilities[i]
        predicted_class = int(predictions[i])
        true_class = int(labels[i])

        inference_results.append({
            "sample_index": i,
            "probabilities": {
                "IDLE": round(float(probs[0]), 6),
                "TERRESTRIAL": round(float(probs[1]), 6),
                "MARITIME": round(float(probs[2]), 6),
                "LIFT": round(float(probs[3]), 6),
                "IDLE_ANOM": round(float(probs[4]), 6),
                "TERRESTRIAL_ANOM": round(float(probs[5]), 6),
                "MARITIME_ANOM": round(float(probs[6]), 6),
                "LIFT_ANOM": round(float(probs[7]), 6),
            },
            "predicted_class": CLASS_NAMES[predicted_class],
            "true_class": CLASS_NAMES[true_class],
        })

    results_path = Path(args.results_output)
    results_path.parent.mkdir(parents=True, exist_ok=True)

    with open(results_path, 'w') as f:
        json.dump(inference_results, f, indent=2)

    print(f"  Saved {len(inference_results)} inference results to {args.results_output}")

    # =========================================================================
    # 8. Save training history
    # =========================================================================
    history_path = Path(args.history_output)
    history_path.parent.mkdir(parents=True, exist_ok=True)

    with open(history_path, 'w') as f:
        json.dump(history, f, indent=2)

    print("\n" + "=" * 60)
    print("Training complete!")
    print("=" * 60)
    print(f"Best model saved to:       {args.model_output}")
    print(f"Training history saved to: {args.history_output}")
    print(f"Inference results saved to: {args.results_output}")
    print(f"Best validation accuracy:  {best_val_acc:.4f}")
    print(f"Test accuracy:             {test_acc:.4f}")


if __name__ == '__main__':
    main()
