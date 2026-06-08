import unittest
import numpy as np
from src.estimation.likelihood import calculate_log_likelihood
from src.model.parameterization import ATSMParams

class TestKalmanBasic(unittest.TestCase):
    def setUp(self):
        self.n_factors = 1
        self.n_yields = 1
        self.delta_t = 1.0
        self.maturities = np.array([1.0])
        
        # Initialize ATSMParams for a simple 1-factor model
        self.params = ATSMParams(n_factors=self.n_factors, n_yields=self.n_yields)
        self.param_vector = self.params.get_parameter_vector()
        
        # Generate dummy observations
        num_timesteps = 100
        self.dummy_observations = np.random.randn(num_timesteps, self.n_yields) * 0.02 + 0.03
        
    def test_finite_log_likelihood_with_synthetic_data(self):
        """
        Test that the Kalman filter produces a finite log-likelihood for a
        set of valid parameters and synthetic observations.
        """
        log_lik = calculate_log_likelihood(
            param_vector=self.param_vector,
            observations=self.dummy_observations,
            maturities=self.maturities,
            delta_t=self.delta_t,
            n_factors=self.n_factors,
            n_yields=self.n_yields
        )
        
        self.assertTrue(np.isfinite(log_lik), "Log-likelihood should be a finite number.")
        
    def test_robustness_with_non_pd_initial_P(self):
        """
        Test that the likelihood function returns -np.inf if the initial
        state covariance P is not positive definite.
        """
        log_lik = calculate_log_likelihood(
            param_vector=self.param_vector,
            observations=self.dummy_observations,
            maturities=self.maturities,
            delta_t=self.delta_t,
            n_factors=self.n_factors,
            n_yields=self.n_yields,
            initial_P=np.diag([-1.0]) # Non-PD initial covariance
        )
        self.assertEqual(log_lik, -np.inf)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
