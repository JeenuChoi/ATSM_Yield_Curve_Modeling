import pandas as pd
import numpy as np
from statsmodels.tsa.vector_ar.vecm import VECM

# 1. Load data
factors = pd.read_csv('Desktop/ATSM_Project/outputs/smoothed_factors.csv', index_col=0, parse_dates=True)
macro_tp = pd.read_csv('Desktop/ATSM_Project/outputs/macro_tp_merged.csv', index_col=0, parse_dates=True)
df = pd.concat([factors, macro_tp], axis=1).dropna()

# 2. VECM Setup
target_cols = ['Term_Premium', 'INF_UNCERTAIN', 'UNRATE', 'M2_GROWTH']
data_vecm = df[target_cols]

model_vecm = VECM(data_vecm, k_ar_diff=3, coint_rank=1, deterministic='co')
vecm_res = model_vecm.fit()

# 3. Impulse Response Function (IRF)
irf = vecm_res.irf(periods=24)
# INF_UNCERTAIN (index 1) shock on Term_Premium (index 0)
# orth_irfs shape: (periods, to_var, from_var)
inf_shock_on_tp = irf.orth_irfs[:, 0, 1] 

# 4. Magnitude Conversion (to basis points)
# Assuming 10Y yield in decimal (0.01 = 100bp)
max_impact_bp = np.max(inf_shock_on_tp) * 10000 
avg_impact_bp = np.mean(inf_shock_on_tp[1:13]) * 10000 # Average impact over first year

print('\n' + '='*75)
print('--- [ACADEMIC TEST] MACRO SHOCK QUANTIFICATION (Strategy B - IRF) ---')
print('='*75)
print(f'Max Impact of INF_UNCERTAIN Shock on 10Y TP: {max_impact_bp:.2f} bps')
print(f'Average Impact over 12 Months: {avg_impact_bp:.2f} bps')

# Find peak period
peak_period = np.argmax(inf_shock_on_tp)
print(f'Peak Impact occurs at month: {peak_period}')

print('\n' + '='*75)
print('Interpretation for Abstract/Conclusion:')
print(f'\"A one-standard-deviation shock to inflation uncertainty leads to a maximum increase of {max_impact_bp:.2f} bps in the 10-year term premium, peaking at month {peak_period}.\"')
print(f'\"The average risk premium elevation remains at {avg_impact_bp:.2f} bps throughout the first year following the shock.\"')
print('='*75)
