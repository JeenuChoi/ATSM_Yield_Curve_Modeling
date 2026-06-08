import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from statsmodels.graphics.tsaplots import plot_acf

def plot_term_premium(fitted_yields: pd.DataFrame, expected_rates: pd.DataFrame, term_premiums: pd.DataFrame, maturities: np.ndarray, save_path: str = None):
    """
    Plots the decomposition of a selected long-term yield into Expected Short Rates and Term Premium.
    """
    # Select the longest maturity (e.g., 10Y or 30Y)
    target_maturity = maturities[-1] 
    
    plt.figure(figsize=(12, 6))
    plt.plot(fitted_yields.index, fitted_yields[target_maturity], label=f"Total Yield ({target_maturity}Y)", color='black', linewidth=2)
    plt.plot(expected_rates.index, expected_rates[target_maturity], label="Expected Avg Short Rate", color='blue', linestyle='--', alpha=0.8)
    plt.fill_between(term_premiums.index, 0, term_premiums[target_maturity], color='red', alpha=0.3, label="Term Premium")
    
    plt.title(f"Term Premium Decomposition: {target_maturity}-Year Maturity", fontsize=14)
    plt.ylabel("Yield")
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.6)
    if save_path: plt.savefig(save_path)
    plt.show()

def plot_loadings(H: np.ndarray, maturities: np.ndarray, title: str = "Factor Loadings (B(tau)/tau)", save_path: str = None):
    """
    Plots the columns of the H matrix to visualize the impact of each factor across maturities.
    """
    n_factors = H.shape[1]
    plt.figure(figsize=(10, 6))

    colors = ['blue', 'green', 'red']
    labels = ['Factor 1 (Level)', 'Factor 2 (Slope)', 'Factor 3 (Curvature)']

    for i in range(n_factors):
        plt.plot(maturities, H[:, i], marker='o', label=labels[i] if i < len(labels) else f"Factor {i+1}", color=colors[i] if i < len(colors) else None)

    plt.title(title, fontsize=14)
    plt.xlabel("Maturity (Years)")
    plt.ylabel("Loading")
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.6)
    if save_path: plt.savefig(save_path)
    plt.show()

def plot_yield_fit(observed_yields: pd.DataFrame, estimated_yields: pd.DataFrame, title: str = "Observed vs. Fitted Yields (All Maturities)", save_path: str = None):
    """
    Plots observed versus estimated yield curves for all available maturities.
    Uses a grid layout to accommodate many maturities.
    """
    if not observed_yields.index.equals(estimated_yields.index):
        raise ValueError("Indices of observed and estimated yields must match.")
    
    maturities = observed_yields.columns
    n_maturities = len(maturities)
    
    # Calculate grid size
    n_cols = 2
    n_rows = (n_maturities + 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4 * n_rows), sharex=True)
    fig.suptitle(title, fontsize=18)
    axes = axes.flatten()

    for i, maturity in enumerate(maturities):
        ax = axes[i]
        ax.plot(observed_yields.index, observed_yields[maturity], label="Observed", color='blue', alpha=0.7)
        ax.plot(estimated_yields.index, estimated_yields[maturity], label="Fitted", color='red', linestyle='--', alpha=0.8)
        ax.set_title(f"Maturity: {maturity} Years", fontsize=12)
        ax.set_ylabel("Yield")
        ax.legend(fontsize=10)
        ax.grid(True, linestyle=':', alpha=0.6)

    # Hide unused axes
    for j in range(i + 1, len(axes)):
        axes[j].axis('off')

    plt.xlabel("Date")
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    if save_path: plt.savefig(save_path)
    plt.show()

def plot_term_premium_surface(term_premiums: pd.DataFrame, maturities: np.ndarray, save_path: str = None):
    """
    Visualizes the entire term premium curve over time using a 3D surface plot.
    """
    from mpl_toolkits.mplot3d import Axes3D
    from matplotlib import cm

    fig = plt.figure(figsize=(14, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Create meshgrid
    X, Y = np.meshgrid(maturities, np.arange(len(term_premiums.index)))
    Z = term_premiums.values

    surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm, linewidth=0, antialiased=True, alpha=0.8)
    
    ax.set_xlabel('Maturity (Years)')
    ax.set_ylabel('Time (Months from Start)')
    ax.set_zlabel('Term Premium')
    ax.set_title('Term Premium Surface: All Maturities over Time', fontsize=16)
    
    fig.colorbar(surf, shrink=0.5, aspect=5)
    
    if save_path: plt.savefig(save_path)
    plt.show()

def plot_factors(X_smoothed: np.ndarray, P_smoothed: np.ndarray, dates: pd.DatetimeIndex, title: str = "Smoothed Latent Factors", save_path: str = None):
    """
    Plots smoothed latent factors with 95% confidence intervals.
    """
    n_factors = X_smoothed.shape[1]

    fig, axes = plt.subplots(n_factors, 1, figsize=(12, 3 * n_factors), sharex=True)
    if n_factors == 1:
        axes = [axes]
    fig.suptitle(title, fontsize=16)

    for i in range(n_factors):
        ax = axes[i]
        factor_mean = X_smoothed[:, i]
        factor_std = np.sqrt(np.maximum(P_smoothed[:, i, i], 0))

        ax.plot(dates, factor_mean, label=f"Smoothed Factor {i+1}", color='green')
        ax.fill_between(dates, factor_mean - 1.96 * factor_std, factor_mean + 1.96 * factor_std, 
                        color='green', alpha=0.2, label="95% Confidence Interval")

        ax.set_ylabel(f"Factor {i+1}")
        ax.legend()
        ax.grid(True, linestyle=':', alpha=0.6)

    plt.xlabel("Date")
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    if save_path: plt.savefig(save_path)
    plt.show()

def plot_residuals(residuals: np.ndarray, maturities: np.ndarray, title="Kalman Filter Residuals (Innovations)", save_path: str = None):
    """
    Plots the time series and ACF of residuals for selected maturities.
    """
    n_yields = residuals.shape[1]

    # Select a few representative maturities to plot residuals for
    indices_to_plot = [0, n_yields // 2, n_yields - 1]

    fig, axes = plt.subplots(len(indices_to_plot), 2, figsize=(14, 4 * len(indices_to_plot)))
    fig.suptitle(title, fontsize=16)

    for i, res_idx in enumerate(indices_to_plot):
        maturity = maturities[res_idx]

        # Plot residual time series
        axes[i, 0].plot(residuals[:, res_idx])
        axes[i, 0].set_title(f"Residuals for {maturity}-Year Yield")
        axes[i, 0].set_ylabel("Residual")
        axes[i, 0].grid(True, linestyle=':', alpha=0.6)

        # Plot ACF of residuals
        plot_acf(residuals[:, res_idx], ax=axes[i, 1], title=f"ACF of {maturity}-Year Residuals")

    plt.xlabel("Time Step / Lag")
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    if save_path: plt.savefig(save_path)
    plt.show()