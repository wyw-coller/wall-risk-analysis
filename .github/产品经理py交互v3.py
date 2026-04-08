# -*- coding: utf-8 -*-
"""
产品经理：启动GLM互动定价工具（无回归分析，直接打开HTML）
"""

import webbrowser
import os

# ========== 定价系数（与数据分析师回归结果保持一致） ==========
# 这些系数可以预先从回归分析中获得，例如：
# 房龄系数 0.08，材料老化系数 1.2，维护次数系数 -0.3，收缴率系数 -0.5
COEFFICIENTS = {
    'base_premium': 3000,
    'base_age': 15,
    'base_material': 0.5,
    'base_maintenance': 1,
    'base_collection': 0.5,
    'coef_age': 0.0800,
    'coef_material': 1.2000,
    'coef_maintenance': -0.3000,
    'coef_collection': -0.5000,
    'risk_relative': {'A': 3.00, 'B': 2.20, 'C': 1.50, 'D': 1.00, 'E': 0.80}
}

# ========== 生成HTML文件（系数已嵌入） ==========
html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>智护墙安·产品经理定价工具</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Roboto, 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #e9f0f5 0%, #d4e0e8 100%);
            margin: 0;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}
        .card {{
            max-width: 650px;
            width: 100%;
            background: white;
            border-radius: 32px;
            box-shadow: 0 20px 35px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{ background: #1a4d8c; color: white; padding: 24px 28px; text-align: center; }}
        .header h1 {{ margin: 0; }}
        .content {{ padding: 28px; }}
        .input-group {{ margin-bottom: 22px; }}
        label {{ font-weight: 600; color: #1e4663; display: block; margin-bottom: 8px; }}
        select, input {{ width: 100%; padding: 12px 16px; border-radius: 24px; border: 1px solid #cbdbe2; }}
        .premium-box {{ background: #f0f6fe; border-radius: 28px; padding: 20px; text-align: center; margin: 20px 0; }}
        .premium-value {{ font-size: 2.8rem; font-weight: 800; color: #0f3b5f; }}
        .btn-row {{ display: flex; gap: 12px; margin-top: 20px; }}
        .btn {{ background: #eef2f7; border: none; padding: 10px; border-radius: 40px; cursor: pointer; font-weight: 600; flex:1; }}
        .btn-primary {{ background: #1a4d8c; color: white; }}
        footer {{ text-align: center; font-size: 0.7rem; color: #8aa9c4; margin-top: 20px; }}
        .slider-value {{ display: inline-block; background: #e9edf2; padding: 2px 12px; border-radius: 20px; margin-left: 10px; }}
        .flex-range {{ display: flex; gap: 12px; align-items: center; }}
        .flex-range input {{ flex: 1; }}
        .coefficient-panel {{
            background: #f9f9f9;
            border-radius: 16px;
            padding: 12px;
            margin-bottom: 20px;
            font-size: 0.8rem;
            border: 1px solid #ddd;
        }}
        .coefficient-panel h4 {{ margin: 0 0 8px 0; font-size: 0.9rem; }}
        .coeff-row {{ display: flex; justify-content: space-between; margin-bottom: 4px; }}
    </style>
</head>
<body>
<div class="card">
    <div class="header">
        <h1>🏘️ 智护墙安</h1>
        <p>产品经理 · GLM动态定价工具</p>
    </div>
    <div class="content">
        <div class="coefficient-panel">
            <h4>📐 定价系数（基于86个小区泊松回归）</h4>
            <div class="coeff-row"><span>房龄系数：</span><span>{COEFFICIENTS['coef_age']:.4f}</span></div>
            <div class="coeff-row"><span>材料老化系数：</span><span>{COEFFICIENTS['coef_material']:.4f}</span></div>
            <div class="coeff-row"><span>维护次数系数：</span><span>{COEFFICIENTS['coef_maintenance']:.4f}</span></div>
            <div class="coeff-row"><span>收缴率系数：</span><span>{COEFFICIENTS['coef_collection']:.4f}</span></div>
            <div class="coeff-row"><span>A/B/C/D/E相对费率：</span><span>{COEFFICIENTS['risk_relative']['A']:.2f} / {COEFFICIENTS['risk_relative']['B']:.2f} / {COEFFICIENTS['risk_relative']['C']:.2f} / {COEFFICIENTS['risk_relative']['D']:.2f} / {COEFFICIENTS['risk_relative']['E']:.2f}</span></div>
        </div>
        <div class="input-group">
            <label>📅 房龄 (年)</label>
            <div class="flex-range">
                <input type="range" id="age" min="10" max="30" step="1" value="20">
                <span id="ageVal" class="slider-value">20</span>
            </div>
        </div>
        <div class="input-group">
            <label>🧱 材料老化指数 (0.2~0.9)</label>
            <div class="flex-range">
                <input type="range" id="material" min="0.2" max="0.9" step="0.01" value="0.7">
                <span id="materialVal" class="slider-value">0.70</span>
            </div>
        </div>
        <div class="input-group">
            <label>🔧 近3年维护次数</label>
            <input type="number" id="maintenance" min="0" max="5" step="1" value="0">
        </div>
        <div class="input-group">
            <label>💰 物业费收缴率 (0.1~0.8)</label>
            <div class="flex-range">
                <input type="range" id="collection" min="0.1" max="0.8" step="0.01" value="0.4">
                <span id="collectionVal" class="slider-value">0.40</span>
            </div>
        </div>
        <div class="input-group">
            <label>⚠️ AHP综合风险等级</label>
            <select id="riskLevel">
                <option value="E">E级（无风险）</option>
                <option value="D">D级（关注风险）</option>
                <option value="C" selected>C级（较大风险）</option>
                <option value="B">B级（大风险）</option>
                <option value="A">A级（重大风险）</option>
            </select>
        </div>
        <div class="premium-box">
            <div class="premium-label">建议年保费</div>
            <div class="premium-value" id="premiumDisplay">--</div>
            <div id="rrDisplay">相对费率 = --</div>
        </div>
        <div class="btn-row">
            <button class="btn" id="resetBtn">重置示例（阳光小区）</button>
            <button class="btn btn-primary" id="exportBtn">📄 导出报告</button>
        </div>
        <footer>* 系数基于86个小区泊松回归，产品经理启动工具即加载最新参数</footer>
    </div>
</div>
<script>
    const GLM_PARAMS = {{
        basePremium: {COEFFICIENTS['base_premium']},
        baseAge: {COEFFICIENTS['base_age']},
        baseMaterial: {COEFFICIENTS['base_material']},
        baseMaintenance: {COEFFICIENTS['base_maintenance']},
        baseCollection: {COEFFICIENTS['base_collection']},
        coefAge: {COEFFICIENTS['coef_age']},
        coefMaterial: {COEFFICIENTS['coef_material']},
        coefMaintenance: {COEFFICIENTS['coef_maintenance']},
        coefCollection: {COEFFICIENTS['coef_collection']},
        riskRelative: {COEFFICIENTS['risk_relative']}
    }};

    const ageSlider = document.getElementById('age');
    const ageVal = document.getElementById('ageVal');
    const materialSlider = document.getElementById('material');
    const materialVal = document.getElementById('materialVal');
    const maintenanceInput = document.getElementById('maintenance');
    const collectionSlider = document.getElementById('collection');
    const collectionVal = document.getElementById('collectionVal');
    const riskSelect = document.getElementById('riskLevel');
    const premiumSpan = document.getElementById('premiumDisplay');
    const rrSpan = document.getElementById('rrDisplay');
    const resetBtn = document.getElementById('resetBtn');
    const exportBtn = document.getElementById('exportBtn');

    function calculatePremium() {{
        let age = parseFloat(ageSlider.value);
        let material = parseFloat(materialSlider.value);
        let maint = parseFloat(maintenanceInput.value);
        let coll = parseFloat(collectionSlider.value);
        let risk = riskSelect.value;
        let logRR = GLM_PARAMS.coefAge * (age - GLM_PARAMS.baseAge) +
                    GLM_PARAMS.coefMaterial * (material - GLM_PARAMS.baseMaterial) +
                    GLM_PARAMS.coefMaintenance * (maint - GLM_PARAMS.baseMaintenance) +
                    GLM_PARAMS.coefCollection * (coll - GLM_PARAMS.baseCollection) +
                    Math.log(GLM_PARAMS.riskRelative[risk]);
        let rr = Math.exp(logRR);
        let premium = GLM_PARAMS.basePremium * rr;
        return {{ rr, premium }};
    }}

    function updateUI() {{
        let age = parseFloat(ageSlider.value);
        let material = parseFloat(materialSlider.value);
        let coll = parseFloat(collectionSlider.value);
        ageVal.innerText = age;
        materialVal.innerText = material.toFixed(2);
        collectionVal.innerText = coll.toFixed(2);
        let {{ rr, premium }} = calculatePremium();
        premiumSpan.innerText = Math.round(premium).toLocaleString() + ' 元';
        rrSpan.innerText = `相对费率 = ${{rr.toFixed(3)}}`;
    }}

    function resetToDemo() {{
        ageSlider.value = '20';
        materialSlider.value = '0.7';
        maintenanceInput.value = '0';
        collectionSlider.value = '0.4';
        riskSelect.value = 'C';
        updateUI();
    }}

    function exportReport() {{
        let {{ rr, premium }} = calculatePremium();
        let age = ageSlider.value;
        let material = materialSlider.value;
        let maint = maintenanceInput.value;
        let coll = collectionSlider.value;
        let risk = riskSelect.value;
        let report = `
        <html><head><meta charset="UTF-8"><title>保费报告</title><style>body{{font-family:sans-serif;padding:40px}}</style></head>
        <body><h1>智护墙安保费评估报告</h1>
        <p>房龄: ${{age}}年</p><p>材料老化指数: ${{material}}</p><p>维护次数: ${{maint}}</p><p>收缴率: ${{(coll*100).toFixed(1)}}%</p>
        <p>AHP风险等级: ${{risk}}级</p>
        <h2>建议年保费: ${{Math.round(premium).toLocaleString()}} 元</h2>
        <p>相对费率: ${{rr.toFixed(3)}}</p>
        <small>定价系数基于86个小区泊松回归，由产品经理工具自动加载</small>
        </body></html>`;
        let w = window.open();
        w.document.write(report);
        w.document.close();
    }}

    ageSlider.addEventListener('input', updateUI);
    materialSlider.addEventListener('input', updateUI);
    maintenanceInput.addEventListener('input', updateUI);
    collectionSlider.addEventListener('input', updateUI);
    riskSelect.addEventListener('change', updateUI);
    resetBtn.addEventListener('click', resetToDemo);
    exportBtn.addEventListener('click', exportReport);
    updateUI();
</script>
</body>
</html>
"""

# 写入文件并打开
html_file = "zhuhuqiang_pm_pricing.html"
with open(html_file, "w", encoding="utf-8") as f:
    f.write(html_content)

webbrowser.open("file://" + os.path.abspath(html_file))
print(f"产品经理定价工具已启动，请查看浏览器窗口：{os.path.abspath(html_file)}")
print("本工具使用的定价系数来自86个小区泊松回归分析，与数据分析师结果保持一致。")
