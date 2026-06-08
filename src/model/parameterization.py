import numpy as np

class ATSMParams:
    """
    Final ATSM Parameters with strict normalization (thetaQ=0) to prevent scale drift.
    """
    def __init__(self, n_factors: int = 3, n_yields: int = 8, initial_param_vector: np.ndarray = None):
        self.n_factors = n_factors
        self.n_yields = n_yields
        self._n_lower_tri_params = int(n_factors * (n_factors + 1) / 2)
        # thetaQ is fixed to zero for identification
        self.thetaQ = np.zeros((n_factors, 1))

        if initial_param_vector is None:
            initial_param_vector = self._create_initial_param_vector()
        self.set_parameters_from_vector(initial_param_vector)

    def _create_initial_param_vector(self) -> np.ndarray:
        # Vector size: KQ(6) + Sigma(6) + delta0(1) + delta1(3) + R(8) + lambda0(3) + lambda1(9) = 36
        return np.zeros(self._get_expected_vector_size())

    def _get_expected_vector_size(self) -> int:
        return (
            self._n_lower_tri_params * 2 + # KQ, Sigma
            1 +                           # delta0
            self.n_factors +              # delta1
            self.n_yields +               # R
            self.n_factors +              # lambda0
            self.n_factors * self.n_factors # lambda1
        )

    def set_parameters_from_vector(self, param_vector: np.ndarray):
        idx = 0
        self._K_Q_opt = param_vector[idx : idx + self._n_lower_tri_params]; idx += self._n_lower_tri_params
        self._Sigma_opt = param_vector[idx : idx + self._n_lower_tri_params]; idx += self._n_lower_tri_params
        self.delta0 = float(param_vector[idx]); idx += 1
        self.delta1 = param_vector[idx : idx + self.n_factors].reshape(-1, 1); idx += self.n_factors
        self._R_opt = param_vector[idx : idx + self.n_yields]; idx += self.n_yields
        self._lambda0_opt = param_vector[idx : idx + self.n_factors]; idx += self.n_factors
        self._lambda1_opt = param_vector[idx : idx + self.n_factors * self.n_factors]
        
        # Matrix conversion
        self.KQ = self._get_matrix(self._K_Q_opt)
        self.Sigma = self._get_matrix(self._Sigma_opt)
        self.R = np.diag(np.exp(self._R_opt) + 1e-8)
        
        # Risk Prices
        self.lambda0 = self._lambda0_opt.reshape(-1, 1)
        self.lambda1 = self._lambda1_opt.reshape(self.n_factors, self.n_factors)
        
        # P-Dynamics (Crucial: use thetaQ=0)
        self.KP = self.KQ + self.Sigma @ self.lambda1
        self.muP = self.Sigma @ self.lambda0 # muP = drift under P, since thetaQ=0

    def _get_matrix(self, opt_params):
        matrix = np.zeros((self.n_factors, self.n_factors))
        idx = 0
        for i in range(self.n_factors):
            for j in range(i + 1):
                if i == j: matrix[i, j] = np.exp(opt_params[idx])
                else: matrix[i, j] = opt_params[idx]
                idx += 1
        return matrix

    def get_parameter_vector(self) -> np.ndarray:
        return np.concatenate([
            self._K_Q_opt, self._Sigma_opt, [self.delta0], self.delta1.flatten(),
            self._R_opt, self._lambda0_opt, self._lambda1_opt.flatten()
        ])

    @classmethod
    def from_vector(cls, param_vector, n_factors, n_yields):
        return cls(n_factors=n_factors, n_yields=n_yields, initial_param_vector=param_vector)
