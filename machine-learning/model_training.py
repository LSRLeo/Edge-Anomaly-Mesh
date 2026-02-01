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