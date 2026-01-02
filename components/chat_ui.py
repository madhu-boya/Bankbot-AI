import streamlit as st
from datetime import datetime
from ai.ollama_client import ollama


BANK_KEYWORDS = [
    "account", "balance", "loan", "emi", "interest", "card", "credit",
    "debit", "statement", "transaction", "transfer", "upi", "imps",
    "neft", "rtgs", "fd", "rd", "net banking", "netbanking",
    "cheque", "branch", "ifsc", "limit", "otp", "pin", "security"
]

def is_banking_question(text: str) -> bool:
    text_lower = text.lower()
    return any(word in text_lower for word in BANK_KEYWORDS)


def render_chat_ui():
    """Render complete chat interface"""   
    # Header
    col1, col2 = st.columns([1, 3])
    with col1:
        chat_title = "SmartBank Chat" if st.session_state.current_chat_id == 0 else f"Chat #{st.session_state.current_chat_id + 1}"
        st.markdown(f"### 🏦 **{chat_title}**")
    with col2:
        st.markdown(f"**Model:** {st.session_state.ollama_model}")
    st.markdown("---")
    # Welcome Card
    if not st.session_state.messages:
        st.markdown("""
        <div class="header-card">
            <div style='font-size:12px;color:#a5b4fc;'>Powered by Ollama + Llama3</div>
            <div style='font-size:28px;font-weight:700;color:white;'>Local AI Banking Chat</div>
            <div style='font-size:14px;color:#a5b4fc;margin-top:12px;'>
                💬 Ask about accounts, transfers, loans<br>
                🤖 Runs 100% locally - no API costs!
            </div>
        </div>
        """, unsafe_allow_html=True)
    # Chat Messages
    chat_container = st.container(height=600)
    render_messages(chat_container)
    # Chat Input + AI
    handle_chat_input(chat_container)
def render_messages(chat_container):
    """Render all chat messages"""
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

def handle_chat_input(chat_container):
    """Handle user input and generate AI response"""
    if prompt := st.chat_input("Ask about banking, balances, transfers..."):
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "time": datetime.now()
        })
        render_new_message(chat_container, "user", prompt)

        # Check if question is banking related
        if not is_banking_question(prompt):
            with chat_container:
                with st.chat_message("assistant"):
                    msg = (
                        "I am your SmartBank virtual officer and can help **only** with "
                        "banking-related questions like balances, transfers, cards, loans, "
                        "EMIs, and security issues."
                    )
                    st.markdown(msg)
            st.session_state.messages.append({
                "role": "assistant",
                "content": msg,
                "time": datetime.now()
            })
            return  # do NOT call the AI

        # Generate AI response for valid banking questions
        generate_ai_response(chat_container)

def render_new_message(chat_container, role: str, content: str):
    """Render single new message"""
    with chat_container:
        with st.chat_message(role):
            st.markdown(f"""
            <div class="chat-bubble {'user-bubble' if role=='user' else 'bot-bubble'}">
                <div style="font-size:15px;line-height:1.5;">{content}</div>
                <div style="font-size:11px;color:#a5b4fc;margin-top:6px;">
                    {datetime.now().strftime('%H:%M')}
                </div>
            </div>
            """, unsafe_allow_html=True)

def generate_ai_response(chat_container):
    """Generate streaming AI response"""
    with chat_container:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            system_prompt = """You are SmartBank AI, a professional banking assistant for Indian customers.
            Use ₹ symbol for Indian Rupees. Sample balances: Savings ₹3,45,200.
            Services: balance, transfer, statement, cards, EMI, security.
            Always respond as a bank officer."""
            
            messages_for_ai = [
                {"role": "system", "content": system_prompt},
                *[{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages]
            ]
            
            try:
                model = st.session_state.get("ollama_model", "llama3.2")
                response_generator = ollama.generate(messages_for_ai, model)
                
                for chunk in response_generator:
                    full_response += chunk
                    message_placeholder.markdown(f"""
                    <div class="chat-bubble bot-bubble">
                        <div style="font-size:15px;line-height:1.5;">{full_response}</div>
                        <div style="font-size:11px;color:#a5b4fc;margin-top:6px;">
                            {datetime.now().strftime('%H:%M')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Save final response
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": full_response, 
                    "time": datetime.now()
                })
                
            except Exception as e:
                error_msg = f"❌ AI Error: {str(e)}"
                st.session_state.messages.append({
                    "role": "assistant", "content": error_msg, "time": datetime.now()
                })
                st.error(error_msg)
