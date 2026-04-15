import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import os

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# ---------------------------- 1. 读取数据（自动定位到桌面） ----------------------------
# 获取当前用户的桌面路径
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
file_name = '回归分析数据-3因素 .xlsx'
file_path = os.path.join(desktop_path, file_name)

# 如果桌面找不到，再尝试其他位置（保留原脚本的逻辑作为备选）
if not os.path.exists(file_path):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, file_name)
if not os.path.exists(file_path):
    file_path = file_name
if not os.path.exists(file_path):
    abs_path = r'C:/Users/李一帆/Desktop/多元线性回归/回归分析数据-3因素 .xlsx'
    if os.path.exists(abs_path):
        file_path = abs_path
    else:
        raise FileNotFoundError(f"找不到文件 {file_name}，请将文件放在桌面或脚本目录下。")

print(f"正在读取文件：{file_path}")
df = pd.read_excel(file_path, sheet_name='Sheet1')

print("数据前5行：")
print(df.head())

# ---------------------------- 2. 定义变量 ----------------------------
X = df[['age', 'material', 'maintenance']]
y = df['accident']
X_const = sm.add_constant(X)

# ---------------------------- 3. 拟合模型 ----------------------------
model = sm.OLS(y, X_const).fit()
print("\n========== 回归模型摘要 ==========")
print(model.summary())

# ---------------------------- 4. 系数表（明确标签） ----------------------------
print("\n========== 各因素系数表 ==========")
# 使用标签索引避免警告
coef_names = ['常数项', 'age', 'material', 'maintenance']
coef_values = [model.params['const'], model.params['age'], 
               model.params['material'], model.params['maintenance']]
p_values = [model.pvalues['const'], model.pvalues['age'], 
            model.pvalues['material'], model.pvalues['maintenance']]

coef_df = pd.DataFrame({
    '变量': coef_names,
    '系数': coef_values,
    'P值': p_values,
    '显著性': ['显著' if p < 0.05 else '不显著' for p in p_values]
})
print(coef_df.to_string(index=False))

# 单独输出回归方程（使用标签，避免警告）
print("\n回归方程：")
print(f"accident = {model.params['const']:.4f} + {model.params['age']:.4f}*age + "
      f"{model.params['material']:.4f}*material + {model.params['maintenance']:.4f}*maintenance")

# ---------------------------- 5. 显著性验证 ----------------------------
alpha = 0.05
significant_vars = []
for var in ['age', 'material', 'maintenance']:
    pval = model.pvalues[var]
    if pval < alpha:
        significant_vars.append(var)
        print(f"✅ 变量 {var} 的 P 值 = {pval:.4e} < {alpha}，显著")
    else:
        print(f"❌ 变量 {var} 的 P 值 = {pval:.4f} >= {alpha}，不显著")

# ---------------------------- 6. 可视化 ----------------------------
y_pred = model.predict(X_const)

plt.figure(figsize=(8, 6))
plt.scatter(y, y_pred, alpha=0.6, edgecolors='k', c='steelblue', label='预测值 vs 实际值')
min_val = min(y.min(), y_pred.min())
max_val = max(y.max(), y_pred.max())
plt.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='理想拟合线 (y = x)')

plt.xlabel('实际事故发生次数', fontsize=12)
plt.ylabel('预测事故发生次数', fontsize=12)
plt.title('三因素线性回归：实际值 vs 预测值', fontsize=14)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)

plt.text(0.05, 0.95, f'$R^2 = {model.rsquared:.4f}$\n调整后 $R^2 = {model.rsquared_adj:.4f}$', 
         transform=plt.gca().transAxes, fontsize=12, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.show()

# ---------------------------- 7. 模型可行性结论 ---------------------------
print("\n========== 模型可行性结论 ==========")
if model.f_pvalue < alpha:
    print("✅ 回归模型整体显著（p < 0.05），具有统计学意义。")
else:
    print("❌ 回归模型整体不显著，需重新考虑变量。")

print(f"调整后 R² = {model.rsquared_adj:.4f}，自变量解释了约 {model.rsquared_adj*100:.2f}% 的事故次数变异。")

if len(significant_vars) == 3:
    print("✅ 所有三个自变量（age, material, maintenance）均显著，模型可行。")
elif len(significant_vars) > 0:
    print(f"⚠️ 只有部分变量显著：{significant_vars}，可考虑剔除不显著变量。")
else:
    print("❌ 所有变量均不显著，模型不可行。")

# 输出各因素系数（再次强调）
print("\n各因素系数（即斜率）：")
print(f"  房龄 (age) 的系数: {model.params['age']:.4f}")
print(f"  材料老化程度 (material) 的系数: {model.params['material']:.4f}")
print(f"  维护次数 (maintenance) 的系数: {model.params['maintenance']:.4f}")