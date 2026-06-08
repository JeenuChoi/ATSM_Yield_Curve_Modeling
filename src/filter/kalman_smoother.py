import numpy as np
from scipy.linalg import cho_factor, cho_solve

class KalmanSmoother:
    """
    Implements the Rauch-Tung-Striebel (RTS) Kalman Smoother.
    """
    def __init__(self, Phi: np.ndarray, Q: np.ndarray):
        """
        Initializes the Kalman Smoother with state transition matrices.

        Args:
            Phi (np.ndarray): n_factors x n_factors state transition matrix.
            Q (np.ndarray): n_factors x n_factors covariance matrix of state innovations.
        """
        self.Phi = Phi
        self.Q = Q
        self.n_factors = Phi.shape[0]

    def smooth(self, X_filtered: np.ndarray, P_filtered: np.ndarray,
               X_predicted: np.ndarray, P_predicted: np.ndarray) \
            -> tuple[np.ndarray, np.ndarray]:
        """
        Applies the RTS smoother to filtered and predicted Kalman filter outputs.

        Args:
            X_filtered (np.ndarray): Filtered state estimates. Shape (num_timesteps, n_factors).
            P_filtered (np.ndarray): Filtered state covariances. Shape (num_timesteps, n_factors, n_factors).
            X_predicted (np.ndarray): Predicted state estimates. Shape (num_timesteps, n_factors).
            P_predicted (np.ndarray): Predicted state covariances. Shape (num_timesteps, n_factors, n_factors).

        Returns:
            A tuple containing:
            - X_smoothed (np.ndarray): Smoothed state estimates. Shape (num_timesteps, n_factors).
            - P_smoothed (np.ndarray): Smoothed state covariances. Shape (num_timesteps, n_factors, n_factors).
        """
        num_timesteps = X_filtered.shape[0]

        X_smoothed = np.zeros_like(X_filtered)
        P_smoothed = np.zeros_like(P_filtered)

        # Initialize with the last filtered state
        X_smoothed[-1, :] = X_filtered[-1, :]
        P_smoothed[-1, :, :] = P_filtered[-1, :, :]

        for t in range(num_timesteps - 2, -1, -1):
            # Get filtered and predicted estimates for time t and t+1
            P_t_filt = P_filtered[t, :, :]
            P_t_plus_1_pred = P_predicted[t+1, :, :]

            try:
                # Smoother Gain: G_t = P_{t|t} * Phi' * (P_{t+1|t})^{-1}
                c, lower = cho_factor(P_t_plus_1_pred, lower=True)
                smoother_gain = (cho_solve((c, lower), self.Phi @ P_t_filt)).T
            except (np.linalg.LinAlgError, ValueError):
                # If singular, we cannot improve the estimate using future data
                smoother_gain = np.zeros((self.n_factors, self.n_factors))

            # Smoothed state
            X_smoothed[t, :] = X_filtered[t, :] + smoother_gain @ (X_smoothed[t+1, :] - X_predicted[t+1, :])

            # Smoothed covariance
            P_smoothed[t, :, :] = P_t_filt + smoother_gain @ (P_smoothed[t+1, :, :] - P_t_plus_1_pred) @ smoother_gain.T
            P_smoothed[t, :, :] = (P_smoothed[t, :, :] + P_smoothed[t, :, :].T) / 2.0

        return X_smoothed, P_smoothed