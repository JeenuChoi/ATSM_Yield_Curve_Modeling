import numpy as np
from scipy.integrate import solve_ivp

class _RiccatiSolver:
    """
    Internal class to solve the Riccati ODEs for the ATSM.
    This class holds the model parameters and the ODE system.
    """
    def __init__(self, KQ, thetaQ, Sigma, delta0, delta1):
        self.KQ = KQ
        self.thetaQ = thetaQ
        self.Sigma = Sigma
        self.delta0 = delta0
        self.delta1 = delta1
        self.n_factors = KQ.shape[0]
        self.Sigma_Omega = Sigma @ Sigma.T

        # Ensure thetaQ and delta1 are column vectors
        if self.thetaQ.shape == (self.n_factors,):
            self.thetaQ = self.thetaQ.reshape(-1, 1)
        if self.delta1.shape == (self.n_factors,):
            self.delta1 = self.delta1.reshape(-1, 1)
            
    def _ode_system(self, tau, AB_vec):
        A = AB_vec[0]
        B = AB_vec[1:].reshape(-1, 1)

        # Extreme safety clipping for interpretability
        B_clipped = np.clip(B, -50.0, 50.0)
        
        # dB/dtau = -KQ.T @ B + delta1
        dB_dtau = -self.KQ.T @ B_clipped + self.delta1
        
        # dA/dtau = -(KQ @ thetaQ).T @ B + 0.5 * B' * Sigma * Sigma' * B - delta0
        dA_dtau = -(self.KQ @ self.thetaQ).T @ B_clipped + 0.5 * (B_clipped.T @ self.Sigma_Omega @ B_clipped) - self.delta0
        
        return np.concatenate([[dA_dtau.item()], dB_dtau.flatten()])

def compute_A_B(
    maturities: np.ndarray,
    KQ: np.ndarray,
    thetaQ: np.ndarray,
    Sigma: np.ndarray,
    delta0: float,
    delta1: np.ndarray,
    rtol: float = 1e-8,
    atol: float = 1e-8
) -> tuple[np.ndarray, np.ndarray]:
    """
    Computes the A(tau) and B(tau) coefficients of the ATSM by solving the Riccati ODEs.

    The short rate is modeled as: r_t = delta0 + delta1' * X_t
    The state process is: dX_t = KQ * (thetaQ - X_t) * dt + Sigma * dW_t

    Args:
        maturities (np.ndarray): 1D array of maturities (tau) in years to solve for.
        KQ (np.ndarray): n x n mean-reversion matrix.
        thetaQ (np.ndarray): n x 1 long-run mean vector.
        Sigma (np.ndarray): n x n volatility matrix.
        delta0 (float): Scalar constant for the short rate model.
        delta1 (np.ndarray): n x 1 vector of factor loadings for the short rate model.
        rtol (float): Relative tolerance for the ODE solver.
        atol (float): Absolute tolerance for the ODE solver.

    Returns:
        tuple[np.ndarray, np.ndarray]:
            A (np.ndarray): 1D array of A(tau) coefficients, shape (m,).
            B (np.ndarray): 2D array of B(tau) coefficients, shape (m, n).
    """
    n_factors = KQ.shape[0]
    
    if not np.all(np.diff(maturities) >= 0):
        raise ValueError("Maturities must be sorted in increasing order.")

    solver = _RiccatiSolver(KQ, thetaQ, Sigma, delta0, delta1)
    
    # Initial conditions at tau=0: A(0)=0, B(0)=0
    initial_conditions = np.zeros(n_factors + 1)
    
    max_maturity = maturities.max() if len(maturities) > 0 else 0
    if max_maturity == 0 and len(maturities)>0:
        A_coeffs = np.array([0.0] * len(maturities))
        B_coeffs = np.zeros((len(maturities), n_factors))
        return A_coeffs, B_coeffs
    if max_maturity == 0 and len(maturities)==0:
        return np.array([]), np.empty((0, n_factors))

    sol = solve_ivp(
        solver._ode_system,
        [0, max_maturity],
        initial_conditions,
        method='RK45',
        t_eval=maturities,
        rtol=rtol,
        atol=atol
    )

    if not sol.success:
        raise RuntimeError(f"ODE solver failed: {sol.message}")

    A_coeffs = sol.y[0, :]
    B_coeffs = sol.y[1:, :].T # Transpose to get (m, n)

    return A_coeffs, B_coeffs
