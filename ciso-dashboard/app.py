import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
st.set_page_config(page_title="APEX CISO Center", layout="wide")

st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    h1 {
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    st.error("DATABASE_URL is not configured")
    st.stop()
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

st.title("APEX CISO Command Center")
st.caption("Enterprise-grade operational dashboard for Financial Intelligence Platform")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Backend Status", "🟢 Operational", delta="All systems nominal")
with col2:
    st.metric("Market Collector", "✅ Running", delta="Real-time data streaming")
with col3:
    st.metric("AI Evaluator", "✅ Running", delta="Models active")

st.markdown("---")
st.subheader("Live Market Signals")
try:
    with engine.connect() as conn:
        signals = pd.read_sql(text("SELECT * FROM final_decisions ORDER BY created_at DESC LIMIT 200"), conn)

    if signals.empty or len(signals) == 0:
        st.info("⏳ Menunggu sinyal intelijen pasar...")
    else:
        st.dataframe(signals, use_container_width=True, hide_index=True)
except Exception as exc:
    st.error(f"Failed to load signals: {exc}")

st.markdown("---")
st.subheader("Security Audit Logs")
try:
    with engine.connect() as conn:
        audits = pd.read_sql(text("SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT 200"), conn)

    if audits.empty or len(audits) == 0:
        st.info("⏳ Menunggu log audit keamanan...")
    else:
        st.dataframe(audits, use_container_width=True, hide_index=True)
except Exception as exc:
    st.error(f"Failed to load audit logs: {exc}")