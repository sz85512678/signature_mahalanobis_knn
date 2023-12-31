import numpy as np
from numpy import ndarray

__all__ = "Mahalanobis"


class Mahalanobis():
    """
    After fit is called, becomes callable and intended to be used as a distance function in sklearn nearest neighbour
    """

    def __init__(self):
        self.Vt: ndarray = np.empty(0)  # Truncated right singular matrix transposed of the corpus
        self.mu: ndarray = np.empty(0)  # Mean of the corpus
        self.S: ndarray = np.empty(0)  # Truncated singular values of the corpus
        self.subspace_thres: float = 1e-3  # Threshold to decide whether a point is in the data subspace
        self.svd_thres: float = 1e-12  # Threshold to decide numerical rank of the data matrix
        self.numerical_rank: int = -1  # Numerical rank

    def fit(self, X: ndarray, y=None) -> None:
        """
        Fit the object to a corpus X
        :param X: ND array, panel data representing the corpus, each row is a data point
        :param y: No use, here for interface consistency
        :return: None
        """
        # mean centering
        self.mu = np.mean(X, axis=0)
        X = X - self.mu

        U, S, Vt = np.linalg.svd(X)
        k = np.sum(S >= self.svd_thres)  # detected numerical rank
        self.numerical_rank = k
        self.Vt = Vt[:k]
        self.S = S[:k]

    def distance(self, x1: ndarray, x2: ndarray) -> float:
        """
        Compute the variance norm between x1 and x2
        :param x1: 1D array, row vector
        :param x2: 1D array, row vector
        :return: a value representing distance between x, y
        """
        x = x1 - x2
        # quantifies the amount that x is outside the row-subspace
        if np.linalg.norm(x) < 1e-15:
            return 0
        rho = np.linalg.norm(x - x @ self.Vt.T @ self.Vt) / np.linalg.norm(x)

        if rho > self.subspace_thres:
            return np.inf
        else:
            return x @ self.Vt.T @ np.diag(self.S ** (-2)) @ self.Vt @ x.T
