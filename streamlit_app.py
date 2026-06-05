import os
import sys

# Change working directory to the directory containing streamlit_app.py to prevent path errors
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir:
    os.chdir(script_dir)
if script_dir not in sys.path:
    sys.path.append(script_dir)

import streamlit as st
import datetime
import re
from chatbot import FAQChatbot

# Page configuration
st.set_page_config(
    page_title="Groww AI - Mutual Fund Wealth Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to mimic Groww Emerald Green styling
st.markdown("""
<style>
    /* Background and theme colors */
    .stApp {
        background-color: #0b0f19;
        color: #f0f2f5;
    }
    section[data-testid="stSidebar"] {
        background-color: #111622 !important;
        border-right: 1px solid #1f2736 !important;
    }
    
    /* Styled metric panels */
    div[data-testid="metric-container"] {
        background-color: #161c2a;
        border: 1px solid #232c3f;
        padding: 0.75rem;
        border-radius: 10px;
    }
    
    /* Custom buttons styling */
    .stButton>button {
        background-color: #00d09c !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        width: 100%;
        transition: transform 0.1s ease;
    }
    .stButton>button:hover {
        background-color: #00b084 !important;
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# Initialize Chatbot in session state to preserve database indexing
if "chatbot" not in st.session_state:
    st.session_state.chatbot = FAQChatbot()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "**Hello Alex!** I am your facts-only FAQ assistant for **Motilal Oswal mutual fund schemes**.\n\nI retrieve details directly from verified AMC documents. How can I assist you with NAV, expense ratios, exit loads, benchmarks, or managers today?"}
    ]

# Sidebar Navigation Layout
with st.sidebar:
    st.markdown("### 🟢 Groww AI")
    st.markdown("*Your Wealth Assistant*")
    
    st.markdown("---")
    
    # Navigation views routing
    view = st.radio("Workspace Navigation", ["Chat Assistant", "Explore Schemes", "Compliance & Settings"])
    
    st.markdown("---")
    if st.button("Reset Conversation"):
        st.session_state.messages = [
            {"role": "assistant", "content": "**Conversation Reset.** Ask me anything about Motilal Oswal mutual fund schemes."}
        ]
        st.rerun()
        
    st.caption("Groww AI FAQ Assistant • Verified AMC details.")

# View Router
if view == "Chat Assistant":
    st.subheader("💬 Wealth Assistant Chat Workspace")
    st.info("⚠️ **Disclaimer:** Facts-only database context. No investment advice, recommendations, or opinions are provided.")
    
    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "footer" in msg and msg["footer"]:
                st.caption(msg["footer"])
                
    # Suggested Questions (chips)
    st.markdown("#### Suggested Questions")
    cols = st.columns(3)
    suggestions = [
        ("📊 Expense Ratio: Large & Midcap Fund", "What is the expense ratio of the Motilal Oswal Large and Midcap Fund?"),
        ("👨‍💼 Managers: Contra Fund", "Who is the fund manager of the Motilal Oswal Contra Fund?"),
        ("⚖️ Exit Load: Active Momentum Fund", "What is the exit load of the Motilal Oswal Active Momentum Fund?")
    ]
    
    clicked_query = None
    for idx, (label, query) in enumerate(suggestions):
        if cols[idx % 3].button(label, key=f"sug_{idx}"):
            clicked_query = query
            
    # Input Bar
    user_query = st.chat_input("Ask about mutual funds, expense ratios, exit loads...")
    
    if clicked_query:
        user_query = clicked_query
        
    if user_query:
        # User message
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)
            
        # Assistant response
        with st.chat_message("assistant"):
            with st.spinner("Retrieving facts from source documents..."):
                res = st.session_state.chatbot.answer_query(user_query)
                answer = res["answer"]
                footer = res["footer"]
                
                # Append citation if present
                if "citations" in res and res["citations"]:
                    answer += f"\n\n📚 Source: [Groww official source page]({res['citations'][0]})"
                
                st.markdown(answer)
                st.caption(footer)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "footer": footer
                })
                
elif view == "Explore Schemes":
    st.subheader("📊 Explore Mutual Fund Schemes")
    st.write("Factual metrics extracted from Groww official fund pages.")
    
    schemes = [
        {"name": "Motilal Oswal Large and Midcap Fund Direct Growth", "nav": "₹38.72", "expense": "0.73%", "exit": "1% (365 days)", "benchmark": "NIFTY Large Midcap 250 TRI"},
        {"name": "Motilal Oswal Contra Fund Direct Growth", "nav": "₹14.28", "expense": "0.72%", "exit": "1% (365 days)", "benchmark": "Nifty 500 TRI"},
        {"name": "Motilal Oswal Digital India Fund Direct Growth", "nav": "₹18.42", "expense": "0.76%", "exit": "1% (15 days)", "benchmark": "BSE Teck TRI"},
        {"name": "Motilal Oswal Multi Cap Fund Direct Growth", "nav": "₹10.92", "expense": "0.80%", "exit": "1% (365 days)", "benchmark": "Nifty 500 Multicap 50:25:25 TRI"},
        {"name": "Motilal Oswal Active Momentum Fund Direct Growth", "nav": "₹12.65", "expense": "0.78%", "exit": "1% (15 days)", "benchmark": "Nifty 200 Momentum 30 TRI"},
        {"name": "Motilal Oswal Most Focused Long Term Fund Direct Growth", "nav": "₹82.64", "expense": "0.75%", "exit": "3 Years Lock-in (ELSS)", "benchmark": "Nifty 500 TRI"},
        {"name": "Motilal Oswal Most Focused Multicap 35 Fund Direct Growth", "nav": "₹53.40", "expense": "0.82%", "exit": "1% (365 days)", "benchmark": "Nifty 500 TRI"}
    ]
    
    for s in schemes:
        with st.expander(s["name"]):
            col1, col2 = st.columns(2)
            col1.metric("NAV (Direct)", s["nav"])
            col1.metric("Expense Ratio", s["expense"])
            col2.metric("Exit Load Details", s["exit"])
            col2.metric("Benchmark Index", s["benchmark"])

elif view == "Compliance & Settings":
    st.subheader("👤 Compliance Profile & settings")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Account Information (Masked)")
        st.markdown("**Holder Name:** Alex Mercer")
        st.markdown("**Email:** `a.mercer@groww.io`")
        st.markdown("**PAN Number:** `XXXXX9482X` (masked)")
        st.markdown("**Aadhaar Card:** `XXXX-XXXX-9182` (masked)")
        st.markdown("**Bank Account:** `XXXXXXXX8910` (masked)")
        
    with col2:
        st.markdown("#### Privacy Guardrails & Policies")
        st.success("🔒 **Zero-PII Storage active:** Personal identifiers are blocked before parsing queries.")
        st.warning("⚖️ **Facts-only enforced:** Speculation and investment advice are strictly refused.")
        st.info("📚 **Verified citations:** All factual answers link directly back to verified official sources.")
