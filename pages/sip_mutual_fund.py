"""
SIP / Mutual Fund Page
Track monthly SIPs and mutual fund lump sum investments
"""
import streamlit as st
import requests
import pandas as pd
from datetime import date
import sys
sys.path.append('..')

from config.settings import settings
from utils.calculations import financial_calculator

# Try to import ML model with graceful fallback
try:
    from ml_models.xgboost_returns import predict_investment_return
except Exception as e:
    st.warning(f"⚠️ XGBoost returns module unavailable: {type(e).__name__}")
    predict_investment_return = None

st.set_page_config(page_title="SIP / Mutual Funds", page_icon="💼", layout="wide")

API_URL = f"http://{settings.API_HOST}:{settings.API_PORT}/api"
USER_ID = 1

st.title("💼 SIP & Mutual Funds")

# Tabs
sip_tab, mf_tab = st.tabs(["📅 SIP", "💸 Mutual Fund (Lump Sum)"])

with sip_tab:
    st.markdown("### 📅 Add Monthly SIP")
    with st.form("sip_form"):
        fund_name = st.text_input("Fund Name", value="Nifty 50 Index Fund")
        monthly_amount = st.number_input("Monthly Amount (₹)", min_value=500.0, value=5000.0, format="%.2f")
        start_date = st.date_input("Start Date", value=date.today())
        expected_return_rate = st.number_input("Expected Annual Return (%)", min_value=0.0, value=11.0)
        submit_sip = st.form_submit_button("💾 Save SIP")

        if submit_sip:
            data = {
                "user_id": USER_ID,
                "fund_name": fund_name,
                "monthly_amount": monthly_amount,
                "start_date": start_date.isoformat(),
                "expected_return_rate": expected_return_rate
            }
            try:
                resp = requests.post(f"{API_URL}/sip", json=data)
                if resp.status_code == 201:
                    st.success("✅ SIP saved!")
                else:
                    st.error(f"❌ Error: {resp.text}")
            except Exception as e:
                st.error(f"❌ API error: {e}")

    st.markdown("### 📈 SIP Value Estimator")
    months = st.slider("Duration (months)", 6, 120, 36)
    calc = financial_calculator.calculate_sip_value(monthly_amount, expected_return_rate, months)
    st.info(f"Total Invested: ₹{calc['total_invested']:,.2f} | Estimated Value: ₹{calc['current_value']:,.2f}")

    st.markdown("### 📁 Active SIPs")
    try:
        resp = requests.get(f"{API_URL}/sip/{USER_ID}")
        if resp.status_code == 200:
            df = pd.DataFrame(resp.json())
            if not df.empty:
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No SIPs found.")
    except Exception as e:
        st.error(f"Error: {e}")

with mf_tab:
    st.markdown("### 💸 Add Mutual Fund (Lump Sum)")
    with st.form("mf_form"):
        fund_name = st.text_input("Fund Name", value="Large Cap Equity Fund")
        investment_amount = st.number_input("Investment Amount (₹)", min_value=1000.0, value=50000.0)
        investment_date = st.date_input("Investment Date", value=date.today())
        expected_return_rate = st.number_input("Expected Annual Return (%)", min_value=0.0, value=12.0)
        submit_mf = st.form_submit_button("💾 Save Mutual Fund")

        if submit_mf:
            data = {
                "user_id": USER_ID,
                "fund_name": fund_name,
                "investment_amount": investment_amount,
                "investment_date": investment_date.isoformat(),
                "expected_return_rate": expected_return_rate
            }
            try:
                resp = requests.post(f"{API_URL}/mutual-fund", json=data)
                if resp.status_code == 201:
                    st.success("✅ Mutual fund saved!")
                else:
                    st.error(f"❌ Error: {resp.text}")
            except Exception as e:
                st.error(f"❌ API error: {e}")

    st.markdown("### 📈 Return Prediction (XGBoost)")
    if st.button("🔮 Predict Returns", use_container_width=True):
        result = predict_investment_return(investment_amount, 36, "Medium", asset_type="Equity")
        st.info(
            f"Predicted Annual Return: {result['predicted_annual_return']}% | "
            f"Estimated Future Value (3y): ₹{result['estimated_future_value']:,.2f}"
        )

    st.markdown("### 📁 Mutual Funds")
    try:
        resp = requests.get(f"{API_URL}/mutual-fund/{USER_ID}")
        if resp.status_code == 200:
            df = pd.DataFrame(resp.json())
            if not df.empty:
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No mutual funds found.")
    except Exception as e:
        st.error(f"Error: {e}")

with st.sidebar:
    if st.button("🏠 Back to Hub"):
        st.switch_page("pages/3_financial_products.py")
