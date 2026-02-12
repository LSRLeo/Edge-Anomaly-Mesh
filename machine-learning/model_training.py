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

# ============================================================================
# EVALUATION METRICS
# ============================================================================

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
    
    model.eval()  # disables dropout / batchnorm updates

    total_loss = 0.0
    correct = 0
    total = 0

    all_predictions = []
    all_labels = []

    with torch.no_grad():  # no gradient computation during evaluation

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