import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# ---------------------------- 1. 读取数据（自动定位到桌面） ----------------------------
# 获取当前用户的桌面路径
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
file_name = '回归分析数据.xlsx'
file_path = os.path.join(desktop_path, file_name)

# 如果桌面找不到，再尝试其他位置（保留原脚本的逻辑作为备选）
if not os.path.exists(file_path):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, file_name)
if not os.path.exists(file_path):
    file_path = file_name
if not os.path.exists(file_path):
    # 最后尝试原来的绝对路径（以防万一）
    abs_path = r'C:/Users/李一帆/Desktop/多元线性回归/回归分析数据.xlsx'
    if os.path.exists(abs_path):
        file_path = abs_path
    else:
        raise FileNotFoundError(f"找不到文件 {file_name}，请将文件放在桌面或脚本目录下。")

print(f"正在读取文件：{file_path}")
df = pd.read_excel(file_path, sheet_name='Sheet1')

print("数据前5行：")
print(df.head())

# ---------------------------- 2. 定义变量 ----------------------------
X = df[['age', 'material', 'maintenance', 'collection']]
y = df['accident']
X_const = sm.add_constant(X)

# ---------------------------- 3. 拟合多元线性回归模型 ----------------------------
model = sm.OLS(y, X_const).fit()
print("\n========== 回归模型摘要 ==========")
print(model.summary())

print("\n========== 回归系数表 ==========")
coef_df = pd.DataFrame({
    '变量': ['常数项'] + list(X.columns),
    '系数': model.params.values,
    '标准误': model.bse.values,
    't统计量': model.tvalues.values,
    'P值': model.pvalues.values,
    '95%置信区间下限': model.conf_int()[0],
    '95%置信区间上限': model.conf_int()[1]
})
print(coef_df.to_string(index=False))

# ---------------------------- 4. 模型预测 ----------------------------
y_pred = model.predict(X_const)

# ---------------------------- 5. 可视化线性拟合图（实际值 vs 预测值） ----------------------------
plt.figure(figsize=(8, 6))
plt.scatter(y, y_pred, alpha=0.6, edgecolors='k', c='steelblue', label='预测值 vs 实际值')
min_val = min(y.min(), y_pred.min())
max_val = max(y.max(), y_pred.max())
plt.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='理想拟合线 (y = x)')

plt.xlabel('实际事故发生次数', fontsize=12)
plt.ylabel('预测事故发生次数', fontsize=12)
plt.title('多元线性回归：实际值 vs 预测值（线性拟合图）', fontsize=14)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)

# 在图上添加 R² 值
r_squared = model.rsquared
plt.text(0.05, 0.95, f'$R^2 = {r_squared:.4f}$', transform=plt.gca().transAxes,
         fontsize=12, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.show()

# ---------------------------- 6. 输出分析结论 ---------------------------
print("\n========== 分析结论 ==========")
print(f"模型整体显著性：F({int(model.df_model)}, {int(model.df_resid)}) = {model.fvalue:.2f}, p-value = {model.f_pvalue:.4e} (远小于0.05，模型整体显著)")
print(f"调整后 R² = {model.rsquared_adj:.4f}，说明自变量解释了约{model.rsquared_adj*100:.2f}%的事故次数变异。")
print("\n各变量影响方向及显著性：")
for var, coef, pval in zip(['age', 'material', 'maintenance', 'collection'], 
                            model.params[1:], model.pvalues[1:]):
    if pval < 0.05:
        sign = "显著"
        effect = "正相关" if coef > 0 else "负相关"
    else:
        sign = "不显著"
        effect = "无明显影响"
    print(f"  - {var}: 系数 = {coef:.4f}, P值 = {pval:.4e} ({sign})，对事故次数呈{effect}。")
print("\n注：物业费收缴率(collection)的P值 > 0.05，统计上不显著，说明在本数据中它对事故次数无显著线性影响。")