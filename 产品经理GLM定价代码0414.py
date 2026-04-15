# -*- coding: utf-8 -*-
"""
产品经理：读取 coef.json 中的系数，生成互动定价工具并自动打开浏览器
（已移除收缴率因子，报告样式已美化，含动态图表）
"""

import webbrowser
import os
import json

# 读取数据分析师保存的系数文件
coef_file = 'coef.json'
if not os.path.exists(coef_file):
    print(f"错误：找不到 {coef_file}，请先运行数据分析师脚本生成系数文件。")
    # 后备默认系数（保证演示不中断）
    coef_data = {
        'base_premium': 3000,
        'base_age': 15,
        'base_material': 0.5,
        'base_maintenance': 1,
        'coef_age': 0.0208,
        'coef_material': 1.5181,
        'coef_maintenance': -0.134,
        'risk_relative': {'A': 3.00, 'B': 2.20, 'C': 1.50, 'D': 1.00, 'E': 0.80}
    }
else:
    with open(coef_file, 'r', encoding='utf-8') as f:
        coef_data = json.load(f)

print("已加载定价系数：")
print(f"房龄系数: {coef_data['coef_age']:.6f}")
print(f"材料老化系数: {coef_data['coef_material']:.6f}")
print(f"维护次数系数: {coef_data['coef_maintenance']:.6f}")

# 准备需要嵌入的变量
risk_relative_json = json.dumps(coef_data['risk_relative'])
base_premium = coef_data['base_premium']
base_age = coef_data['base_age']
base_material = coef_data['base_material']
base_maintenance = coef_data['base_maintenance']
coef_age = coef_data['coef_age']
coef_material = coef_data['coef_material']
coef_maintenance = coef_data['coef_maintenance']

