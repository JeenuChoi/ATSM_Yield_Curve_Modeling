import numpy as np
from src.model.parameterization import ATSMParams
from src.model.riccati import compute_A_B
from src.model.ou_discretization import discretize_ou

class StateSpaceModel:
    """
    Constructs the discrete-time state-space representation of the ATSM from a raw parameter vector.

    State equation: X_{t+1} = Phi @ X_t + drift + epsilon_{t+1}, epsilon_{t+1} ~ N(0, Q)
    Observation equation: Y_t = H @ X_t + intercept + eta_t, eta_t ~ N(0, R)
    """
    def __init__(self, param_vector: np.ndarray, maturities: np.ndarray, delta_t: float, n_factors: int, n_yields: int):
        # 1. Instantiate ATSMParams and set parameters from the vector
        params = ATSMParams(n_factors=n_factors, n_yields=n_yields)
        params.set_parameters_from_vector(param_vector)

        # 2. Transition Dynamics (under Physical measure P)
        # We use KP and muP for state transition
        # But wait, discretize_ou expects continuous-time parameters.
        # muP was calculated as a continuous-time drift term Sigma*lambda0 + KQ*thetaQ
        # Let's derive thetaP = KP^-1 * muP for the discretize function
        thetaP = np.linalg.solve(params.KP, params.muP)
        self.Phi, self.drift, self.Q = discretize_ou(params.KP, thetaP, params.Sigma, delta_t)
        
        if self.drift.ndim == 1:
            self.drift = self.drift.reshape(-1, 1)

        # 3. Solve Riccati ODEs for A(tau) and B(tau) (under Risk-Neutral measure Q)
        A_coeffs, B_coeffs = compute_A_B(maturities, params.KQ, params.thetaQ, params.Sigma, params.delta0, params.delta1)

        # 4. Construct observation matrix H and intercept (Q-measure)
        self.H = np.zeros((n_yields, n_factors))
        self.intercept = np.zeros((n_yields, 1))
        self.R = params.R

        for i, tau in enumerate(maturities):
            self.intercept[i, 0] = -A_coeffs[i] / tau
            self.H[i, :] = B_coeffs[i, :] / tau

def build_state_space_from_vector(
    param_vector: np.ndarray,
    maturities: np.ndarray,
    delta_t: float,
    n_factors: int,
    n_yields: int
) -> StateSpaceModel:
    """
    Given a raw parameter vector and maturities, returns a full StateSpace object.
    """
    return StateSpaceModel(param_vector, maturities, delta_t, n_factors, n_yields)
