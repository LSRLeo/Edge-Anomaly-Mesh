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
        # Accept lists or arrays
        features = np.asarray(features, dtype=np.float32)
        labels = np.asarray(labels, dtype=np.int64)

        # Basic shape validation
        if features.ndim != 2:
            raise ValueError(f"features must be 2D (n_samples, n_features). Got {features.shape}")
        if labels.ndim != 1:
            raise ValueError(f"labels must be 1D (n_samples,). Got {labels.shape}")
        if features.shape[0] != labels.shape[0]:
            raise ValueError(f"mismatch: features has {features.shape[0]} rows, labels has {labels.shape[0]}")

        self.features = torch.from_numpy(features)  # float32
        self.labels = torch.from_numpy(labels)      # int64 (LongTensor)

    
    def __len__(self):
        """
        Return the total number of samples.
        
        Returns:
            int: Number of samples in dataset
        """
        return self.features.shape[0]

    
    def __getitem__(self, idx):

        """
        Return one sample by index.
        
        Args:
            idx: integer index
        
        Returns:
            tuple: (features_tensor, label_tensor) for sample at idx
        """
        if torch.is_tensor(idx):
            idx = idx.item()

        return self.features[idx], self.labels[idx]


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
    # If scaler not provided, compute from the data (training scenario)
    if scaler is None:
        mean = np.mean(features, axis=0)
        std = np.std(features, axis=0)
    else:
        # Use provided scaler (test/validation scenario)
        mean, std = scaler

    # Handle std=0 case to avoid division by zero
    # If std is 0, the feature is constant, so we don't normalize it
    std = np.where(std == 0, 1, std)

    # Normalize: (x - mean) / std
    normalized = (features - mean) / std

    # Return normalized features and scaler for future use
    return normalized, (mean, std)