# 生成 HTML 内容（使用 format 避免 f-string 转义问题）
html_template = r"""<!DOCTYPE html>
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
        <p>GLM动态定价工具（系数自动同步）</p>
    </div>
    <div class="content">
        <div class="coefficient-panel">
            <h4>📐 定价系数</h4>
            <div class="coeff-row"><span>房龄系数：</span><span>{coef_age:.6f}</span></div>
            <div class="coeff-row"><span>材料老化系数：</span><span>{coef_material:.6f}</span></div>
            <div class="coeff-row"><span>维护次数系数：</span><span>{coef_maintenance:.6f}</span></div>
            <div class="coeff-row"><span>A/B/C/D/E相对费率：</span><span>{risk_relative_A:.2f} / {risk_relative_B:.2f} / {risk_relative_C:.2f} / {risk_relative_D:.2f} / {risk_relative_E:.2f}</span></div>
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
        <footer>* 系数自动同步自数据分析师回归结果，产品经理无需手动输入</footer>
    </div>
</div>
<script>
    const GLM_PARAMS = {{
        basePremium: {base_premium},
        baseAge: {base_age},
        baseMaterial: {base_material},
        baseMaintenance: {base_maintenance},
        coefAge: {coef_age},
        coefMaterial: {coef_material},
        coefMaintenance: {coef_maintenance},
        riskRelative: {risk_relative_json}
    }};

    const ageSlider = document.getElementById('age');
    const ageVal = document.getElementById('ageVal');
    const materialSlider = document.getElementById('material');
    const materialVal = document.getElementById('materialVal');
    const maintenanceInput = document.getElementById('maintenance');
    const riskSelect = document.getElementById('riskLevel');
    const premiumSpan = document.getElementById('premiumDisplay');
    const rrSpan = document.getElementById('rrDisplay');
    const resetBtn = document.getElementById('resetBtn');
    const exportBtn = document.getElementById('exportBtn');

    function calculatePremiumForParams(age, material, maint, risk) {{
        let logRR = GLM_PARAMS.coefAge * (age - GLM_PARAMS.baseAge) +
                    GLM_PARAMS.coefMaterial * (material - GLM_PARAMS.baseMaterial) +
                    GLM_PARAMS.coefMaintenance * (maint - GLM_PARAMS.baseMaintenance) +
                    Math.log(GLM_PARAMS.riskRelative[risk]);
        let rr = Math.exp(logRR);
        let premium = GLM_PARAMS.basePremium * rr;
        return {{ rr, premium }};
    }}

    function calculatePremium() {{
        let age = parseFloat(ageSlider.value);
        let material = parseFloat(materialSlider.value);
        let maint = parseFloat(maintenanceInput.value);
        let risk = riskSelect.value;
        return calculatePremiumForParams(age, material, maint, risk);
    }}

    function updateUI() {{
        let age = parseFloat(ageSlider.value);
        let material = parseFloat(materialSlider.value);
        ageVal.innerText = age;
        materialVal.innerText = material.toFixed(2);
        let {{ rr, premium }} = calculatePremium();
        premiumSpan.innerText = Math.round(premium).toLocaleString() + ' 元';
        rrSpan.innerText = `相对费率 = ${{rr.toFixed(3)}}`;
    }}

    function resetToDemo() {{
        ageSlider.value = '20';
        materialSlider.value = '0.7';
        maintenanceInput.value = '0';
        riskSelect.value = 'C';
        updateUI();
    }}

    // 美化后的导出报告功能（含图表，布局先突出报价）
    function exportReport() {{
        let currentAge = parseFloat(ageSlider.value);
        let currentMaterial = parseFloat(materialSlider.value);
        let currentMaint = parseFloat(maintenanceInput.value);
        let currentRisk = riskSelect.value;
        let riskName = riskSelect.options[riskSelect.selectedIndex].text;
        let {{ rr, premium }} = calculatePremiumForParams(currentAge, currentMaterial, currentMaint, currentRisk);
        
        // 生成房龄-保费曲线数据（10~30岁，步长1，其他参数固定为当前值）
        let ageRange = [];
        let premiumRange = [];
        for (let age = 10; age <= 30; age++) {{
            let {{ premium: p }} = calculatePremiumForParams(age, currentMaterial, currentMaint, currentRisk);
            ageRange.push(age);
            premiumRange.push(p);
        }}
        
        let now = new Date();
        let dateStr = now.toLocaleString('zh-CN');

        let report = `
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>智护墙安·保费精算报告</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"><\/script>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    background: #fef7e8;
                    font-family: 'Segoe UI', 'Roboto', 'Microsoft YaHei', system-ui, sans-serif;
                    padding: 40px 24px;
                    color: #3e2a1f;
                }}
                .report-card {{
                    max-width: 900px;
                    margin: 0 auto;
                    background: #ffffff;
                    border-radius: 40px;
                    box-shadow: 0 20px 35px rgba(0,0,0,0.05);
                    overflow: hidden;
                }}
                /* 头部突出报价 */
                .premium-hero {{
                    background: linear-gradient(120deg, #ffd89b, #ffb347);
                    padding: 48px 28px;
                    text-align: center;
                    color: #2c1a0c;
                }}
                .premium-hero .label {{
                    font-size: 1rem;
                    letter-spacing: 2px;
                    text-transform: uppercase;
                    opacity: 0.8;
                }}
                .premium-hero .amount {{
                    font-size: 4rem;
                    font-weight: 800;
                    margin: 12px 0 8px;
                    line-height: 1.1;
                }}
                .premium-hero .rr {{
                    background: rgba(255,255,240,0.3);
                    display: inline-block;
                    padding: 4px 16px;
                    border-radius: 40px;
                    font-size: 0.9rem;
                }}
                /* 内容区域 */
                .report-content {{
                    padding: 32px 32px 40px;
                }}
                .params-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px,1fr));
                    gap: 16px;
                    background: #fff9f0;
                    border-radius: 28px;
                    padding: 20px;
                    margin-bottom: 32px;
                }}
                .param-item {{
                    display: flex;
                    justify-content: space-between;
                    align-items: baseline;
                    border-bottom: 1px dashed #ffe0b5;
                    padding: 8px 0;
                }}
                .param-label {{
                    font-weight: 500;
                    color: #b97f44;
                }}
                .param-value {{
                    font-weight: 600;
                    color: #5a3a22;
                }}
                .chart-container {{
                    margin: 32px 0 24px;
                    background: #fefaf5;
                    border-radius: 28px;
                    padding: 20px;
                }}
                .chart-title {{
                    text-align: center;
                    font-weight: 600;
                    margin-bottom: 16px;
                    color: #c47e3a;
                }}
                canvas {{
                    max-height: 300px;
                    width: 100%;
                }}
                .footnote {{
                    text-align: center;
                    font-size: 0.7rem;
                    color: #bc9a6f;
                    border-top: 1px solid #fae6cf;
                    padding-top: 24px;
                    margin-top: 16px;
                }}
                @media (max-width: 600px) {{
                    .premium-hero .amount {{ font-size: 2.8rem; }}
                    .report-content {{ padding: 20px; }}
                }}
            </style>
        </head>
        <body>
            <div class="report-card">
                <div class="premium-hero">
                    <div class="label">✨ 建议年保费 ✨</div>
                    <div class="amount">¥ ${{Math.round(premium).toLocaleString()}}</div>
                    <div class="rr">相对基准保费: ${{rr.toFixed(3)}}x</div>
                </div>
                <div class="report-content">
                    <div class="params-grid">
                        <div class="param-item"><span class="param-label">📅 房龄</span><span class="param-value">${{currentAge}} 年</span></div>
                        <div class="param-item"><span class="param-label">🧱 材料老化指数</span><span class="param-value">${{currentMaterial}}</span></div>
                        <div class="param-item"><span class="param-label">🔧 近3年维护次数</span><span class="param-value">${{currentMaint}} 次</span></div>
                        <div class="param-item"><span class="param-label">⚠️ AHP风险等级</span><span class="param-value">${{currentRisk}} — ${{riskName}}</span></div>
                    </div>

                    <div class="chart-container">
                        <div class="chart-title">📈 保费随房龄波动曲线（其他参数保持当前值）</div>
                        <canvas id="agePremiumChart" width="800" height="300"></canvas>
                        <div style="text-align:center; font-size:0.7rem; color:#b97f44; margin-top:12px;">房龄范围 10~30 年，步长1年</div>
                    </div>

                    <div class="footnote">
                        报告生成时间：${{dateStr}}<br>
                        本定价基于广义线性模型，系数自动同步自数据分析师最新回归结果。
                    </div>
                </div>
            </div>
            <script>
                const ctx = document.getElementById('agePremiumChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: {{JSON.stringify(ageRange)}},
                        datasets: [{{
                            label: '年保费 (元)',
                            data: {{JSON.stringify(premiumRange.map(v => Math.round(v)))}},
                            borderColor: '#ff9f4a',
                            backgroundColor: 'rgba(255, 159, 74, 0.05)',
                            borderWidth: 3,
                            pointRadius: 3,
                            pointBackgroundColor: '#ff7e2e',
                            pointBorderColor: '#fff',
                            tension: 0.2,
                            fill: true
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: true,
                        plugins: {{
                            tooltip: {{
                                callbacks: {{
                                    label: function(context) {{
                                        return '保费: ¥' + context.raw.toLocaleString();
                                    }}
                                }}
                            }},
                            legend: {{
                                position: 'top',
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: false,
                                title: {{
                                    display: true,
                                    text: '保费 (元)',
                                    color: '#b97f44'
                                }},
                                ticks: {{
                                    callback: function(val) {{
                                        return '¥' + val.toLocaleString();
                                    }}
                                }}
                            }},
                            x: {{
                                title: {{
                                    display: true,
                                    text: '房龄 (年)',
                                    color: '#b97f44'
                                }}
                            }}
                        }}
                    }}
                }});
            <\/script>
        </body>
        </html>
        `;
        let w = window.open();
        w.document.write(report);
        w.document.close();
    }}

    ageSlider.addEventListener('input', updateUI);
    materialSlider.addEventListener('input', updateUI);
    maintenanceInput.addEventListener('input', updateUI);
    riskSelect.addEventListener('change', updateUI);
    resetBtn.addEventListener('click', resetToDemo);
    exportBtn.addEventListener('click', exportReport);
    updateUI();
</script>
</body>
</html>
"""

# 准备所有要传入 format 的变量（注意：risk_relative 需要拆解为单独的值）
risk_rel = coef_data['risk_relative']
format_vars = {
    'coef_age': coef_age,
    'coef_material': coef_material,
    'coef_maintenance': coef_maintenance,
    'risk_relative_A': risk_rel['A'],
    'risk_relative_B': risk_rel['B'],
    'risk_relative_C': risk_rel['C'],
    'risk_relative_D': risk_rel['D'],
    'risk_relative_E': risk_rel['E'],
    'base_premium': base_premium,
    'base_age': base_age,
    'base_material': base_material,
    'base_maintenance': base_maintenance,
    'risk_relative_json': risk_relative_json,
}

html_content = html_template.format(**format_vars)

# 写入文件并打开浏览器
html_file = "zhuhuqiang_pm_pricing.html"
with open(html_file, "w", encoding="utf-8") as f:
    f.write(html_content)

webbrowser.open("file://" + os.path.abspath(html_file))
print(f"产品经理定价工具已启动，系数来自 {coef_file}")
print(f"浏览器已打开：{os.path.abspath(html_file)}")
