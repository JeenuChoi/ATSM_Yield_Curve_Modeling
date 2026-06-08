# ATSM Project: Affine Term Structure Model & Macroeconomic Linkages

This repository contains a research-grade Python implementation of a no-arbitrage **Gaussian 3-Factor Affine Term Structure Model (ATSM)** for the U.S. Treasury yield curve. It investigates the dynamic interactions between the unobservable yield curve factors (Level, Slope, Curvature) and macroeconomic variables under rigorous statistical and no-arbitrage constraints.

## 🚀 Key Achievements & Features

*   **Robust ATSM Estimation:** Implemented a continuous-time Ornstein-Uhlenbeck (OU) state dynamics model using GSW zero-coupon yields. Ensures no-arbitrage conditions while extracting the exact Term Premium.
*   **Macro-Finance Integration:** Combined 1990–2026 U.S. Treasury yields with FRED macroeconomic indicators (Unemployment, Industrial Production, M2, Uncertainty indices).
*   **VECM Cointegration Framework:** Identified Cointegration Rank 4 using Johansen tests. Replaced standard differencing with a Vector Error Correction Model (VECM) to resolve severe spurious regression issues (DW index ≈ 0.03 improved to ≈ 2.0).
*   **Federal Reserve Benchmarking:** Achieved a highly robust **0.9757 correlation** with the Federal Reserve Bank of New York's official ACM Model for term premium estimates.
*   **Nelson-Siegel Constraints:** Enforced Nelson-Siegel asymptotic properties and risk-neutral pricing measure restrictions to prevent term premium collapse during ZLB (Zero Lower Bound) optimization.

## 📂 Repository Structure

```text
ATSM_Project/
├── main.py                   # Main execution pipeline (Estimation, Filtering, Smoothing)
├── data/                     # Data directory (Yields, Macro indicators)
│   └── feds200628_clean.csv  # GSW Yield Curve Data
├── src/                      # Source code
│   ├── model/                # State-space, Riccati ODEs, Parameterization
│   ├── filter/               # Kalman Filter & Smoother implementations
│   ├── estimation/           # MLE Optimizer, Likelihood calculation
│   └── analysis/             # Econometrics (VECM), Forecasting, Robustness
├── docs/                     # Documentation & Specifications
│   ├── reports/              # HTML/Markdown research reports
│   ├── specs/                # Model specifications & math derivations
│   └── presentations/        # Academic presentation materials (PDF/PPTX)
├── outputs/                  # Results (CSVs, PNGs, Diagnostics)
├── tests/                    # Unit tests for core mathematical functions
└── requirements.txt          # Python dependencies
```

## ⚙️ Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/ATSM_Project.git
    cd ATSM_Project
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## 🚀 Usage

Run the main estimation and analysis pipeline:

```bash
python main.py
```

**The script executes the following stages:**
1.  **Data Loading:** Ingests the `feds200628_clean.csv` yield curve data.
2.  **Initialization:** Uses PCA and VAR(1) to establish robust initial states for optimization.
3.  **Optimization:** Runs L-BFGS-B optimizer to maximize the log-likelihood of the state-space model subject to no-arbitrage Riccati equations.
4.  **Filtering & Smoothing:** Applies the Kalman Filter and Smoother to extract the latent factors (Level, Slope, Curvature).
5.  **Reporting:** Exports expected short rates, term premiums, and highly detailed visual diagnostics (residuals, fitted vs. observed yields) to the `outputs/` directory.

## 📜 Research Notes

For deep-dives into the mathematics, the `docs/specs/` folder contains the detailed model specification, robustness checks, and handling of the Zero Lower Bound (ZLB). The findings regarding VECM macro-finance integration have been formatted for an academic paper (see `docs/reports/`).

## ⚖️ License
Internal / Academic Use.
