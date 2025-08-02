# ahp.py
import numpy as np

def ahp_weights(matrix):
    """
    Compute criterion weights from an AHP pairwise comparison matrix.
    The matrix should be a square (NxN) numpy array or nested list, 
    where matrix[i][j] is the relative importance of criterion i vs j.
    We normalize each column and average rows to get the weight vector:contentReference[oaicite:8]{index=8}.
    """
    A = np.array(matrix, dtype=float)
    # Check for square matrix
    if A.shape[0] != A.shape[1]:
        raise ValueError("AHP matrix must be square")
    # Normalize columns
    col_sums = A.sum(axis=0)
    if np.any(col_sums == 0):
        raise ValueError("Column sums must not be zero")
    norm_matrix = A / col_sums
    # Average rows to get weights (priority vector)
    weights = norm_matrix.mean(axis=1)
    # Normalize weights to sum to 1
    return weights / weights.sum()
