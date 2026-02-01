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