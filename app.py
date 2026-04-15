import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Momentum Scanner", layout="wide")
st.title("⚡ Momentum Scanner")

def vectorize(ticker, price, strength, confluence, catalyst, magnitude, timing, vol, momentum, debt):
    conv = round((min(strength/10, 1)*0.5) + (min(confluence*0.1, 0.4)*0.3) + 0.1, 2)
    cat_map = {'today': 1.0, 'this_week': 0.8, 'next_week': 0.5, 'uncertain': 0.3}
    tf = round((cat_map.get(timing, 0.3)*0.5) + (0.9*0.5) + 0.1, 2)
    vol_score = 1.0 if vol >= 2.0 else 0.8 if vol >= 1.5 else 0.4
    cat_map2 = {'earnings': 0.9, 'macro': 0.8, 'sector': 0.7, 'supply_shock': 0.85, 'none': 0.3}
    mag_map = {'major': 1.0, 'moderate': 0.7, 'minor': 0.4}
    cat_score = round((cat_map2.get(catalyst, 0.3)*0.6) + (mag_map.get(magnitude, 0.4)*0.4), 2)
    shariah_pass = debt < 0.33
    composite = round((conv*0.35 + tf*0.25 + cat_score*0.25 + vol_score*0.15), 2) if shariah_pass else 0.0
    return {"ticker": ticker.upper(), "price": price, "composite": composite, "shariah": shariah_pass}

if 'signals' not in st.session_state:
    st.session_state.signals = []

st.subheader("Enter Signal Data")
col1, col2, col3 = st.columns(3)

with col1:
    ticker = st.text_input("Ticker", "UUUU")
    price = st.number_input("Price", 6.45)
    debt = st.number_input("Debt/MCap", 0.18)

with col2:
    strength = st.slider("Signal Strength", 0.0, 10.0, 7.5)
    confluence = st.number_input("Confluence", 0, 5, 2)
    vol = st.number_input("Volume Ratio", 2.1)
    momentum = st.number_input("5d Momentum %", 3.2)

with col3:
    catalyst = st.selectbox("Catalyst", ["earnings", "macro", "sector", "supply_shock", "insider_activity", "none"], index=3)
    magnitude = st.selectbox("Magnitude", ["major", "moderate", "minor"], index=0)
    timing = st.selectbox("Timing", ["today", "this_week", "next_week", "uncertain"], index=1)

if st.button("Vectorize", type="primary"):
    result = vectorize(ticker, price, strength, confluence, catalyst, magnitude, timing, vol, momentum, debt)
    st.session_state.signals.append(result)
    st.success(f"{ticker.upper()} → Composite: {result['composite']}")

if st.session_state.signals:
    st.divider()
    st.dataframe(pd.DataFrame(st.session_state.signals))
    st.text_area("JSON", json.dumps(st.session_state.signals, indent=2), height=200)