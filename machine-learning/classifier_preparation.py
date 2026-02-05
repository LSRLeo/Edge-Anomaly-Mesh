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

def normalize_features(features, scaler=None):
    """
    Normalize features to zero mean and unit variance.
    
    Normalization is important because:
        - Features have different scales (accel in m/s², gyro in rad/s)
        - Neural networks train better with normalized inputs
        - Prevents features with large values from dominating
    
    Args:
        features: numpy array of shape (n_samples, n_features)
        scaler: optional tuple of (mean, std) from training data
                If None, compute from the input features.
                If provided, use these values (for test data).
    
    Returns:
        normalized: numpy array of same shape, normalized
        scaler: tuple of (mean, std) arrays for reuse
    
    Formula:
        normalized = (features - mean) / std
    
    Implementation hints:
        - Compute mean and std along axis=0 (per feature)
        - Handle std=0 case: set to 1 to avoid division by zero
        - Save scaler during training, reuse for inference
    """
    pass  # TODO: Implement

# def load_all_data(data_dir):

#     """
#     Load and process data from all motion types.
    
#     Args:
#         data_dir: Path to data/generated_data directory
    
#     Returns:
#         X: numpy array of features, shape (n_samples, n_features)
#         y: numpy array of labels, shape (n_samples,)
#         extractor: FeatureExtractor instance (for n_features info)
    
#     Implementation:
#         1. Create FeatureExtractor
#         2. For each motion type (idle, terrestrial, maritime, lift):
#             a. Load CSV data
#             b. Create windows
#             c. Extract features
#             d. Add to lists with appropriate labels
#         3. Stack all features and labels
#     """
#     pass  # TODO: Implement