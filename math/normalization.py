# normalization.py
import numpy as np

def min_max_scale(arr):
    """
    Min-Max normalize a 1D list or numpy array to range [0, 1]. 
    Each value is transformed as (x - min) / (max - min).
    """
    arr = np.array(arr, dtype=float)
    min_val = np.min(arr)
    max_val = np.max(arr)
    if max_val - min_val == 0:
        # Avoid division by zero if constant array
        return np.zeros_like(arr)
    return (arr - min_val) / (max_val - min_val)

def z_score_scale(arr):
    """
    Z-score normalize a 1D list or numpy array to zero mean and unit variance.
    Each value is transformed as (x - mean) / std_dev.
    """
    arr = np.array(arr, dtype=float)
    mean = np.mean(arr)
    std = np.std(arr, ddof=0)
    if std == 0:
        # Avoid division by zero if constant array
        return np.zeros_like(arr)
    return (arr - mean) / std

