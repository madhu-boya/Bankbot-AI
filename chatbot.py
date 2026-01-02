import streamlit as st
from datetime import datetime
import time

st.set_page_config(
    page_title="SmartBank Chatbot",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- GLOBAL THEME ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }

/* Main background */
.main { 
    background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 50%, #1d4ed8 100%);
}
.stApp { background-color: transparent; }

/* Sidebar container */
[data-testid="stSidebar"] > div:first-child {
    background: radial-gradient(circle at top left, #1e40af 0%, #020617 55%, #000 100%);
    border-right: 1px solid rgba(148,163,184,0.4);
    box-shadow: 0 0 25px rgba(15,23,42,0.9);
    padding-top: 0.6rem;
}

/* Sidebar title + subtitle */
.smartbank-title {
    font-size: 20px;
    font-weight: 700;
    color: #e5e7eb;
}
.smartbank-subtitle {
    font-size: 12px;
    color: #9ca3af;
}

/* Chat history label */
.chat-history-label {
    font-size: 13px;
    font-weight: 600;
    color: #c7d2fe;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

/* History row layout */
.history-row {
    display: flex;
    align-items: center;
    gap: 6px;
    margin: 4px 0;
}

/* History "open" button look */
.history-open-btn {
    flex: 1;
    padding: 8px 10px;
    border-radius: 10px;
    background: linear-gradient(135deg, rgba(15,23,42,0.9), rgba(30,64,175,0.9));
    border: 1px solid rgba(129,140,248,0.45);
    color: #e5e7eb;
    font-size: 12px;
    text-align: left;
    cursor: pointer;
}
.history-open-btn:hover {
    background: linear-gradient(135deg, rgba(37,99,235,0.95), rgba(30,64,175,1));
}

/* Delete button style */
.history-del-btn {
    padding: 6px 8px;
    border-radius: 999px;
    border: 1px solid rgba(239,68,68,0.7);
    background: rgba(127,29,29,0.9);
    color: #fecaca;
    font-size: 11px;
    cursor: pointer;
}
.history-del-btn:hover {
    background: rgba(248,113,113,0.95);
    color: #111827;
}

/* Chat bubbles */
.chat-bubble { 
    padding: 16px 20px; margin: 8px 0; border-radius: 18px; max-width: 85%;
    backdrop-filter: blur(15px); border: 1px solid rgba(255,255,255,0.2);
}
.user-bubble { background: rgba(34,197,94,0.2); margin-left: auto; }
.bot-bubble { background: rgba(255,255,255,0.15); }

/* Header card */
.header-card {
    background: rgba(255,255,255,0.1); backdrop-filter: blur(20px);
    border-radius: 20px; padding: 24px; border: 1px solid rgba(255,255,255,0.2);
}
</style>
""", unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_action" not in st.session_state:
    st.session_state.last_action = None
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = 0

# ---------- SIDEBAR: TITLE + CHAT HISTORY + DELETE ----------
with st.sidebar:
    st.markdown(
        """
        <div class="smartbank-title">🏦 SmartBank AI</div>
        <div class="smartbank-subtitle">Your Banking Copilot</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<hr style='border-color: rgba(75,85,99,0.6);'>", unsafe_allow_html=True)

    st.markdown("<div class='chat-history-label'>💬 Chat History</div>", unsafe_allow_html=True)

    # New Chat Button
    if st.button("➕ New Chat", key="new_chat", use_container_width=True):
        if st.session_state.messages:
            st.session_state.chat_history.append({
                "id": len(st.session_state.chat_history),
                "title": f"Chat {len(st.session_state.chat_history) + 1}",
                "preview": st.session_state.messages[-1]["content"][:40] + "...",
                "time": datetime.now().strftime("%d %b %H:%M"),
                "messages": st.session_state.messages.copy()
            })
        st.session_state.messages = []
        st.session_state.current_chat_id = -1
        st.rerun()

    # Display Chat History with individual delete buttons
    if st.session_state.chat_history:
        # enumerate to know index for deletion
        for idx, chat in enumerate(st.session_state.chat_history[-8:]):  # show last 8
            real_index = len(st.session_state.chat_history) - len(st.session_state.chat_history[-8:]) + idx

            row_cols = st.columns([4, 1])  # open button + delete button

            with row_cols[0]:
                open_clicked = st.button(
                    f"📄 {chat['title']} • {chat['time']}",
                    key=f"open_{chat['id']}",
                    help=chat["preview"],
                    use_container_width=True,
                )
            with row_cols[1]:
                del_clicked = st.button(
                    "🗑️",
                    key=f"del_{chat['id']}",
                    use_container_width=True,
                )

            if open_clicked:
                st.session_state.messages = chat["messages"].copy()
                st.session_state.current_chat_id = chat["id"]
                st.rerun()

            if del_clicked:
                # delete from chat_history
                st.session_state.chat_history.pop(real_index)
                # if deleting currently open chat, reset messages
                if st.session_state.current_chat_id == chat["id"]:
                    st.session_state.messages = []
                    st.session_state.current_chat_id = 0
                st.rerun()
    else:
        st.markdown(
            "<div style='color:#9ca3af;font-size:12px;margin-top:8px;'>No chats yet<br>Start your first chat 👆</div>",
            unsafe_allow_html=True,
        )

# ---------- MAIN CHAT AREA ----------
col1, col2 = st.columns([1, 3])
with col1:
    chat_title = "SmartBank Chat" if not st.session_state.chat_history else f"Chat #{st.session_state.current_chat_id + 1}"
    st.markdown(f"### 🏦 **{chat_title}**")
with col2:
    st.markdown("<div style='color:#a5b4fc;font-size:14px;'></div>", unsafe_allow_html=True)

st.markdown("---")

# Welcome Card (only if no messages)
if not st.session_state.messages:
    st.markdown("""
    <div class="header-card">
        <div style='font-size:12px;color:#a5b4fc;'>Welcome to SmartBank AI</div>
        <div style='font-size:28px;font-weight:700;color:white;'>Your Banking Assistant</div>
        <div style='font-size:14px;color:#a5b4fc;margin-top:12px;'>
            💰 Check balances • 💸 Make transfers • 📄 Get statements<br>
            Use chat below 👇
        </div>
    </div>
    """, unsafe_allow_html=True)

# Chat Messages
chat_container = st.container(height=600)
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(f"""
            <div class="chat-bubble {'user-bubble' if message['role']=='user' else 'bot-bubble'}">
                <div style="font-size:15px;line-height:1.5;">{message['content']}</div>
                <div style="font-size:11px;color:#a5b4fc;margin-top:6px;">
                    {message['time'].strftime('%H:%M')}
                </div>
            </div>
            """, unsafe_allow_html=True)

# Chat Input
user_input = st.chat_input("Ask about banking... 👇")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input, "time": datetime.now()})
    
    lower_input = user_input.lower()
    quick_responses = {
        "balance": "💰 Quick balance:\n• Savings: ₹3,45,200 | Current: ₹2,10,500",
        "help": "✅ Use this chat to ask any banking questions!\n💳 Accounts • 💸 Transfers • 💳 Cards • 🏠 Loans"
    }

    if "balance" in lower_input:
        response = quick_responses["balance"]
    elif "help" in lower_input or "how" in lower_input:
        response = quick_responses["help"]
    else:
        response = f"✅ Got it: '{user_input}'.\n\n💡 You can ask about balances, transfers, cards, EMIs and more!"

    st.session_state.messages.append({"role": "assistant", "content": response, "time": datetime.now()})
    st.rerun()

# Footer
st.markdown("""
<div style='text-align:center;padding:20px;color:#a5b4fc;font-size:12px;'>
    🔗 Ready for backend integration | Banking-grade security
</div>
""", unsafe_allow_html=True)
