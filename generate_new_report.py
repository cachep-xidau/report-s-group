"""
Tạo Báo Cáo Tình Hình Kinh Doanh YTD - Tập Đoàn S Group
Báo cáo mới hoàn toàn với cấu trúc rõ ràng
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# ============================================================================
# HÀM TIỆN ÍCH
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
    if pd.isna(value):
        return "-"
    return f"{value:,.0f} M".replace(',', '.')

def get_month_column(df, month_name):
    """Lấy tên cột đúng cho tháng"""
    col_with_space = f' {month_name} '
    col_no_space = month_name
    if col_with_space in df.columns:
        return col_with_space
    elif col_no_space in df.columns:
        return col_no_space
    else:
        return month_name

def calc_quarter(df, row_idx, quarter):
    """Tính tổng theo quý"""
    if quarter == 'Q1':
        month_names = ['T01', 'T02', 'T03']
    elif quarter == 'Q2':
        month_names = ['T04', 'T05', 'T06']
    elif quarter == 'Q3':
        month_names = ['T07', 'T08', 'T09']
    elif quarter == 'Q4':
        month_names = ['T10', 'T11', 'T12']
    else:
        return np.nan
    
    total = 0
    for m_name in month_names:
        col = get_month_column(df, m_name)
        val = clean_currency_value(df.iloc[row_idx].get(col, np.nan))
        if not pd.isna(val):
            total += val
    return total

# ============================================================================
# ĐỌC DỮ LIỆU
# ============================================================================

# Đọc file 2024
df_2024 = pd.read_csv('/Users/lucasbraci/Desktop/S Group/Phan tich 2024.csv')
df_2024.columns = df_2024.columns.str.strip()

# Đọc file 2025
df_2025 = pd.read_csv('/Users/lucasbraci/Desktop/S Group/Phan tich 2025.csv')
df_2025.columns = df_2025.columns.str.strip()

# Tên cột - một số có khoảng trắng, một số không
def get_month_columns(df):
    """Lấy danh sách tên cột cho các tháng"""
    months = []
    for m in ['T01', 'T02', 'T03', 'T04', 'T05', 'T06', 'T07', 'T08', 'T09', 'T10']:
        col_with_space = f' {m} '
        col_no_space = m
        if col_with_space in df.columns:
            months.append(col_with_space)
        elif col_no_space in df.columns:
            months.append(col_no_space)
        else:
            months.append(m)
    return months

months_ytd_2024 = get_month_columns(df_2024)
months_ytd_2025 = get_month_columns(df_2025)

# Row indices trong CSV (index bắt đầu từ 0)
# Row 0 (index 0): DOANH THU THUẦN TỪ BÁN HÀNG (Total)
# Row 18 (index 18): LÃI GỘP (Total) - cần kiểm tra lại
# Row 124 (index 124): LỢI NHUẬN KẾ TOÁN TRƯỚC THUẾ (Total) - cần kiểm tra lại

# Tìm đúng dòng bằng cách tìm theo tên
def find_row_by_name(df, name_pattern):
    for i in range(len(df)):
        name = str(df.iloc[i].get('CHỈ TIÊU BÁO CÁO', '')).strip()
        if name_pattern in name:
            return i
    return None

revenue_row_2024 = find_row_by_name(df_2024, 'DOANH THU THUẦN TỪ BÁN HÀNG')
revenue_row_2025 = find_row_by_name(df_2025, 'DOANH THU THUẦN TỪ BÁN HÀNG')
gross_profit_row_2024 = find_row_by_name(df_2024, 'LÃI GỘP')
gross_profit_row_2025 = find_row_by_name(df_2025, 'LÃI GỘP')
pbt_row_2024 = find_row_by_name(df_2024, 'LỢI NHUẬN KẾ TOÁN TRƯỚC THUẾ')
pbt_row_2025 = find_row_by_name(df_2025, 'LỢI NHUẬN KẾ TOÁN TRƯỚC THUẾ')

# Tính toán YTD 10T
revenue_2024_ytd = sum([clean_currency_value(df_2024.iloc[revenue_row_2024].get(m, np.nan)) for m in months_ytd_2024])
revenue_2025_ytd = sum([clean_currency_value(df_2025.iloc[revenue_row_2025].get(m, np.nan)) for m in months_ytd_2025])
gross_profit_2024_ytd = sum([clean_currency_value(df_2024.iloc[gross_profit_row_2024].get(m, np.nan)) for m in months_ytd_2024])
gross_profit_2025_ytd = sum([clean_currency_value(df_2025.iloc[gross_profit_row_2025].get(m, np.nan)) for m in months_ytd_2025])
pbt_2024_ytd = sum([clean_currency_value(df_2024.iloc[pbt_row_2024].get(m, np.nan)) for m in months_ytd_2024])
pbt_2025_ytd = sum([clean_currency_value(df_2025.iloc[pbt_row_2025].get(m, np.nan)) for m in months_ytd_2025])

# Tính toán theo quý
quarters = ['Q1', 'Q2', 'Q3', 'Q4']
revenue_2024_q = {q: calc_quarter(df_2024, revenue_row_2024, q) for q in quarters}
revenue_2025_q = {q: calc_quarter(df_2025, revenue_row_2025, q) for q in quarters}
pbt_2024_q = {q: calc_quarter(df_2024, pbt_row_2024, q) for q in quarters}
pbt_2025_q = {q: calc_quarter(df_2025, pbt_row_2025, q) for q in quarters}

# Đọc kế hoạch từ file 2025
# Cột "Kế hoạch" cho Q1, "Kế hoạch.1" cho Q2, "Kế hoạch.2" cho Q3
revenue_plan_q = {}
pbt_plan_q = {}
for q_idx, q in enumerate(['Q1', 'Q2', 'Q3']):
    if q_idx == 0:
        col_name = 'Kế hoạch'
    elif q_idx == 1:
        col_name = 'Kế hoạch.1'
    else:
        col_name = 'Kế hoạch.2'
    
    revenue_plan_q[q] = clean_currency_value(df_2025.iloc[revenue_row_2025].get(col_name, np.nan))
    pbt_plan_q[q] = clean_currency_value(df_2025.iloc[pbt_row_2025].get(col_name, np.nan))

# Tính % hoàn thành kế hoạch
revenue_achieve_q = {}
pbt_achieve_q = {}
for q in ['Q1', 'Q2', 'Q3']:
    if revenue_plan_q[q] and revenue_plan_q[q] != 0:
        revenue_achieve_q[q] = (revenue_2025_q[q] / revenue_plan_q[q] * 100) if not pd.isna(revenue_2025_q[q]) else 0
    else:
        revenue_achieve_q[q] = 0
    
    if pbt_plan_q[q] and pbt_plan_q[q] != 0:
        pbt_achieve_q[q] = (pbt_2025_q[q] / pbt_plan_q[q] * 100) if not pd.isna(pbt_2025_q[q]) else 0
    else:
        pbt_achieve_q[q] = 0

# Tính trung bình % hoàn thành
avg_revenue_achieve = np.mean([revenue_achieve_q[q] for q in ['Q1', 'Q2', 'Q3']])
avg_pbt_achieve = np.mean([pbt_achieve_q[q] for q in ['Q1', 'Q2', 'Q3']])

# Tính toán các chỉ số
revenue_change_pct = ((revenue_2025_ytd - revenue_2024_ytd) / revenue_2024_ytd * 100) if revenue_2024_ytd != 0 else 0
pbt_multiple = (pbt_2025_ytd / pbt_2024_ytd) if pbt_2024_ytd != 0 else 0
gross_margin_2024 = (gross_profit_2024_ytd / revenue_2024_ytd * 100) if revenue_2024_ytd != 0 else 0
gross_margin_2025 = (gross_profit_2025_ytd / revenue_2025_ytd * 100) if revenue_2025_ytd != 0 else 0
pbt_margin_2024 = (pbt_2024_ytd / revenue_2024_ytd * 100) if revenue_2024_ytd != 0 else 0
pbt_margin_2025 = (pbt_2025_ytd / revenue_2025_ytd * 100) if revenue_2025_ytd != 0 else 0

# ============================================================================
# DỮ LIỆU THEO TỪNG CÔNG TY (S/T/I)
# ============================================================================

# Row indices cho từng công ty (theo cấu trúc CSV)
metrics_rows = {
    'Revenue': {'Total': 0, 'SAN': 1, 'TEENNIE': 2, 'TGIL': 3},
    'COGS': {'Total': 4, 'SAN': 5, 'TEENNIE': 9, 'TGIL': 13},
    'Gross Profit': {'Total': 17, 'SAN': 18, 'TEENNIE': 19, 'TGIL': 20},
    'Selling Expenses': {'Total': 33, 'SAN': 34, 'TEENNIE': 46, 'TGIL': 58},
    'Admin Expenses': {'Total': 74, 'SAN': 75, 'TEENNIE': 86, 'TGIL': 97},
    'Other Expenses': {'Total': 108, 'SAN': 109, 'TEENNIE': 113, 'TGIL': 117},
    'Profit Before Tax': {'Total': 123, 'SAN': 124, 'TEENNIE': 125, 'TGIL': 126},
}

# Tính YTD cho từng công ty
companies = ['SAN', 'TEENNIE', 'TGIL']
company_data = {}

for company in companies:
    # Doanh thu
    rev_row_2024 = metrics_rows['Revenue'][company]
    rev_row_2025 = metrics_rows['Revenue'][company]
    revenue_2024_company = sum([clean_currency_value(df_2024.iloc[rev_row_2024].get(m, np.nan)) for m in months_ytd_2024])
    revenue_2025_company = sum([clean_currency_value(df_2025.iloc[rev_row_2025].get(m, np.nan)) for m in months_ytd_2025])
    
    # Lợi nhuận gộp
    gp_row_2025 = metrics_rows['Gross Profit'][company]
    gross_profit_2025_company = sum([clean_currency_value(df_2025.iloc[gp_row_2025].get(m, np.nan)) for m in months_ytd_2025])
    
    # LNTT
    pbt_row_2024 = metrics_rows['Profit Before Tax'][company]
    pbt_row_2025 = metrics_rows['Profit Before Tax'][company]
    pbt_2024_company = sum([clean_currency_value(df_2024.iloc[pbt_row_2024].get(m, np.nan)) for m in months_ytd_2024])
    pbt_2025_company = sum([clean_currency_value(df_2025.iloc[pbt_row_2025].get(m, np.nan)) for m in months_ytd_2025])
    
    # Chi phí
    cogs_row_2025 = metrics_rows['COGS'][company]
    selling_row_2025 = metrics_rows['Selling Expenses'][company]
    admin_row_2025 = metrics_rows['Admin Expenses'][company]
    other_row_2025 = metrics_rows['Other Expenses'][company]
    
    cogs_2025_company = sum([clean_currency_value(df_2025.iloc[cogs_row_2025].get(m, np.nan)) for m in months_ytd_2025])
    selling_2025_company = sum([clean_currency_value(df_2025.iloc[selling_row_2025].get(m, np.nan)) for m in months_ytd_2025])
    admin_2025_company = sum([clean_currency_value(df_2025.iloc[admin_row_2025].get(m, np.nan)) for m in months_ytd_2025])
    other_2025_company = sum([clean_currency_value(df_2025.iloc[other_row_2025].get(m, np.nan)) for m in months_ytd_2025])
    
    # Tính % YoY
    revenue_yoy = ((revenue_2025_company - revenue_2024_company) / revenue_2024_company * 100) if revenue_2024_company != 0 else 0
    
    # Tính biên LNTT
    pbt_margin_company = (pbt_2025_company / revenue_2025_company * 100) if revenue_2025_company != 0 else 0
    
    # Tính % KH LNTT (trung bình Q1-Q3)
    pbt_plan_company = {}
    pbt_achieve_company = []
    for q_idx, q in enumerate(['Q1', 'Q2', 'Q3']):
        if q_idx == 0:
            col_name = 'Kế hoạch'
        elif q_idx == 1:
            col_name = 'Kế hoạch.1'
        else:
            col_name = 'Kế hoạch.2'
        pbt_plan_val = clean_currency_value(df_2025.iloc[pbt_row_2025].get(col_name, np.nan))
        pbt_actual_val = calc_quarter(df_2025, pbt_row_2025, q)
        if pbt_plan_val and pbt_plan_val != 0 and not pd.isna(pbt_actual_val):
            pbt_achieve_company.append(pbt_actual_val / pbt_plan_val * 100)
    avg_pbt_achieve_company = np.mean(pbt_achieve_company) if pbt_achieve_company else 0
    
    company_data[company] = {
        'revenue_2024': revenue_2024_company,
        'revenue_2025': revenue_2025_company,
        'revenue_yoy': revenue_yoy,
        'gross_profit_2025': gross_profit_2025_company,
        'pbt_2025': pbt_2025_company,
        'pbt_margin': pbt_margin_company,
        'pbt_achieve': avg_pbt_achieve_company,
        'cogs': cogs_2025_company,
        'selling': selling_2025_company,
        'admin': admin_2025_company,
        'other': other_2025_company,
    }

# Tính % đóng góp LNTT
total_pbt_2025 = sum([company_data[c]['pbt_2025'] for c in companies])
for company in companies:
    company_data[company]['pbt_contribution'] = (company_data[company]['pbt_2025'] / total_pbt_2025 * 100) if total_pbt_2025 != 0 else 0

# ============================================================================
# TẠO BIỂU ĐỒ
# ============================================================================

# Chart 1: Doanh thu & LNTT theo quý (2024 vs 2025)
fig1 = make_subplots(specs=[[{"secondary_y": True}]])

# Cột doanh thu
fig1.add_trace(
    go.Bar(
        name='Doanh thu 2024',
        x=['Q1', 'Q2', 'Q3', 'Q4'],
        y=[revenue_2024_q['Q1'], revenue_2024_q['Q2'], revenue_2024_q['Q3'], revenue_2024_q['Q4']],
        marker_color='#E5E6E5',
        text=[format_number(v) for v in [revenue_2024_q['Q1'], revenue_2024_q['Q2'], revenue_2024_q['Q3'], revenue_2024_q['Q4']]],
        textposition='outside'
    ),
    secondary_y=False
)

fig1.add_trace(
    go.Bar(
        name='Doanh thu 2025',
        x=['Q1', 'Q2', 'Q3', 'Q4'],
        y=[revenue_2025_q['Q1'], revenue_2025_q['Q2'], revenue_2025_q['Q3'], revenue_2025_q['Q4'] if not pd.isna(revenue_2025_q['Q4']) else 0],
        marker_color='#3A464E',
        text=[format_number(v) if not pd.isna(v) else '-' for v in [revenue_2025_q['Q1'], revenue_2025_q['Q2'], revenue_2025_q['Q3'], revenue_2025_q['Q4']]],
        textposition='outside'
    ),
    secondary_y=False
)

# Đường LNTT (giá trị tuyệt đối)
fig1.add_trace(
    go.Scatter(
        name='LNTT 2024',
        x=['Q1', 'Q2', 'Q3', 'Q4'],
        y=[pbt_2024_q['Q1'], pbt_2024_q['Q2'], pbt_2024_q['Q3'], pbt_2024_q['Q4']],
        mode='lines+markers',
        line=dict(color='#FE3A45', width=2, dash='dot'),
        marker=dict(size=8),
        text=[format_number(v) for v in [pbt_2024_q['Q1'], pbt_2024_q['Q2'], pbt_2024_q['Q3'], pbt_2024_q['Q4']]],
        textposition='top center'
    ),
    secondary_y=True
)

fig1.add_trace(
    go.Scatter(
        name='LNTT 2025',
        x=['Q1', 'Q2', 'Q3', 'Q4'],
        y=[pbt_2025_q['Q1'], pbt_2025_q['Q2'], pbt_2025_q['Q3'], pbt_2025_q['Q4'] if not pd.isna(pbt_2025_q['Q4']) else 0],
        mode='lines+markers',
        line=dict(color='#2E7D32', width=2),
        marker=dict(size=8),
        text=[format_number(v) if not pd.isna(v) else '-' for v in [pbt_2025_q['Q1'], pbt_2025_q['Q2'], pbt_2025_q['Q3'], pbt_2025_q['Q4']]],
        textposition='top center'
    ),
    secondary_y=True
)

fig1.update_xaxes(title_text="Quý")
fig1.update_yaxes(title_text="Doanh thu (M)", secondary_y=False)
fig1.update_yaxes(title_text="LNTT (M)", secondary_y=True)

fig1.update_layout(
    title='<b>Doanh thu & Biên LNTT theo quý (2024 vs 2025)</b>',
    barmode='group',
    height=500,
    template='plotly_white',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

# Chart 2: Thực tế vs Kế hoạch theo quý (Q1-Q3)
fig2 = go.Figure()

# Doanh thu Actual
fig2.add_trace(go.Bar(
    name='Doanh thu Actual',
    x=['Q1', 'Q2', 'Q3'],
    y=[revenue_2025_q['Q1'], revenue_2025_q['Q2'], revenue_2025_q['Q3']],
    marker_color='#3A464E',
    text=[format_number(v) for v in [revenue_2025_q['Q1'], revenue_2025_q['Q2'], revenue_2025_q['Q3']]],
    textposition='outside'
))

# Doanh thu Plan
fig2.add_trace(go.Bar(
    name='Doanh thu Plan',
    x=['Q1', 'Q2', 'Q3'],
    y=[revenue_plan_q['Q1'], revenue_plan_q['Q2'], revenue_plan_q['Q3']],
    marker_color='#E5E6E5',
    text=[format_number(v) for v in [revenue_plan_q['Q1'], revenue_plan_q['Q2'], revenue_plan_q['Q3']]],
    textposition='outside'
))

fig2.update_layout(
    title='<b>Thực tế vs Kế hoạch theo quý (Q1-Q3)</b>',
    barmode='group',
    height=400,
    template='plotly_white',
    xaxis_title='Quý',
    yaxis_title='Doanh thu (M)',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

# Chart 3: Đóng góp doanh thu & LNTT theo công ty
fig3 = go.Figure()

fig3.add_trace(go.Bar(
    name='Doanh thu YTD',
    x=['S', 'T', 'I'],
    y=[company_data['SAN']['revenue_2025'], company_data['TEENNIE']['revenue_2025'], company_data['TGIL']['revenue_2025']],
    marker_color='#3A464E',
    text=[format_number(company_data['SAN']['revenue_2025']), format_number(company_data['TEENNIE']['revenue_2025']), format_number(company_data['TGIL']['revenue_2025'])],
    textposition='outside'
))

fig3.add_trace(go.Bar(
    name='LNTT YTD',
    x=['S', 'T', 'I'],
    y=[company_data['SAN']['pbt_2025'], company_data['TEENNIE']['pbt_2025'], company_data['TGIL']['pbt_2025']],
    marker_color='#2E7D32',
    text=[format_number(company_data['SAN']['pbt_2025']), format_number(company_data['TEENNIE']['pbt_2025']), format_number(company_data['TGIL']['pbt_2025'])],
    textposition='outside'
))

fig3.update_layout(
    title='<b>Đóng góp doanh thu & LNTT theo công ty</b>',
    barmode='group',
    height=400,
    template='plotly_white',
    xaxis_title='Công ty',
    yaxis_title='Giá trị (M)',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

# Chart 4: Scatter Growth vs Margin
fig4 = go.Figure()

colors_company = {'SAN': '#FE3A45', 'TEENNIE': '#2E7D32', 'TGIL': '#FFA500'}
labels_company = {'SAN': 'S', 'TEENNIE': 'T', 'TGIL': 'I'}

for company in companies:
    fig4.add_trace(go.Scatter(
        x=[company_data[company]['revenue_yoy']],
        y=[company_data[company]['pbt_margin']],
        mode='markers+text',
        name=labels_company[company],
        marker=dict(size=15, color=colors_company[company]),
        text=[labels_company[company]],
        textposition='top center',
        textfont=dict(size=14, color=colors_company[company], family='Arial Black')
    ))

fig4.update_layout(
    title='<b>Tăng trưởng & biên lợi nhuận (Growth vs Margin)</b>',
    height=500,
    template='plotly_white',
    xaxis_title='% tăng trưởng doanh thu YTD',
    yaxis_title='Biên LNTT (%)',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

# Chart 5: Stacked bar 100% cho cơ cấu chi phí
fig5 = go.Figure()

# Tính % trên doanh thu cho từng công ty
for company, label in zip(companies, ['S', 'T', 'I']):
    revenue = company_data[company]['revenue_2025']
    cogs_pct = (company_data[company]['cogs'] / revenue * 100) if revenue != 0 else 0
    selling_pct = (company_data[company]['selling'] / revenue * 100) if revenue != 0 else 0
    admin_pct = (company_data[company]['admin'] / revenue * 100) if revenue != 0 else 0
    other_pct = (company_data[company]['other'] / revenue * 100) if revenue != 0 else 0
    
    fig5.add_trace(go.Bar(
        name=label,
        x=[label],
        y=[cogs_pct],
        marker_color='#8A9BA8',
        legendgroup='cogs',
        showlegend=(company == 'SAN')
    ))
    
    fig5.add_trace(go.Bar(
        name=label,
        x=[label],
        y=[selling_pct],
        marker_color='#C8CDD1',
        legendgroup='selling',
        showlegend=(company == 'SAN'),
        base=[cogs_pct]
    ))
    
    fig5.add_trace(go.Bar(
        name=label,
        x=[label],
        y=[admin_pct],
        marker_color='#E5E6E5',
        legendgroup='admin',
        showlegend=(company == 'SAN'),
        base=[cogs_pct + selling_pct]
    ))
    
    fig5.add_trace(go.Bar(
        name=label,
        x=[label],
        y=[other_pct],
        marker_color='#FE3A45',
        legendgroup='other',
        showlegend=(company == 'SAN'),
        base=[cogs_pct + selling_pct + admin_pct]
    ))

fig5.update_layout(
    title='<b>Cơ cấu chi phí (% trên doanh thu)</b>',
    barmode='stack',
    height=400,
    template='plotly_white',
    xaxis_title='Công ty',
    yaxis_title='% trên doanh thu',
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        tracegroupgap=5
    )
)

# Chart 6-9: Waterfall charts (Total, S, T, I)
def create_waterfall_chart(company_name, company_label, data):
    """Tạo waterfall chart cho một công ty"""
    revenue = data['revenue_2025']
    cogs = data['cogs']
    selling = data['selling']
    admin = data['admin']
    other = data['other']
    pbt = data['pbt_2025']
    
    fig = go.Figure()
    
    # Doanh thu (start)
    fig.add_trace(go.Waterfall(
        orientation="v",
        measure=["absolute"],
        x=["Doanh thu"],
        textposition="outside",
        text=[format_number(revenue)],
        y=[revenue],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "#3A464E"}},
        decreasing={"marker": {"color": "rgba(254, 58, 69, 0.3)"}},
    ))
    
    # Giá vốn
    fig.add_trace(go.Waterfall(
        orientation="v",
        measure=["relative"],
        x=["Giá vốn"],
        textposition="outside",
        text=[format_number(cogs)],
        y=[-cogs],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "#3A464E"}},
        decreasing={"marker": {"color": "rgba(254, 58, 69, 0.3)"}},
    ))
    
    # CPBH
    fig.add_trace(go.Waterfall(
        orientation="v",
        measure=["relative"],
        x=["CPBH"],
        textposition="outside",
        text=[format_number(selling)],
        y=[-selling],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "#3A464E"}},
        decreasing={"marker": {"color": "rgba(254, 58, 69, 0.3)"}},
    ))
    
    # QLDN
    fig.add_trace(go.Waterfall(
        orientation="v",
        measure=["relative"],
        x=["QLDN"],
        textposition="outside",
        text=[format_number(admin)],
        y=[-admin],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "#3A464E"}},
        decreasing={"marker": {"color": "rgba(254, 58, 69, 0.3)"}},
    ))
    
    # Chi phí khác
    fig.add_trace(go.Waterfall(
        orientation="v",
        measure=["relative"],
        x=["Chi phí khác"],
        textposition="outside",
        text=[format_number(other)],
        y=[-other],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "#3A464E"}},
        decreasing={"marker": {"color": "rgba(254, 58, 69, 0.3)"}},
    ))
    
    # LNTT (final)
    profit_color = "rgba(46, 125, 50, 1)" if pbt >= 0 else "rgba(254, 58, 69, 0.8)"
    fig.add_trace(go.Waterfall(
        orientation="v",
        measure=["total"],
        x=["LNTT"],
        textposition="outside",
        text=[format_number(pbt)],
        y=[pbt],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": profit_color}},
        decreasing={"marker": {"color": profit_color}},
    ))
    
    fig.update_layout(
        title=f'<b>Waterfall: {company_label}</b>',
        height=400,
        template='plotly_white',
        xaxis_title='',
        yaxis_title='Giá trị (M)',
        showlegend=False
    )
    
    return fig

# Tính dữ liệu Total
total_cogs = sum([company_data[c]['cogs'] for c in companies])
total_selling = sum([company_data[c]['selling'] for c in companies])
total_admin = sum([company_data[c]['admin'] for c in companies])
total_other = sum([company_data[c]['other'] for c in companies])

total_data = {
    'revenue_2025': revenue_2025_ytd,
    'cogs': total_cogs,
    'selling': total_selling,
    'admin': total_admin,
    'other': total_other,
    'pbt_2025': pbt_2025_ytd,
}

fig6 = create_waterfall_chart('Total', 'Toàn tập đoàn', total_data)
fig7 = create_waterfall_chart('SAN', 'Công ty S', company_data['SAN'])
fig8 = create_waterfall_chart('TEENNIE', 'Công ty T', company_data['TEENNIE'])
fig9 = create_waterfall_chart('TGIL', 'Công ty I', company_data['TGIL'])

# ============================================================================
# TẠO HTML
# ============================================================================

html_content = f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Báo Cáo Tình Hình Kinh Doanh YTD - S Group</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Arial', 'Helvetica', sans-serif;
            font-size: 14px;
            line-height: 1.4;
            color: #333;
            background: #f5f5f5;
        }}
        
        p, li {{
            line-height: 1.4;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: white;
        }}
        
        /* Cover & Header */
        .cover {{
            text-align: center;
            padding: 60px 20px;
            background: linear-gradient(135deg, #3A464E 0%, #2c3e50 100%);
            color: white;
            margin: -20px -20px 40px -20px;
        }}
        
        .cover h1 {{
            font-size: 38px;
            margin-bottom: 20px;
            font-weight: bold;
            line-height: 1.15;
        }}
        
        .cover .subtitle {{
            font-size: 16px;
            margin-bottom: 30px;
            opacity: 0.9;
            line-height: 1.3;
        }}
        
        .cover .info {{
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 30px;
            font-size: 13px;
        }}
        
        /* KPI Cards */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        .kpi-card {{
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 25px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .kpi-card .label {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 10px;
        }}
        
        .kpi-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #3A464E;
            margin-bottom: 8px;
        }}
        
        .kpi-card .change {{
            font-size: 0.9em;
            color: #2E7D32;
        }}
        
        .kpi-card .change.negative {{
            color: #FE3A45;
        }}
        
        /* Section */
        .section {{
            margin: 40px 0;
            padding: 30px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .section h2 {{
            font-size: 26px;
            color: #3A464E;
            margin-bottom: 20px;
            border-bottom: 3px solid #3A464E;
            padding-bottom: 10px;
            line-height: 1.25;
        }}
        
        .section h3 {{
            font-size: 20px;
            color: #3A464E;
            margin: 30px 0 15px 0;
            line-height: 1.3;
        }}
        
        /* Table */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        table th {{
            background: #3A464E;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }}
        
        table td {{
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        table tr:hover {{
            background: #f9f9f9;
        }}
        
        table td:last-child {{
            text-align: right;
        }}
        
        /* Bullet points */
        .bullet-list {{
            list-style: none;
            padding-left: 0;
        }}
        
        .bullet-list li {{
            padding: 10px 0 10px 25px;
            position: relative;
            font-size: 1.1em;
            line-height: 1.3;
        }}
        
        .bullet-list li:before {{
            content: "•";
            position: absolute;
            left: 0;
            color: #3A464E;
            font-size: 1.5em;
        }}
        
        /* Chart container */
        .chart-container {{
            margin: 30px 0;
        }}
        
        /* Summary text */
        .summary-text {{
            background: #f8f9fa;
            padding: 20px;
            border-left: 4px solid #3A464E;
            margin: 20px 0;
            font-size: 1em;
            line-height: 1.5;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Cover & Header -->
        <div class="cover">
            <h1>BÁO CÁO TÌNH HÌNH KINH DOANH YTD</h1>
            <h2 style="font-size: 1.6em; margin-top: 10px;">TẬP ĐOÀN S Group</h2>
            <div class="subtitle">
                Kỳ: Tháng 01 – Tháng 10/2025<br>
                (so sánh với cùng kỳ 2024 & kế hoạch)
            </div>
            <div class="info">
                <div><strong>Người trình bày:</strong> Nguyễn Thanh Hiền</div>
                <div><strong>Ngày họp:</strong> 01/12/2025</div>
            </div>
        </div>
        
        <!-- 1. Executive Summary -->
        <div class="section">
            <h2>1. Executive Summary (Key highlights)</h2>
            
            <!-- 1.1. KPI Cards -->
            <h3>1.1. Các chỉ số KPI chính</h3>
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="label">Doanh thu YTD 10T 2025</div>
                    <div class="value">{format_number(revenue_2025_ytd)}</div>
                    <div class="change {'negative' if revenue_change_pct < 0 else ''}">
                        ({'+' if revenue_change_pct >= 0 else ''}{revenue_change_pct:.1f}% so với YTD 2024)
                    </div>
                </div>
                
                <div class="kpi-card">
                    <div class="label">Lợi nhuận trước thuế YTD 10T 2025</div>
                    <div class="value">{format_number(pbt_2025_ytd)}</div>
                    <div class="change">
                        (≈ x{pbt_multiple:.1f} lần YTD 2024)
                    </div>
                </div>
                
                <div class="kpi-card">
                    <div class="label">Biên LNTT YTD 2025</div>
                    <div class="value">{pbt_margin_2025:.1f}%</div>
                    <div class="change">
                        (so với {pbt_margin_2024:.1f}% YTD 2024)
                    </div>
                </div>
                
                <div class="kpi-card">
                    <div class="label">% hoàn thành kế hoạch doanh thu (Q1-Q3)</div>
                    <div class="value">{avg_revenue_achieve:.0f}%</div>
                </div>
                
                <div class="kpi-card">
                    <div class="label">% hoàn thành kế hoạch LNTT (Q1-Q3)</div>
                    <div class="value">{avg_pbt_achieve:.0f}%</div>
                </div>
            </div>
            
            <!-- 1.2. Bullet points -->
            <h3>1.2. Kết luận nhanh</h3>
            <ul class="bullet-list">
                <li>Doanh thu tăng hai chữ số, lợi nhuận tăng đa bội, biên lợi nhuận cải thiện rõ rệt.</li>
                <li>TEENNIE & TGIL là động lực chính về tăng trưởng lợi nhuận; SAN đang suy giảm và kéo thấp tổng biên.</li>
                <li>So với kế hoạch 2025, doanh thu bám tương đối, nhưng lợi nhuận còn thấp xa kế hoạch do mix & chi phí.</li>
            </ul>
        </div>
        
        <!-- 2. Kết quả tài chính YTD -->
        <div class="section">
            <h2>2. Kết quả tài chính YTD</h2>
            
            <!-- 2.1. Bảng tổng hợp -->
            <h3>2.1. Bảng tổng hợp</h3>
            <table>
                <thead>
                    <tr>
                        <th>Chỉ tiêu</th>
                        <th style="text-align: right;">YTD 10T 2024</th>
                        <th style="text-align: right;">YTD 10T 2025</th>
                        <th style="text-align: right;">% thay đổi</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Doanh thu thuần</strong></td>
                        <td style="text-align: right;">{format_number(revenue_2024_ytd)}</td>
                        <td style="text-align: right;">{format_number(revenue_2025_ytd)}</td>
                        <td style="text-align: right;">{revenue_change_pct:+.1f}%</td>
                    </tr>
                    <tr>
                        <td><strong>Lợi nhuận gộp</strong></td>
                        <td style="text-align: right;">{format_number(gross_profit_2024_ytd)}</td>
                        <td style="text-align: right;">{format_number(gross_profit_2025_ytd)}</td>
                        <td style="text-align: right;">{((gross_profit_2025_ytd - gross_profit_2024_ytd) / gross_profit_2024_ytd * 100) if gross_profit_2024_ytd != 0 else 0:+.1f}%</td>
                    </tr>
                    <tr>
                        <td><strong>Lợi nhuận trước thuế</strong></td>
                        <td style="text-align: right;">{format_number(pbt_2024_ytd)}</td>
                        <td style="text-align: right;">{format_number(pbt_2025_ytd)}</td>
                        <td style="text-align: right;">{((pbt_2025_ytd - pbt_2024_ytd) / pbt_2024_ytd * 100) if pbt_2024_ytd != 0 else 0:+.1f}%</td>
                    </tr>
                    <tr>
                        <td><strong>Biên lợi nhuận gộp (%)</strong></td>
                        <td style="text-align: right;">{gross_margin_2024:.1f}%</td>
                        <td style="text-align: right;">{gross_margin_2025:.1f}%</td>
                        <td style="text-align: right;">{(gross_margin_2025 - gross_margin_2024):+.1f} pp</td>
                    </tr>
                    <tr>
                        <td><strong>Biên LNTT (%)</strong></td>
                        <td style="text-align: right;">{pbt_margin_2024:.1f}%</td>
                        <td style="text-align: right;">{pbt_margin_2025:.1f}%</td>
                        <td style="text-align: right;">{(pbt_margin_2025 - pbt_margin_2024):+.1f} pp</td>
                    </tr>
                </tbody>
            </table>
            
            <!-- 2.2. Biểu đồ -->
            <h3>2.2. Biểu đồ</h3>
            
            <div class="chart-container">
                <div id="chart1"></div>
            </div>
            
            <div class="chart-container">
                <div id="chart2"></div>
                <div class="summary-text">
                    <strong>YTD doanh thu đạt ~{avg_revenue_achieve:.0f}% kế hoạch; LNTT đạt ~{avg_pbt_achieve:.0f}% kế hoạch.</strong>
                </div>
            </div>
        </div>
        
        <!-- Phần 3: Hiệu suất theo công ty -->
        <div class="section">
            <h2>3. Hiệu suất theo công ty (S / T / I)</h2>
            
            <h3>3.1. Bảng tóm tắt S/T/I</h3>
            <table>
                <thead>
                    <tr>
                        <th>Công ty</th>
                        <th>Doanh thu YTD 2025</th>
                        <th>% YoY</th>
                        <th>LNTT YTD 2025</th>
                        <th>Biên LNTT</th>
                        <th>% KH LNTT</th>
                        <th>Nhận xét</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>S</strong></td>
                        <td>{format_number(company_data['SAN']['revenue_2025'])}</td>
                        <td>{company_data['SAN']['revenue_yoy']:.1f}%</td>
                        <td>{format_number(company_data['SAN']['pbt_2025'])}</td>
                        <td>{company_data['SAN']['pbt_margin']:.1f}%</td>
                        <td>{company_data['SAN']['pbt_achieve']:.0f}%</td>
                        <td>Hiệu suất kém</td>
                    </tr>
                    <tr>
                        <td><strong>T</strong></td>
                        <td>{format_number(company_data['TEENNIE']['revenue_2025'])}</td>
                        <td>{company_data['TEENNIE']['revenue_yoy']:.1f}%</td>
                        <td>{format_number(company_data['TEENNIE']['pbt_2025'])}</td>
                        <td>{company_data['TEENNIE']['pbt_margin']:.1f}%</td>
                        <td>{company_data['TEENNIE']['pbt_achieve']:.0f}%</td>
                        <td>Tăng trưởng tốt, lợi nhuận cao</td>
                    </tr>
                    <tr>
                        <td><strong>I</strong></td>
                        <td>{format_number(company_data['TGIL']['revenue_2025'])}</td>
                        <td>{company_data['TGIL']['revenue_yoy']:.1f}%</td>
                        <td>{format_number(company_data['TGIL']['pbt_2025'])}</td>
                        <td>{company_data['TGIL']['pbt_margin']:.1f}%</td>
                        <td>{company_data['TGIL']['pbt_achieve']:.0f}%</td>
                        <td>Ổn định, đang tạo đà phát triển 2026</td>
                    </tr>
                </tbody>
            </table>
            
            <h3>3.2. Biểu đồ</h3>
            <div class="chart-container">
                <div id="chart3"></div>
            </div>
            
            <div class="chart-container">
                <div id="chart4"></div>
            </div>
            
            <div class="summary-text">
                <ul class="bullet-list">
                    <li>TEENNIE là đầu tàu tăng trưởng & lợi nhuận, đóng góp {company_data['TEENNIE']['pbt_contribution']:.0f}% LNTT tập đoàn.</li>
                    <li>TGIL là case ổn định tích cực, từ lỗ nhẹ năm trước sang biên lợi nhuận ~{company_data['TGIL']['pbt_margin']:.0f}%.</li>
                    <li>SAN là điểm nghẽn, doanh thu giảm ~{abs(company_data['SAN']['revenue_yoy']):.0f}%, lỗ ~{abs(company_data['SAN']['pbt_margin']):.0f}% → trọng tâm tái cấu trúc.</li>
                </ul>
            </div>
        </div>
        
        <!-- Phần 4: Cơ cấu chi phí & biên lợi nhuận -->
        <div class="section">
            <h2>4. Cơ cấu chi phí & biên lợi nhuận</h2>
            
            <h3>4.1. Bảng cơ cấu chi phí (% trên doanh thu)</h3>
            <table>
                <thead>
                    <tr>
                        <th>Chỉ tiêu</th>
                        <th>S</th>
                        <th>T</th>
                        <th>I</th>
                        <th>Toàn tập đoàn</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Giá vốn / Doanh thu</td>
                        <td>{(company_data['SAN']['cogs'] / company_data['SAN']['revenue_2025'] * 100) if company_data['SAN']['revenue_2025'] != 0 else 0:.1f}%</td>
                        <td>{(company_data['TEENNIE']['cogs'] / company_data['TEENNIE']['revenue_2025'] * 100) if company_data['TEENNIE']['revenue_2025'] != 0 else 0:.1f}%</td>
                        <td>{(company_data['TGIL']['cogs'] / company_data['TGIL']['revenue_2025'] * 100) if company_data['TGIL']['revenue_2025'] != 0 else 0:.1f}%</td>
                        <td>{(total_cogs / revenue_2025_ytd * 100) if revenue_2025_ytd != 0 else 0:.1f}%</td>
                    </tr>
                    <tr>
                        <td>CP bán hàng / DT</td>
                        <td>{(company_data['SAN']['selling'] / company_data['SAN']['revenue_2025'] * 100) if company_data['SAN']['revenue_2025'] != 0 else 0:.1f}%</td>
                        <td>{(company_data['TEENNIE']['selling'] / company_data['TEENNIE']['revenue_2025'] * 100) if company_data['TEENNIE']['revenue_2025'] != 0 else 0:.1f}%</td>
                        <td>{(company_data['TGIL']['selling'] / company_data['TGIL']['revenue_2025'] * 100) if company_data['TGIL']['revenue_2025'] != 0 else 0:.1f}%</td>
                        <td>{(total_selling / revenue_2025_ytd * 100) if revenue_2025_ytd != 0 else 0:.1f}%</td>
                    </tr>
                    <tr>
                        <td>CP QLDN / DT</td>
                        <td>{(company_data['SAN']['admin'] / company_data['SAN']['revenue_2025'] * 100) if company_data['SAN']['revenue_2025'] != 0 else 0:.1f}%</td>
                        <td>{(company_data['TEENNIE']['admin'] / company_data['TEENNIE']['revenue_2025'] * 100) if company_data['TEENNIE']['revenue_2025'] != 0 else 0:.1f}%</td>
                        <td>{(company_data['TGIL']['admin'] / company_data['TGIL']['revenue_2025'] * 100) if company_data['TGIL']['revenue_2025'] != 0 else 0:.1f}%</td>
                        <td>{(total_admin / revenue_2025_ytd * 100) if revenue_2025_ytd != 0 else 0:.1f}%</td>
                    </tr>
                    <tr>
                        <td>Chi phí khác / DT</td>
                        <td>{(company_data['SAN']['other'] / company_data['SAN']['revenue_2025'] * 100) if company_data['SAN']['revenue_2025'] != 0 else 0:.1f}%</td>
                        <td>{(company_data['TEENNIE']['other'] / company_data['TEENNIE']['revenue_2025'] * 100) if company_data['TEENNIE']['revenue_2025'] != 0 else 0:.1f}%</td>
                        <td>{(company_data['TGIL']['other'] / company_data['TGIL']['revenue_2025'] * 100) if company_data['TGIL']['revenue_2025'] != 0 else 0:.1f}%</td>
                        <td>{(total_other / revenue_2025_ytd * 100) if revenue_2025_ytd != 0 else 0:.1f}%</td>
                    </tr>
                    <tr>
                        <td>Lợi nhuận gộp / DT</td>
                        <td>{(company_data['SAN']['gross_profit_2025'] / company_data['SAN']['revenue_2025'] * 100) if company_data['SAN']['revenue_2025'] != 0 else 0:.1f}%</td>
                        <td>{(company_data['TEENNIE']['gross_profit_2025'] / company_data['TEENNIE']['revenue_2025'] * 100) if company_data['TEENNIE']['revenue_2025'] != 0 else 0:.1f}%</td>
                        <td>{(company_data['TGIL']['gross_profit_2025'] / company_data['TGIL']['revenue_2025'] * 100) if company_data['TGIL']['revenue_2025'] != 0 else 0:.1f}%</td>
                        <td>{(gross_profit_2025_ytd / revenue_2025_ytd * 100) if revenue_2025_ytd != 0 else 0:.1f}%</td>
                    </tr>
                    <tr>
                        <td>LNTT / DT</td>
                        <td>{company_data['SAN']['pbt_margin']:.1f}%</td>
                        <td>{company_data['TEENNIE']['pbt_margin']:.1f}%</td>
                        <td>{company_data['TGIL']['pbt_margin']:.1f}%</td>
                        <td>{pbt_margin_2025:.1f}%</td>
                    </tr>
                </tbody>
            </table>
            
            <h3>4.2. Biểu đồ</h3>
            <div class="chart-container">
                <div id="chart5"></div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin: 30px 0;">
                <div class="chart-container">
                    <div id="chart6"></div>
                </div>
                <div class="chart-container">
                    <div id="chart7"></div>
                </div>
                <div class="chart-container">
                    <div id="chart8"></div>
                </div>
                <div class="chart-container">
                    <div id="chart9"></div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>5. Rủi ro & biến động (volatility)</h2>
            <p style="color: #666; font-style: italic;">Nội dung sẽ được bổ sung...</p>
        </div>
        
        <div class="section">
            <h2>6. Chiến lược & định hướng 12–18 tháng</h2>
            <p style="color: #666; font-style: italic;">Nội dung sẽ được bổ sung...</p>
        </div>
    </div>
    
    <script>
        // Render Chart 1
        var chart1Data = {fig1.to_json()};
        Plotly.newPlot('chart1', chart1Data.data, chart1Data.layout, {{responsive: true}});
        
        // Render Chart 2
        var chart2Data = {fig2.to_json()};
        Plotly.newPlot('chart2', chart2Data.data, chart2Data.layout, {{responsive: true}});
        
        // Render Chart 3
        var chart3Data = {fig3.to_json()};
        Plotly.newPlot('chart3', chart3Data.data, chart3Data.layout, {{responsive: true}});
        
        // Render Chart 4
        var chart4Data = {fig4.to_json()};
        Plotly.newPlot('chart4', chart4Data.data, chart4Data.layout, {{responsive: true}});
        
        // Render Chart 5
        var chart5Data = {fig5.to_json()};
        Plotly.newPlot('chart5', chart5Data.data, chart5Data.layout, {{responsive: true}});
        
        // Render Chart 6-9 (Waterfall)
        var chart6Data = {fig6.to_json()};
        Plotly.newPlot('chart6', chart6Data.data, chart6Data.layout, {{responsive: true}});
        
        var chart7Data = {fig7.to_json()};
        Plotly.newPlot('chart7', chart7Data.data, chart7Data.layout, {{responsive: true}});
        
        var chart8Data = {fig8.to_json()};
        Plotly.newPlot('chart8', chart8Data.data, chart8Data.layout, {{responsive: true}});
        
        var chart9Data = {fig9.to_json()};
        Plotly.newPlot('chart9', chart9Data.data, chart9Data.layout, {{responsive: true}});
    </script>
</body>
</html>
"""

# Ghi file HTML
output_file = '/Users/lucasbraci/Desktop/S Group/report_web.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print("✅ BÁO CÁO ĐÃ ĐƯỢC TẠO THÀNH CÔNG!")
print(f"📄 File: {output_file}")

