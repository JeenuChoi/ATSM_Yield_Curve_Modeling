import numpy as np
from src.filter.kalman_filter import KalmanFilter
from src.model.state_space import build_state_space_from_vector
from src.model.parameterization import ATSMParams # To get initial param vector

def calculate_log_likelihood(
    param_vector: np.ndarray,
    observations: np.ndarray,
    maturities: np.ndarray,
    delta_t: float,
    n_factors: int,
    n_yields: int,
    initial_X: np.ndarray = None,
    initial_P: np.ndarray = None
) -> float:
    """
    Calculates the log-likelihood of observations using the Kalman filter for the ATSM.
    This function serves as a wrapper for the Kalman filter, used by an optimizer.

    Args:
        param_vector (np.ndarray): 1D array of unconstrained model parameters.
        observations (np.ndarray): Time series of observations (yields).
                                   Shape: (num_timesteps, n_yields).
        maturities (np.ndarray): 1D array of maturities for the observed yields.
        delta_t (float): The time step for discretization.
        n_factors (int): The number of latent factors.
        n_yields (int): The number of observed yields.
        initial_X (np.ndarray, optional): Initial state estimate (n_factors,). 
                                          Defaults to a zero vector.
        initial_P (np.ndarray, optional): Initial state covariance (n_factors, n_factors).
                                          Defaults to a diffuse prior (large diagonal matrix).

    Returns:
        float: The cumulative log-likelihood. Returns -np.inf if any step fails.
    """
    if initial_X is None:
        initial_X = np.zeros(n_factors)
    
    if initial_P is None:
        initial_P = np.eye(n_factors) * 1e6 # Diffuse prior

    try:
        # 1. Build the state-space model from the current parameter vector
        ss_model = build_state_space_from_vector(
            param_vector, maturities, delta_t, n_factors, n_yields
        )

        # 2. Initialize and run the Kalman filter
        kalman_filter = KalmanFilter(
            Phi=ss_model.Phi,
            Q=ss_model.Q,
            H=ss_model.H,
            R=ss_model.R,
            drift=ss_model.drift,
            intercept=ss_model.intercept
        )
        
        # Correctly unpack 5 values
        _, _, _, _, log_likelihood = kalman_filter.filter(observations, initial_X, initial_P)
        
        return log_likelihood

    except (ValueError, RuntimeError, np.linalg.LinAlgError) as e:
        # Debug: Print the reason for failure
        print(f"Likelihood failure: {e}")
        return -1e15
