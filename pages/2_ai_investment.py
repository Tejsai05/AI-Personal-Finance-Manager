"""
Page 2: AI Investment Suggestions
ML/RL-powered investment allocation recommendations
"""
import streamlit as st
import sys
sys.path.append('..')

from config.settings import settings

# Try to import ML models with graceful fallback
try:
    from ml_models.rl_portfolio import get_optimal_allocation
except Exception as e:
    st.warning(f"⚠️ RL Portfolio module unavailable: {type(e).__name__}")
    get_optimal_allocation = None

try:
    from ml_models.xgboost_returns import predict_investment_return
except Exception as e:
    st.warning(f"⚠️ XGBoost returns module unavailable: {type(e).__name__}")
    predict_investment_return = None

try:
    from agents.ai_agents import investment_agent, risk_agent
except Exception as e:
    st.warning(f"⚠️ AI Agents unavailable: {type(e).__name__}")
    investment_agent = None
    risk_agent = None

st.set_page_config(page_title="AI Investment Suggestions", page_icon="🤖", layout="wide")

st.title("🤖 AI-Powered Investment Suggestions")
st.markdown("Get personalized investment recommendations based on your risk profile and financial goals")

# User inputs
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 💰 Financial Information")
    
    salary = st.number_input(
        "Monthly Salary (₹)",
        min_value=0.0,
        value=50000.0,
        step=1000.0,
        format="%.2f"
    )
    
    expenses = st.number_input(
        "Monthly Expenses (₹)",
        min_value=0.0,
        value=30000.0,
        step=1000.0,
        format="%.2f"
    )
    
    other_income = st.number_input(
        "Other Income (₹)",
        min_value=0.0,
        value=0.0,
        step=1000.0,
        format="%.2f"
    )
    
    investable = salary + other_income - expenses
    
    st.info(f"**💵 Investable Amount:** ₹{investable:,.2f}")

with col2:
    st.markdown("### 🎯 Risk Profile")
    
    risk_level = st.select_slider(
        "Select Your Risk Tolerance",
        options=["Low", "Medium", "High"],
        value="Medium",
        help="Low: Conservative (FD, Debt funds)\nMedium: Balanced (Mix of equity & debt)\nHigh: Aggressive (Equity focus)"
    )
    
    investment_goal = st.selectbox(
        "Investment Goal",
        ["Wealth Creation", "Retirement Planning", "Child Education", "Home Purchase", "Emergency Fund"]
    )
    
    time_horizon = st.selectbox(
        "Investment Timeline",
        ["Short-term (< 1 year)", "Medium-term (1-5 years)", "Long-term (> 5 years)"]
    )

# Generate recommendations
if st.button("🚀 Get AI Recommendations", use_container_width=True):
    if investable <= 0:
        st.error("❌ Investable amount must be positive!")
    else:
        with st.spinner("🤖 AI agents analyzing your profile..."):
            # Get allocation from RL model
            allocation_result = get_optimal_allocation(investable, risk_level)
            
            st.success("✅ AI recommendations generated!")
            
            # Display allocation
            st.markdown("### 📊 Recommended Portfolio Allocation")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Allocation table
                allocation_df = []
                for asset, percentage in allocation_result['allocation_percentages'].items():
                    amount = allocation_result['allocation_amounts'][asset]
                    allocation_df.append({
                        "Asset Class": asset,
                        "Allocation (%)": f"{percentage:.1f}%",
                        "Amount (₹)": f"₹{amount:,.2f}"
                    })
                
                import pandas as pd
                df = pd.DataFrame(allocation_df)
                st.dataframe(df, use_container_width=True, hide_index=True)
            
            with col2:
                # Pie chart
                import plotly.express as px
                fig = px.pie(
                    values=list(allocation_result['allocation_percentages'].values()),
                    names=list(allocation_result['allocation_percentages'].keys()),
                    title=f"Portfolio Distribution - {risk_level} Risk",
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Expected returns
            st.markdown("### 📈 Expected Returns")
            
            col1, col2, col3 = st.columns(3)
            
            risk_returns = {"Low": 7.5, "Medium": 11.0, "High": 15.0}
            expected_return = risk_returns[risk_level]
            
            # Calculate future values
            one_year = investable * 12 * (1 + expected_return/100)
            three_year = investable * 36 * ((1 + expected_return/100) ** 3)
            five_year = investable * 60 * ((1 + expected_return/100) ** 5)
            
            col1.metric("1 Year", f"₹{one_year:,.0f}", f"+{expected_return}% p.a.")
            col2.metric("3 Years", f"₹{three_year:,.0f}", f"+{expected_return}% p.a.")
            col3.metric("5 Years", f"₹{five_year:,.0f}", f"+{expected_return}% p.a.")
            
            # AI Agent recommendations
            st.markdown("### 🎯 Personalized Recommendations")
            
            recommendations = investment_agent.get_investment_recommendations(
                investable,
                risk_level,
                investment_goal,
                time_horizon
            )
            
            st.markdown(recommendations['recommendations'])
            
            # Key points
            st.markdown("### ⚠️ Important Considerations")
            
            points = {
                "Low": [
                    "Focus on capital preservation with stable returns",
                    "Ideal for short-term goals and risk-averse investors",
                    "Consider tax-saving FDs and debt mutual funds",
                    "Maintain 6-month emergency fund in liquid assets"
                ],
                "Medium": [
                    "Balanced approach with growth potential",
                    "Diversification across asset classes",
                    "Regular portfolio rebalancing recommended",
                    "Suitable for medium to long-term goals"
                ],
                "High": [
                    "Higher returns with increased volatility",
                    "Requires patience and long investment horizon",
                    "Stay invested through market cycles",
                    "Not suitable for short-term needs"
                ]
            }
            
            for point in points[risk_level]:
                st.markdown(f"• {point}")

# Sidebar
with st.sidebar:
    st.markdown("### 🎯 Risk Profiles")
    
    with st.expander("🟢 Low Risk"):
        st.markdown("""
        **Characteristics:**
        - Capital protection focus
        - 6-8% expected returns
        - Minimal volatility
        
        **Ideal for:**
        - Conservative investors
        - Near-term goals
        - Retirees
        """)
    
    with st.expander("🟡 Medium Risk"):
        st.markdown("""
        **Characteristics:**
        - Balanced growth
        - 10-12% expected returns
        - Moderate volatility
        
        **Ideal for:**
        - Balanced investors
        - 5-10 year goals
        - Wealth accumulation
        """)
    
    with st.expander("🔴 High Risk"):
        st.markdown("""
        **Characteristics:**
        - Aggressive growth
        - 14-18% expected returns
        - High volatility
        
        **Ideal for:**
        - Risk-tolerant investors
        - Long-term goals (10+ years)
        - Young professionals
        """)
    
    st.markdown("---")
    if st.button("🏠 Back to Home"):
        st.switch_page("app.py")
