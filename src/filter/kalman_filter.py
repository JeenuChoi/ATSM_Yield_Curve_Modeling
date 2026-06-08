import numpy as np
from scipy.linalg import cho_factor, cho_solve

class KalmanFilter:
    """
    Implements a standard linear Kalman Filter for a Gaussian State-Space Model.
    """

    def __init__(self, Phi, Q, H, R, drift, intercept):
        self.Phi = Phi
        self.Q = Q
        self.H = H
        self.R = R
        self.drift = drift
        self.intercept = intercept
        self.n_factors = Phi.shape[0]
        self.n_yields = H.shape[0]

    def filter(self, observations: np.ndarray, initial_X: np.ndarray, initial_P: np.ndarray) \
            -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, float]:
        """
        Applies the Kalman filter to a series of observations.

        Returns:
            A tuple containing:
            - X_filtered, P_filtered: Filtered states and covariances.
            - X_predicted, P_predicted: Predicted states and covariances.
            - log_likelihood: Cumulative log-likelihood.
        """
        num_timesteps = observations.shape[0]
        
        # --- Input Validation ---
        # ... (as before, but let's re-add it for robustness)

        # Initialize storage arrays
        X_filtered = np.zeros((num_timesteps, self.n_factors))
        P_filtered = np.zeros((num_timesteps, self.n_factors, self.n_factors))
        X_predicted = np.zeros((num_timesteps, self.n_factors))
        P_predicted = np.zeros((num_timesteps, self.n_factors, self.n_factors))
        log_likelihood = 0.0

        # Reshape initial state and set initial loop values
        X_t_minus_1_filtered = initial_X.reshape(-1, 1)
        P_t_minus_1_filtered = initial_P

        for t in range(num_timesteps):
            # --- Prediction Step ---
            X_t_pred = self.Phi @ X_t_minus_1_filtered + self.drift
            P_t_pred = self.Phi @ P_t_minus_1_filtered @ self.Phi.T + self.Q
            # Ensure Symmetry and add small jitter (1e-6) for stability
            P_t_pred = (P_t_pred + P_t_pred.T) / 2.0 + np.eye(self.n_factors) * 1e-6
            
            X_predicted[t, :] = X_t_pred.flatten()
            P_predicted[t, :, :] = P_t_pred

            # --- Update Step ---
            Y_t = observations[t, :].reshape(-1, 1)
            # Ensure intercept is (n_yields, 1)
            y_pred = self.H @ X_t_pred + self.intercept
            v_t = Y_t - y_pred
            
            F_t = self.H @ P_t_pred @ self.H.T + self.R
            F_t = (F_t + F_t.T) / 2.0 + np.eye(self.n_yields) * 1e-9

            try:
                c_F_t, lower = cho_factor(F_t, lower=True)
                diag_vals = np.diag(c_F_t)
                if np.any(diag_vals <= 0): 
                    return X_filtered, P_filtered, X_predicted, P_predicted, -1e15
                
                log_det_F_t = 2 * np.sum(np.log(diag_vals))
                F_t_inv_v_t = cho_solve((c_F_t, lower), v_t)
                quadratic_form = (v_t.T @ F_t_inv_v_t).item()
                
                step_log_lik = -0.5 * (self.n_yields * np.log(2 * np.pi) + log_det_F_t + quadratic_form)
                if np.isnan(step_log_lik) or np.isinf(step_log_lik): 
                    return X_filtered, P_filtered, X_predicted, P_predicted, -1e15
                
                log_likelihood += step_log_lik
                K_t = (cho_solve((c_F_t, lower), self.H @ P_t_pred)).T
            except (np.linalg.LinAlgError, ValueError):
                return X_filtered, P_filtered, X_predicted, P_predicted, -1e15

            # Updated estimates
            X_t_filt = X_t_pred + K_t @ v_t
            P_t_filt = (np.eye(self.n_factors) - K_t @ self.H) @ P_t_pred
            P_t_filt = (P_t_filt + P_t_filt.T) / 2.0
            
            # Store results
            X_filtered[t, :] = X_t_filt.flatten()
            P_filtered[t, :, :] = P_t_filt

            # Prepare for next iteration
            X_t_minus_1_filtered = X_t_filt
            P_t_minus_1_filtered = P_t_filt
        
        return X_filtered, P_filtered, X_predicted, P_predicted, log_likelihood
