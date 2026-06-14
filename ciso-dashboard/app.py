import os
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
st.set_page_config(page_title="CISO Command Center", layout="wide")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    st.error("DATABASE_URL is not configured")
    st.stop()
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

st.title("CISO Command & Intelligence Center")
st.caption("Read-only operational dashboard for APEX Financial Intelligence Platform")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Backend Status", "Operational")
with col2:
    st.metric("Market Collector", "Running")
with col3:
    st.metric("AI Evaluator", "Running")

st.subheader("Live Market Signals")
try:
    with engine.connect() as conn:
        signals = pd.read_sql(text("SELECT * FROM final_decisions ORDER BY created_at DESC LIMIT 200"), conn)
    st.dataframe(signals, use_container_width=True)
except Exception as exc:
    st.error(f"Failed to load signals: {exc}")

st.subheader("Security Audit Logs")
try:
    with engine.connect() as conn:
        audits = pd.read_sql(text("SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT 200"), conn)
    st.dataframe(audits, use_container_width=True)
except Exception as exc:
    st.error(f"Failed to load audit logs: {exc}")
