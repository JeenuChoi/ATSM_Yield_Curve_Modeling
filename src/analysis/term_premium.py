import numpy as np
import pandas as pd
from scipy.linalg import expm

def decompose_term_premium(X_smoothed, KP, muP, delta0, delta1, maturities, fitted_yields_df):
    """
    Decomposes fitted yields into Expected Average Short Rate and Term Premium using
    continuous-time expectations for better accuracy.
    
    Yield(n) = (1/tau) * integral_0^tau E_t^P[r_{t+s}] ds + TermPremium(n)
    
    E_t^P[X_{t+s}] = exp(-KP*s)*X_t + (I - exp(-KP*s))*thetaP
    where thetaP = KP^-1 * muP
    """
    n_obs, n_factors = X_smoothed.shape
    n_yields = len(maturities)
    dates = fitted_yields_df.index
    I = np.eye(n_factors)
    
    # Calculate thetaP (long-run mean under P)
    # muP = KP @ thetaP  => thetaP = KP^-1 @ muP
    try:
        # Check condition number before solving
        if np.linalg.cond(KP) < 1e12:
            thetaP = np.linalg.solve(KP, muP)
        else:
            thetaP = np.zeros((n_factors, 1))
    except np.linalg.LinAlgError:
        thetaP = np.zeros((n_factors, 1))

    expected_avg_short_rates = np.zeros((n_obs, n_yields))
    d1 = delta1.reshape(1, -1)
    
    for i, tau in enumerate(maturities):
        # The integral of E_t[X_{t+s}] from 0 to tau is:
        # Int = integral_0^tau [exp(-KP*s)X_t + (I - exp(-KP*s))thetaP] ds
        # Let M(tau) = integral_0^tau exp(-KP*s) ds = (I - exp(-KP*tau)) * KP^-1
        
        # Use Van Loan or direct matrix exponential for the integral
        # A simple robust way: integral of exp(-KP*s)
        # Using the same block matrix trick as in discretization
        block = np.block([
            [-KP, np.eye(n_factors)],
            [np.zeros((n_factors, n_factors)), np.zeros((n_factors, n_factors))]
        ]) * tau
        exp_block = expm(block)
        M_tau = exp_block[:n_factors, n_factors:]
        
        # Average X over [0, tau]: (1/tau) * [M_tau @ X_t + (tau*I - M_tau) @ thetaP]
        # X_smoothed is (obs, factors), M_tau is (factors, factors), thetaP is (factors, 1)
        term1 = X_smoothed @ M_tau.T # (obs, factors)
        term2 = (tau * I - M_tau) @ thetaP # (factors, 1)
        
        avg_X = (term1 + term2.flatten()) / tau
        
        # Expected Average Short Rate = delta0 + delta1' @ avg_X
        expected_avg_short_rates[:, i] = delta0 + (avg_X @ d1.T).flatten()
        
    expected_df = pd.DataFrame(expected_avg_short_rates, index=dates, columns=maturities)
    term_premium_df = fitted_yields_df - expected_df
    
    return expected_df, term_premium_df
