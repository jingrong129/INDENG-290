"""
Converted from energy_project_notebook.ipynb
Blocks separated by markers: # %## <block>
"""

# %## 1: Notebook header
# Energy project: model blocks
#
# This notebook scans all CSV files in the current folder (uses the provided data), detects year columns (e.g. 2025-2050), and for each series (row) fits three separate models in distinct code blocks: Linear Regression, Random Forest, and Gradient Boosting. Each model cell contains short analysis as comments in the code.

# %## 2: Block 1: imports and helpers
import os, re, glob, json
from collections import defaultdict
import numpy as np
import pandas as pd
from pandas.errors import ParserError
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error

def find_csv_files(path='.'):
    return glob.glob(os.path.join(path, '*.csv'))

def parse_malformed_year_table(lines, header_row):
    # Fallback parser for semi-structured exports such as EIA downloads.
    header = [part.strip().strip('"') for part in lines[header_row].rstrip('\n').split(',')]
    expected_cols = len(header)
    rows = []
    for raw_line in lines[header_row + 1:]:
        line = raw_line.rstrip('\n')
        if not line.strip():
            continue
        parts = [part.strip() for part in line.split(',')]
        if len(parts) < expected_cols:
            parts.extend([''] * (expected_cols - len(parts)))
        elif len(parts) > expected_cols:
            overflow = len(parts) - expected_cols + 1
            parts = [','.join(parts[:overflow])] + parts[overflow:]
        rows.append([part.strip('"') for part in parts[:expected_cols]])
    return pd.DataFrame(rows, columns=header)

def read_csv_with_header_detection(path):
    # Robust reader: finds the header row that contains a year like 2025 and then reads CSV from there.
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
    header_row = None
    for i, line in enumerate(lines[:50]):
        if re.search(r'20\d{2}', line):
            # require that line contains multiple year tokens or the token 2025 specifically
            if re.search(r'2025', line) or len(re.findall(r'20\d{2}', line)) >= 3:
                header_row = i
                break
    if header_row is None:
        # fallback: read normally
        df = pd.read_csv(path, header=0, engine='python', dtype=object)
        return df
    # read from detected header row
    try:
        df = pd.read_csv(path, header=header_row, engine='python', dtype=object)
    except ParserError:
        df = parse_malformed_year_table(lines, header_row)
    # clean column names
    df.columns = [str(c).strip().strip("") for c in df.columns]
    return df

# %## 3: Block 2: load all CSVs and extract series (uses all provided CSV files in folder)
csvs = find_csv_files('.')
print('Found CSV files:', csvs)
series_list = []
for csv in csvs:
    print('Reading', csv)
    df = read_csv_with_header_detection(csv)
    cols = list(df.columns)
    # identify year columns (20xx)
    year_cols = [c for c in cols if re.fullmatch(r'20\d{2}', str(c).strip())]
    if not year_cols:
        print('  No year columns detected in', csv)
        continue
    # choose label column as first non-year column
    non_year = [c for c in cols if c not in year_cols]
    label_col = non_year[0] if non_year else cols[0]
    for idx, row in df.iterrows():
        label = str(row[label_col]) if label_col in df.columns else f'row_{idx}'
        years = []
        values = []
        for yc in year_cols:
            y_match = re.search(r'(20\d{2})', str(yc))
            if not y_match:
                continue
            year = int(y_match.group(1))
            val = pd.to_numeric(row.get(yc, None), errors='coerce')
            years.append(year)
            values.append(val)
        # require at least 6 non-null points to include series
        if sum(not pd.isna(v) for v in values) >= 6:
            series_list.append({'file': os.path.basename(csv), 'label': label, 'years': years, 'values': [float(v) if not pd.isna(v) else np.nan for v in values]})

print('Extracted', len(series_list), 'series across CSVs.')

