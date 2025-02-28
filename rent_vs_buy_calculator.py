# -*- coding: utf-8 -*-
"""
Created on Fri Feb 28 09:09:27 2025

@author: zhisen
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from datetime import datetime
import matplotlib
matplotlib.use('Agg')

# 设置页面配置
st.set_page_config(
    page_title="买房 vs 租房决策分析器",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #333;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 15px;
        border-left: 4px solid #1E88E5;
    }
    .metric-title {
        font-size: 1rem;
        color: #666;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #333;
    }
    .recommendation-buy {
        background-color: #e8f5e9;
        border-left: 5px solid #4caf50;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .recommendation-rent {
        background-color: #ffebee;
        border-left: 5px solid #f44336;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .recommendation-neutral {
        background-color: #e3f2fd;
        border-left: 5px solid #2196f3;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
        color: #1E88E5;
        margin-left: 5px;
    }
    .tooltip:hover::after {
        content: attr(data-tip);
        position: absolute;
        bottom: 125%;
        left: 50%;
        transform: translateX(-50%);
        background-color: #333;
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 0.8rem;
        white-space: nowrap;
        z-index: 1000;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 4px 4px 0 0;
        padding: 10px 20px;
        height: auto;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E88E5 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# 页面标题
st.markdown('<div class="main-header">买房 vs 租房决策分析工具</div>', unsafe_allow_html=True)
st.markdown('这个工具可以帮助您分析在当前经济和市场条件下，买房和租房哪种选择更加经济。通过调整左侧的参数，探索不同场景下的最佳决策。')

# 创建侧边栏参数输入区
st.sidebar.markdown('## 参数设置')

# 创建参数配置分组
with st.sidebar.expander("经济参数", expanded=True):
    # 房价
    col1, col2 = st.columns([3, 1])
    with col1:
        house_price = st.number_input(
            "房价 (P)", 
            min_value=1000000, 
            max_value=20000000, 
            value=5000000, 
            step=100000,
            format="%d"
        )
    with col2:
        st.markdown('<div class="tooltip" data-tip="目标房产总价">?</div>', unsafe_allow_html=True)
    
    # 首付比例
    col1, col2 = st.columns([3, 1])
    with col1:
        down_payment_percent = st.slider(
            "首付比例 (dp)", 
            min_value=10, 
            max_value=100, 
            value=30, 
            step=5,
            format="%d%%"
        )
    with col2:
        st.markdown('<div class="tooltip" data-tip="首付款占房价的百分比">?</div>', unsafe_allow_html=True)
    
    # 贷款年限
    col1, col2 = st.columns([3, 1])
    with col1:
        loan_years = st.slider(
            "贷款年限 (n_loan)", 
            min_value=10, 
            max_value=30, 
            value=30, 
            step=5
        )
    with col2:
        st.markdown('<div class="tooltip" data-tip="按揭贷款期限">?</div>', unsafe_allow_html=True)
    
    # 贷款利率
    col1, col2 = st.columns([3, 1])
    with col1:
        loan_rate = st.slider(
            "贷款利率 (r_loan)", 
            min_value=1.0, 
            max_value=10.0, 
            value=4.9, 
            step=0.1,
            format="%.1f%%"
        )
    with col2:
        st.markdown('<div class="tooltip" data-tip="商业贷款年利率">?</div>', unsafe_allow_html=True)
    
    # 月租金
    col1, col2 = st.columns([3, 1])
    with col1:
        monthly_rent = st.number_input(
            "月租金 (rent)", 
            min_value=3000, 
            max_value=50000, 
            value=8000, 
            step=500,
            format="%d"
        )
    with col2:
        st.markdown('<div class="tooltip" data-tip="当前市场租金(元/月)">?</div>', unsafe_allow_html=True)
    
    # 租金年涨幅
    col1, col2 = st.columns([3, 1])
    with col1:
        rent_growth = st.slider(
            "租金年涨幅 (g_rent)", 
            min_value=0.0, 
            max_value=15.0, 
            value=5.0, 
            step=0.5,
            format="%.1f%%"
        )
    with col2:
        st.markdown('<div class="tooltip" data-tip="租金年均增长率">?</div>', unsafe_allow_html=True)
    
    # 投资回报率
    col1, col2 = st.columns([3, 1])
    with col1:
        investment_return = st.slider(
            "投资回报率 (r_inv)", 
            min_value=0.0, 
            max_value=20.0, 
            value=6.0, 
            step=0.5,
            format="%.1f%%"
        )
    with col2:
        st.markdown('<div class="tooltip" data-tip="首付款替代投资年化收益">?</div>', unsafe_allow_html=True)
    
    # 物业费
    col1, col2 = st.columns([3, 1])
    with col1:
        property_fee = st.number_input(
            "物业费 (fee)", 
            min_value=0, 
            max_value=20, 
            value=5, 
            step=1,
            format="%d"
        )
    with col2:
        st.markdown('<div class="tooltip" data-tip="物业管理费单价(元/㎡/月)">?</div>', unsafe_allow_html=True)
    
    # 房产面积（计算物业费用）
    col1, col2 = st.columns([3, 1])
    with col1:
        property_area = st.number_input(
            "房产面积 (㎡)", 
            min_value=20, 
            max_value=500, 
            value=100, 
            step=10,
            format="%d"
        )
    with col2:
        st.markdown('<div class="tooltip" data-tip="房产建筑面积，用于计算物业费">?</div>', unsafe_allow_html=True)
    
    # 房产税率
    col1, col2 = st.columns([3, 1])
    with col1:
        property_tax = st.slider(
            "房产税率 (tax)", 
            min_value=0.0, 
            max_value=2.0, 
            value=0.5, 
            step=0.1,
            format="%.1f%%"
        )
    with col2:
        st.markdown('<div class="tooltip" data-tip="房产评估价值年税率">?</div>', unsafe_allow_html=True)
    
    # 维修基金
    col1, col2 = st.columns([3, 1])
    with col1:
        maintenance_fund = st.number_input(
            "维修基金 (maint)", 
            min_value=0, 
            max_value=50000, 
            value=10000, 
            step=1000,
            format="%d",
            help="每年房价的百分比，用于房屋维护和修缮，不同于物业费。例如：0.5%表示每年需拿出房价0.5%的金额用于维护"
        )
    with col2:
        st.markdown('<div class="tooltip" data-tip="年均房屋维护费用(元/年)">?</div>', unsafe_allow_html=True)
    
    st.markdown("### 公积金贷款设置")
    
    use_housing_fund = st.checkbox("使用公积金贷款", value=False)
    
    if use_housing_fund:
        col1, col2 = st.columns([3, 1])
        with col1:
            housing_fund_amount = st.number_input(
                "公积金贷款金额", 
                min_value=0, 
                max_value=1600000,  # 最高夫妻两人各80万
                value=800000, 
                step=100000,
                format="%d",
                help="公积金贷款最高额度，单人80万，夫妻两人最高160万"
            )
        with col2:
            st.markdown('<div class="tooltip" data-tip="公积金贷款额度">?</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            housing_fund_rate = st.slider(
                "公积金贷款利率", 
                min_value=1.0, 
                max_value=5.0, 
                value=3.1, 
                step=0.1,
                format="%.1f%%",
                help="当前公积金贷款基准利率为3.1%"
            )
        with col2:
            st.markdown('<div class="tooltip" data-tip="公积金贷款年利率">?</div>', unsafe_allow_html=True)

# 添加个人财务参数部分
with st.sidebar.expander("个人财务参数", expanded=False):
    monthly_income = st.number_input(
        "月收入 (税后)", 
        min_value=0, 
        max_value=200000, 
        value=30000, 
        step=1000,
        format="%d"
    )
    
    total_assets = st.number_input(
        "个人总资产", 
        min_value=0, 
        max_value=50000000, 
        value=house_price, 
        step=100000,
        format="%d"
    )
    
    emergency_fund_months = st.slider(
        "应急资金储备(月)", 
        min_value=0, 
        max_value=24, 
        value=6, 
        step=1,
        help="购房后保留的应急资金，以月支出为单位"
    )

with st.sidebar.expander("市场参数", expanded=True):
    # 计划居住年限
    col1, col2 = st.columns([3, 1])
    with col1:
        living_years = st.slider(
            "计划居住年限 (n_live)", 
            min_value=1, 
            max_value=30, 
            value=10, 
            step=1
        )
    with col2:
        st.markdown('<div class="tooltip" data-tip="预计持有/租住时长(年)">?</div>', unsafe_allow_html=True)
    
    # 房价年涨幅
    col1, col2 = st.columns([3, 1])
    with col1:
        house_price_growth = st.slider(
            "房价年涨幅 (g_home)", 
            min_value=-10.0, 
            max_value=15.0, 
            value=3.0, 
            step=0.5,
            format="%.1f%%"
        )
    with col2:
        st.markdown('<div class="tooltip" data-tip="预期房产年均增值率">?</div>', unsafe_allow_html=True)
    
    # 通货膨胀率（额外参数）
    col1, col2 = st.columns([3, 1])
    with col1:
        inflation_rate = st.slider(
            "通货膨胀率", 
            min_value=0.0, 
            max_value=10.0, 
            value=2.5, 
            step=0.1,
            format="%.1f%%"
        )
    with col2:
        st.markdown('<div class="tooltip" data-tip="年度通货膨胀率，用于计算实际收益率">?</div>', unsafe_allow_html=True)
    
    # 是否考虑通货膨胀进行实际收益率计算
    use_real_returns = st.checkbox("使用实际收益率计算（考虑通货膨胀）", value=True)
    
    # 添加市场周期位置滑块
    market_cycle = st.slider(
        "市场周期位置", 
        min_value=1, 
        max_value=4, 
        value=2, 
        step=1,
        format="%d",
        help="1=萧条期，2=复苏期，3=扩张期，4=过热期"
    )
    
    # 添加供需平衡状况
    supply_demand_balance = st.slider(
        "供需平衡状况", 
        min_value=-10, 
        max_value=10, 
        value=0, 
        step=1,
        format="%d",
        help="负值表示供大于求，正值表示供不应求，0表示平衡"
    )

with st.sidebar.expander("个人因素", expanded=False):
    career_stability = st.slider(
        "职业稳定性", 
        min_value=1, 
        max_value=10, 
        value=7, 
        step=1,
        help="1=非常不稳定，10=非常稳定"
    )
    
    family_plan = st.radio(
        "未来3-5年家庭计划",
        options=["无变化", "扩大家庭", "缩小家庭", "不确定"]
    )
    
    mobility_need = st.slider(
        "生活流动性需求", 
        min_value=1, 
        max_value=10, 
        value=5, 
        step=1,
        help="1=几乎不需要变动，10=需要高度灵活性"
    )
    
    ownership_importance = st.slider(
        "房屋所有权重要性", 
        min_value=1, 
        max_value=10, 
        value=7, 
        step=1,
        help="拥有自己房子对您的重要程度"
    )

# 计算函数
def calculate_mortgage_payment(loan_amount, annual_rate, years):
    """计算每月等额本息还款额"""
    monthly_rate = annual_rate / 100 / 12
    num_payments = years * 12
    if monthly_rate == 0:
        return loan_amount / num_payments
    return loan_amount * monthly_rate * (1 + monthly_rate) ** num_payments / ((1 + monthly_rate) ** num_payments - 1)

def calculate_buy_vs_rent(params):
    """计算买房与租房的成本对比"""
    # 解析参数
    P = params['house_price']
    dp_percent = params['down_payment_percent'] / 100
    n_loan = params['loan_years']
    r_loan = params['loan_rate'] / 100
    rent = params['monthly_rent']
    g_rent = params['rent_growth'] / 100
    r_inv = params['investment_return'] / 100
    fee = params['property_fee']
    area = params['property_area']
    tax = params['property_tax'] / 100
    maint = params['maintenance_fund']
    n_live = params['living_years']
    g_home = params['house_price_growth'] / 100
    inflation = params['inflation_rate'] / 100
    use_real = params['use_real_returns']
    use_housing_fund = params.get('use_housing_fund', False)
    housing_fund_amount = params.get('housing_fund_amount', 0)
    housing_fund_rate = params.get('housing_fund_rate', 0) / 100
    
    # 计算实际利率（如果启用）
    if use_real:
        r_inv_real = (1 + r_inv) / (1 + inflation) - 1
    else:
        r_inv_real = r_inv
    
    # 买房成本计算
    down_payment = P * dp_percent
    total_loan_amount = P * (1 - dp_percent)
    
    # 分配贷款金额
    if use_housing_fund and housing_fund_amount > 0:
        # 确保公积金贷款不超过总贷款额
        housing_fund_amount = min(housing_fund_amount, total_loan_amount)
        commercial_loan_amount = total_loan_amount - housing_fund_amount
    else:
        housing_fund_amount = 0
        commercial_loan_amount = total_loan_amount
    
    # 计算公积金贷款月供
    housing_fund_monthly_payment = calculate_mortgage_payment(housing_fund_amount, housing_fund_rate * 100, n_loan)
    
    # 计算商业贷款月供
    commercial_monthly_payment = calculate_mortgage_payment(commercial_loan_amount, r_loan * 100, n_loan)
    
    # 总月供
    monthly_payment = housing_fund_monthly_payment + commercial_monthly_payment
    
    # 初始化结果数据
    years = np.arange(1, n_live + 1)
    results = pd.DataFrame(index=years)
    
    # 购房成本随时间变化
    total_payments = np.zeros(n_live)
    remaining_principal = np.zeros(n_live)
    
    # 计算每年的贷款支付和剩余本金
    for i in range(n_live):
        year_payments = monthly_payment * 12
        if i == 0:
            total_payments[i] = down_payment + year_payments
            if n_loan > 0:
                # 计算第一年后的剩余本金
                monthly_rate = r_loan / 12
                remaining = loan_amount
                for _ in range(12):
                    interest = remaining * monthly_rate
                    principal = monthly_payment - interest
                    remaining -= principal
                remaining_principal[i] = remaining if remaining > 0 else 0
            else:
                remaining_principal[i] = 0
        else:
            total_payments[i] = total_payments[i-1] + year_payments
            if i < n_loan:
                # 计算之后年份的剩余本金
                monthly_rate = r_loan / 12
                remaining = remaining_principal[i-1]
                for _ in range(12):
                    if remaining <= 0:
                        break
                    interest = remaining * monthly_rate
                    principal = monthly_payment - interest
                    remaining -= principal
                remaining_principal[i] = remaining if remaining > 0 else 0
            else:
                remaining_principal[i] = 0
    
    # 房屋持有成本
    annual_property_fee = fee * area * 12
    annual_property_tax = P * tax
    annual_holding_costs = np.zeros(n_live)
    
    for i in range(n_live):
        # 计算第i年的房产价值（用于计算房产税）
        current_property_value = P * (1 + g_home) ** i
        annual_property_tax = current_property_value * tax
        annual_holding_costs[i] = annual_property_fee + annual_property_tax + maint
        if i > 0:
            annual_holding_costs[i] = annual_holding_costs[i-1] + annual_holding_costs[i]
    
    # 房产残值
    property_final_value = P * (1 + g_home) ** n_live
    
    # 买房总成本
    buy_total_costs = total_payments + annual_holding_costs
    
    # 租房成本计算
    rent_costs = np.zeros(n_live)
    for i in range(n_live):
        annual_rent = rent * 12 * (1 + g_rent) ** i
        if i == 0:
            rent_costs[i] = annual_rent
        else:
            rent_costs[i] = rent_costs[i-1] + annual_rent
    
    # 首付投资收益
    investment_value = np.zeros(n_live)
    for i in range(n_live):
        investment_value[i] = down_payment * (1 + r_inv_real) ** (i + 1)
    
    # 租房总成本（考虑投资收益为负成本）
    rent_total_costs = rent_costs
    
    # 投资机会成本（买房的隐性成本）
    opportunity_cost = investment_value - down_payment
    
    # 净房屋价值（扣除贷款剩余）
    net_property_value = property_final_value - remaining_principal
    
    # 有效买房成本（考虑房产增值为负成本）
    effective_buy_costs = np.zeros(n_live)
    for i in range(n_live):
        current_property_value = P * (1 + g_home) ** (i + 1)
        current_remaining_loan = remaining_principal[i]
        property_equity = current_property_value - current_remaining_loan
        effective_buy_costs[i] = buy_total_costs[i] - (property_equity - down_payment)
    
    # 有效租房成本（考虑投资收益为负成本）
    effective_rent_costs = np.zeros(n_live)
    for i in range(n_live):
        effective_rent_costs[i] = rent_costs[i] - opportunity_cost[i]
    
    # 整合结果
    results['买房累计支出'] = buy_total_costs
    results['租房累计支出'] = rent_costs
    results['买房机会成本'] = opportunity_cost
    results['房产净值'] = np.array([P * (1 + g_home) ** (i + 1) - remaining_principal[i] for i in range(n_live)])
    results['有效买房成本'] = effective_buy_costs
    results['有效租房成本'] = effective_rent_costs
    results['成本差额(租-买)'] = effective_rent_costs - effective_buy_costs
    
    # 计算关键指标
    break_even_year = None
    for i in range(n_live):
        if effective_rent_costs[i] > effective_buy_costs[i]:
            break_even_year = i + 1
            break
    
    # 计算价格租金比
    price_to_rent_ratio = P / (rent * 12)
    
    # 计算剩余贷款占比
    if n_live <= n_loan:
        loan_remaining_percent = remaining_principal[n_live-1] / loan_amount * 100 if loan_amount > 0 else 0
    else:
        loan_remaining_percent = 0
    
    # 计算租金覆盖率（月租金占每月房贷的百分比）
    rent_coverage_ratio = rent / monthly_payment * 100 if monthly_payment > 0 else float('inf')
    
    # 总结果
    summary = {
        'break_even_year': break_even_year,
        'price_to_rent_ratio': price_to_rent_ratio,
        'final_property_value': property_final_value,
        'total_mortgage_payment': total_payments[n_live-1] - down_payment,
        'total_holding_cost': annual_holding_costs[n_live-1],
        'total_rent_cost': rent_costs[n_live-1],
        'investment_return': investment_value[n_live-1] - down_payment,
        'loan_remaining_percent': loan_remaining_percent,
        'rent_coverage_ratio': rent_coverage_ratio,
        'down_payment': down_payment,
        'monthly_payment': monthly_payment,
        'annual_property_cost': annual_property_fee + maint + annual_property_tax,
        # 添加公积金贷款相关字段
        'housing_fund_amount': housing_fund_amount,
        'housing_fund_monthly_payment': housing_fund_monthly_payment,
        'commercial_loan_amount': commercial_loan_amount,
        'commercial_monthly_payment': commercial_monthly_payment,
        'total_monthly_payment': monthly_payment,
        'housing_fund_interest_rate': housing_fund_rate * 100,
        'commercial_interest_rate': r_loan * 100,
        'use_housing_fund': use_housing_fund
    }
    
    return results, summary

# 计算首付和贷款金额
down_payment = house_price * down_payment_percent / 100
loan_amount = house_price - down_payment

# 执行计算
params = {
    'house_price': house_price,
    'down_payment_percent': down_payment_percent,
    'loan_years': loan_years,
    'loan_rate': loan_rate,
    'monthly_rent': monthly_rent,
    'rent_growth': rent_growth,
    'investment_return': investment_return,
    'property_fee': property_fee,
    'property_area': property_area,
    'property_tax': property_tax,
    'maintenance_fund': maintenance_fund,
    'living_years': living_years,
    'house_price_growth': house_price_growth,
    'inflation_rate': inflation_rate,
    'use_real_returns': use_real_returns,
    # 添加公积金贷款参数
    'use_housing_fund': use_housing_fund if 'use_housing_fund' in locals() else False,
    'housing_fund_amount': housing_fund_amount if 'housing_fund_amount' in locals() else 0,
    'housing_fund_rate': housing_fund_rate if 'housing_fund_rate' in locals() else 3.1
}

results, summary = calculate_buy_vs_rent(params)

# 创建主容器布局
main_col1, main_col2 = st.columns([2, 1])

with main_col1:
    # 关键指标显示
    st.markdown('<div class="sub-header">关键决策指标</div>', unsafe_allow_html=True)
    
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    with metric_col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">价格租金比</div>
            <div class="metric-value">{summary['price_to_rent_ratio']:.1f}x</div>
            <div>房价相当于{summary['price_to_rent_ratio']:.1f}年的租金总和。低于15买房更划算，高于25租房更划算</div>
        </div>
        """, unsafe_allow_html=True)
    
    with metric_col2:
        if summary['break_even_year'] is None:
            break_even_text = "永远不会平衡"
        elif summary['break_even_year'] > living_years:
            break_even_text = f"超过计划居住期 (约{summary['break_even_year']:.1f}年)"
        else:
            break_even_text = f"{summary['break_even_year']:.1f}年"
            
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">收支平衡年限</div>
            <div class="metric-value">{break_even_text}</div>
            <div>租房成本超过买房成本的时间点</div>
        </div>
        """, unsafe_allow_html=True)
    
    with metric_col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">租金覆盖率</div>
            <div class="metric-value">{summary['rent_coverage_ratio']:.1f}%</div>
            <div>月租金占月供的百分比。高于100%表示租金超过月供，低于100%表示月供超过租金</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 基于价格租金比和收支平衡年限的决策逻辑
    price_rent_ratio = summary['price_to_rent_ratio']

    # 价格租金比判断
    if price_rent_ratio < 15:
        ratio_suggests_buy = True
    elif price_rent_ratio > 25:
        ratio_suggests_buy = False
    else:
        ratio_suggests_buy = None  # 中性建议

    # 收支平衡年限判断
    if summary['break_even_year'] and summary['break_even_year'] <= living_years / 2:
        balance_suggests_buy = True
    elif not summary['break_even_year'] or summary['break_even_year'] > living_years:
        balance_suggests_buy = False
    else:
        balance_suggests_buy = None  # 中性建议

    # 综合两个指标给出建议
    if balance_suggests_buy == True and (ratio_suggests_buy == True or ratio_suggests_buy == None):
        # 收支平衡支持买房，价格租金比支持或中性
        recommendation_class = "recommendation-buy"
        recommendation_title = "推荐买房"
        recommendation_text = f"分析显示，如果您计划居住{living_years}年，在第{summary['break_even_year']}年就能达到收支平衡。价格租金比为{price_rent_ratio:.1f}x，{'处于合理范围内' if ratio_suggests_buy == None else '较低，买房较为经济'}。长期来看，买房更经济。"
    elif balance_suggests_buy == False and (ratio_suggests_buy == False or ratio_suggests_buy == None):
        # 收支平衡支持租房，价格租金比支持或中性
        recommendation_class = "recommendation-rent"
        recommendation_title = "推荐租房"
        if not summary['break_even_year']:
            break_even_text = "租房始终比买房更经济"
        else:
            break_even_text = f"收支平衡要等到第{summary['break_even_year']}年"
            
        ratio_text = "处于合理范围内" if ratio_suggests_buy == None else "较高，租房较为经济"
        recommendation_text = f"在您计划的{living_years}年居住期内，{break_even_text}。价格租金比为{price_rent_ratio:.1f}x，{ratio_text}。如果不打算长期居住，租房是更好的选择。"
    elif ratio_suggests_buy == True and balance_suggests_buy != False:
        # 价格租金比强烈支持买房，收支平衡不反对
        recommendation_class = "recommendation-buy"
        recommendation_title = "偏向买房"
        if balance_suggests_buy == True:
            balance_text = f"同时，收支平衡点在第{summary['break_even_year']}年，支持买房决策。"
        else:
            balance_text = "但收支平衡分析显示需要权衡考虑其他因素。"
            
        recommendation_text = f"价格租金比为{price_rent_ratio:.1f}x，低于15的合理范围，买房较为经济。{balance_text}"
    elif ratio_suggests_buy == False and balance_suggests_buy != True:
        # 价格租金比强烈支持租房，收支平衡不反对
        recommendation_class = "recommendation-rent"
        recommendation_title = "偏向租房"
        if balance_suggests_buy == False:
            balance_text = f"同时，在您计划的{living_years}年居住期内，租房始终比买房更经济。"
        else:
            balance_text = "但收支平衡分析显示需要权衡考虑其他因素。"
            
        recommendation_text = f"价格租金比为{price_rent_ratio:.1f}x，高于25的合理范围，租房较为经济。{balance_text}"
    else:
        # 两个指标给出相反建议或都是中性
        recommendation_class = "recommendation-neutral"
        recommendation_title = "需权衡考虑"
        recommendation_text = f"价格租金比为{price_rent_ratio:.1f}x，处于{('较低水平' if ratio_suggests_buy == True else '较高水平' if ratio_suggests_buy == False else '15-25的合理范围')}。"
        if summary['break_even_year']:
            recommendation_text += f" 收支平衡点在第{summary['break_even_year']}年。"
        else:
            recommendation_text += " 在计划居住期内不会达到收支平衡。"
        recommendation_text += " 您需要权衡短期经济性与长期稳定性等多方面因素。"
    
    st.markdown(f"""
    <div class="{recommendation_class}">
        <h3>{recommendation_title}</h3>
        <p>{recommendation_text}</p>
        <ul>
            <li>价格租金比: {summary['price_to_rent_ratio']:.1f}x (15-20为合理范围，<15买房更划算，>25租房更划算)</li>
            <li>首付金额: {summary['down_payment']:,.0f}元</li>
            <li>月供: {summary['monthly_payment']:,.0f}元/月</li>
            <li>年房屋持有成本: {summary['annual_property_cost']:,.0f}元/年</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("价格租金比详细解释"):
        st.markdown("""
        **价格租金比是衡量房产投资价值的重要指标：**
        - **<15**: 买房相对更经济
        - **15-20**: 市场公认的合理范围
        - **20-25**: 稍高但仍可接受
        - **>25**: 租房相对更经济
        - **>30**: 可能存在房价泡沫风险
        
        该指标表示需要多少年的租金才能抵消房价，计算方式为：房价/(月租金×12)
        
        价格租金比仅反映市场价格情况，需要结合收支平衡年限和个人因素综合判断。
        """)
    
    # 市场周期分析
    market_cycle_names = ["萧条期", "复苏期", "扩张期", "过热期"]
    cycle_name = market_cycle_names[market_cycle-1]

    # 根据市场周期给出建议
    market_advice = ""
    if market_cycle == 1:
        market_advice = "当前处于**萧条期**，房价可能处于低点，对买房有利，但需警惕下行风险。"
    elif market_cycle == 2:
        market_advice = "当前处于**复苏期**，房价可能开始稳步回升，买入时机较好。"
    elif market_cycle == 3:
        market_advice = "当前处于**扩张期**，房价上涨较快，买房需谨慎评估高位风险。"
    elif market_cycle == 4:
        market_advice = "当前处于**过热期**，房价可能处于高位，租房可能更经济，等待市场调整。"

    supply_advice = ""
    if supply_demand_balance < -5:
        supply_advice = "市场**供过于求**明显，买方议价空间大，可能不利于房价上涨。"
    elif supply_demand_balance < 0:
        supply_advice = "市场供应略大于需求，买方有一定议价空间。"
    elif supply_demand_balance == 0:
        supply_advice = "市场供需基本平衡。"
    elif supply_demand_balance <= 5:
        supply_advice = "市场需求略大于供应，卖方有一定议价优势。"
    else:
        supply_advice = "市场**供不应求**明显，卖方市场，房价有上涨压力。"

    st.markdown(f"""
    <div class="card">
        <h3>市场周期分析</h3>
        <p>{market_advice}</p>
        <p>{supply_advice}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 成本对比图
    st.markdown('<div class="sub-header">成本对比趋势</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["累计成本对比", "有效成本对比", "详细数据"])
    
    with tab1:
        st.markdown("""
        **累计成本对比说明:**
        - **买房累计支出** = 首付 + 月供 + 持有成本
        - **租房累计支出** = 租金总额
        - **成本差额** = 租房成本 - 买房成本
        
        正的成本差额表示租房更贵，负的差额表示买房更贵。不考虑房产增值和投资收益。
        """)
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Scatter(
                x=results.index, 
                y=results['买房累计支出'], 
                name="买房累计支出",
                line=dict(color='#1E88E5', width=3)
            ),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(
                x=results.index, 
                y=results['租房累计支出'], 
                name="租房累计支出",
                line=dict(color='#FFC107', width=3)
            ),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(
                x=results.index, 
                y=results['成本差额(租-买)'], 
                name="成本差额(租-买)",
                line=dict(color='#4CAF50', width=2, dash='dash')
            ),
            secondary_y=True
        )
        
        # 添加收支平衡点标记
        if summary['break_even_year']:
            be_year = summary['break_even_year']
            if be_year <= living_years:
                # 找到最接近交叉点的年份
                years_array = np.array(results.index)
                closest_idx = np.abs(years_array - be_year).argmin()
                
                # 在图表上添加标记
                fig.add_trace(
                    go.Scatter(
                        x=[be_year],
                        y=[results.iloc[closest_idx]['买房累计支出']],
                        mode='markers',
                        marker=dict(
                            size=12,
                            symbol='star',
                            color='red'
                        ),
                        name="收支平衡点"
                    ),
                    secondary_y=False
                )
                
                # 添加标注
                fig.add_annotation(
                    x=be_year,
                    y=results.iloc[closest_idx]['买房累计支出'],
                    text=f"收支平衡: {be_year:.1f}年",
                    showarrow=True,
                    arrowhead=1,
                    ax=0,
                    ay=-40
                )
        
        fig.update_layout(
            title='买房vs租房累计成本对比',
            xaxis_title='年份',
            yaxis_title='累计成本(元)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="x unified",
            height=500,
            template="plotly_white"
        )
        
        fig.update_yaxes(title_text="累计成本(元)", secondary_y=False)
        fig.update_yaxes(title_text="成本差额(元)", secondary_y=True)
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("""
        **有效成本计算说明:**
        - **买房有效成本** = 直接买房支出 - (房产增值 - 首付)
        - **租房有效成本** = 租金支出 - 首付投资收益
        
        投资收益假设将等同于首付的资金按照设定的投资回报率进行投资所获得的收益。
        较高的投资回报率会降低租房的有效成本，使租房更有吸引力。
        """)
        
        fig = go.Figure()
        
        fig.add_trace(
            go.Scatter(
                x=results.index, 
                y=results['有效买房成本'], 
                name="有效买房成本",
                line=dict(color='#1E88E5', width=3)
            )
        )
        
        fig.add_trace(
            go.Scatter(
                x=results.index, 
                y=results['有效租房成本'], 
                name="有效租房成本",
                line=dict(color='#FFC107', width=3)
            )
        )
        
        # 添加收支平衡点标记
        if summary['break_even_year']:
            break_even_year = summary['break_even_year']
            if break_even_year <= living_years:
                break_even_value = results.loc[int(break_even_year), '有效买房成本']
                
                fig.add_trace(
                    go.Scatter(
                        x=[break_even_year],
                        y=[break_even_value],
                        mode='markers+text',
                        marker=dict(size=12, color='red', symbol='star'),
                        text=["收支平衡点"],
                        textposition="top center",
                        name="收支平衡点"
                    )
                )
        
        fig.update_layout(
            title='考虑机会成本和资产增值后的有效成本',
            xaxis_title='年份',
            yaxis_title='有效成本(元)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="x unified",
            height=500,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.dataframe(results)
    
    # 敏感度分析
    st.markdown('<div class="sub-header">参数敏感度分析</div>', unsafe_allow_html=True)
    
    sensitivity_tab1, sensitivity_tab2 = st.tabs(["房价与租金变化影响", "利率敏感度"])
    
    with sensitivity_tab1:
        # 添加中文字体支持
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'Arial']
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        
        # 创建房价和租金增长率变化的敏感度矩阵
        house_growth_range = np.linspace(house_price_growth - 5, house_price_growth + 5, 5)
        rent_growth_range = np.linspace(rent_growth - 5, rent_growth + 5, 5)
        
        break_even_matrix = np.zeros((len(house_growth_range), len(rent_growth_range)))
        
        for i, hg in enumerate(house_growth_range):
            for j, rg in enumerate(rent_growth_range):
                # 创建新参数集合
                new_params = params.copy()
                new_params['house_price_growth'] = hg
                new_params['rent_growth'] = rg
                
                # 计算新结果
                _, new_summary = calculate_buy_vs_rent(new_params)
                
                # 填充矩阵
                if new_summary['break_even_year']:
                    break_even_matrix[i, j] = new_summary['break_even_year']
                else:
                    break_even_matrix[i, j] = living_years + 5  # 表示超过居住年限
        
        # 创建热力图
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 格式化标签显示为百分比
        house_growth_labels = [f"{x:.1f}%" for x in house_growth_range]
        rent_growth_labels = [f"{x:.1f}%" for x in rent_growth_range]
        
        # 设置颜色映射，红色表示租房有利，绿色表示买房有利
        cmap = plt.cm.RdYlGn_r
        
        im = ax.imshow(break_even_matrix, cmap=cmap)
        
        # 添加数值标签
        for i in range(len(house_growth_range)):
            for j in range(len(rent_growth_range)):
                value = break_even_matrix[i, j]
                if value > living_years:
                    text = "超过\n计划期"
                else:
                    text = f"{int(value)}年"
                ax.text(j, i, text, ha="center", va="center", 
                        color="white" if 5 <= value <= living_years else "black",
                        fontweight='bold')
        
        # 设置坐标轴
        ax.set_xticks(np.arange(len(rent_growth_range)))
        ax.set_yticks(np.arange(len(house_growth_range)))
        ax.set_xticklabels(rent_growth_labels)
        ax.set_yticklabels(house_growth_labels)
        
        # 添加标题和标签
        plt.title("收支平衡年限敏感度分析")
        plt.xlabel("租金年增长率")
        plt.ylabel("房价年增长率")
        
        # 添加颜色条
        cbar = plt.colorbar(im)
        cbar.set_label('收支平衡年限')
        
        # 突出显示当前设置点
        current_house_growth_idx = np.argmin(np.abs(house_growth_range - house_price_growth))
        current_rent_growth_idx = np.argmin(np.abs(rent_growth_range - rent_growth))
        ax.plot(current_rent_growth_idx, current_house_growth_idx, 'o', markersize=12, 
                markerfacecolor='none', markeredgecolor='blue', markeredgewidth=2)
        
        plt.tight_layout()
        st.pyplot(fig)
    
    with sensitivity_tab2:
        # 添加中文字体支持
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'Arial']
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        
        # 创建贷款利率和投资回报率变化的敏感度矩阵
        loan_rate_range = np.linspace(max(loan_rate - 3, 1), loan_rate + 3, 5)
        investment_return_range = np.linspace(max(investment_return - 3, 1), investment_return + 3, 5)
        
        break_even_matrix = np.zeros((len(loan_rate_range), len(investment_return_range)))
        
        for i, lr in enumerate(loan_rate_range):
            for j, ir in enumerate(investment_return_range):
                # 创建新参数集合
                new_params = params.copy()
                new_params['loan_rate'] = lr
                new_params['investment_return'] = ir
                
                # 计算新结果
                _, new_summary = calculate_buy_vs_rent(new_params)
                
                # 填充矩阵
                if new_summary['break_even_year']:
                    break_even_matrix[i, j] = new_summary['break_even_year']
                else:
                    break_even_matrix[i, j] = living_years + 5  # 表示超过居住年限
        
        # 创建热力图
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 格式化标签显示为百分比
        loan_rate_labels = [f"{x:.1f}%" for x in loan_rate_range]
        investment_return_labels = [f"{x:.1f}%" for x in investment_return_range]
        
        # 设置颜色映射
        cmap = plt.cm.RdYlGn_r
        
        im = ax.imshow(break_even_matrix, cmap=cmap)
        
        # 添加数值标签
        for i in range(len(loan_rate_range)):
            for j in range(len(investment_return_range)):
                value = break_even_matrix[i, j]
                if value > living_years:
                    text = "超过\n计划期"
                else:
                    text = f"{int(value)}年"
                ax.text(j, i, text, ha="center", va="center", 
                        color="white" if 5 <= value <= living_years else "black",
                        fontweight='bold')
        
        # 设置坐标轴
        ax.set_xticks(np.arange(len(investment_return_range)))
        ax.set_yticks(np.arange(len(loan_rate_range)))
        ax.set_xticklabels(investment_return_labels)
        ax.set_yticklabels(loan_rate_labels)
        
        # 添加标题和标签
        plt.title("利率敏感度分析 - 收支平衡年限")
        plt.xlabel("投资回报率")
        plt.ylabel("贷款利率")
        
        # 添加颜色条
        cbar = plt.colorbar(im)
        cbar.set_label('收支平衡年限')
        
        # 突出显示当前设置点
        current_loan_rate_idx = np.argmin(np.abs(loan_rate_range - loan_rate))
        current_investment_return_idx = np.argmin(np.abs(investment_return_range - investment_return))
        ax.plot(current_investment_return_idx, current_loan_rate_idx, 'o', markersize=12, 
                markerfacecolor='none', markeredgecolor='blue', markeredgewidth=2)
        
        plt.tight_layout()
        st.pyplot(fig)

    # 添加决策矩阵部分
    st.markdown('<div class="sub-header">决策矩阵分析</div>', unsafe_allow_html=True)

    # 定义评分函数，生成经济性和灵活性得分
    def calculate_economic_score(params, summary):
        """计算长期经济性得分 (0-100)"""
        score = 50  # 中性起点
        
        # 价格租金比影响 (-20 到 +20)
        pr_ratio = summary['price_to_rent_ratio']
        if pr_ratio < 12:
            score += 20  # 买房极其有利
        elif pr_ratio < 15:
            score += 15  # 买房非常有利
        elif pr_ratio < 20:
            score += 5   # 买房略有优势
        elif pr_ratio > 30:
            score -= 20  # 租房极其有利
        elif pr_ratio > 25:
            score -= 15  # 租房非常有利
        elif pr_ratio > 20:
            score -= 5   # 租房略有优势
        
        # 收支平衡点影响 (-25 到 +25)
        living_years = params['living_years']
        if summary['break_even_year'] and summary['break_even_year'] <= living_years / 3:
            score += 25  # 买房极其有利
        elif summary['break_even_year'] and summary['break_even_year'] <= living_years / 2:
            score += 15  # 买房非常有利
        elif summary['break_even_year'] and summary['break_even_year'] <= living_years:
            score += 5   # 买房略有优势
        elif not summary['break_even_year']:
            score -= 25  # 租房极其有利
        else:
            score -= 10  # 租房有一定优势
        
        # 房价增长预期影响 (-15 到 +15)
        g_home = params['house_price_growth']
        if g_home > 8:
            score += 15  # 买房极其有利
        elif g_home > 5:
            score += 10  # 买房非常有利
        elif g_home > 3:
            score += 5   # 买房略有优势
        elif g_home < 0:
            score -= 15  # 租房极其有利
        elif g_home < 1:
            score -= 10  # 租房非常有利
        elif g_home < 3:
            score -= 5   # 租房略有优势
        
        # 投资回报率影响 (-15 到 +15)
        r_inv = params['investment_return']
        if r_inv > 10:
            score -= 15  # 租房极其有利
        elif r_inv > 8:
            score -= 10  # 租房非常有利
        elif r_inv > 6:
            score -= 5   # 租房略有优势
        elif r_inv < 2:
            score += 15  # 买房极其有利
        elif r_inv < 3:
            score += 10  # 买房非常有利
        elif r_inv < 4:
            score += 5   # 买房略有优势
        
        # 确保得分在0-100范围内
        return max(0, min(100, score))

    def calculate_flexibility_score(params, summary):
        """计算短期灵活性得分 (0-100)，高分表示更灵活"""
        score = 50  # 中性起点
        
        # 首付比例影响 (-20 到 +20)
        dp_percent = params['down_payment_percent']
        if dp_percent >= 70:
            score += 10  # 高首付增加灵活性
        elif dp_percent >= 50:
            score += 5   # 较高首付略增灵活性
        elif dp_percent <= 20:
            score -= 20  # 极低首付大幅降低灵活性
        elif dp_percent <= 30:
            score -= 10  # 低首付降低灵活性
        
        # 贷款压力影响 (-20 到 +20)
        rent_coverage = summary['rent_coverage_ratio']
        if rent_coverage > 150:
            score -= 20  # 租金远高于月供，买房更灵活
        elif rent_coverage > 120:
            score -= 10  # 租金高于月供，买房较灵活
        elif rent_coverage < 70:
            score += 20  # 月供远高于租金，租房更灵活
        elif rent_coverage < 90:
            score += 10  # 月供高于租金，租房较灵活
        
        # 资金占用影响 (恒定 -20 对买房)
        score += 20  # 租房更灵活，资金不会被房产占用
        
        # 居住年限影响
        living_years = params['living_years']
        if living_years <= 3:
            score += 15  # 短期居住，租房灵活性优势明显
        elif living_years <= 5:
            score += 10  # 中短期居住，租房有灵活性优势
        elif living_years >= 15:
            score -= 15  # 长期居住，买房灵活性成本降低
        elif living_years >= 10:
            score -= 10  # 中长期居住，买房灵活性成本较低
        
        # 确保得分在0-100范围内
        return max(0, min(100, score))

    # 计算经济性和灵活性得分
    economic_score = calculate_economic_score(params, summary)
    flexibility_score = calculate_flexibility_score(params, summary)

    # 决定买房租房在矩阵中的位置
    # 买房：经济性依赖计算得分，灵活性固定为低
    buy_economic = economic_score
    buy_flexibility = 25  # 固定值，买房灵活性较低

    # 租房：经济性是买房的对立面，灵活性固定为高
    rent_economic = 100 - economic_score
    rent_flexibility = 75  # 固定值，租房灵活性较高

    # 创建决策矩阵
    fig = go.Figure()

    # 添加象限分隔线
    fig.add_shape(
        type="line",
        x0=0, y0=50, x1=100, y1=50,
        line=dict(color="gray", width=1, dash="dash"),
    )

    fig.add_shape(
        type="line",
        x0=50, y0=0, x1=50, y1=100,
        line=dict(color="gray", width=1, dash="dash"),
    )

    # 添加象限标签
    fig.add_annotation(x=25, y=75, text="买房占优",
                    showarrow=False, font=dict(size=14))
    fig.add_annotation(x=75, y=75, text="需权衡考虑",
                    showarrow=False, font=dict(size=14))
    fig.add_annotation(x=25, y=25, text="需权衡考虑",
                    showarrow=False, font=dict(size=14))
    fig.add_annotation(x=75, y=25, text="租房占优",
                    showarrow=False, font=dict(size=14))

    # 添加买房和租房的点
    fig.add_trace(go.Scatter(
        x=[buy_flexibility], 
        y=[buy_economic],
        mode="markers+text",
        marker=dict(size=15, color="#1E88E5"),
        text=["买房"],
        textposition="top center",
        name="买房选项"
    ))

    fig.add_trace(go.Scatter(
        x=[rent_flexibility], 
        y=[rent_economic],
        mode="markers+text",
        marker=dict(size=15, color="#FFC107"),
        text=["租房"],
        textposition="top center",
        name="租房选项"
    ))

    # 添加当前状态指示
    current_situation = ""
    if buy_economic > 60 and buy_flexibility < 40:
        current_situation = "当前状态：买房具有明显的长期经济优势，但灵活性较低"
    elif rent_economic > 60 and rent_flexibility > 60:
        current_situation = "当前状态：租房具有明显的经济和灵活性双重优势"
    elif buy_economic > 60 and buy_flexibility > 60:
        current_situation = "当前状态：买房同时具有经济和灵活性优势（罕见情况）"
    elif rent_economic > 60 and rent_flexibility < 40:
        current_situation = "当前状态：租房具有经济优势但灵活性不足（罕见情况）"
    elif buy_economic > rent_economic:
        current_situation = "当前状态：买房经济性略占优势，需权衡灵活性需求"
    else:
        current_situation = "当前状态：租房经济性略占优势，且保持了较高灵活性"

    # 更新布局
    fig.update_layout(
        title=dict(
            text="买房vs租房决策矩阵",
            x=0.5,
            y=0.95
        ),
        xaxis=dict(
            title="短期灵活性",
            range=[0, 100],
            tickvals=[0, 25, 50, 75, 100],
            ticktext=["极低", "低", "中等", "高", "极高"]
        ),
        yaxis=dict(
            title="长期经济性",
            range=[0, 100],
            tickvals=[0, 25, 50, 75, 100],
            ticktext=["极低", "低", "中等", "高", "极高"]
        ),
        height=500,
        template="plotly_white",
        annotations=[
            dict(
                x=50,
                y=-0.15,
                xref="x domain",
                yref="y domain",
                text=current_situation,
                showarrow=False,
                font=dict(size=12)
            )
        ]
    )

    # 显示决策矩阵
    st.plotly_chart(fig, use_container_width=True)

    # 添加决策矩阵解释
    with st.expander("决策矩阵详细解释"):
        st.markdown(f"""
        ### 决策矩阵分析结果
        
        当前分析得分:
        - **买房经济性得分**: {buy_economic}/100
        - **租房经济性得分**: {rent_economic}/100
        - **买房灵活性得分**: {buy_flexibility}/100
        - **租房灵活性得分**: {rent_flexibility}/100
        
        ### 四个象限解释:
        
        1. **左上象限 (买房占优)**
        - 买房具有较高的长期经济回报
        - 灵活性限制在可接受范围内
        - 适合：预期长期稳定居住，且首付压力不大的情况
        
        2. **右上象限 (需权衡考虑)**
        - 经济上买房有优势
        - 但灵活性需求也很高
        - 适合：考虑折中方案，如购买小户型/可出租房产
        
        3. **左下象限 (需权衡考虑)**
        - 经济上租房有优势
        - 但需要稳定性
        - 适合：考虑长期租约或寻找价格更合理的购房选择
        
        4. **右下象限 (租房占优)**
        - 租房既经济又灵活
        - 买房无明显优势
        - 适合：预期生活变动较多或房价过高的情况
        
        ### 影响因素:
        
        **经济性评分考虑因素:**
        - 价格租金比: {summary['price_to_rent_ratio']:.1f}倍
        - 收支平衡年限: {summary['break_even_year'] if summary['break_even_year'] else '超出计划期限'}
        - 房价年增长预期: {params['house_price_growth']}%
        - 投资回报率: {params['investment_return']}%
        
        **灵活性评分考虑因素:**
        - 首付比例: {params['down_payment_percent']}%
        - 租金覆盖率: {summary['rent_coverage_ratio']:.1f}%
        - 计划居住年限: {params['living_years']}年
        """)

    # 添加个性化建议
    matrix_recommendation = ""
    if buy_economic >= 70 and buy_flexibility >= 40:
        matrix_recommendation = """
        <div class="recommendation-buy">
            <h3>矩阵分析结果: 强烈推荐买房</h3>
            <p>当前市场和个人条件下，买房不仅具有出色的长期经济效益，灵活性限制也在可接受范围内。这是购房的理想时机。</p>
        </div>
        """
    elif buy_economic >= 60 and buy_flexibility < 40:
        matrix_recommendation = """
        <div class="recommendation-buy">
            <h3>矩阵分析结果: 建议买房，但注意流动性</h3>
            <p>买房具有良好的长期经济效益，但会限制您的资金流动性。若您重视长期稳定性且有足够的剩余资金应对紧急情况，买房是合适的选择。</p>
        </div>
        """
    elif rent_economic >= 70 and rent_flexibility >= 60:
        matrix_recommendation = """
        <div class="recommendation-rent">
            <h3>矩阵分析结果: 强烈推荐租房</h3>
            <p>当前条件下，租房同时具备经济和灵活性双重优势。房价可能偏高，租房能够保持资金流动性并获得更好的经济回报。</p>
        </div>
        """
    elif rent_economic >= 60 and rent_flexibility >= 50:
        matrix_recommendation = """
        <div class="recommendation-rent">
            <h3>矩阵分析结果: 倾向于租房</h3>
            <p>从综合分析看，租房提供了更好的经济和灵活性平衡。特别是如果您对未来居住地有不确定性，租房更为明智。</p>
        </div>
        """
    else:
        matrix_recommendation = """
        <div class="recommendation-neutral">
            <h3>矩阵分析结果: 需要权衡考虑</h3>
            <p>买房和租房各有优劣，没有明显的优势选项。请结合个人生活规划、风险偏好和情感因素做出决策。</p>
            <p>可以考虑的折中方案：
            - 购买小户型或可出租的房产，提高灵活性
            - 寻找更长期的租约，增加稳定性
            - 再等待一段时间，观察市场变化
            </p>
        </div>
        """

    st.markdown(matrix_recommendation, unsafe_allow_html=True)

    # 情景分析功能
    st.markdown("### 情景分析")
    scenario_cols = st.columns(4)

    with scenario_cols[0]:
        scenario_price_growth = st.slider(
            "假设房价年增长率", 
            min_value=-10.0, 
            max_value=15.0, 
            value=house_price_growth, 
            step=0.5,
            format="%.1f%%",
            key="scenario_price"
        )
        
    with scenario_cols[1]:
        scenario_rent_growth = st.slider(
            "假设租金年增长率", 
            min_value=-5.0, 
            max_value=15.0, 
            value=rent_growth, 
            step=0.5,
            format="%.1f%%",
            key="scenario_rent"
        )
        
    with scenario_cols[2]:
        scenario_investment = st.slider(
            "假设投资回报率", 
            min_value=1.0, 
            max_value=15.0, 
            value=investment_return, 
            step=0.5,
            format="%.1f%%",
            key="scenario_inv"
        )

    with scenario_cols[3]:
        run_scenario = st.button("运行情景分析")

    if run_scenario:
        # 创建新的参数集合
        scenario_params = params.copy()
        scenario_params['house_price_growth'] = scenario_price_growth
        scenario_params['rent_growth'] = scenario_rent_growth
        scenario_params['investment_return'] = scenario_investment
        
        # 计算新的结果
        scenario_results, scenario_summary = calculate_buy_vs_rent(scenario_params)
        
        # 计算新的矩阵位置
        scenario_economic_score = calculate_economic_score(scenario_params, scenario_summary)
        scenario_flexibility_score = calculate_flexibility_score(scenario_params, scenario_summary)
        
        scenario_buy_economic = scenario_economic_score
        scenario_buy_flexibility = 25
        scenario_rent_economic = 100 - scenario_economic_score
        scenario_rent_flexibility = 75
        
        # 显示情景分析结果
        st.markdown("#### 情景分析结果")
        
        scenario_cols = st.columns(2)
        with scenario_cols[0]:
            st.metric("情景收支平衡年限", 
                    f"{scenario_summary['break_even_year']:.1f}年" if scenario_summary['break_even_year'] else "超过计划期限", 
                    f"{scenario_summary['break_even_year'] - summary['break_even_year']:.1f}年" if scenario_summary['break_even_year'] and summary['break_even_year'] else "无法比较")
        
        with scenario_cols[1]:
            st.metric("情景买房经济性得分", 
                    f"{scenario_buy_economic:.1f}/100", 
                    f"{scenario_buy_economic - buy_economic:.1f}")
        
        # 创建情景分析矩阵图
        fig = go.Figure()

        # 添加象限分隔线
        fig.add_shape(
            type="line",
            x0=0, y0=50, x1=100, y1=50,
            line=dict(color="gray", width=1, dash="dash"),
        )

        fig.add_shape(
            type="line",
            x0=50, y0=0, x1=50, y1=100,
            line=dict(color="gray", width=1, dash="dash"),
        )

        # 添加原始买房和租房的点
        fig.add_trace(go.Scatter(
            x=[buy_flexibility], 
            y=[buy_economic],
            mode="markers+text",
            marker=dict(size=12, color="#1E88E5"),
            text=["买房(当前)"],
            textposition="top center",
            name="买房(当前)"
        ))

        fig.add_trace(go.Scatter(
            x=[rent_flexibility], 
            y=[rent_economic],
            mode="markers+text",
            marker=dict(size=12, color="#FFC107"),
            text=["租房(当前)"],
            textposition="top center",
            name="租房(当前)"
        ))

        # 添加情景分析的点
        fig.add_trace(go.Scatter(
            x=[scenario_buy_flexibility], 
            y=[scenario_buy_economic],
            mode="markers+text",
            marker=dict(size=15, color="#1E88E5", symbol="star"),
            text=["买房(情景)"],
            textposition="top center",
            name="买房(情景)"
        ))

        fig.add_trace(go.Scatter(
            x=[scenario_rent_flexibility], 
            y=[scenario_rent_economic],
            mode="markers+text",
            marker=dict(size=15, color="#FFC107", symbol="star"),
            text=["租房(情景)"],
            textposition="top center",
            name="租房(情景)"
        ))

        # 添加连接线
        fig.add_trace(go.Scatter(
            x=[buy_flexibility, scenario_buy_flexibility],
            y=[buy_economic, scenario_buy_economic],
            mode="lines",
            line=dict(color="#1E88E5", width=1, dash="dot"),
            showlegend=False
        ))

        fig.add_trace(go.Scatter(
            x=[rent_flexibility, scenario_rent_flexibility],
            y=[rent_economic, scenario_rent_economic],
            mode="lines",
            line=dict(color="#FFC107", width=1, dash="dot"),
            showlegend=False
        ))

        # 更新布局
        fig.update_layout(
            title="情景分析决策矩阵比较",
            xaxis=dict(
                title="短期灵活性",
                range=[0, 100],
                tickvals=[0, 25, 50, 75, 100],
                ticktext=["极低", "低", "中等", "高", "极高"]
            ),
            yaxis=dict(
                title="长期经济性",
                range=[0, 100],
                tickvals=[0, 25, 50, 75, 100],
                ticktext=["极低", "低", "中等", "高", "极高"]
            ),
            height=500,
            template="plotly_white"
        )

        st.plotly_chart(fig, use_container_width=True)
        
        # 显示情景分析建议
        if scenario_buy_economic - buy_economic > 10:
            st.success("情景分析表明：在这种情况下，买房的经济性大幅提升，更加有利")
        elif scenario_buy_economic - buy_economic < -10:
            st.error("情景分析表明：在这种情况下，买房的经济性显著下降，租房更为有利")
        else:
            st.info("情景分析表明：在这种情况下，经济性变化不大，决策不会有根本改变")

    # 综合风险评估部分
    st.markdown('<div class="sub-header">风险评估</div>', unsafe_allow_html=True)

    # 创建风险评估卡片
    risk_factors = [
        {
            "name": "流动性风险",
            "buy_score": 7,  # 1-10，越高风险越大
            "rent_score": 2,
            "description": "买房锁定大量资金，可能影响应对紧急情况的能力"
        },
        {
            "name": "财务压力",
            "buy_score": 8 if summary['monthly_payment'] > monthly_rent * 1.5 else 5,
            "rent_score": 3,
            "description": "高额月供可能造成长期财务压力"
        },
        {
            "name": "资产集中度",
            "buy_score": 9,
            "rent_score": 3,
            "description": "买房导致资产高度集中在单一不动产"
        },
        {
            "name": "市场风险",
            "buy_score": 6 if house_price_growth > inflation_rate else 8,
            "rent_score": 4,
            "description": "房价波动风险，特别是在价格高位购买"
        },
        {
            "name": "灵活性限制",
            "buy_score": 8,
            "rent_score": 2,
            "description": "买房降低职业和生活方式变动的灵活性"
        }
    ]

    # 计算买房和租房的总体风险分数
    buy_risk_score = sum([f["buy_score"] for f in risk_factors]) / len(risk_factors)
    rent_risk_score = sum([f["rent_score"] for f in risk_factors]) / len(risk_factors)

    # 显示风险雷达图
    risk_labels = [f["name"] for f in risk_factors]
    buy_scores = [f["buy_score"] for f in risk_factors]
    rent_scores = [f["rent_score"] for f in risk_factors]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=buy_scores,
        theta=risk_labels,
        fill='toself',
        name='买房风险'
    ))

    fig.add_trace(go.Scatterpolar(
        r=rent_scores,
        theta=risk_labels,
        fill='toself',
        name='租房风险'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )
        ),
        showlegend=True,
        title="买房vs租房风险对比",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    # 添加风险解释
    with st.expander("风险因素详细解释"):
        for factor in risk_factors:
            st.markdown(f"**{factor['name']}** (买房: {factor['buy_score']}/10, 租房: {factor['rent_score']}/10)")
            st.markdown(f"{factor['description']}")
            st.markdown("---")

with main_col2:
    # 财务摘要
    st.markdown('<div class="sub-header">财务摘要</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("首付款", f"{summary['down_payment']:,.0f}元", 
                 f"{summary['down_payment']/house_price*100:.1f}%")
    with col2:
        st.metric("月供", f"{summary['monthly_payment']:,.0f}元/月", 
                 f"{summary['monthly_payment']*12/summary['total_mortgage_payment']*100:.1f}%年")
    
    # 如果使用了公积金贷款，显示贷款明细
    if params.get('use_housing_fund', False) and summary['housing_fund_amount'] > 0:
        st.markdown('<div class="card"><h3>贷款明细</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("公积金贷款", f"{summary['housing_fund_amount']:,.0f}元", 
                     f"{summary['housing_fund_amount']/(summary['housing_fund_amount'] + summary['commercial_loan_amount'])*100:.1f}%总贷款")
        with col2:
            st.metric("公积金月供", f"{summary['housing_fund_monthly_payment']:,.0f}元/月", 
                     f"{summary['housing_fund_interest_rate']:.1f}%利率")
            
        col1, col2 = st.columns(2)
        with col1:
            st.metric("商业贷款", f"{summary['commercial_loan_amount']:,.0f}元", 
                     f"{summary['commercial_loan_amount']/(summary['housing_fund_amount'] + summary['commercial_loan_amount'])*100:.1f}%总贷款")
        with col2:
            st.metric("商业贷款月供", f"{summary['commercial_monthly_payment']:,.0f}元/月", 
                     f"{summary['commercial_interest_rate']:.1f}%利率")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if loan_amount > 0:  # 防止除以零错误
            interest_text = f"{summary['total_mortgage_payment']/loan_amount*100-100:.1f}%利息"
        else:
            interest_text = "全款购房"
        st.metric("总贷款支出", f"{summary['total_mortgage_payment']:,.0f}元", interest_text)
    with col2:
        st.metric("总房屋持有成本", f"{summary['total_holding_cost']:,.0f}元", 
                 help="持有房产期间的所有费用总和，包括物业费、维修费、房产税等")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("总租金支出", f"{summary['total_rent_cost']:,.0f}元")
    with col2:
        st.metric("首付投资收益", f"{summary['investment_return']:,.0f}元", 
                 f"{summary['investment_return']/summary['down_payment']*100:.1f}%",
                 help="如果将首付款用于投资，在同期内可能获得的收益，反映了买房的机会成本")
    
    # 添加月供收入比和资产配置评估
    if monthly_income > 0:
        mortgage_to_income_ratio = summary['monthly_payment'] / monthly_income * 100
        rent_to_income_ratio = monthly_rent / monthly_income * 100
        
        col1, col2 = st.columns(2)
        with col1:
            color = "normal" if mortgage_to_income_ratio <= 40 else "off"
            st.metric("月供收入比", f"{mortgage_to_income_ratio:.1f}%", 
                     delta=f"{'安全' if mortgage_to_income_ratio <= 30 else '警戒' if mortgage_to_income_ratio <= 40 else '压力大'}", 
                     delta_color=f"{'normal' if mortgage_to_income_ratio <= 30 else 'off' if mortgage_to_income_ratio <= 40 else 'inverse'}")
        with col2:
            st.metric("租金收入比", f"{rent_to_income_ratio:.1f}%",
                     delta=f"{'安全' if rent_to_income_ratio <= 30 else '警戒' if rent_to_income_ratio <= 40 else '压力大'}", 
                     delta_color=f"{'normal' if rent_to_income_ratio <= 30 else 'off' if rent_to_income_ratio <= 40 else 'inverse'}")

    if total_assets > 0:
        down_payment_to_assets_ratio = down_payment / total_assets * 100
        st.metric("首付占总资产比", f"{down_payment_to_assets_ratio:.1f}%",
                 delta=f"{'分散' if down_payment_to_assets_ratio <= 40 else '集中' if down_payment_to_assets_ratio <= 60 else '高度集中'}", 
                 delta_color=f"{'normal' if down_payment_to_assets_ratio <= 40 else 'off' if down_payment_to_assets_ratio <= 60 else 'inverse'}")
    
    # 最终房产估值卡片
    st.markdown(f"""
    <div class="card">
        <h3>最终房产估值 ({living_years}年后)</h3>
        <h2 style="color:#1E88E5;">{summary['final_property_value']:,.0f}元</h2>
        <p>增值: {summary['final_property_value']-house_price:,.0f}元 
           ({(summary['final_property_value']/house_price-1)*100:.1f}%)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 个人因素评估
    st.markdown('<div class="sub-header">个人因素评估</div>', unsafe_allow_html=True)
    
    # 基于个人因素打分
    personal_buy_score = 0
    personal_rent_score = 0
    
    # 职业稳定性影响
    if career_stability >= 8:
        personal_buy_score += 15
    elif career_stability >= 5:
        personal_buy_score += 5
    else:
        personal_rent_score += 15
    
    # 家庭计划影响
    if family_plan == "扩大家庭":
        personal_buy_score += 10
    elif family_plan == "缩小家庭":
        personal_rent_score += 5
    elif family_plan == "不确定":
        personal_rent_score += 10
    
    # 流动性需求影响
    if mobility_need >= 7:
        personal_rent_score += 15
    elif mobility_need <= 3:
        personal_buy_score += 15
    
    # 所有权重要性
    if ownership_importance >= 8:
        personal_buy_score += 15
    elif ownership_importance <= 3:
        personal_rent_score += 10
    
    # 归一化分数到100分制
    max_possible_score = 40  # 根据上面规则的最大可能得分
    personal_buy_score = (personal_buy_score / max_possible_score) * 100
    personal_rent_score = (personal_rent_score / max_possible_score) * 100
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("个人因素-买房倾向", f"{personal_buy_score:.0f}/100")
    with col2:
        st.metric("个人因素-租房倾向", f"{personal_rent_score:.0f}/100")
    
    # 个人因素推荐
    personal_recommendation = ""
    if personal_buy_score > personal_rent_score + 20:
        personal_recommendation = "从个人因素考虑，**强烈建议买房**。您的职业稳定性高、家庭需求明确，且重视房屋所有权。"
    elif personal_buy_score > personal_rent_score:
        personal_recommendation = "从个人因素考虑，**偏向于买房**。您的个人情况比较适合置业，但仍有一些灵活性需求。"
    elif personal_rent_score > personal_buy_score + 20:
        personal_recommendation = "从个人因素考虑，**强烈建议租房**。您可能有较高的流动性需求或职业变动可能性。"
    elif personal_rent_score > personal_buy_score:
        personal_recommendation = "从个人因素考虑，**偏向于租房**。您的个人情况目前可能更适合保持灵活性。"
    else:
        personal_recommendation = "从个人因素考虑，买房和租房没有明显偏好，可以更多关注财务因素。"
    
    st.markdown(f"""
    <div class="card">
        <h3>个人因素建议</h3>
        <p>{personal_recommendation}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 资产配置建议
    if summary['break_even_year'] and summary['break_even_year'] <= living_years / 2:
        asset_advice = """
        <div class="card">
            <h3>资产配置建议</h3>
            <p><strong>买房优势明显</strong> - 考虑以下建议：</p>
            <ul>
                <li>提高首付比例，降低贷款利息支出</li>
                <li>考虑较短贷款年限，减少总利息</li>
                <li>规划好房屋维护基金</li>
            </ul>
        </div>
        """
    elif not summary['break_even_year'] or summary['break_even_year'] > living_years:
        asset_advice = """
        <div class="card">
            <h3>资产配置建议</h3>
            <p><strong>租房优势明显</strong> - 考虑以下建议：</p>
            <ul>
                <li>将首付等同资金投资于多元化资产组合</li>
                <li>寻找长期租约，锁定租金增长</li>
                <li>规划好资产增值策略</li>
            </ul>
        </div>
        """
    else:
        asset_advice = """
        <div class="card">
            <h3>资产配置建议</h3>
            <p><strong>买租各有优势</strong> - 考虑以下因素：</p>
            <ul>
                <li>评估生活稳定性和流动性需求</li>
                <li>权衡房产增值预期和投资收益率</li>
                <li>兼顾个人偏好和家庭长期规划</li>
            </ul>
        </div>
        """
    
    st.markdown(asset_advice, unsafe_allow_html=True)
    
    # 非财务因素考量清单
    with st.expander("除财务外的考虑因素"):
        st.markdown("""
        ### 买房优势
        - **稳定性**: 不受房东决策影响，可自由装修和改造
        - **资产建设**: 随时间推移建立房产净值，可能成为重要资产
        - **心理安全感**: 拥有自己的住所带来的安全感和归属感
        - **税收优惠**: 部分地区有房贷利息抵税等政策
        - **抗通胀**: 房产通常是良好的通胀对冲工具
        
        ### 租房优势
        - **高流动性**: 维持较高财务流动性，应对紧急情况能力强
        - **生活灵活性**: 易于搬迁，适应工作和生活变化
        - **省心**: 无需承担维修、物业等责任
        - **资产配置灵活**: 可将资金投资于更多元化的资产组合
        - **居住选择多样**: 可能住在买不起的高价值区域
        
        ### 个人情况评估清单
        - [ ] 未来5年的工作和居住地是否可能变动？
        - [ ] 首付支出是否影响应急资金和退休规划？
        - [ ] 是否有能力应对房屋的突发维修和额外费用？
        - [ ] 家庭规模是否在未来几年可能发生变化？
        - [ ] 您是否有足够时间和精力处理房屋维护问题？
        """)
    
    # 房贷和投资收益对比
    st.markdown('<div class="sub-header">房贷与投资收益对比</div>', unsafe_allow_html=True)
    
    # 创建房贷与投资收益对比图
    loan_payments = np.zeros(living_years)
    investment_values = np.zeros(living_years)
    property_values = np.zeros(living_years)
    
    down_payment = house_price * down_payment_percent / 100
    monthly_payment = summary['monthly_payment']
    
    for i in range(living_years):
        # 计算房贷总支出（首付+累计月供）
        if i == 0:
            loan_payments[i] = down_payment + monthly_payment * 12
        else:
            loan_payments[i] = loan_payments[i-1] + monthly_payment * 12
        
        # 计算等额首付投资收益
        if use_real_returns:
            r_inv_real = (1 + investment_return / 100) / (1 + inflation_rate / 100) - 1
        else:
            r_inv_real = investment_return / 100
        investment_values[i] = down_payment * (1 + r_inv_real) ** (i + 1)
        
        # 计算房产价值
        property_values[i] = house_price * (1 + house_price_growth / 100) ** (i + 1)
    
    # 创建对比图
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=list(range(1, living_years + 1)), 
            y=loan_payments, 
            name="买房累计支出",
            line=dict(color='#FFC107', width=3)
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=list(range(1, living_years + 1)), 
            y=investment_values, 
            name="首付投资收益",
            line=dict(color='#4CAF50', width=3)
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=list(range(1, living_years + 1)), 
            y=property_values, 
            name="房产估值",
            line=dict(color='#1E88E5', width=3, dash='dash')
        )
    )
    
    fig.update_layout(
        title='投资收益与房产价值对比',
        xaxis_title='年份',
        yaxis_title='金额(元)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
        height=400,
        template="plotly_white"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 帮助文档
    with st.expander("公式说明"):
        st.markdown("""
        ### 核心计算公式
        
        #### 买房成本模型
        - **总成本** = 首付 + 月供总额 + 持有成本 - 房产残值
        - **月供计算** (等额本息): $M = P \\times \\frac{r(1+r)^n}{(1+r)^n-1}$
          - $M$: 月供
          - $P$: 贷款本金
          - $r$: 月利率
          - $n$: 还款月数
        - **持有成本** = (物业费×面积 + 维修基金 + 房产税×房价)×每年累计
        - **房产残值** = 房价×(1+年增值率)^居住年限
        
        #### 组合贷款计算
        - **总月供** = 公积金贷款月供 + 商业贷款月供
        - **公积金贷款月供**: 使用公积金贷款利率(通常3.1%)计算的月供
        - **商业贷款月供**: 使用商业贷款利率计算的月供
        - **公积金贷款优势**: 利率较低，可减轻总体月供压力
        
        #### 租房成本模型
        - **总成本** = 租金总额 + 机会成本 - 投资收益
        - **租金总额** = 初始月租×12×[1-(1+年租金增长率)^居住年限]/(1-年租金增长率)
        - **机会成本** = 首付金额×(1+投资回报率)^居住年限 - 首付金额
        
        #### 关键指标计算
        - **价格租金比** = 房价/(月租×12)
        - **收支平衡年限**: 租房总成本超过买房总成本的年限
        - **租金覆盖率** = 月租金/月供×100%
        
        ### 实际收益率计算
        当启用"考虑通货膨胀"选项时，实际收益率按以下公式计算:
        - **实际收益率** = (1+名义收益率)/(1+通货膨胀率) - 1
        """)
    
    with st.expander("常见问题"):
        st.markdown("""
        ### 常见问题解答
        
        **Q: 如何设置公积金贷款?**  
        A: 上海地区公积金贷款最高额度为单人80万，夫妻共同申请最高160万。公积金贷款利率一般低于商业贷款利率，目前基准利率为3.1%。使用公积金贷款可以显著降低月供压力。
        
        **Q: 如何估算房价涨幅？**  
        A: 可以参考当地过去5-10年的房价历史数据，分析平均年化增长率。也可查询当地房产研究机构发布的预测报告。通常，长期房价涨幅与GDP增长和通货膨胀有一定相关性。
        
        **Q: 投资回报率应如何设置？**  
        A: 这取决于您的风险偏好和投资策略。保守型投资者可参考银行定期存款(2-3%)或债券收益率(3-5%)；平衡型投资者可参考混合型基金(5-8%)；积极型投资者可参考股票市场长期回报率(8-10%)。
        
        **Q: 价格租金比多少合理？**  
        A: 国际公认的合理区间通常在15-20之间。如果比值<15，一般认为买入更有优势；如果比值>30，则租房可能更经济。不同城市和地区会有差异。
        
        **Q: 为什么要考虑实际收益率？**  
        A: 通货膨胀会侵蚀名义回报的购买力。例如，如果名义收益率为6%，通货膨胀率为2%，则实际收益率约为3.9%。在长期财务规划中，使用实际收益率可更准确评估投资的真实增值。
        """)

with st.expander("决策指标详细解释"):
    st.markdown("""
    **我们的建议综合考虑了两个关键指标：**
    
    1. **价格租金比**：房价与年租金总额的比值
       - **<15**：房价相对租金较低，通常买房更经济
       - **15-25**：市场公认的合理范围，需考虑其他因素
       - **>25**：房价相对租金较高，通常租房更经济
    
    2. **收支平衡年限**：租房累计成本超过买房累计成本的时间点
       - **短于计划居住期一半**：买房通常更有优势
       - **长于计划居住期**：租房通常更有优势
       - **介于两者之间**：需要考虑其他因素
    
    3. **其他重要考量因素**：
       - **财务因素**：首付资金占比、月供收入比、资产多元化
       - **市场因素**：房地产周期、供需状况、政策环境
       - **个人因素**：职业稳定性、家庭规划、生活方式偏好
    
    当两个核心指标给出一致建议时，决策较为明确；当存在分歧时，需要结合个人情况、风险偏好和对未来预期进行综合判断。
    """)

# 添加报告生成功能
st.markdown('<div class="sub-header">报告生成</div>', unsafe_allow_html=True)
report_col1, report_col2 = st.columns(2)

def generate_excel():
    """生成Excel格式报告"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # 添加参数表
        params_list = [{
            '参数名': '房价',
            '符号': 'P',
            '值': f"{house_price:,.0f}元",
            '说明': '目标房产总价'
        }, {
            '参数名': '首付比例',
            '符号': 'dp',
            '值': f"{down_payment_percent}%",
            '说明': '首付款占比'
        }, {
            '参数名': '贷款年限',
            '符号': 'n_loan',
            '值': f"{loan_years}年",
            '说明': '按揭贷款期限'
        }, {
            '参数名': '贷款利率',
            '符号': 'r_loan',
            '值': f"{loan_rate}%/年",
            '说明': '商业贷款年利率'
        }, {
            '参数名': '月租金',
            '符号': 'rent',
            '值': f"{monthly_rent:,.0f}元/月",
            '说明': '当前市场租金'
        }, {
            '参数名': '租金年涨幅',
            '符号': 'g_rent',
            '值': f"{rent_growth}%/年",
            '说明': '租金年均增长率'
        }, {
            '参数名': '投资回报率',
            '符号': 'r_inv',
            '值': f"{investment_return}%/年",
            '说明': '首付款替代投资年化收益'
        }, {
            '参数名': '物业费',
            '符号': 'fee',
            '值': f"{property_fee}元/m²/月",
            '说明': '物业管理费单价'
        }, {
            '参数名': '房产税率',
            '符号': 'tax',
            '值': f"{property_tax}%/年",
            '说明': '房产评估价值年税率'
        }, {
            '参数名': '维修基金',
            '符号': 'maint',
            '值': f"{maintenance_fund:,.0f}元/年",
            '说明': '年均房屋维护费用'
        }, {
            '参数名': '计划居住年限',
            '符号': 'n_live',
            '值': f"{living_years}年",
            '说明': '预计持有/租住时长'
        }, {
            '参数名': '房价年涨幅',
            '符号': 'g_home',
            '值': f"{house_price_growth}%/年",
            '说明': '预期房产年均增值率'
        }, {
            '参数名': '通货膨胀率',
            '符号': 'inflation',
            '值': f"{inflation_rate}%/年",
            '说明': '年度通货膨胀率'
        }]
        
        # 添加公积金贷款参数
        if params.get('use_housing_fund', False):
            params_list.extend([{
                '参数名': '公积金贷款',
                '符号': 'HF',
                '值': f"{params.get('housing_fund_amount', 0):,.0f}元",
                '说明': '公积金贷款金额'
            }, {
                '参数名': '公积金贷款利率',
                '符号': 'r_hf',
                '值': f"{params.get('housing_fund_rate', 3.1)}%/年",
                '说明': '公积金贷款年利率'
            }])

        params_df = pd.DataFrame(params_list)
        params_df.to_excel(writer, sheet_name='参数设置', index=False)
        
        # 添加结果表
        results.to_excel(writer, sheet_name='详细数据', index_label='年份')
        
        # 添加摘要表
        summary_list = [{
            '指标': '价格租金比',
            '值': f"{summary['price_to_rent_ratio']:.1f}",
            '说明': '房价相当于多少年的租金总和'
        }, {
            '指标': '收支平衡年限',
            '值': f"{summary['break_even_year'] if summary['break_even_year'] else '超过计划居住期'}",
            '说明': '租房成本超过买房成本的时间点'
        }, {
            '指标': '租金覆盖率',
            '值': f"{summary['rent_coverage_ratio']:.1f}%",
            '说明': '月租金占月供的百分比'
        }, {
            '指标': '首付金额',
            '值': f"{summary['down_payment']:,.0f}元",
            '说明': '房价的首付款金额'
        }, {
            '指标': '月供',
            '值': f"{summary['monthly_payment']:,.0f}元/月",
            '说明': '每月按揭还款金额'
        }, {
            '指标': '总贷款支出',
            '值': f"{summary['total_mortgage_payment']:,.0f}元",
            '说明': '贷款期内所有还款总额'
        }, {
            '指标': '总房屋持有成本',
            '值': f"{summary['total_holding_cost']:,.0f}元",
            '说明': '物业费、维修费和房产税总和'
        }, {
            '指标': '总租金支出',
            '值': f"{summary['total_rent_cost']:,.0f}元",
            '说明': '租房期内所有租金总和'
        }, {
            '指标': '首付投资收益',
            '值': f"{summary['investment_return']:,.0f}元",
            '说明': '首付金额投资后的收益'
        }, {
            '指标': '最终房产估值',
            '值': f"{summary['final_property_value']:,.0f}元",
            '说明': f"{living_years}年后的房产价值"
        }, {
            '指标': '买房经济性得分',
            '值': f"{buy_economic:.1f}/100",
            '说明': '买房在决策矩阵中的经济性评分'
        }, {
            '指标': '买房灵活性得分',
            '值': f"{buy_flexibility:.1f}/100",
            '说明': '买房在决策矩阵中的灵活性评分'
        }, {
            '指标': '租房经济性得分',
            '值': f"{rent_economic:.1f}/100",
            '说明': '租房在决策矩阵中的经济性评分'
        }, {
            '指标': '租房灵活性得分',
            '值': f"{rent_flexibility:.1f}/100",
            '说明': '租房在决策矩阵中的灵活性评分'
        }]

        if params.get('use_housing_fund', False):
            summary_list.extend([{
                '指标': '公积金贷款金额',
                '值': f"{summary['housing_fund_amount']:,.0f}元",
                '说明': '使用的公积金贷款金额'
            }, {
                '指标': '公积金贷款月供',
                '值': f"{summary['housing_fund_monthly_payment']:,.0f}元/月",
                '说明': '公积金贷款部分的月供'
            }, {
                '指标': '商业贷款金额',
                '值': f"{summary['commercial_loan_amount']:,.0f}元",
                '说明': '使用的商业贷款金额'
            }, {
                '指标': '商业贷款月供',
                '值': f"{summary['commercial_monthly_payment']:,.0f}元/月",
                '说明': '商业贷款部分的月供'
            }])

        summary_df = pd.DataFrame(summary_list)
        summary_df.to_excel(writer, sheet_name='摘要指标', index=False)
        
        # 配置工作簿
        workbook = writer.book
        
        # 格式化数字
        number_format = workbook.add_format({'num_format': '#,##0'})
        percent_format = workbook.add_format({'num_format': '0.0%'})
        
        # 设置列宽
        worksheet = writer.sheets['详细数据']
        worksheet.set_column('A:H', 15, number_format)
    
    output.seek(0)
    return output

# 添加报告下载按钮
with report_col1:
    excel_data = generate_excel()
    st.download_button(
        label="下载Excel报告",
        data=excel_data,
        file_name=f"买房vs租房分析_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

with report_col2:
    # 保存参数配置
    if st.button("保存当前参数配置"):
        # 这里只是示例，实际的持久化需要使用数据库或文件系统
        st.session_state['saved_configs'] = st.session_state.get('saved_configs', []) + [params]
        st.success(f"参数配置已保存! 当前共有 {len(st.session_state.get('saved_configs', []))} 组配置")

# 页脚
st.markdown("""
---
<div style="text-align:center; color:#666; padding:20px;">
买房 vs 租房决策分析工具 | © 2025 | 版本 1.0<br>
基于Streamlit开发 | 使用Plotly和Matplotlib进行数据可视化
</div>
""", unsafe_allow_html=True)
