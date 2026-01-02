import streamlit as st
from datetime import datetime
from ai.ollama_client import ollama


def render_sidebar():
    """Render complete sidebar with Ollama config + chat history"""

    st.markdown("""
    <div class="smartbank-title">🏦 SmartBank AI</div>
    <div class="smartbank-subtitle">Llama3 Local AI</div>
    """, unsafe_allow_html=True)

    # Ollama Config
    with st.expander("🤖 **Ollama Setup**", expanded=False):
        st.info("🚀 **Run first:**\n``````")

        if ollama.is_running():
            st.success("✅ Ollama **running**")
            models = ollama.get_models()
            if models:
                model = st.selectbox("AI Model", models, key="model_select")
                st.session_state.ollama_model = model
            else:
                st.warning("No models found. Run: `ollama pull llama3.2`")
        else:
            st.error("❌ **Ollama not running!**\nStart: `ollama serve`")
            st.stop()

        if st.button("🧪 Test AI", key="test_ollama"):
            with st.spinner("Testing..."):
                try:
                    for chunk in ollama.generate([{"role": "user", "content": "Say 'Ready!'"}]):
                        st.success("✅ **Test OK**!")
                        break
                except Exception as e:
                    st.error(f"❌ Test failed: {str(e)}")

    st.markdown("<hr style='border-color: rgba(75,85,99,0.6);'>", unsafe_allow_html=True)

    # Chat History
    render_chat_history()


def render_chat_history():
    """Render chat history with delete buttons"""
    st.markdown("<div class='chat-history-label'>💬 Chat History</div>", unsafe_allow_html=True)

    # ➕ New Chat button
    if st.button("➕ New Chat", key="new_chat", use_container_width=True):
        if st.session_state.messages:
            # Get first user question as preview (like ChatGPT / Perplexity)
            first_user_msg = next(
                (m["content"] for m in st.session_state.messages if m["role"] == "user"),
                st.session_state.messages[0]["content"]
            )
            preview_text = first_user_msg.strip().split("\n")[0]  # first line only
            preview_text = preview_text[:40] + ("..." if len(preview_text) > 40 else "")

            st.session_state.chat_history.append({
                "id": len(st.session_state.chat_history),
                "title": f"Chat {len(st.session_state.chat_history) + 1}",
                "preview": preview_text,
                "messages": st.session_state.messages.copy()
            })
        st.session_state.messages = []
        st.session_state.current_chat_id = -1
        st.rerun()

    # Existing chats
    if st.session_state.chat_history:
        last_chats = st.session_state.chat_history[-8:]
        for idx, chat in enumerate(last_chats):
            real_index = len(st.session_state.chat_history) - len(last_chats) + idx
            row_cols = st.columns([4, 1])

            # Open chat button with preview as label
            with row_cols[0]:
                label_preview = chat.get("preview") or f"Chat {chat['id'] + 1}"
                label = f"📄 {label_preview}"
                if st.button(label, key=f"open_{chat['id']}", use_container_width=True):
                    st.session_state.messages = chat["messages"].copy()
                    st.session_state.current_chat_id = chat["id"]
                    st.rerun()

            # Delete chat button
            with row_cols[1]:
                if st.button("🗑️", key=f"del_{chat['id']}", use_container_width=True):
                    st.session_state.chat_history.pop(real_index)
                    if st.session_state.current_chat_id == chat["id"]:
                        st.session_state.messages = []
                        st.session_state.current_chat_id = 0
                    st.rerun()
    else:
        st.markdown("<div style='color:#9ca3af;font-size:12px;'>No chats yet</div>", unsafe_allow_html=True)