# %## 4: Block 3: Linear Regression (each series processed here)
# 分析（注释）: 线性回归是最简单、可解释的模型。
# 适用于长期平稳线性趋势的序列。如果序列存在非线性或局部波动，线性回归通常会欠拟合。
from sklearn.linear_model import LinearRegression
results_lr = []
for s in series_list:
    yrs = np.array(s['years']).reshape(-1,1)
    vals = np.array(s['values'], dtype=float)
    mask = ~np.isnan(vals)
    yrs2 = yrs[mask].reshape(-1,1)
    vals2 = vals[mask]
    if len(vals2) < 6:
        continue
    # chronological split 80/20
    split = max(3, int(len(vals2)*0.8))
    X_train, X_test = yrs2[:split], yrs2[split:]
    y_train, y_test = vals2[:split], vals2[split:]
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    y_pred = lr.predict(X_test)
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    mape = mean_absolute_percentage_error(y_test, y_pred)
    results_lr.append(rmse)
    print(f"[LR] {s['file']} | {s['label']} | RMSE={rmse:.6f} | MAPE={mape:.6f}")

print('Finished Linear Regression block. Processed series:', len(results_lr))

# %## 5: Block 4: Random Forest (each series processed here)
# 分析（注释）: 随机森林为非参数模型，能捕捉非线性和局部波动。
# 它在小数据集上可能会有过拟合风险，但通常比线性模型更灵活。
from sklearn.ensemble import RandomForestRegressor
results_rf = []
for s in series_list:
    yrs = np.array(s['years']).reshape(-1,1)
    vals = np.array(s['values'], dtype=float)
    mask = ~np.isnan(vals)
    yrs2 = yrs[mask].reshape(-1,1)
    vals2 = vals[mask]
    if len(vals2) < 6:
        continue
    split = max(3, int(len(vals2)*0.8))
    X_train, X_test = yrs2[:split], yrs2[split:]
    y_train, y_test = vals2[:split], vals2[split:]
    rf = RandomForestRegressor(n_estimators=100, random_state=0)
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    results_rf.append(rmse)
    print(f"[RF] {s['file']} | {s['label']} | RMSE={rmse:.6f}")

print('Finished Random Forest block. Processed series:', len(results_rf))

# %## 6: Block 5: Gradient Boosting (each series processed here)
# 分析（注释）: 梯度提升通常在偏差-方差之间表现平衡，且在小到中等尺寸数据上表现良好。
# 需要调参以获得最佳性能，但默认设置通常能提供可靠的基线。
from sklearn.ensemble import GradientBoostingRegressor
results_gb = []
for s in series_list:
    yrs = np.array(s['years']).reshape(-1,1)
    vals = np.array(s['values'], dtype=float)
    mask = ~np.isnan(vals)
    yrs2 = yrs[mask].reshape(-1,1)
    vals2 = vals[mask]
    if len(vals2) < 6:
        continue
    split = max(3, int(len(vals2)*0.8))
    X_train, X_test = yrs2[:split], yrs2[split:]
    y_train, y_test = vals2[:split], vals2[split:]
    gb = GradientBoostingRegressor(n_estimators=100, random_state=0)
    gb.fit(X_train, y_train)
    y_pred = gb.predict(X_test)
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    results_gb.append(rmse)
    print(f"[GB] {s['file']} | {s['label']} | RMSE={rmse:.6f}")

print('Finished Gradient Boosting block. Processed series:', len(results_gb))

# %## 7: Block 6: Overall comparison and final analysis (as comments)
# 分析（注释）: 总体上我们用平均 RMSE 比较三种模型。
# - 如果线性回归具有最低的平均 RMSE，说明长期趋势以线性为主，且模型简单可解释。
# - 如果随机森林或梯度提升较优，说明存在非线性或局部波动特征，需更灵活的模型。
# - 对于重要序列，建议进一步做交叉验证、超参调优，并绘制预测与真实值对比图。
from statistics import mean
avg_lr = mean(results_lr) if results_lr else None
avg_rf = mean(results_rf) if results_rf else None
avg_gb = mean(results_gb) if results_gb else None
print('Mean RMSEs:')
print('  Linear Regression:', avg_lr)
print('  Random Forest    :', avg_rf)
print('  Gradient Boosting:', avg_gb)
candidates = {k:v for k,v in [('LR',avg_lr),('RF',avg_rf),('GB',avg_gb)] if v is not None}
if candidates:
    best = min(candidates, key=candidates.get)
    print('Recommended overall model (lowest mean RMSE):', best)

# 保存结果到 ./results/summary.json
out = {'mean_rmse': {'linear_regression': avg_lr, 'random_forest': avg_rf, 'gradient_boosting': avg_gb}}
os.makedirs('results', exist_ok=True)
with open('results/summary.json','w') as fo:
    json.dump(out, fo, indent=2)
print('Wrote results/summary.json')
