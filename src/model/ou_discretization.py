import numpy as np
from scipy.linalg import expm

def discretize_ou(K: np.ndarray, theta: np.ndarray, Sigma: np.ndarray, dt: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Discretizes a continuous-time Ornstein-Uhlenbeck process.

    The continuous-time process is defined as:
    dX_t = K * (theta - X_t) * dt + Sigma * dW_t

    The equivalent discrete-time process is:
    X_{t+1} = Phi * X_t + c + epsilon_{t+1}, where epsilon_{t+1} ~ N(0, Q)

    Args:
        K (np.ndarray): n x n mean-reversion matrix.
        theta (np.ndarray): n-dimensional vector for the long-run mean.
        Sigma (np.ndarray): n x n volatility matrix.
        dt (float): The time step for discretization (e.g., 1/12 for monthly data).

    Returns:
        tuple[np.ndarray, np.ndarray, np.ndarray]:
            Phi (np.ndarray): n x n state transition matrix.
            c (np.ndarray): n-dimensional constant term (drift) vector.
            Q (np.ndarray): n x n covariance matrix of the innovation noise.
    """
    n_factors = K.shape[0]

    if dt <= 0:
        raise ValueError("Time step dt must be positive.")

    # 1. Compute Phi = expm(-K*dt)
    # Clip K values if they are extreme to prevent expm explosion
    K_safe = np.clip(K, -10.0, 10.0) 
    Phi = expm(-K_safe * dt)

    # 2. Compute c = (I - Phi) * theta
    if theta.ndim == 1:
        theta = theta.reshape(-1, 1)
    c = (np.eye(n_factors) - Phi) @ theta
    c = c.flatten()

    # 3. Compute Q via Van Loan method
    A_cont = -K_safe
    G_cont = Sigma @ Sigma.T

    # Form the block matrix for the matrix exponential calculation
    M = np.block([
        [A_cont, G_cont],
        [np.zeros_like(A_cont), -A_cont.T]
    ]) * dt

    exp_M = expm(M)

    # Extract the relevant blocks to compute Q
    # E11 is Phi (exp(A_cont*dt)), E12 is the integrated term
    E11 = exp_M[:n_factors, :n_factors]
    E12 = exp_M[:n_factors, n_factors:]
    
    # The integral Q is given by E12 * E11^T
    Q = E12 @ E11.T
    
    # Enforce symmetry numerically, as small errors can accumulate
    Q = (Q + Q.T) / 2.0
    
    return Phi, c, Q
