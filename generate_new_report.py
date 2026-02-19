"""
Generate YTD Business Performance Report - S Group
Full report with clear structure
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from string import Template
from pathlib import Path

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def clean_currency_value(value):
    """Convert Vietnamese number format to float"""
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
    """Format number with dot separator and add M"""
    if pd.isna(value):
        return "-"
    return f"{value:,.0f} M".replace(',', '.')

def get_month_column(df, month_name):
    """Get correct column name for month"""
    col_with_space = f' {month_name} '
    col_no_space = month_name
    if col_with_space in df.columns:
        return col_with_space
    elif col_no_space in df.columns:
        return col_no_space
    else:
        return month_name

def calc_quarter(df, row_idx, quarter):
    """Calculate total by quarter"""
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
# READ DATA
# ============================================================================

# Read 2024 file
df_2024 = pd.read_csv('/Users/lucasbraci/Desktop/S Group/Phan tich 2024.csv')
df_2024.columns = df_2024.columns.str.strip()

# Read 2025 file
df_2025 = pd.read_csv('/Users/lucasbraci/Desktop/S Group/Phan tich 2025.csv')
df_2025.columns = df_2025.columns.str.strip()

# Column names - some with spaces, some without
def get_month_columns(df):
    """Get list of column names for months"""
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

# Row indices in CSV (index starts from 0)
# Row 0 (index 0): NET REVENUE FROM SALES (Total)
# Row 18 (index 18): GROSS PROFIT (Total) - need to verify
# Row 124 (index 124): PROFIT BEFORE TAX (Total) - need to verify

# Find correct row by name pattern
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

# Calculate YTD 10M
revenue_2024_ytd = sum([clean_currency_value(df_2024.iloc[revenue_row_2024].get(m, np.nan)) for m in months_ytd_2024])
revenue_2025_ytd = sum([clean_currency_value(df_2025.iloc[revenue_row_2025].get(m, np.nan)) for m in months_ytd_2025])
gross_profit_2024_ytd = sum([clean_currency_value(df_2024.iloc[gross_profit_row_2024].get(m, np.nan)) for m in months_ytd_2024])
gross_profit_2025_ytd = sum([clean_currency_value(df_2025.iloc[gross_profit_row_2025].get(m, np.nan)) for m in months_ytd_2025])
pbt_2024_ytd = sum([clean_currency_value(df_2024.iloc[pbt_row_2024].get(m, np.nan)) for m in months_ytd_2024])
pbt_2025_ytd = sum([clean_currency_value(df_2025.iloc[pbt_row_2025].get(m, np.nan)) for m in months_ytd_2025])

# Calculate full year 2024 (12 months)
months_2024_full = get_month_columns(df_2024)
if len(months_2024_full) < 12:
    # If less than 12 months, add remaining months
    for m in ['T11', 'T12']:
        col_with_space = f' {m} '
        col_no_space = m
        if col_with_space in df_2024.columns:
            months_2024_full.append(col_with_space)
        elif col_no_space in df_2024.columns:
            months_2024_full.append(col_no_space)
        else:
            months_2024_full.append(m)

revenue_2024_full = sum([clean_currency_value(df_2024.iloc[revenue_row_2024].get(m, np.nan)) for m in months_2024_full if m in df_2024.columns or f' {m} ' in df_2024.columns])
gross_profit_2024_full = sum([clean_currency_value(df_2024.iloc[gross_profit_row_2024].get(m, np.nan)) for m in months_2024_full if m in df_2024.columns or f' {m} ' in df_2024.columns])
pbt_2024_full = sum([clean_currency_value(df_2024.iloc[pbt_row_2024].get(m, np.nan)) for m in months_2024_full if m in df_2024.columns or f' {m} ' in df_2024.columns])

# Calculate by quarter
quarters = ['Q1', 'Q2', 'Q3', 'Q4']
revenue_2024_q = {q: calc_quarter(df_2024, revenue_row_2024, q) for q in quarters}
revenue_2025_q = {q: calc_quarter(df_2025, revenue_row_2025, q) for q in quarters}
pbt_2024_q = {q: calc_quarter(df_2024, pbt_row_2024, q) for q in quarters}
pbt_2025_q = {q: calc_quarter(df_2025, pbt_row_2025, q) for q in quarters}

# Read plan from 2025 file
# Column "Kế hoạch" for Q1, "Kế hoạch.1" for Q2, "Kế hoạch.2" for Q3
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

# Calculate % plan completion
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

# Calculate average % completion
avg_revenue_achieve = np.mean([revenue_achieve_q[q] for q in ['Q1', 'Q2', 'Q3']])
avg_pbt_achieve = np.mean([pbt_achieve_q[q] for q in ['Q1', 'Q2', 'Q3']])

# Calculate metrics
revenue_change_pct = ((revenue_2025_ytd - revenue_2024_ytd) / revenue_2024_ytd * 100) if revenue_2024_ytd != 0 else 0
pbt_multiple = (pbt_2025_ytd / pbt_2024_ytd) if pbt_2024_ytd != 0 else 0
gross_margin_2024 = (gross_profit_2024_ytd / revenue_2024_ytd * 100) if revenue_2024_ytd != 0 else 0
gross_margin_2025 = (gross_profit_2025_ytd / revenue_2025_ytd * 100) if revenue_2025_ytd != 0 else 0
pbt_margin_2024 = (pbt_2024_ytd / revenue_2024_ytd * 100) if revenue_2024_ytd != 0 else 0
pbt_margin_2025 = (pbt_2025_ytd / revenue_2025_ytd * 100) if revenue_2025_ytd != 0 else 0

# ============================================================================
# DATA BY COMPANY (S/T/I)
# ============================================================================

# Row indices per company (per CSV structure)
metrics_rows = {
    'Revenue': {'Total': 0, 'SAN': 1, 'TEENNIE': 2, 'TGIL': 3},
    'COGS': {'Total': 4, 'SAN': 5, 'TEENNIE': 9, 'TGIL': 13},
    'Gross Profit': {'Total': 17, 'SAN': 18, 'TEENNIE': 19, 'TGIL': 20},
    'Selling Expenses': {'Total': 33, 'SAN': 34, 'TEENNIE': 46, 'TGIL': 58},
    'Admin Expenses': {'Total': 74, 'SAN': 75, 'TEENNIE': 86, 'TGIL': 97},
    'Other Expenses': {'Total': 108, 'SAN': 109, 'TEENNIE': 113, 'TGIL': 117},
    'Profit Before Tax': {'Total': 123, 'SAN': 124, 'TEENNIE': 125, 'TGIL': 126},
}

# Calculate YTD per company
companies = ['SAN', 'TEENNIE', 'TGIL']
company_data = {}

for company in companies:
    # Revenue
    rev_row_2024 = metrics_rows['Revenue'][company]
    rev_row_2025 = metrics_rows['Revenue'][company]
    revenue_2024_company = sum([clean_currency_value(df_2024.iloc[rev_row_2024].get(m, np.nan)) for m in months_ytd_2024])
    revenue_2025_company = sum([clean_currency_value(df_2025.iloc[rev_row_2025].get(m, np.nan)) for m in months_ytd_2025])
    
    # Gross profit
    gp_row_2025 = metrics_rows['Gross Profit'][company]
    gross_profit_2025_company = sum([clean_currency_value(df_2025.iloc[gp_row_2025].get(m, np.nan)) for m in months_ytd_2025])
    
    # PBT
    pbt_row_2024 = metrics_rows['Profit Before Tax'][company]
    pbt_row_2025 = metrics_rows['Profit Before Tax'][company]
    pbt_2024_company = sum([clean_currency_value(df_2024.iloc[pbt_row_2024].get(m, np.nan)) for m in months_ytd_2024])
    pbt_2025_company = sum([clean_currency_value(df_2025.iloc[pbt_row_2025].get(m, np.nan)) for m in months_ytd_2025])
    
    # Expenses
    cogs_row_2025 = metrics_rows['COGS'][company]
    selling_row_2025 = metrics_rows['Selling Expenses'][company]
    admin_row_2025 = metrics_rows['Admin Expenses'][company]
    other_row_2025 = metrics_rows['Other Expenses'][company]
    
    cogs_2025_company = sum([clean_currency_value(df_2025.iloc[cogs_row_2025].get(m, np.nan)) for m in months_ytd_2025])
    selling_2025_company = sum([clean_currency_value(df_2025.iloc[selling_row_2025].get(m, np.nan)) for m in months_ytd_2025])
    admin_2025_company = sum([clean_currency_value(df_2025.iloc[admin_row_2025].get(m, np.nan)) for m in months_ytd_2025])
    other_2025_company = sum([clean_currency_value(df_2025.iloc[other_row_2025].get(m, np.nan)) for m in months_ytd_2025])
    
    # Calculate % YoY
    revenue_yoy = ((revenue_2025_company - revenue_2024_company) / revenue_2024_company * 100) if revenue_2024_company != 0 else 0
    
    # Calculate pre-tax margin
    pbt_margin_company = (pbt_2025_company / revenue_2025_company * 100) if revenue_2025_company != 0 else 0
    
    # Calculate % profit plan (average Q1-Q3)
    pbt_plan_company = {}
    pbt_achieve_company = []
    pbt_plan_total = 0
    pbt_actual_total = 0
    for q_idx, q in enumerate(['Q1', 'Q2', 'Q3']):
        if q_idx == 0:
            col_name = 'Kế hoạch'
        elif q_idx == 1:
            col_name = 'Kế hoạch.1'
        else:
            col_name = 'Kế hoạch.2'
        pbt_plan_val = clean_currency_value(df_2025.iloc[pbt_row_2025].get(col_name, np.nan))
        pbt_actual_val = calc_quarter(df_2025, pbt_row_2025, q)
        if pbt_plan_val and not pd.isna(pbt_plan_val) and not pd.isna(pbt_actual_val):
            pbt_plan_total += pbt_plan_val
            pbt_actual_total += pbt_actual_val
            if pbt_plan_val != 0:
                pbt_achieve_company.append(pbt_actual_val / pbt_plan_val * 100)
    
    # Check if plan is positive but actual is negative
    if pbt_plan_total > 0 and pbt_actual_total < 0:
        avg_pbt_achieve_company = "Missed (Loss)"
    elif pbt_achieve_company:
        avg_pbt_achieve_company = np.mean(pbt_achieve_company)
    else:
        avg_pbt_achieve_company = 0
    
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

# Calculate % profit contribution
total_pbt_2025 = sum([company_data[c]['pbt_2025'] for c in companies])
for company in companies:
    company_data[company]['pbt_contribution'] = (company_data[company]['pbt_2025'] / total_pbt_2025 * 100) if total_pbt_2025 != 0 else 0

# ============================================================================
# CALCULATE CV (COEFFICIENT OF VARIATION) FOR COST VOLATILITY
# ============================================================================

# Calculate CV per cost type by month
cv_data = {}
for company in companies:
    cogs_row = metrics_rows['COGS'][company]
    selling_row = metrics_rows['Selling Expenses'][company]
    admin_row = metrics_rows['Admin Expenses'][company]
    other_row = metrics_rows['Other Expenses'][company]
    
    # Get monthly data
    cogs_monthly = [clean_currency_value(df_2025.iloc[cogs_row].get(m, np.nan)) for m in months_ytd_2025]
    selling_monthly = [clean_currency_value(df_2025.iloc[selling_row].get(m, np.nan)) for m in months_ytd_2025]
    admin_monthly = [clean_currency_value(df_2025.iloc[admin_row].get(m, np.nan)) for m in months_ytd_2025]
    other_monthly = [clean_currency_value(df_2025.iloc[other_row].get(m, np.nan)) for m in months_ytd_2025]
    
    # Remove NaN
    cogs_monthly = [x for x in cogs_monthly if not pd.isna(x) and x != 0]
    selling_monthly = [x for x in selling_monthly if not pd.isna(x) and x != 0]
    admin_monthly = [x for x in admin_monthly if not pd.isna(x) and x != 0]
    other_monthly = [x for x in other_monthly if not pd.isna(x) and x != 0]
    
    # Calculate CV = (std / mean) * 100
    def calc_cv(values):
        if len(values) == 0:
            return 0
        mean_val = np.mean(values)
        if mean_val == 0:
            return 0
        std_val = np.std(values)
        return (std_val / mean_val) * 100
    
    cv_data[company] = {
        'cogs_cv': calc_cv(cogs_monthly),
        'selling_cv': calc_cv(selling_monthly),
        'admin_cv': calc_cv(admin_monthly),
        'other_cv': calc_cv(other_monthly),
    }

# ============================================================================
# CALCULATE Q3 PER COMPANY
# ============================================================================
for company in companies:
    rev_row_2024 = metrics_rows['Revenue'][company]
    rev_row_2025 = metrics_rows['Revenue'][company]
    revenue_q3_2024 = calc_quarter(df_2024, rev_row_2024, 'Q3')
    revenue_q3_2025 = calc_quarter(df_2025, rev_row_2025, 'Q3')
    revenue_q3_change = ((revenue_q3_2025 - revenue_q3_2024) / revenue_q3_2024 * 100) if revenue_q3_2024 != 0 else 0
    company_data[company]['revenue_q3_2024'] = revenue_q3_2024
    company_data[company]['revenue_q3_2025'] = revenue_q3_2025
    company_data[company]['revenue_q3_change'] = revenue_q3_change

# ============================================================================
# CREATE CHARTS
# ============================================================================

# Chart 1: Revenue by Quarter (2024 vs 2025 vs Plan)
fig1 = go.Figure()

# Revenue 2024 bars (all quarters)
fig1.add_trace(go.Bar(
    name='Actual 2024',
    x=['Q1', 'Q2', 'Q3', 'Q4'],
    y=[revenue_2024_q['Q1'], revenue_2024_q['Q2'], revenue_2024_q['Q3'], revenue_2024_q['Q4']],
    marker_color='#E5E6E5',
    text=[format_number(v) for v in [revenue_2024_q['Q1'], revenue_2024_q['Q2'], revenue_2024_q['Q3'], revenue_2024_q['Q4']]],
    textposition='outside',
    showlegend=True
))

# Revenue 2025 bars (all quarters)
fig1.add_trace(go.Bar(
    name='Actual 2025',
    x=['Q1', 'Q2', 'Q3', 'Q4'],
    y=[revenue_2025_q['Q1'], revenue_2025_q['Q2'], revenue_2025_q['Q3'], revenue_2025_q['Q4'] if not pd.isna(revenue_2025_q['Q4']) else 0],
    marker_color='#3A464E',
    text=[format_number(v) if not pd.isna(v) else '-' for v in [revenue_2025_q['Q1'], revenue_2025_q['Q2'], revenue_2025_q['Q3'], revenue_2025_q['Q4']]],
    textposition='outside',
    showlegend=True
))

# Plan 2025 bars (Q1-Q3)
fig1.add_trace(go.Bar(
    name='Plan 2025',
    x=['Q1', 'Q2', 'Q3'],
    y=[revenue_plan_q['Q1'], revenue_plan_q['Q2'], revenue_plan_q['Q3']],
    marker_color='#8A9BA8',
    text=[format_number(v) for v in [revenue_plan_q['Q1'], revenue_plan_q['Q2'], revenue_plan_q['Q3']]],
    textposition='outside',
    showlegend=True
))

# Format y-axis with full numbers (no k)
fig1.update_xaxes(title_text="Quarter")
fig1.update_yaxes(
    title_text="",
    tickformat=',.0f',
    tickmode='linear',
    tick0=0,
    dtick=5000
)

fig1.update_layout(
    title='<b>Revenue by Quarter</b>',
    barmode='group',
    height=500,
    template='plotly_white',
    legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
    dragmode=False
)
fig1.update_xaxes(fixedrange=True)
fig1.update_yaxes(fixedrange=True)

# Chart 2: Pre-tax Profit by Quarter (2024 vs 2025 vs Plan)
fig2 = go.Figure()

# PBT 2024 bars (absolute values)
fig2.add_trace(go.Bar(
    name='Actual 2024',
    x=['Q1', 'Q2', 'Q3', 'Q4'],
    y=[pbt_2024_q['Q1'], pbt_2024_q['Q2'], pbt_2024_q['Q3'], pbt_2024_q['Q4']],
    marker_color='#E5E6E5',
    text=[format_number(v) for v in [pbt_2024_q['Q1'], pbt_2024_q['Q2'], pbt_2024_q['Q3'], pbt_2024_q['Q4']]],
    textposition='outside',
    showlegend=True
))

# PBT 2025 bars (absolute values)
fig2.add_trace(go.Bar(
    name='Actual 2025',
    x=['Q1', 'Q2', 'Q3', 'Q4'],
    y=[pbt_2025_q['Q1'], pbt_2025_q['Q2'], pbt_2025_q['Q3'], pbt_2025_q['Q4'] if not pd.isna(pbt_2025_q['Q4']) else 0],
    marker_color='#3A464E',
    text=[format_number(v) if not pd.isna(v) else '-' for v in [pbt_2025_q['Q1'], pbt_2025_q['Q2'], pbt_2025_q['Q3'], pbt_2025_q['Q4']]],
    textposition='outside',
    showlegend=True
))

# PBT Plan bars (Q1-Q3)
fig2.add_trace(go.Bar(
    name='Plan 2025',
    x=['Q1', 'Q2', 'Q3'],
    y=[pbt_plan_q['Q1'], pbt_plan_q['Q2'], pbt_plan_q['Q3']],
    marker_color='#8A9BA8',
    text=[format_number(v) for v in [pbt_plan_q['Q1'], pbt_plan_q['Q2'], pbt_plan_q['Q3']]],
    textposition='outside',
    showlegend=True
))

# Format y-axis with full numbers
fig2.update_xaxes(title_text="Quarter")
fig2.update_yaxes(
    title_text="",
    tickformat=',.0f',
    tickmode='linear',
    tick0=0,
    dtick=1000
)

fig2.update_layout(
    title='<b>Pre-tax Profit by Quarter</b>',
    barmode='group',
    height=500,
    template='plotly_white',
    legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
    dragmode=False
)
fig2.update_xaxes(fixedrange=True)
fig2.update_yaxes(fixedrange=True)


# Chart 3: Monthly Revenue and Profit per company
month_labels = ['T01', 'T02', 'T03', 'T04', 'T05', 'T06', 'T07', 'T08', 'T09', 'T10']
month_display = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10']

company_chart_styles = {
    'SAN': {'line': '#F45C67', 'bar': 'rgba(244, 92, 103, 0.35)', 'name': 'Company S'},
    'TEENNIE': {'line': '#2E7D32', 'bar': 'rgba(46, 125, 50, 0.25)', 'name': 'Company T'},
    'TGIL': {'line': '#F6A623', 'bar': 'rgba(246, 166, 35, 0.30)', 'name': 'Company I'},
}

fig3_S = go.Figure()
fig3_T = go.Figure()
fig3_I = go.Figure()
company_figs = {'SAN': fig3_S, 'TEENNIE': fig3_T, 'TGIL': fig3_I}

for company in companies:
    rev_row = metrics_rows['Revenue'][company]
    pbt_row = metrics_rows['Profit Before Tax'][company]
    revenue_monthly = []
    pbt_monthly = []
    for m in month_labels:
        col = get_month_column(df_2025, m)
        revenue_monthly.append(clean_currency_value(df_2025.iloc[rev_row].get(col, np.nan)))
        pbt_monthly.append(clean_currency_value(df_2025.iloc[pbt_row].get(col, np.nan)))
    
    fig = company_figs[company]
    style = company_chart_styles[company]
    
    fig.add_trace(go.Scatter(
        name='Revenue',
        x=month_display,
        y=revenue_monthly,
        mode='lines+markers',
        line=dict(color=style['line'], width=3, shape='spline', smoothing=1.2),
        marker=dict(size=6, color=style['line']),
        hovertemplate='%{y:.0f} M'
    ))
    
    # Revenue annotations
    for month, value in zip(month_display, revenue_monthly):
        if not pd.isna(value):
            fig.add_annotation(
                x=month,
                y=value,
                text=format_number(value),
                showarrow=False,
                font=dict(color=style['line'], size=11),
                bgcolor='rgba(255,255,255,0.9)',
                bordercolor=style['line'],
                borderwidth=1,
                borderpad=4,
                yshift=18
            )
    
    fig.add_trace(go.Bar(
        name='Pre-tax Profit',
        x=month_display,
        y=pbt_monthly,
        marker=dict(color=style['bar'], line=dict(color=style['line'], width=1)),
        hovertemplate='%{y:.0f} M',
        text=[format_number(v) if not pd.isna(v) else '' for v in pbt_monthly],
        textposition='outside',
        textfont=dict(color=style['line'], size=11)
    ))
    
    values = [v for v in revenue_monthly + pbt_monthly if not pd.isna(v)]
    y_min = min(values) if values else 0
    y_max = max(values) if values else 0
    y_range = y_max - y_min if values else 0
    padding = y_range * 0.2 if y_range else (abs(y_max) * 0.3 if y_max != 0 else 1000)
    
    fig.update_layout(
        title=f"{company_chart_styles[company]['name']}: Monthly Revenue and Profit (10T 2025)",
        height=380,
        template='plotly_white',
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        dragmode=False,
        margin=dict(l=40, r=20, t=60, b=40),
    )
    fig.update_xaxes(title_text="Month", fixedrange=True)
    fig.update_yaxes(title_text="Amount (M)", fixedrange=True, range=[y_min - padding, y_max + padding])

def calc_cost_pct(company_key):
    revenue = company_data[company_key]['revenue_2025']
    if revenue == 0:
        return {'cogs': 0, 'selling': 0, 'admin': 0, 'other': 0}
    return {
        'cogs': company_data[company_key]['cogs'] / revenue * 100,
        'selling': company_data[company_key]['selling'] / revenue * 100,
        'admin': company_data[company_key]['admin'] / revenue * 100,
        'other': company_data[company_key]['other'] / revenue * 100,
    }

cost_pct = {
    'SAN': calc_cost_pct('SAN'),
    'TEENNIE': calc_cost_pct('TEENNIE'),
    'TGIL': calc_cost_pct('TGIL'),
}

# Chart 6-9: Waterfall charts (Total, S, T, I)
def create_waterfall_chart(company_name, company_label, data):
    """Create waterfall chart for a company"""
    revenue = data['revenue_2025']
    cogs = data['cogs']
    selling = data['selling']
    admin = data['admin']
    other = data['other']
    pbt = data['pbt_2025']
    
    # Calculate gross profit
    gross_profit = revenue - cogs
    
    fig = go.Figure()
    
    # Create waterfall chart with a single trace
    # Color for PBT
    profit_color = "#2E7D32" if pbt >= 0 else "rgba(254, 58, 69, 0.8)"
    
    fig.add_trace(go.Waterfall(
        orientation="v",
        measure=["absolute", "relative", "total", "relative", "relative", "relative", "total"],
        x=["Revenue", "COGS", "Gross Profit", "Selling Exp", "G&A Exp", "Other Exp", "Pre-tax Profit"],
        textposition="outside",
        text=[format_number(revenue), format_number(cogs), format_number(gross_profit), 
              format_number(selling), format_number(admin), format_number(other), format_number(pbt)],
        y=[revenue, -cogs, gross_profit, -selling, -admin, -other, pbt],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "#2E7D32"}},
        decreasing={"marker": {"color": "rgba(254, 58, 69, 0.3)"}},
        totals={"marker": {"color": "#2E7D32"}},
    ))
    
    # Update color for PBT bar (last total)
    # Use hovertemplate for correct display
    fig.update_traces(
        totals=dict(marker=dict(color=profit_color))
    )
    
    # Calculate min and max to expand axis range
    values = [revenue, -cogs, gross_profit, -selling, -admin, -other, pbt]
    cumulative_values = []
    cumsum = 0
    for i, v in enumerate(values):
        if i == 0:  # absolute
            cumsum = v
        elif i == 2 or i == 6:  # total
            cumsum = v
        else:  # relative
            cumsum += v
        cumulative_values.append(cumsum)
    
    y_min = min(cumulative_values)
    y_max = max(cumulative_values)
    y_range = y_max - y_min
    
    # Add 15% padding for both min and max
    y_min_padded = y_min - (y_range * 0.15)
    y_max_padded = y_max + (y_range * 0.15)
    
    fig.update_layout(
        title=f'<b>{company_label}</b>',
        height=400,
        template='plotly_white',
        xaxis_title='',
        yaxis_title='Amount (Million)',
        showlegend=False,
        waterfallgroupgap=0.1,
        yaxis=dict(range=[y_min_padded, y_max_padded]),
        dragmode=False
    )
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    
    return fig

# Calculate Total data
total_cogs = sum([company_data[c]['cogs'] for c in companies])
total_selling = sum([company_data[c]['selling'] for c in companies])
total_admin = sum([company_data[c]['admin'] for c in companies])
total_other = sum([company_data[c]['other'] for c in companies])

# ============================================================================
# CALCULATE COST STRUCTURE
# ============================================================================
# Group cost structure
total_cogs_pct = (total_cogs / revenue_2025_ytd * 100) if revenue_2025_ytd != 0 else 0
total_selling_pct = (total_selling / revenue_2025_ytd * 100) if revenue_2025_ytd != 0 else 0
total_admin_pct = (total_admin / revenue_2025_ytd * 100) if revenue_2025_ytd != 0 else 0
total_other_pct = (total_other / revenue_2025_ytd * 100) if revenue_2025_ytd != 0 else 0
total_opex_pct = total_selling_pct + total_admin_pct + total_other_pct

group_cost_pct = {
    'cogs': total_cogs_pct,
    'selling': total_selling_pct,
    'admin': total_admin_pct,
    'other': total_other_pct,
    'gross': gross_margin_2025,
    'pbt': pbt_margin_2025
}

# Company S cost structure
san_revenue = company_data['SAN']['revenue_2025']
san_cogs_pct = (company_data['SAN']['cogs'] / san_revenue * 100) if san_revenue != 0 else 0
san_selling_pct = (company_data['SAN']['selling'] / san_revenue * 100) if san_revenue != 0 else 0
san_admin_pct = (company_data['SAN']['admin'] / san_revenue * 100) if san_revenue != 0 else 0
san_other_pct = (company_data['SAN']['other'] / san_revenue * 100) if san_revenue != 0 else 0
san_opex_pct = san_selling_pct + san_admin_pct + san_other_pct

# Compare S vs Group
san_cogs_diff = san_cogs_pct - total_cogs_pct
san_selling_diff = san_selling_pct - total_selling_pct
san_admin_diff = san_admin_pct - total_admin_pct
san_other_diff = san_other_pct - total_other_pct
san_opex_diff = san_opex_pct - total_opex_pct

total_data = {
    'revenue_2025': revenue_2025_ytd,
    'cogs': total_cogs,
    'selling': total_selling,
    'admin': total_admin,
    'other': total_other,
    'pbt_2025': pbt_2025_ytd,
}

fig6 = create_waterfall_chart('Total', 'Total Group', total_data)
fig7 = create_waterfall_chart('SAN', 'Company S', company_data['SAN'])
fig8 = create_waterfall_chart('TEENNIE', 'Company T', company_data['TEENNIE'])
fig9 = create_waterfall_chart('TGIL', 'Company I', company_data['TGIL'])

gross_profit_change_pct = ((gross_profit_2025_ytd - gross_profit_2024_ytd) / gross_profit_2024_ytd * 100) if gross_profit_2024_ytd != 0 else 0
pbt_change_pct = ((pbt_2025_ytd - pbt_2024_ytd) / pbt_2024_ytd * 100) if pbt_2024_ytd != 0 else 0
group_q3_change = ((revenue_2025_q['Q3'] - revenue_2024_q['Q3']) / revenue_2024_q['Q3'] * 100) if revenue_2024_q['Q3'] != 0 else 0
san_q3_change = company_data['SAN']['revenue_q3_change']
teennie_q3_change = company_data['TEENNIE']['revenue_q3_change']
tgil_q3_change = company_data['TGIL']['revenue_q3_change']
teennie_contribution = company_data['TEENNIE']['pbt_contribution']
tgil_contribution = company_data['TGIL']['pbt_contribution']
san_contribution = company_data['SAN']['pbt_contribution']

template_path = Path('/Users/lucasbraci/Desktop/S Group/report_template_cached.html')
template_str = template_path.read_text()

def format_plan_value(value):
    if isinstance(value, str):
        return value
    return f"{value:.0f}%"

context = {
    'kpi_revenue': format_number(revenue_2025_ytd),
    'kpi_revenue_delta': f"({'+' if revenue_change_pct >= 0 else ''}{revenue_change_pct:.1f}% vs YTD 2024)",
    'kpi_revenue_change_class': 'negative' if revenue_change_pct < 0 else '',
    'kpi_pbt': format_number(pbt_2025_ytd),
    'kpi_pbt_multiple': f"(≈ x{pbt_multiple:.1f} x vs YTD 2024)",
    'kpi_margin': f"{pbt_margin_2025:.1f}%",
    'kpi_margin_delta': f"(vs {pbt_margin_2024:.1f}% YTD 2024)",
    'kpi_plan_revenue': f"{avg_revenue_achieve:.0f}%",
    'kpi_plan_pbt': f"{avg_pbt_achieve:.0f}%",
    'table_rev_2024': format_number(revenue_2024_ytd),
    'table_rev_2025': format_number(revenue_2025_ytd),
    'table_rev_pct': f"{revenue_change_pct:+.1f}%",
    'table_gross_2024': format_number(gross_profit_2024_ytd),
    'table_gross_2025': format_number(gross_profit_2025_ytd),
    'table_gross_pct': f"{gross_profit_change_pct:+.1f}%",
    'table_pbt_2024': format_number(pbt_2024_ytd),
    'table_pbt_2025': format_number(pbt_2025_ytd),
    'table_pbt_pct': f"{pbt_change_pct:+.1f}%",
    'table_gross_margin_2024': f"{gross_margin_2024:.1f}%",
    'table_gross_margin_2025': f"{gross_margin_2025:.1f}%",
    'table_gross_margin_pct': f"{(gross_margin_2025 - gross_margin_2024):+.1f} pp",
    'table_pbt_margin_2024': f"{pbt_margin_2024:.1f}%",
    'table_pbt_margin_2025': f"{pbt_margin_2025:.1f}%",
    'table_pbt_margin_pct': f"{(pbt_margin_2025 - pbt_margin_2024):+.1f} pp",
    'company_s_revenue': format_number(company_data['SAN']['revenue_2025']),
    'company_s_yoy': f"{company_data['SAN']['revenue_yoy']:.1f}%",
    'company_s_pbt': format_number(company_data['SAN']['pbt_2025']),
    'company_s_margin': f"{company_data['SAN']['pbt_margin']:.1f}%",
    'company_s_plan': format_plan_value(company_data['SAN']['pbt_achieve']),
    'company_t_revenue': format_number(company_data['TEENNIE']['revenue_2025']),
    'company_t_yoy': f"{company_data['TEENNIE']['revenue_yoy']:.1f}%",
    'company_t_pbt': format_number(company_data['TEENNIE']['pbt_2025']),
    'company_t_margin': f"{company_data['TEENNIE']['pbt_margin']:.1f}%",
    'company_t_plan': format_plan_value(company_data['TEENNIE']['pbt_achieve']),
    'company_i_revenue': format_number(company_data['TGIL']['revenue_2025']),
    'company_i_yoy': f"{company_data['TGIL']['revenue_yoy']:.1f}%",
    'company_i_pbt': format_number(company_data['TGIL']['pbt_2025']),
    'company_i_margin': f"{company_data['TGIL']['pbt_margin']:.1f}%",
    'company_i_plan': format_plan_value(company_data['TGIL']['pbt_achieve']),
    'company_s_yoy_magnitude': f"{abs(company_data['SAN']['revenue_yoy']):.0f}%",
    'company_s_margin_magnitude': f"{abs(company_data['SAN']['pbt_margin']):.1f}%",
    'teennie_contribution': f"{teennie_contribution:.0f}",
    'cost_cogs_s': f"{cost_pct['SAN']['cogs']:.1f}%",
    'cost_cogs_t': f"{cost_pct['TEENNIE']['cogs']:.1f}%",
    'cost_cogs_i': f"{cost_pct['TGIL']['cogs']:.1f}%",
    'cost_cogs_group': f"{group_cost_pct['cogs']:.1f}%",
    'cost_selling_s': f"{cost_pct['SAN']['selling']:.1f}%",
    'cost_selling_t': f"{cost_pct['TEENNIE']['selling']:.1f}%",
    'cost_selling_i': f"{cost_pct['TGIL']['selling']:.1f}%",
    'cost_selling_group': f"{group_cost_pct['selling']:.1f}%",
    'cost_admin_s': f"{cost_pct['SAN']['admin']:.1f}%",
    'cost_admin_t': f"{cost_pct['TEENNIE']['admin']:.1f}%",
    'cost_admin_i': f"{cost_pct['TGIL']['admin']:.1f}%",
    'cost_admin_group': f"{group_cost_pct['admin']:.1f}%",
    'cost_other_s': f"{cost_pct['SAN']['other']:.1f}%",
    'cost_other_t': f"{cost_pct['TEENNIE']['other']:.1f}%",
    'cost_other_i': f"{cost_pct['TGIL']['other']:.1f}%",
    'cost_other_group': f"{group_cost_pct['other']:.1f}%",
    'cost_gross_s': f"{(company_data['SAN']['gross_profit_2025'] / company_data['SAN']['revenue_2025'] * 100) if company_data['SAN']['revenue_2025'] != 0 else 0:.1f}%",
    'cost_gross_t': f"{(company_data['TEENNIE']['gross_profit_2025'] / company_data['TEENNIE']['revenue_2025'] * 100) if company_data['TEENNIE']['revenue_2025'] != 0 else 0:.1f}%",
    'cost_gross_i': f"{(company_data['TGIL']['gross_profit_2025'] / company_data['TGIL']['revenue_2025'] * 100) if company_data['TGIL']['revenue_2025'] != 0 else 0:.1f}%",
    'cost_gross_group': f"{group_cost_pct['gross']:.1f}%",
    'cost_pbt_group': f"{group_cost_pct['pbt']:.1f}%",
    'chart1_json': fig1.to_json(),
    'chart2_json': fig2.to_json(),
    'chart3_s_json': fig3_S.to_json(),
    'chart3_t_json': fig3_T.to_json(),
    'chart3_i_json': fig3_I.to_json(),
    'chart6_json': fig6.to_json(),
    'chart7_json': fig7.to_json(),
    'chart8_json': fig8.to_json(),
    'chart9_json': fig9.to_json(),
}

html_content = Template(template_str).substitute(context)

# Ghi file HTML
output_file = '/Users/lucasbraci/Desktop/S Group/report_web.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print("✅ REPORT GENERATED SUCCESSFULLY!")
print(f"📄 File: {output_file}")

