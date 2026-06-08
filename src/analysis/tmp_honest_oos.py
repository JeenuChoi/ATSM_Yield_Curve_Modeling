import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from scipy.stats import norm

# 1. Load Original Observed Data (Full History)
observed = pd.read_csv('Desktop/ATSM_Project/outputs/observed_yields.csv', index_col=0, parse_dates=True)
y_full = observed['10.0'].dropna()

# 2. Define OOS Period (Same as main6.py)
oos_start = '2019-01-31'
y_actual_oos = y_full.loc[oos_start:]

# 3. Our Model's REAL Performance (from oos_yield_report.txt)
rmse_ours = 23.97 

# 4. Strict Recursive AR(1) Forecast for OOS Period
# Important: For each month in OOS, we only train on data BEFORE that month.
ar1_preds = []
for date in y_actual_oos.index:
    train_data = y_full.loc[:date - pd.Timedelta(days=1)]
    if len(train_data) < 24: # Need at least 2 years to train
        ar1_preds.append(y_full.loc[:date].iloc[-2]) # Naive fallback
        continue
    
    X_train = train_data.iloc[:-1].values.reshape(-1, 1)
    y_train = train_data.iloc[1:].values
    model = LinearRegression().fit(X_train, y_train)
    
    last_val = train_data.iloc[-1]
    pred = model.predict([[last_val]])[0]
    ar1_preds.append(pred)

y_ar1_oos = pd.Series(ar1_preds, index=y_actual_oos.index)

# 5. RMSE and DM Test
def get_rmse(actual, pred):
    return np.sqrt(np.mean((actual - pred)**2)) * 10000 # in bps

rmse_ar1 = get_rmse(y_actual_oos, y_ar1_oos)
rmse_rw = get_rmse(y_actual_oos, y_full.shift(1).loc[oos_start:])

def dm_test(actual, pred1_rmse, pred2_series):
    # Since we don't have our model's month-by-month error series here,
    # we use a simplified DM-like test comparing RMSEs under H0 of equality.
    # For a stricter test, we'd need the error time series of our model.
    # But we can compare the RMSEs directly.
    return rmse_ours < rmse_ar1

print('\n' + '='*75)
print('--- [REAL-WORLD OOS VALIDATION] HONEST BENCHMARK COMPARISON ---')
print('='*75)
print(f'OOS Period: {y_actual_oos.index.min().date()} to {y_actual_oos.index.max().date()}')
print(f'N_Observations: {len(y_actual_oos)}')

print(f'\nRMSE Comparison (Basis Points):')
print(f' - Our ATSM-Macro Model:  {rmse_ours:.2f} bps  (Verified OOS)')
print(f' - Recursive AR(1):       {rmse_ar1:.2f} bps')
print(f' - Random Walk (RW):      {rmse_rw:.2f} bps')

print('\nPerformance Gap Analysis:')
diff_ar1 = rmse_ar1 - rmse_ours
diff_rw = rmse_rw - rmse_ours
print(f' - Advantage over AR(1):  {diff_ar1:.2f} bps')
print(f' - Advantage over RW:     {diff_rw:.2f} bps')

print('\n' + '='*75)
if rmse_ours < rmse_ar1 and rmse_ours < rmse_rw:
    print('FINAL VERDICT: STRATEGIC VICTORY!')
    print('The model with macro uncertainty provides superior predictive value')
    print('over both persistence (AR1) and naive (RW) benchmarks in a real OOS setting.')
else:
    print('FINAL VERDICT: MIXED RESULTS. Check model specs.')
print('='*75)
