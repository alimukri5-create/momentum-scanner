import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# --- CORE LOGIC ---
class SignalVectorizer:
    def __init__(self):
        self.shariah_exclusions = {
            'alcohol': ['BUD', 'STZ', 'KO'], 'gambling': ['LVS', 'MGM', 'PENN'],
            'weapons': ['RTX', 'LMT', 'NOC'], 'tobacco': ['MO', 'PM'],
            'financial_services': ['BAC', 'GS', 'MS']
        }
    
    def shariah_screen(self, ticker, debt_to_mcap):
        violations = [cat for cat, tks in self.shariah_exclusions.items() if ticker.upper() in tks]
        if debt_to_mcap >= 0.33: violations.append("debt_ratio_exceeds_33_percent")
        return {"passed": len(violations) == 0, "violations": violations}

    def vectorize(self, ticker, price, strength, confluence_count, c_type, magnitude, timing, pa_tf, vol, mom, debt, notes=""):
        # Scoring Math
        conv = round((min(strength/10, 1)*0.5) + (min(confluence_count*0.1, 0.4)*0.3) + (min(max(0.2, (0.55-0.35)/0.3), 1)*0.2), 2)
        tf = round(min(({'today':1,'this_week':0.8,'next_week':0.5}.get(timing, 0.3)*0.5) + ({'intraday':0.4,'1d':0.9,'multiday':0.8}.get(pa_tf, 0.5)*0.5) + 0.1, 1), 2)
        vol_s = round(min((1.0 if vol>=2 else 0.6 if vol>=1.2 else 0.2) + (0.1 if abs(mom)>=5 and vol>=1.5 else 0), 1), 2)
        cat_s = round(({'earnings':0.9,'macro':0.8,'supply_shock':0.85}.get(c_type, 0.3)*0.6) + ({'major':1,'moderate':0.7}.get(magnitude, 0.4)*0.4), 2)
        
        shariah = self.shariah_screen(ticker, debt)
        composite = round((conv*0.35 + tf*0.25 + cat_s*0.25 + vol_s*0.15), 2) if shariah['passed'] else 0.0
        
        pkt = pytz.timezone('Asia/Karachi')
        timestamp = datetime.now(pkt).strftime('%Y-%m-%d %H:%M:%S PKT')

        return {
            "Timestamp": timestamp,
            "Ticker": ticker.upper(), 
            "Price": price, 
            "Composite": composite, 
            "Shariah": shariah['passed'], 
            "Notes": notes
        }

# --- STREAMLIT UI ---
st.set_page_config(page_title="Momentum Scanner", layout="wide")
st.title("⚡ Alpha Momentum Vectorizer")
st.markdown("Long-only execution scanner. Input qualitative setup data to generate structured vector scores.")

# Initialize session state to remember past scans in the same session
if 'history' not in st.session_state:
    st.session_state.history = []

scanner = SignalVectorizer()

# Input UI Layout
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Asset Data")
    ticker = st.text_input("Ticker Symbol", value="UUUU")
    price = st.number_input("Current Price", value=6.45)
    debt = st.number_input("Debt to Market Cap Ratio", value=0.18, step=0.01)
    notes = st.text_area("Research Notes", value="Uranium supply shock thesis.")

with col2:
    st.subheader("Technical Setup")
    strength = st.slider("Signal Strength (0-10)", 0.0, 10.0, 7.5)
    confluence = st.number_input("Confluence Factors (Count)", min_value=0, max_value=5, value=2)
    pa_tf = st.selectbox("Price Action Timeframe", ["intraday", "1d", "multiday", "weekly"], index=1)
    vol = st.number_input("Volume vs 20-day Avg (e.g., 2.1x)", value=2.1, step=0.1)
    mom = st.number_input("5-Day Momentum (%)", value=3.2)

with col3:
    st.subheader("Catalyst Context")
    c_type = st.selectbox("Catalyst Type", ["earnings", "macro", "sector", "supply_shock", "insider_activity", "none"], index=3)
    magnitude = st.selectbox("Magnitude", ["major", "moderate", "minor"], index=0)
    timing = st.selectbox("Timing", ["today", "this_week", "next_week", "uncertain"], index=1)

# Execution Button
if st.button("Vectorize Signal", type="primary"):
    result = scanner.vectorize(ticker, price, strength, confluence, c_type, magnitude, timing, pa_tf, vol, mom, debt, notes)
    st.session_state.history.append(result)
    st.success(f"Signal Logged for {ticker.upper()} — Composite Score: {result['Composite']}")

# Display Data
if st.session_state.history:
    st.divider()
    st.subheader("Session Ledger")
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df, use_container_width=True)