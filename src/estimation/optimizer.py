import numpy as np
from scipy.optimize import minimize, differential_evolution
from src.model.parameterization import ATSMParams
from src.estimation.likelihood import calculate_log_likelihood

class ATSMOptimizer:
    """
    Optimizes the parameters of the ATSM by maximizing the log-likelihood function.
    """
    def __init__(self, n_factors: int, n_yields: int, maturities: np.ndarray, delta_t: float):
        self.n_factors = n_factors
        self.n_yields = n_yields
        self.maturities = maturities
        self.delta_t = delta_t
        self._params_instance = ATSMParams(n_factors=n_factors, n_yields=n_yields)

    def _objective_function(self, param_vector: np.ndarray, observations: np.ndarray) -> float:
        log_lik = calculate_log_likelihood(
            param_vector=param_vector,
            observations=observations,
            maturities=self.maturities,
            delta_t=self.delta_t,
            n_factors=self.n_factors,
            n_yields=self.n_yields
        )
        # Handle cases where likelihood is -1e15 (penalty) or -inf/NaN
        if log_lik <= -1e14 or np.isneginf(log_lik) or np.isnan(log_lik):
            # Return a massive positive value for minimizing
            return 1e15 
        return -log_lik

    def get_initial_guess(self) -> np.ndarray:
        return self._params_instance.get_parameter_vector()

    def optimize(self, observations: np.ndarray, initial_guess_vector: np.ndarray = None, bounds: list = None) -> dict:
        """
        Runs a 2-stage optimization:
        1. Global search with differential_evolution to find a good region.
        2. Local search with L-BFGS-B to fine-tune the result.
        """
        if initial_guess_vector is None:
            initial_guess_vector = self.get_initial_guess()

        # Check initial likelihood
        initial_lik = self._objective_function(initial_guess_vector, observations)
        print(f"Initial Neg-LogLik: {initial_lik}")
        if initial_lik >= 1e14:
            print("Warning: Initial guess is in the penalty zone. Optimization may struggle.")
            # Debug: Print first few parameters
            print("Initial Params (first 12):", initial_guess_vector[:12])
            n_lt = self._params_instance._n_lower_tri_params
            print("Initial delta0, delta1:", initial_guess_vector[2*n_lt + self.n_factors : 2*n_lt + 2*self.n_factors + 1])

        # --- Stage 1: Global Optimization (abbreviated) ---
        print("\n--- Starting Stage 1: Global Optimization (differential_evolution) ---")
        if bounds is None:
            n_lower_tri = self._params_instance._n_lower_tri_params
            bounds = (
                [(-5, 5)] * (n_lower_tri * 2) +          # KQ, Sigma
                [(-1, 1)] * self.n_factors +             # theta
                [(-1, 1)] +                              # alpha
                [(-2, 2)] * self.n_factors +             # beta
                [(-10, 0)] * self.n_yields               # R (log-space)
            )

        # Progress tracking callback
        self._de_iter_count = 0
        def callback(xk, convergence):
            self._de_iter_count += 1
            # scopy.optimize.differential_evolution passes (xk, convergence)
            # convergence is a number between 0 and 1 indicating progress towards tolerance
            print(f"Global Stage 1 - Iteration {self._de_iter_count}/10: Current convergence index: {convergence:.4f}")

        global_search_result = differential_evolution(
            func=self._objective_function,
            bounds=bounds,
            args=(observations,),
            strategy='best1bin',
            maxiter=1000, # Increased for high-precision final run
            popsize=20, 

            tol=0.01,
            mutation=(0.5, 1),
            recombination=0.7,
            workers=4, # Re-enable parallel processing
            disp=True,
            polish=False,
            callback=callback
            )


        if not global_search_result.success:
            print("Warning: Global optimization did not converge fully (as expected with low maxiter).")
        
        print("\n--- Global Search Finished. Best Neg-LogLik:", global_search_result.fun)
        de_result_vector = global_search_result.x

        # --- Stage 2: Local Optimization with L-BFGS-B ---
        print("\n--- Starting Stage 2: Local Optimization (L-BFGS-B) to fine-tune ---")
        
        local_search_result = minimize(
            fun=self._objective_function,
            x0=de_result_vector,
            args=(observations,),
            method='L-BFGS-B',
            bounds=bounds,
            options={
                'disp': True, 
                'maxiter': 500, # Keep local search iterations reasonable
                'gtol': 1e-7,
                'ftol': 2.22e-09
            }
        )
        
        print("--- Local Optimization Finished ---")
        return local_search_result

def print_parameter_summary(params: ATSMParams):
    print("\n--- Final Parameter Summary ---")
    print("\n[Risk-Neutral Q-Measure]")
    print("KQ (Mean Reversion):\n", params.KQ)
    print("Sigma (Volatility):\n", params.Sigma)
    print("delta0 (Short-rate Constant):", params.delta0)
    print("delta1 (Short-rate Factor Loadings):", params.delta1.flatten())
    
    print("\n[Physical P-Measure]")
    print("KP (Mean Reversion P):\n", params.KP)
    print("muP (Drift P):\n", params.muP.flatten())
    print("lambda0 (Risk Price Constant):", params.lambda0.flatten())
    print("lambda1 (Risk Price Diagonal):", np.diag(params.lambda1))
    
    print("\n[Other]")
    print("R (Observation Noise Diagonal):\n", np.diag(params.R))
    print("---------------------------------")
