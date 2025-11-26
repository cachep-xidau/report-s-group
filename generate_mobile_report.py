"""
Tạo Báo Cáo Tài Chính Mobile
Thiết kế tối ưu cho iPhone 15 Pro Max và Oppo Find X8 Pro
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import json

# ============================================================================
# TẢI DỮ LIỆU
# ============================================================================

def clean_currency_value(value):
    """Chuyển đổi định dạng số Việt Nam sang float"""
    if pd.isna(value) or value == '' or value == '-':
        return np.nan
    if isinstance(value, str):
        value = value.replace(' M', '').replace('M', '').strip()
        value = value.replace('.', '')
        value = value.replace(',', '.')
        try:
            return float(value)
        except:
            return np.nan
    return float(value)

def format_number(value):
    """Format số với dấu chấm phân cách hàng nghìn và thêm M"""
    return f"{value:,.0f} M".replace(',', '.')

# Tải dữ liệu
file_path = '/Users/lucasbraci/Documents/Lucas/Phan tich CSV.csv'
df_raw = pd.read_csv(file_path)
df_raw.columns = df_raw.columns.str.strip()

months = ['T01', 'T02', 'T03', 'T04', 'T05', 'T06', 'T07', 'T08', 'T09', 'T10']
companies = ['SAN', 'TEENNIE', 'TGIL']
company_display_names = {'SAN': 'S', 'TEENNIE': 'T', 'TGIL': 'I'}
company_full_names = {'SAN': 'SAN', 'TEENNIE': 'TEENNIE', 'TGIL': 'TGIL'}

def extract_company_data(df, row_indices, metric_name):
    """Trích xuất dữ liệu hàng tháng cho chỉ tiêu cụ thể"""
    data = {}
    for company, idx in row_indices.items():
        row = df.iloc[idx]
        values = [clean_currency_value(row[month]) for month in months]
        data[company] = values
    return pd.DataFrame(data, index=months)

# Chỉ số hàng các chỉ tiêu chính
metrics_rows = {
    'Revenue': {'Total': 0, 'SAN': 1, 'TEENNIE': 2, 'TGIL': 3},
    'COGS': {'Total': 4, 'SAN': 5, 'TEENNIE': 9, 'TGIL': 13},
    'Gross Profit': {'Total': 17, 'SAN': 18, 'TEENNIE': 19, 'TGIL': 20},
    'Selling Expenses': {'Total': 33, 'SAN': 34, 'TEENNIE': 46, 'TGIL': 58},
    'Operating Profit': {'Total': 70, 'SAN': 71, 'TEENNIE': 72, 'TGIL': 73},
    'Admin Expenses': {'Total': 74, 'SAN': 75, 'TEENNIE': 86, 'TGIL': 97},
    'Other Expenses': {'Total': 108, 'SAN': 109, 'TEENNIE': 113, 'TGIL': 117},
    'Profit Before Tax': {'Total': 131, 'SAN': 132, 'TEENNIE': 133, 'TGIL': 134},
}

# Trích xuất dữ liệu
revenue_df = extract_company_data(df_raw, metrics_rows['Revenue'], 'Revenue')
pbt_df = extract_company_data(df_raw, metrics_rows['Profit Before Tax'], 'Profit Before Tax')
cogs_df = extract_company_data(df_raw, metrics_rows['COGS'], 'COGS')
selling_exp_df = extract_company_data(df_raw, metrics_rows['Selling Expenses'], 'Selling Expenses')
admin_exp_df = extract_company_data(df_raw, metrics_rows['Admin Expenses'], 'Admin Expenses')
other_exp_df = extract_company_data(df_raw, metrics_rows['Other Expenses'], 'Other Expenses')

def create_quarterly_data(df):
    """Tổng hợp dữ liệu hàng tháng thành quý"""
    q1 = df.iloc[0:3].sum()
    q2 = df.iloc[3:6].sum()
    q3 = df.iloc[6:9].sum()
    q4 = df.iloc[9:10].sum()
    return pd.DataFrame([q1, q2, q3, q4], index=['Q1', 'Q2', 'Q3', 'Q4'])

revenue_quarterly = create_quarterly_data(revenue_df)
pbt_quarterly = create_quarterly_data(pbt_df)

# Đọc % đạt kế hoạch
def extract_achievement_rate(df, row_idx):
    """Trích xuất % đạt kế hoạch từ các cột trong CSV"""
    q1_pct = df.iloc[row_idx, 17]
    q2_pct = df.iloc[row_idx, 20]
    q3_pct = df.iloc[row_idx, 23]

    def parse_pct(val):
        if pd.isna(val) or val == '' or val == '-':
            return np.nan
        if isinstance(val, str):
            val = val.replace('%', '').replace(',', '.').strip()
            try:
                return float(val)
            except:
                return np.nan
        return float(val)

    return [parse_pct(q1_pct), parse_pct(q2_pct), parse_pct(q3_pct)]

# Lấy % đạt kế hoạch doanh thu
revenue_achievement = {
    'SAN': extract_achievement_rate(df_raw, 1),
    'TEENNIE': extract_achievement_rate(df_raw, 2),
    'TGIL': extract_achievement_rate(df_raw, 3)
}

# Tính toán các chỉ số chính cho Tab 1
total_revenue = revenue_df['Total'].sum()
total_pbt = pbt_df['Total'].sum()
total_cogs = cogs_df['Total'].sum()
total_gross_profit = total_revenue - total_cogs
gross_margin_rate = (total_gross_profit / total_revenue * 100) if total_revenue > 0 else 0
overall_margin = (total_pbt / total_revenue * 100) if total_revenue > 0 else 0
avg_monthly_revenue = total_revenue / 10

# Dữ liệu từng công ty cho Tab 2 & General
company_data = []
for company in companies:
    rev = revenue_df[company].sum()
    pbt_val = pbt_df[company].sum()
    margin = (pbt_val / rev * 100) if rev > 0 else 0
    achieve_rates = revenue_achievement[company]
    avg_achieve = np.nanmean(achieve_rates)
    
    # Status logic
    if margin < 0:
        status = "CẦN CHÚ Ý NGAY"
        status_short = "NGHIÊM TRỌNG"
        status_class = "critical"
        icon = "🚨"
    elif margin > 20:
        status = "HOẠT ĐỘNG XUẤT SẮC"
        status_short = "XUẤT SẮC"
        status_class = "excellent"
        icon = "✅"
    else:
        status = "CẦN ỔN ĐỊNH"
        status_short = "TRUNG BÌNH"
        status_class = "average" # renamed from warning for CSS consistency
        icon = "⚠️"
        
    # Expense Ratios for Tab 3
    cogs = cogs_df[company].sum()
    selling = selling_exp_df[company].sum()
    admin = admin_exp_df[company].sum()
    other = other_exp_df[company].sum()
    
    expense_ratios = {
        'COGS': (cogs / rev * 100) if rev > 0 else 0,
        'Selling': (selling / rev * 100) if rev > 0 else 0,
        'Admin': (admin / rev * 100) if rev > 0 else 0,
        'Other': (other / rev * 100) if rev > 0 else 0
    }

    # CV Calculations for Tab 3
    def calc_cv(series):
        mean = series.mean()
        if mean == 0: return 0
        return (series.std() / mean) * 100

    cv_data = {
        'COGS': calc_cv(cogs_df[company]),
        'Selling': calc_cv(selling_exp_df[company]),
        'Admin': calc_cv(admin_exp_df[company]),
        'Other': calc_cv(other_exp_df[company])
    }

    # Monthly PBT data for Tab 2 Chart
    monthly_pbt = [pbt_df.loc[month, company] for month in months]
    cumulative_pbt = []
    cum_sum = 0
    for pbt_val in monthly_pbt:
        cum_sum += pbt_val
        cumulative_pbt.append(cum_sum)
    
    # Insights for Tab 2 Accordion
    if company == 'SAN':
        insight = f"- LN/DT {margin:.2f}%, không đạt kế hoạch doanh thu ({avg_achieve:.1f}%).<br>- Cơ cấu chi phí bán hàng, quản lý cao, ảnh hưởng mạnh đến lợi nhuận."
    elif company == 'TEENNIE':
        insight = f"- LN/DT {margin:.2f}%, đạt {avg_achieve:.1f}% kế hoạch.<br>- Tỷ suất khỏe, là đầu tàu lợi nhuận."
    else: # TGIL
        insight = f"- LN/DT {margin:.2f}%, nhưng chi phí biến động.<br>- Cần ổn định vận hành và kiểm soát chi phí."

    company_data.append({
        'id': company,
        'name': company_display_names[company],
        'full_name': company_full_names[company],
        'revenue': rev,
        'pbt': pbt_val,
        'margin': margin,
        'avg_achieve': avg_achieve,
        'status': status,
        'status_short': status_short,
        'status_class': status_class,
        'icon': icon,
        'expense_ratios': expense_ratios,
        'cv_data': cv_data,
        'monthly_pbt': monthly_pbt,
        'cumulative_pbt': cumulative_pbt,
        'insight': insight
    })

# Sắp xếp cho Tab 1 Ranking
company_data_sorted = sorted(company_data, key=lambda x: x['margin'], reverse=True)
best_company = company_data_sorted[0]

# Sức khỏe tập đoàn
has_negative = any(c['margin'] < 0 for c in company_data)
if has_negative:
    health_status = "⚠️ TRUNG BÌNH"
    health_subtitle = "SAN âm, TGIL biến động"
    health_class = "average"
else:
    health_status = "✅ TỐT"
    health_subtitle = "Tất cả công ty đều có lãi"
    health_class = "excellent"

# Tab 4: Action Plan Data
action_plans = {
    '0-30': {
        'SAN': [
            'Kiểm toán chi phí toàn diện & cắt giảm khẩn cấp',
            'Rà soát chi phí lab & hợp đồng nhà cung cấp',
            'Phân tích ROI marketing & cắt kênh kém hiệu quả',
            'Đánh giá năng suất & siết kiểm soát chi phí vận hành'
        ],
        'TEENNIE': [
            'Rà soát chi phí tăng đột biến Quý 2',
            'Chuẩn bị kế hoạch mở rộng'
        ],
        'TGIL': [
            'Phân tích nguyên nhân gốc rễ biến động chi phí',
            'Rà soát quản trị tồn kho & nhà cung cấp'
        ],
        'GROUP': [
            'Thương lượng lại hợp đồng cung cấp cho toàn tập đoàn',
            'Triển khai báo cáo quản lý hàng tháng'
        ]
    },
    '30-60': {
        'SAN': ['Khởi động các sáng kiến phục hồi doanh thu'],
        'TEENNIE': ['Xây dựng và phê duyệt kế hoạch mở rộng'],
        'TGIL': ['Triển khai quy trình phê duyệt chi phí', 'Tập trung mua hàng nếu có thể'],
        'GROUP': ['Triển khai quy trình phê duyệt chi phí tập đoàn']
    },
    '60-90': {
        'SAN': ['Đánh giá tiến độ chuyển hướng, đưa ra quyết định chiến lược'],
        'TEENNIE': ['Thực hiện đầu tư tăng trưởng'],
        'TGIL': ['Triển khai các biện pháp ổn định hoạt động'],
        'GROUP': ['Rà soát và đặt lại mục tiêu Quý 4 dựa trên bài học kinh nghiệm']
    }
}

# Prepare JSON for JS
js_company_data = json.dumps(company_data)
js_action_plans = json.dumps(action_plans)

# ============================================================================
# TẠO HTML MOBILE
# ============================================================================

html_content = f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <title>Báo Cáo Tài Chính - Mobile</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        :root {{
            --primary: #3A464E;
            --success: #27ae60;
            --warning: #f39c12;
            --danger: #FE3A45;
            --bg: #f5f5f5;
            --card-bg: #ffffff;
            --text: #333333;
            --text-light: #666666;
            --border: #e0e0e0;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            padding-bottom: 80px; /* Space for bottom nav */
            overflow-x: hidden;
        }}

        /* Utility Classes */
        .text-success {{ color: var(--success); }}
        .text-warning {{ color: var(--warning); }}
        .text-danger {{ color: var(--danger); }}
        .bg-success-light {{ background: #e8f5e9; color: var(--success); }}
        .bg-warning-light {{ background: #fff3e0; color: var(--warning); }}
        .bg-danger-light {{ background: #ffebee; color: var(--danger); }}
        
        /* Header */
        .header {{
            background: linear-gradient(135deg, var(--primary) 0%, #2c3e50 100%);
            color: white;
            padding: 20px 16px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .header h1 {{ font-size: 18px; font-weight: 700; margin-bottom: 4px; }}
        .header p {{ font-size: 12px; opacity: 0.9; }}

        /* Tab System */
        .tab-content {{ display: none; padding: 16px; animation: fadeIn 0.3s; }}
        .tab-content.active {{ display: block; }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}

        /* Cards */
        .card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}
        .card-title {{ font-size: 16px; font-weight: 700; margin-bottom: 12px; color: var(--primary); display: flex; justify-content: space-between; align-items: center; }}
        
        /* KPI Grid */
        .kpi-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; }}
        .kpi-card {{ background: white; border-radius: 12px; padding: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.05); display: flex; flex-direction: column; align-items: flex-start; }}
        .kpi-label {{ font-size: 11px; color: var(--text-light); margin-bottom: 4px; font-weight: 500; text-align: left; padding: 0; }}
        .kpi-value {{ font-size: 20px; font-weight: 700; color: var(--primary); line-height: 1.2; margin-bottom: 2px; }}
        .kpi-sub {{ font-size: 10px; color: var(--text-light); }}

        /* Ranking List */
        .ranking-item {{ display: flex; align-items: center; padding: 12px 0; border-bottom: 1px solid var(--border); }}
        .ranking-item:last-child {{ border-bottom: none; }}
        .ranking-icon {{ width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 18px; margin-right: 12px; flex-shrink: 0; }}
        .ranking-info {{ flex: 1; }}
        .ranking-name {{ font-weight: 700; font-size: 15px; }}
        .ranking-detail {{ font-size: 12px; color: var(--text-light); margin-top: 2px; }}
        .ranking-badge {{ font-size: 11px; font-weight: 600; padding: 4px 8px; border-radius: 12px; white-space: nowrap; }}

        /* Accordion */
        .accordion {{ background: white; border-radius: 12px; overflow: hidden; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.05); }}
        .accordion-header {{ padding: 16px; font-weight: 600; display: flex; justify-content: space-between; align-items: center; cursor: pointer; background: #fff; }}
        .accordion-content {{ padding: 0 16px 16px; display: none; font-size: 13px; line-height: 1.5; color: #555; border-top: 1px solid #f0f0f0; }}
        .accordion-content.open {{ display: block; }}
        .accordion-content ul {{ padding-left: 20px; margin-top: 8px; }}
        .accordion-content li {{ margin-bottom: 6px; }}

        /* Segmented Control */
        .segmented-control {{ display: flex; background: #e0e0e0; padding: 4px; border-radius: 8px; margin-bottom: 16px; }}
        .segment-btn {{ flex: 1; padding: 8px; border: none; background: transparent; border-radius: 6px; font-size: 13px; font-weight: 600; color: #666; cursor: pointer; transition: all 0.2s; }}
        .segment-btn.active {{ background: white; color: var(--primary); box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}

        /* Toggle Switch */
        .toggle-container {{ display: flex; justify-content: center; margin-bottom: 16px; }}
        .toggle-wrapper {{ display: flex; background: #e0e0e0; border-radius: 20px; padding: 3px; position: relative; }}
        .toggle-btn {{ padding: 6px 20px; border-radius: 18px; border: none; background: transparent; font-size: 13px; font-weight: 600; color: #666; z-index: 1; position: relative; cursor: pointer; transition: color 0.2s; }}
        .toggle-btn.active {{ color: var(--primary); }}
        .toggle-bg {{ position: absolute; top: 3px; bottom: 3px; left: 3px; width: 50%; background: white; border-radius: 18px; transition: transform 0.2s; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}

        /* Chips */
        .chips-container {{ display: flex; gap: 8px; margin-bottom: 16px; overflow-x: auto; padding-bottom: 4px; }}
        .chip {{ padding: 8px 16px; background: white; border: 1px solid var(--border); border-radius: 20px; font-size: 13px; font-weight: 500; color: #666; white-space: nowrap; cursor: pointer; transition: all 0.2s; }}
        .chip.active {{ background: var(--primary); color: white; border-color: var(--primary); }}

        /* Buttons */
        .btn {{ display: block; width: 100%; padding: 12px; border-radius: 8px; font-size: 14px; font-weight: 600; text-align: center; border: none; cursor: pointer; margin-bottom: 12px; transition: opacity 0.2s; }}
        .btn-primary {{ background: var(--primary); color: white; }}
        .btn-outline {{ background: transparent; border: 1px solid var(--border); color: var(--primary); }}
        .btn:active {{ opacity: 0.8; }}

        /* Action List */
        .action-item {{ padding: 12px 0; border-bottom: 1px dashed var(--border); display: flex; align-items: flex-start; }}
        .action-item:last-child {{ border-bottom: none; }}
        .action-check {{ margin-right: 10px; color: var(--success); font-weight: bold; }}

        /* Bottom Nav */
        .bottom-nav {{ position: fixed; bottom: 0; left: 0; right: 0; background: white; border-top: 1px solid var(--border); display: flex; justify-content: space-around; padding: 8px 0; padding-bottom: max(8px, env(safe-area-inset-bottom)); z-index: 1000; box-shadow: 0 -2px 10px rgba(0,0,0,0.05); }}
        .nav-item {{ flex: 1; display: flex; flex-direction: column; align-items: center; padding: 4px; cursor: pointer; color: #999; transition: color 0.2s; }}
        .nav-item.active {{ color: var(--primary); }}
        .nav-icon {{ font-size: 22px; margin-bottom: 2px; }}
        .nav-label {{ font-size: 10px; font-weight: 500; }}

    </style>
</head>
<body>
    <!-- Header -->
    <div class="header">
        <h1>📊 Báo Cáo Tài Chính</h1>
        <p>Tháng 1-10 2024 • S, T, I Group</p>
    </div>

    <!-- TAB 1: TỔNG QUAN -->
    <div id="tab-overview" class="tab-content active">
        <!-- KPI Grid -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Tổng Doanh Thu</div>
                <div class="kpi-value">{format_number(total_revenue)}</div>
                <div class="kpi-sub">~{format_number(avg_monthly_revenue)}/tháng</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Tổng LNTT</div>
                <div class="kpi-value">{format_number(total_pbt)}</div>
                <div class="kpi-sub">LN/DT: {overall_margin:.2f}%</div>
            </div>
            <div class="kpi-card bg-success-light" style="box-shadow: none; border: 1px solid #c8e6c9;">
                <div class="kpi-label text-success">Hoạt động tốt nhất</div>
                <div class="kpi-value text-success" style="font-size: 18px">{best_company['name']}</div>
                <div class="kpi-sub text-success">LN/DT {best_company['margin']:.1f}% ✅</div>
            </div>
            <div class="kpi-card bg-warning-light" style="box-shadow: none; border: 1px solid #ffe0b2;">
                <div class="kpi-label text-warning">Sức khỏe tập đoàn</div>
                <div class="kpi-value text-warning" style="font-size: 18px">{health_status}</div>
                <div class="kpi-sub text-warning">{health_subtitle}</div>
            </div>
        </div>

        <!-- Ranking -->
        <div class="card">
            <div class="card-title">Xem xét tổng quan</div>
            {"".join([f'''
            <div class="ranking-item">
                <div class="ranking-icon {c['status_class']}">
                    {c['icon']}
                </div>
                <div class="ranking-info">
                    <div class="ranking-name">{c['name']}</div>
                    <div class="ranking-detail">
                        Doanh thu: {format_number(c['revenue'])} • Lợi nhuận trước thuế: {format_number(c['pbt'])} ({c['margin']:.1f}%)
                    </div>
                </div>
                <div class="ranking-badge bg-{c['status_class']}-light text-{c['status_class']}">{c['status_short']}</div>
            </div>
            ''' for c in company_data])}
            <button class="btn btn-outline" onclick="switchTab('tab-company')" style="margin-top: 12px;">Xem chi tiết theo công ty →</button>
        </div>

        <!-- Chart -->
        <div class="card">
            <div class="card-title">Doanh thu và lợi nhuận theo tháng</div>
            <div id="chart-overview" style="height: 250px;"></div>
        </div>

        <!-- Accordion Insight -->
        <div class="accordion">
            <div class="accordion-header" onclick="toggleAccordion(this)">
                💡 Nhận xét <span style="font-size: 10px">▼</span>
            </div>
            <div class="accordion-content open">
                <ul>
                    <li><strong>{best_company['name']}</strong> dẫn đầu về doanh thu ({format_number(best_company['revenue'])}) & tỷ suất lợi nhuận ({best_company['margin']:.2f}%).</li>
                    <li><strong>{company_data[0]['name']}</strong> lỗ {format_number(abs(company_data[0]['pbt']))}, không đạt kế hoạch ({company_data[0]['avg_achieve']:.1f}%), LN/DT {company_data[0]['margin']:.2f}%.</li>
                    <li><strong>{company_data[2]['name']}</strong> biên lợi nhuận {company_data[2]['margin']:.2f}% nhưng chi phí biến động.</li>
                    <li>Tỷ suất lãi gộp toàn tập đoàn {gross_margin_rate:.2f}%, tổng doanh thu {format_number(total_revenue)}, tổng lợi nhuận {format_number(total_pbt)}.</li>
                </ul>
            </div>
        </div>
    </div>

    <!-- TAB 2: THEO CÔNG TY -->
    <div id="tab-company" class="tab-content">
        <!-- Company Switcher -->
        <div class="segmented-control">
            <button class="segment-btn active" onclick="switchCompany('SAN')">S</button>
            <button class="segment-btn" onclick="switchCompany('TEENNIE')">T</button>
            <button class="segment-btn" onclick="switchCompany('TGIL')">I</button>
        </div>

        <!-- KPI Grid Dynamic -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Doanh Thu (10T)</div>
                <div class="kpi-value" id="comp-revenue">...</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">LN lũy kế</div>
                <div class="kpi-value" id="comp-cumulative">...</div>
                <div class="kpi-sub" id="comp-margin">...</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">%KPI</div>
                <div class="kpi-value" id="comp-plan">...</div>
                <div class="kpi-sub" id="comp-plan-sub">...</div>
            </div>
            <div class="kpi-card" id="comp-status-card">
                <div class="kpi-label">Trạng thái</div>
                <div class="kpi-value" style="font-size: 16px;" id="comp-status">...</div>
            </div>
        </div>

        <!-- Mini Chart -->
        <div class="card" style="overflow: hidden; width: 100%;">
            <div class="card-title">Lợi nhuận luỹ kế</div>
            <div id="chart-company" style="height: 220px; width: 100%; max-width: 100%; box-sizing: border-box;"></div>
        </div>

        <!-- Current Situation -->
        <div class="accordion">
            <div class="accordion-header" onclick="toggleAccordion(this)">
                📌 Tình hình hiện tại <span style="font-size: 10px">▼</span>
            </div>
            <div class="accordion-content open" id="comp-insight">
                ...
            </div>
        </div>

        <!-- Action Buttons -->
        <button class="btn btn-outline" onclick="goToExpenseTab()">Xem chi tiết chi phí →</button>
        <button class="btn btn-primary" onclick="goToActionTab()">Xem việc cần làm 90 ngày →</button>
    </div>

    <!-- TAB 3: CHI PHÍ & BIẾN ĐỘNG -->
    <div id="tab-expense" class="tab-content">
        <!-- View Toggle -->
        <div class="toggle-container">
            <div class="toggle-wrapper">
                <div class="toggle-bg" id="expense-toggle-bg"></div>
                <button class="toggle-btn active" onclick="toggleExpenseView('ratio')">Tỷ lệ</button>
                <button class="toggle-btn" onclick="toggleExpenseView('cv')">Biến động</button>
            </div>
        </div>

        <!-- VIEW 1: RATIO -->
        <div id="view-ratio">
            <div class="segmented-control">
                <button class="segment-btn active" onclick="switchExpenseCompany('SAN')">S</button>
                <button class="segment-btn" onclick="switchExpenseCompany('TEENNIE')">T</button>
                <button class="segment-btn" onclick="switchExpenseCompany('TGIL')">I</button>
            </div>
            
            <div class="card">
                <div class="card-title">Cơ cấu chi phí (% Doanh thu)</div>
                <div id="chart-expense-ratio" style="height: 220px;"></div>
            </div>

            <div class="card bg-warning-light" style="border: 1px solid #ffe0b2; box-shadow: none;">
                <div class="card-title text-warning" style="font-size: 14px;">⚠️ Đánh giá</div>
                <div style="font-size: 13px; color: #555;" id="expense-insight">
                    ...
                </div>
            </div>
        </div>

        <!-- VIEW 2: CV -->
        <div id="view-cv" style="display: none;">
            <div class="card">
                <div class="card-title">Biến động chi phí (CV%)</div>
                <div style="font-size: 12px; color: #666; margin-bottom: 10px;">
                    Chỉ số càng cao = Càng không ổn định (Rủi ro)
                </div>
                <div id="chart-cv" style="height: 300px;"></div>
            </div>
            
            <div class="card">
                <div class="card-title">Phát hiện bất thường</div>
                <ul style="font-size: 13px; color: #555; padding-left: 20px; line-height: 1.6;">
                    <li><strong>I:</strong> Biến động giá vốn thấp nhất (ổn định).</li>
                    <li><strong>S & T:</strong> Chi phí khác biến động rất mạnh (>69%), cần kiểm soát các khoản chi bất thường.</li>
                    <li><strong>S:</strong> Chi phí bán hàng biến động cao ({company_data[0]['cv_data']['Selling']:.1f}%), cho thấy chi tiêu marketing chưa đều đặn.</li>
                </ul>
            </div>
        </div>
    </div>

    <!-- TAB 4: HÀNH ĐỘNG -->
    <div id="tab-action" class="tab-content">
        <!-- Time Filters -->
        <div class="chips-container">
            <div class="chip active" onclick="filterAction('0-30', this)">0-30 ngày</div>
            <div class="chip" onclick="filterAction('30-60', this)">30-60 ngày</div>
            <div class="chip" onclick="filterAction('60-90', this)">60-90 ngày</div>
        </div>

        <div style="margin-bottom: 16px; font-size: 13px; color: #666; font-style: italic;" id="action-subtitle">
            Ưu tiên khẩn cấp: Cắt giảm chi phí & Ổn định
        </div>

        <!-- Dynamic Accordions -->
        <div id="action-list">
            <!-- Injected by JS -->
        </div>

        <div style="margin-top: 24px;">
            <button class="btn btn-primary">📥 Tải kế hoạch (PDF)</button>
            <button class="btn btn-outline">Xem báo cáo chi tiết (Desktop)</button>
        </div>
    </div>

    <!-- Bottom Nav -->
    <div class="bottom-nav">
        <div class="nav-item active" onclick="switchTab('tab-overview')">
            <div class="nav-icon">📊</div>
            <div class="nav-label">Tổng quan</div>
        </div>
        <div class="nav-item" onclick="switchTab('tab-company')">
            <div class="nav-icon">🏢</div>
            <div class="nav-label">Doanh thu</div>
        </div>
        <div class="nav-item" onclick="switchTab('tab-expense')">
            <div class="nav-icon">💰</div>
            <div class="nav-label">Chi phí</div>
        </div>
        <div class="nav-item" onclick="switchTab('tab-action')">
            <div class="nav-icon">📋</div>
            <div class="nav-label">Hành động</div>
        </div>
    </div>

    <!-- DATA & LOGIC -->
    <script>
        const companyData = {js_company_data};
        const actionPlans = {js_action_plans};
        let currentCompanyId = 'SAN';
        let currentExpenseCompanyId = 'SAN';
        let currentTimeframe = '0-30';

        // --- INIT ---
        // Khởi tạo khi DOM ready
        document.addEventListener('DOMContentLoaded', () => {{
            renderOverviewChart();
            updateExpenseRatioChart('SAN');
            renderCVChart();
            renderActions('0-30');
            
            // Đợi một chút để đảm bảo layout đã render xong
            setTimeout(() => {{
                updateCompanyTab('SAN');
            }}, 150);
        }});

        // --- NAVIGATION ---
        function switchTab(tabId) {{
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            event.currentTarget.classList.add('active');
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
            
            // Nếu chuyển sang tab company, resize biểu đồ sau khi tab được hiển thị
            if (tabId === 'tab-company') {{
                setTimeout(() => {{
                    Plotly.Plots.resize('chart-company');
                }}, 200);
            }}
        }}

        function goToExpenseTab() {{
            switchTab('tab-expense');
            // Simulate click on nav item
            document.querySelectorAll('.nav-item')[2].classList.add('active');
            document.querySelectorAll('.nav-item')[1].classList.remove('active');
        }}

        function goToActionTab() {{
            switchTab('tab-action');
            document.querySelectorAll('.nav-item')[3].classList.add('active');
            document.querySelectorAll('.nav-item')[1].classList.remove('active');
        }}

        // --- TAB 2: COMPANY ---
        function switchCompany(compId) {{
            currentCompanyId = compId;
            updateCompanyTab(compId);
            
            // Update active state of buttons
            document.querySelectorAll('#tab-company .segment-btn').forEach(btn => {{
                btn.classList.remove('active');
                if(btn.textContent === (compId === 'SAN' ? 'S' : compId === 'TEENNIE' ? 'T' : 'I')) 
                    btn.classList.add('active');
            }});
            
            // Resize biểu đồ sau khi chuyển công ty
            setTimeout(() => {{
                Plotly.Plots.resize('chart-company');
            }}, 100);
        }}

        function updateCompanyTab(compId) {{
            const data = companyData.find(c => c.id === compId);
            if (!data) return;

            // KPI
            document.getElementById('comp-revenue').textContent = formatNumber(data.revenue);
            // Lợi nhuận luỹ kế (tháng 10, index 9)
            const cumulativeValue = data.cumulative_pbt[9];
            document.getElementById('comp-cumulative').textContent = formatNumber(cumulativeValue);
            document.getElementById('comp-margin').textContent = `LN/DT: ${{data.margin.toFixed(2)}}%`;
            
            document.getElementById('comp-plan').textContent = `${{data.avg_achieve.toFixed(1)}}%`;
            document.getElementById('comp-plan-sub').textContent = data.avg_achieve >= 100 ? '✅ Vượt mục tiêu' : data.avg_achieve < 90 ? '⚠️ Dưới mục tiêu' : '➡️ Đạt mục tiêu';
            
            const statusEl = document.getElementById('comp-status');
            const statusCard = document.getElementById('comp-status-card');
            statusEl.textContent = data.status;
            
            // Styling status card
            statusCard.className = 'kpi-card'; // reset
            if (data.status_class === 'critical') statusCard.classList.add('bg-danger-light', 'text-danger');
            else if (data.status_class === 'excellent') statusCard.classList.add('bg-success-light', 'text-success');
            else statusCard.classList.add('bg-warning-light', 'text-warning');

            // Insight (dùng innerHTML để hiển thị <br>)
            document.getElementById('comp-insight').innerHTML = data.insight;

            // Chart: Lợi nhuận luỹ kế của công ty đang chọn
            const months = {json.dumps(months)};
            const chartColor = data.status_class === 'critical' ? '#FE3A45' : data.status_class === 'excellent' ? '#27ae60' : '#f39c12';
            
            // Tính toán min/max cho yaxis với padding
            const allValues = [...data.monthly_pbt, ...data.cumulative_pbt];
            const dataMin = Math.min(...allValues);
            const dataMax = Math.max(...allValues);
            const range = dataMax - dataMin;
            
            // Thêm padding 15% cho phần dương và âm
            let yMin = dataMin - (range * 0.15);
            let yMax = dataMax + (range * 0.15);
            
            // Đảm bảo có khoảng trống tối thiểu nếu dữ liệu quá nhỏ
            if (Math.abs(dataMin) < 1 && Math.abs(dataMax) < 1) {{
                yMin = Math.min(yMin, -1);
                yMax = Math.max(yMax, 1);
            }}
            
            // Trace 1: Cột lợi nhuận hàng tháng
            const traceBar = {{
                x: months,
                y: data.monthly_pbt,
                type: 'bar',
                name: 'Lợi nhuận hàng tháng',
                marker: {{ 
                    color: chartColor,
                    opacity: 0.7,
                    line: {{ color: 'white', width: 0.5 }}
                }}
            }};
            
            // Trace 2: Đường lợi nhuận luỹ kế
            const traceLine = {{
                x: months,
                y: data.cumulative_pbt,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Lợi nhuận luỹ kế',
                line: {{ 
                    color: chartColor,
                    width: 3
                }},
                marker: {{
                    size: 6,
                    color: chartColor
                }}
            }};
            
            const layout = {{
                margin: {{ t: 10, b: 40, l: 45, r: 10 }},
                xaxis: {{ 
                    title: '',
                    tickangle: -45,
                    tickfont: {{ size: 9 }},
                    fixedrange: true
                }},
                yaxis: {{
                    title: 'Lợi nhuận (M)',
                    titlefont: {{ size: 10 }},
                    tickfont: {{ size: 9 }},
                    zeroline: true,
                    zerolinecolor: '#999',
                    zerolinewidth: 1,
                    range: [yMin, yMax],
                    fixedrange: true
                }},
                legend: {{
                    orientation: 'h',
                    y: -0.2,
                    x: 0.5,
                    xanchor: 'center',
                    font: {{ size: 9 }}
                }},
                height: 220,
                hovermode: 'x unified',
                autosize: true
            }};
            
            Plotly.newPlot('chart-company', [traceBar, traceLine], layout, {{staticPlot: false, responsive: true, displayModeBar: false}});
        }}

        // --- TAB 3: EXPENSE ---
        function toggleExpenseView(view) {{
            const bg = document.getElementById('expense-toggle-bg');
            const btns = document.querySelectorAll('.toggle-btn');
            
            if (view === 'ratio') {{
                document.getElementById('view-ratio').style.display = 'block';
                document.getElementById('view-cv').style.display = 'none';
                bg.style.transform = 'translateX(0)';
                btns[0].classList.add('active');
                btns[1].classList.remove('active');
            }} else {{
                document.getElementById('view-ratio').style.display = 'none';
                document.getElementById('view-cv').style.display = 'block';
                bg.style.transform = 'translateX(100%)';
                btns[0].classList.remove('active');
                btns[1].classList.add('active');
                renderCVChart(); // Render when shown
            }}
        }}

        function switchExpenseCompany(compId) {{
            currentExpenseCompanyId = compId;
            updateExpenseRatioChart(compId);
            
            // Update buttons
            document.querySelectorAll('#view-ratio .segment-btn').forEach(btn => {{
                btn.classList.remove('active');
                if(btn.textContent === (compId === 'SAN' ? 'S' : compId === 'TEENNIE' ? 'T' : 'I')) 
                    btn.classList.add('active');
            }});
        }}

        function updateExpenseRatioChart(compId) {{
            const data = companyData.find(c => c.id === compId);
            const ratios = data.expense_ratios;
            
            const xValues = [ratios.COGS, ratios.Selling, ratios.Admin, ratios.Other];
            const yValues = ['Giá vốn', 'Bán hàng', 'Quản lý', 'Khác'];
            
            const trace = {{
                x: xValues,
                y: yValues,
                type: 'bar',
                orientation: 'h',
                text: xValues.map(v => v.toFixed(1) + '%'),
                textposition: 'auto',
                marker: {{ color: '#3A464E', opacity: 0.8 }}
            }};

            const layout = {{
                margin: {{ t: 10, b: 20, l: 80, r: 20 }},
                xaxis: {{ range: [0, 100], title: '% Doanh thu' }},
                height: 220
            }};
            
            Plotly.newPlot('chart-expense-ratio', [trace], layout, {{staticPlot: true, responsive: true}});

            // Update Insight
            const insightEl = document.getElementById('expense-insight');
            if (compId === 'SAN') {{
                insightEl.innerHTML = '• Tỷ lệ CP Quản lý (42.6%) và Bán hàng (29.6%) quá cao, bóp nghẹt lợi nhuận.<br>• Giá vốn chiếm 30.5%, mức trung bình.';
            }} else if (compId === 'TEENNIE') {{
                insightEl.innerHTML = '• Giá vốn rất thấp (7.9%), giúp biên lợi nhuận gộp cao.<br>• Quản lý tốt các chi phí vận hành.';
            }} else {{
                insightEl.innerHTML = '• Các chỉ số ở mức trung bình.<br>• Cần chú ý biến động giá vốn trong các tháng tới.';
            }}
        }}

        function renderCVChart() {{
            // Data preparation
            const categories = ['Giá vốn', 'Bán hàng', 'Quản lý', 'Khác'];
            const companies = ['SAN', 'TEENNIE', 'TGIL'];
            const colors = ['#FE3A45', '#27ae60', '#f39c12']; // S=Red, T=Green, I=Orange
            
            const traces = companies.map((compId, idx) => {{
                const data = companyData.find(c => c.id === compId).cv_data;
                return {{
                    x: categories,
                    y: [data.COGS, data.Selling, data.Admin, data.Other],
                    name: compId === 'SAN' ? 'S' : compId === 'TEENNIE' ? 'T' : 'I',
                    type: 'bar',
                    marker: {{ color: colors[idx] }}
                }};
            }});

            const layout = {{
                barmode: 'group',
                margin: {{ t: 10, b: 40, l: 40, r: 10 }},
                yaxis: {{ title: 'CV % (Biến động)' }},
                legend: {{ orientation: 'h', y: -0.2 }},
                height: 300
            }};

            Plotly.newPlot('chart-cv', traces, layout, {{staticPlot: false, responsive: true, displayModeBar: false}});
        }}

        // --- TAB 4: ACTION ---
        function filterAction(timeframe, btn) {{
            currentTimeframe = timeframe;
            renderActions(timeframe);
            
            // Update chips
            document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');

            const sub = document.getElementById('action-subtitle');
            if(timeframe === '0-30') sub.textContent = 'Ưu tiên khẩn cấp: Cắt giảm chi phí & Ổn định';
            else if(timeframe === '30-60') sub.textContent = 'Triển khai các sáng kiến tăng trưởng & Quy trình';
            else sub.textContent = 'Chiến lược dài hạn & Đầu tư';
        }}

        function renderActions(timeframe) {{
            const container = document.getElementById('action-list');
            container.innerHTML = '';
            
            const plans = actionPlans[timeframe];
            const order = ['SAN', 'TEENNIE', 'TGIL', 'GROUP'];
            const names = {{'SAN': 'S - Cần chú ý', 'TEENNIE': 'T', 'TGIL': 'I', 'GROUP': 'Cấp Tập Đoàn'}};
            
            order.forEach(key => {{
                const items = plans[key];
                if (!items || items.length === 0) return;
                
                const isOpen = (timeframe === '0-30' && key === 'SAN') ? 'open' : '';
                
                let html = `
                <div class="accordion">
                    <div class="accordion-header" onclick="toggleAccordion(this)">
                        ${{names[key]}} <span style="font-size: 10px">▼</span>
                    </div>
                    <div class="accordion-content ${{isOpen}}">
                `;
                
                items.forEach(action => {{
                    html += `
                    <div class="action-item">
                        <span class="action-check">☐</span>
                        <span>${{action}}</span>
                    </div>`;
                }});
                
                html += `</div></div>`;
                container.insertAdjacentHTML('beforeend', html);
            }});
        }}

        // --- HELPERS ---
        function renderOverviewChart() {{
            // Dữ liệu doanh thu và lợi nhuận theo tháng
            const months = {json.dumps(['T01', 'T02', 'T03', 'T04', 'T05', 'T06', 'T07', 'T08', 'T09', 'T10'])};
            const revenueData = {json.dumps([revenue_df.loc[month, 'Total'] for month in months])};
            const pbtData = {json.dumps([pbt_df.loc[month, 'Total'] for month in months])};
            
            // Trace 1: Doanh thu (Cột)
            const traceRevenue = {{
                x: months,
                y: revenueData,
                type: 'bar',
                name: 'Doanh thu',
                marker: {{ color: '#3A464E', opacity: 0.8 }},
                text: revenueData.map(v => formatNumber(v)),
                textposition: 'outside',
                textfont: {{ size: 10 }},
                yaxis: 'y'
            }};
            
            // Trace 2: Lợi nhuận (Đường)
            const tracePBT = {{
                x: months,
                y: pbtData,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Lợi nhuận trước thuế',
                line: {{ color: '#FE3A45', width: 3 }},
                marker: {{ size: 8, color: '#FE3A45' }},
                yaxis: 'y2'
            }};
            
            const layout = {{
                margin: {{ t: 20, b: 40, l: 50, r: 50 }},
                xaxis: {{ 
                    title: '',
                    tickangle: -45
                }},
                yaxis: {{
                    title: 'Doanh thu (M)',
                    side: 'left',
                    titlefont: {{ color: '#3A464E', size: 11 }},
                    tickfont: {{ color: '#3A464E', size: 10 }}
                }},
                yaxis2: {{
                    title: 'Lợi nhuận (M)',
                    side: 'right',
                    overlaying: 'y',
                    titlefont: {{ color: '#FE3A45', size: 11 }},
                    tickfont: {{ color: '#FE3A45', size: 10 }}
                }},
                showlegend: false,
                height: 250,
                barmode: 'group'
            }};
            
            Plotly.newPlot('chart-overview', [traceRevenue, tracePBT], layout, {{staticPlot: false, responsive: true, displayModeBar: false}});
        }}

        function formatNumber(num) {{
            return new Intl.NumberFormat('vi-VN').format(Math.round(num)) + ' M';
        }}

        function toggleAccordion(header) {{
            const content = header.nextElementSibling;
            content.classList.toggle('open');
            const icon = header.querySelector('span');
            icon.textContent = content.classList.contains('open') ? '▼' : '▶';
        }}
    </script>
</body>
</html>
"""

# Ghi file HTML
output_file = '/Users/lucasbraci/Desktop/S Group/report_mobile.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print("=" * 80)
print("✅ BÁO CÁO MOBILE FULL TABS ĐÃ ĐƯỢC TẠO THÀNH CÔNG!")
print("=" * 80)
print(f"\nFile được lưu tại: {output_file}")
