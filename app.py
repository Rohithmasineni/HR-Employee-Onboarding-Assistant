"""
app.py
------
Streamlit frontend for the HR & Employee Onboarding Assistant.
Run with: streamlit run app.py
"""

import streamlit as st
from llm_client import chat_with_groq, build_user_message, build_system_message

# PAGE CONFIG

st.set_page_config(
    page_title="HR Onboarding Assistant",
    page_icon="🏢",
    layout="centered"
)

# CUSTOM CSS

# SIDEBAR

with st.sidebar:
    st.markdown("# 🏢 HR Assistant")
    
    st.markdown("---")
    st.markdown("### Try asking:")
    sample_questions = [
        "What is the leave policy?",
        "How many leaves do I have left?",
        "What should I do on Day 1?",
        "I'm experienced — what documents do I need?",
        "What is the full onboarding process?",
        "Who is my reporting manager?",
    ]
    for q in sample_questions:
        if st.button(q, key=f"btn_{q}", use_container_width=True):
            st.session_state["prefill_input"] = q

    st.markdown("---")
    if st.button("Clear Chat", use_container_width=True):
        st.session_state["messages"] = []
        st.session_state["conversation_history"] = []
        st.rerun()

# SESSION STATE INIT

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# conversation_history always starts with system message
if "conversation_history" not in st.session_state:
    st.session_state["conversation_history"] = [build_system_message()]

if "prefill_input" not in st.session_state:
    st.session_state["prefill_input"] = ""

# HEADER

st.markdown("## HR & Employee Onboarding Assistant")
st.markdown(
    "Ask me anything about **leave policies**, **onboarding steps**, or your **employee profile**. "
    "All data is fetched live via MCP — nothing is hardcoded."
)
st.markdown("---")

# CHAT HISTORY DISPLAY

if not st.session_state["messages"]:
    with st.chat_message("assistant"):
        st.markdown(
            "👋 Hello! I'm your HR Assistant.\n\n"
            "I can help you with:\n"
            "- **Leave policies** — types, rules, how to apply\n"
            "- **Leave balance** — yearly remaining & monthly usage\n"
            "- **Onboarding guide** — Day 1, Week 1, Week 2 (Fresher & Experienced)\n"
            "- **Your profile** — manager, department, designation\n\n"
            "What would you like to know?"
        )

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# CHAT INPUT

prefill = st.session_state.pop("prefill_input", "")
user_input = st.chat_input("Please drop your query here...")
query = user_input or prefill

if query:
    # Show user message
    st.session_state["messages"].append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # Add to conversation history
    st.session_state["conversation_history"].append(build_user_message(query))

    # Get response via Groq + MCP loop
    with st.chat_message("assistant"):
        with st.spinner("Fetching data via MCP..."):
            try:
                response_text, updated_history = chat_with_groq(
                    st.session_state["conversation_history"]
                )
                st.session_state["conversation_history"] = updated_history
                st.markdown(response_text)
                st.session_state["messages"].append(
                    {"role": "assistant", "content": response_text}
                )
            except ValueError as e:
                # Catches missing API key
                error_msg = f"⚠️ Configuration Error: {str(e)}"
                st.error(error_msg)
                st.session_state["messages"].append(
                    {"role": "assistant", "content": error_msg}
                )
            except Exception as e:
                error_msg = f"⚠️ Unexpected error: {str(e)}\n\nPlease try again."
                st.error(error_msg)
                st.session_state["messages"].append(
                    {"role": "assistant", "content": error_msg}
                )