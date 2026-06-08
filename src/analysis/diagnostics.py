import numpy as np
import pandas as pd

def compute_residuals(
    observations: np.ndarray,
    X_predicted: np.ndarray,
    H: np.ndarray,
    intercept: np.ndarray
) -> np.ndarray:
    """
    Computes the measurement residuals (innovations) from the Kalman filter's predictions.
    """
    num_timesteps = observations.shape[0]
    n_yields = observations.shape[1]
    residuals = np.zeros((num_timesteps, n_yields))

    for t in range(num_timesteps):
        Y_t = observations[t, :].reshape(-1, 1)
        X_t_pred = X_predicted[t, :].reshape(-1, 1)
        
        predicted_obs = H @ X_t_pred + intercept
        residuals[t, :] = (Y_t - predicted_obs).flatten()
        
    return residuals

def calculate_performance_metrics(observed: np.ndarray, fitted: np.ndarray, log_lik: float, n_params: int):
    """
    Calculates RMSE, AIC, and BIC.
    """
    n_obs, n_yields = observed.shape
    total_n = n_obs * n_yields
    
    # RMSE per maturity
    errors = observed - fitted
    rmse_per_maturity = np.sqrt(np.mean(errors**2, axis=0))
    total_rmse = np.sqrt(np.mean(errors**2))
    
    # AIC/BIC (Using the standard definitions)
    # AIC = 2k - 2ln(L)
    # BIC = ln(n)k - 2ln(L)
    aic = 2 * n_params - 2 * log_lik
    bic = np.log(n_obs) * n_params - 2 * log_lik
    
    return {
        "rmse_per_maturity": rmse_per_maturity,
        "total_rmse": total_rmse,
        "aic": aic,
        "bic": bic,
        "log_lik": log_lik,
        "n_params": n_params,
        "n_obs": n_obs
    }

def get_summary_statistics(df: pd.DataFrame):
    """
    Returns mean, std, min, max, and persistence (for factors).
    """
    stats = df.describe().transpose()[['mean', 'std', 'min', 'max']]
    
    # Add persistence (AR1 coefficient) for each column
    persistence = []
    for col in df.columns:
        valid_data = df[col].dropna()
        if len(valid_data) > 1:
            rho = np.corrcoef(valid_data[:-1], valid_data[1:])[0, 1]
            persistence.append(rho)
        else:
            persistence.append(np.nan)
    
    stats['persistence_ar1'] = persistence
    return stats
