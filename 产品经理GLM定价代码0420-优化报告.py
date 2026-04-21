# -*- coding: utf-8 -*-
"""
产品经理：读取 coef.json 中的系数，生成互动定价工具并自动打开浏览器
（已移除收缴率因子，导出报告为保险报价单风格）
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
risk_relative_A = coef_data['risk_relative']['A']
risk_relative_B = coef_data['risk_relative']['B']
risk_relative_C = coef_data['risk_relative']['C']
risk_relative_D = coef_data['risk_relative']['D']
risk_relative_E = coef_data['risk_relative']['E']

# HTML 模板，使用 {变量名} 作为 Python 占位符，所有其他花括号都双写转义
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

    // 导出报告：保险报价单风格
    function exportReport() {{
        let currentAge = parseFloat(ageSlider.value);
        let currentMaterial = parseFloat(materialSlider.value);
        let currentMaint = parseFloat(maintenanceInput.value);
        let currentRisk = riskSelect.value;
        let riskName = riskSelect.options[riskSelect.selectedIndex].text;
        let {{ rr, premium }} = calculatePremiumForParams(currentAge, currentMaterial, currentMaint, currentRisk);
        
        // 虚构房屋基本信息
        const address = "上海市浦东新区锦绣路300号·阳光花园12栋301室";
        const insuredName = "李阳明";
        const houseArea = "128.6 m²";
        const houseStructure = "钢混结构";
        const usage = "家庭自住";
        const builtYear = 2004;
        const insurancePeriod = "2025-06-01 00:00:00 至 2026-06-01 00:00:00";
        
        // 根据总保费分配各险别保费
        let mainPremium = premium * 0.65;
        let decorationPremium = premium * 0.15;
        let liabilityPremium = premium * 0.12;
        let pipePremium = premium * 0.08;
        
        // 虚构保险金额
        const mainSumInsured = 1800000;
        const decorationSumInsured = 300000;
        const liabilitySumInsured = 1000000;
        const pipeSumInsured = 50000;
        
        let now = new Date();
        let dateStr = now.toLocaleString('zh-CN');

        let report = `
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>智护墙安·房屋保险报价单</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    background: #f0f2f5;
                    font-family: 'Segoe UI', 'Roboto', 'Microsoft YaHei', system-ui, sans-serif;
                    padding: 30px 20px;
                    color: #1e2f3e;
                }}
                .quote-container {{
                    max-width: 1000px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
                    overflow: hidden;
                }}
                .header {{
                    background: #1a4d8c;
                    color: white;
                    padding: 24px 28px;
                    text-align: center;
                }}
                .header h1 {{
                    font-size: 1.8rem;
                    margin-bottom: 6px;
                }}
                .header p {{
                    opacity: 0.85;
                    font-size: 0.9rem;
                }}
                .content {{
                    padding: 28px 32px;
                }}
                .info-section {{
                    background: #f8fafc;
                    border-radius: 16px;
                    padding: 20px;
                    margin-bottom: 28px;
                    border: 1px solid #e4e9f0;
                }}
                .info-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(280px,1fr));
                    gap: 16px;
                }}
                .info-item {{
                    display: flex;
                    align-items: baseline;
                    font-size: 0.9rem;
                }}
                .info-label {{
                    width: 110px;
                    font-weight: 600;
                    color: #4a627a;
                }}
                .info-value {{
                    flex: 1;
                    color: #1e4663;
                    font-weight: 500;
                }}
                .table-wrapper {{
                    overflow-x: auto;
                    margin: 24px 0;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 0.85rem;
                }}
                th {{
                    background: #eef2f7;
                    padding: 12px 10px;
                    text-align: center;
                    font-weight: 600;
                    color: #1e4663;
                    border-bottom: 1px solid #d0dbe8;
                }}
                td {{
                    padding: 12px 10px;
                    text-align: center;
                    border-bottom: 1px solid #eef2f7;
                }}
                .text-left {{
                    text-align: left;
                }}
                .premium-total {{
                    background: #fef7e8;
                    border-radius: 16px;
                    padding: 20px;
                    margin-top: 20px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    flex-wrap: wrap;
                    gap: 16px;
                }}
                .total-label {{
                    font-size: 1.1rem;
                    font-weight: 600;
                    color: #b97f44;
                }}
                .total-amount {{
                    font-size: 2rem;
                    font-weight: 800;
                    color: #1a4d8c;
                }}
                .footnote {{
                    text-align: center;
                    font-size: 0.7rem;
                    color: #8aa9c4;
                    margin-top: 28px;
                    padding-top: 16px;
                    border-top: 1px solid #eef2f8;
                }}
                @media (max-width: 650px) {{
                    .content {{ padding: 20px; }}
                    .info-item {{ flex-direction: column; gap: 4px; }}
                    .info-label {{ width: auto; }}
                }}
            </style>
        </head>
        <body>
            <div class="quote-container">
                <div class="header">
                    <h1>🏘️ 智护墙安·房屋保险报价预览</h1>
                    <p>基于广义线性模型动态定价 | 报价仅供参考</p>
                </div>
                <div class="content">
                    <div class="info-section">
                        <div class="info-grid">
                            <div class="info-item"><span class="info-label">房屋地址：</span><span class="info-value">${{address}}</span></div>
                            <div class="info-item"><span class="info-label">被保险人：</span><span class="info-value">${{insuredName}}</span></div>
                            <div class="info-item"><span class="info-label">建筑面积：</span><span class="info-value">${{houseArea}}</span></div>
                            <div class="info-item"><span class="info-label">建筑结构：</span><span class="info-value">${{houseStructure}}</span></div>
                            <div class="info-item"><span class="info-label">使用性质：</span><span class="info-value">${{usage}}</span></div>
                            <div class="info-item"><span class="info-label">建成年份：</span><span class="info-value">${{builtYear}}年</span></div>
                            <div class="info-item"><span class="info-label">房龄：</span><span class="info-value">${{currentAge}}年</span></div>
                            <div class="info-item"><span class="info-label">材料老化指数：</span><span class="info-value">${{currentMaterial}}</span></div>
                            <div class="info-item"><span class="info-label">近3年维护次数：</span><span class="info-value">${{currentMaint}}次</span></div>
                            <div class="info-item"><span class="info-label">AHP风险等级：</span><span class="info-value">${{currentRisk}} — ${{riskName}}</span></div>
                            <div class="info-item"><span class="info-label">保险期限：</span><span class="info-value">${{insurancePeriod}}</span></div>
                        </div>
                    </div>

                    <div class="table-wrapper">
                        <table>
                            <thead>
                                <tr><th>险别名称</th><th>保险金额（元）</th><th>保费（元）</th></tr>
                            </thead>
                            <tbody>
                                <tr><td class="text-left">🏠 房屋主体损失保险</td><td>${{mainSumInsured.toLocaleString()}}</td><td>${{Math.round(mainPremium).toLocaleString()}}</td></tr>
                                <tr><td class="text-left">🛋️ 室内装修及附属设施损失保险</td><td>${{decorationSumInsured.toLocaleString()}}</td><td>${{Math.round(decorationPremium).toLocaleString()}}</td></tr>
                                <tr><td class="text-left">⚖️ 居家第三者责任保险</td><td>${{liabilitySumInsured.toLocaleString()}}</td><td>${{Math.round(liabilityPremium).toLocaleString()}}</td></tr>
                                <tr><td class="text-left">💧 管道破裂及水渍保险</td><td>${{pipeSumInsured.toLocaleString()}}</td><td>${{Math.round(pipePremium).toLocaleString()}}</td></tr>
                                <tr><td class="text-left">🔧 附加家用电器安全保险</td><td>80,000</td><td>${{Math.round(premium * 0.05).toLocaleString()}}</td></tr>
                            </tbody>
                        </table>
                    </div>

                    <div class="premium-total">
                        <span class="total-label">📄 商业房屋保险保费合计：</span>
                        <span class="total-amount">¥ ${{Math.round(premium).toLocaleString()}}</span>
                    </div>
                    <div style="margin-top: 12px; font-size:0.85rem; background:#f0f6fe; padding:12px; border-radius:16px;">
                        <strong>💡 说明：</strong> 以上保费基于GLM模型计算，其中房龄、材料老化、维护次数及风险等级为动态因子。本报价为试算保费，仅供参考，最终以保险单为准。
                    </div>
                    <div class="footnote">
                        报价时间：${{dateStr}}<br>
                        智护墙安 · 让每一面墙都安心
                    </div>
                </div>
            </div>
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

# 准备所有要传入 format 的变量
format_vars = {
    'coef_age': coef_age,
    'coef_material': coef_material,
    'coef_maintenance': coef_maintenance,
    'risk_relative_A': risk_relative_A,
    'risk_relative_B': risk_relative_B,
    'risk_relative_C': risk_relative_C,
    'risk_relative_D': risk_relative_D,
    'risk_relative_E': risk_relative_E,
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
