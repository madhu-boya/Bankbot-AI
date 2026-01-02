import streamlit as st
from datetime import datetime
st.set_page_config(
    page_title="SmartBank Chatbot",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)
from components.sidebar import render_sidebar
from components.chat_ui import render_chat_ui
# Load CSS AFTER set_page_config
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
# ---------- SESSION STATE ----------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = 0
if "ollama_model" not in st.session_state:
    st.session_state.ollama_model = "llama3.2"
# ---------- RENDER LAYOUT ----------
with st.sidebar:
    render_sidebar()
render_chat_ui()
# Footer
st.markdown("""
<div style='text-align:center;padding:20px;color:#a5b4fc;font-size:12px;'>
    🤖 Modular SmartBank AI | Ollama + Llama3
</div>
""", unsafe_allow_html=True)
