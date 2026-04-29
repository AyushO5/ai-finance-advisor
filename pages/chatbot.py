import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from utils.memory import load_memory, save_memory, update_profile, get_current_chat, create_new_chat

st.set_page_config(page_title="Finance Advisor", page_icon="💰", layout="wide")

# ---------------- 🧠 LOAD MEMORY ---------------- #
memory = load_memory()
current_chat = get_current_chat(memory)

if "messages" not in st.session_state:
    st.session_state.messages = current_chat["messages"]

# ---------------- 🎨 CLEAN UI STYLE ---------------- #
st.markdown("""
<style>
.block-container {
    max-width: 900px;
    padding-top: 2rem;
}
section[data-testid="stSidebar"] {
    width: 260px !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------- 📂 SIDEBAR ---------------- #
st.sidebar.title("💬 Chats")

if st.sidebar.button("➕ New Chat"):
    memory = create_new_chat(memory)
    save_memory(memory)

    new_chat = get_current_chat(memory)
    st.session_state.messages = new_chat["messages"]
    st.rerun()

st.sidebar.markdown("---")

for chat in memory["chats"]:
    if st.sidebar.button(f"Chat {chat['id']}"):
        memory["current_chat_id"] = chat["id"]
        save_memory(memory)

        new_chat = get_current_chat(memory)
        st.session_state.messages = new_chat["messages"]
        st.rerun()

# ---------------- 🧾 HEADER ---------------- #
st.title("💰 AI Financial Advisor")
st.caption("Smart assistant for budgeting, savings, and investments")

# ---------------- 💬 CHAT AREA ---------------- #
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# ---------------- ⌨️ INPUT ---------------- #

# 🔥 add vertical spacing
st.markdown(
    "<div style='height: 40px;'></div>",
    unsafe_allow_html=True
)

input_container = st.container()

with input_container:
    left, center, right = st.columns([1, 6, 1])

    with center:
        uploaded_file = st.file_uploader(
            "Upload CSV for expense analysis",
            type=["csv"]
        )

        # 🔥 more spacing between uploader and chatbox
        st.markdown("<br>", unsafe_allow_html=True)

        user_input = st.chat_input(
            "Ask about saving, investing, budgeting..."
        )
# ---------------- 🚀 LOGIC ---------------- #
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    memory["profile"] = update_profile(user_input, memory["profile"])

    try:
        res = requests.post(
            "http://127.0.0.1:5000/chat",
            json={
                "message": user_input,
                "history": st.session_state.messages,
                "profile": memory["profile"]
            }
        )
        data = res.json()
        bot_reply = data.get("reply", "Error")

    except Exception as e:
        bot_reply = f"Backend error: {str(e)}"

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    current_chat = get_current_chat(memory)
    current_chat["messages"] = st.session_state.messages
    save_memory(memory)

    st.rerun()

# ---------------- 📊 CSV ---------------- #
if uploaded_file:
    try:
        files = {"file": uploaded_file}

        res = requests.post(
            "http://127.0.0.1:5000/upload/",
            files=files
        )

        data = res.json()

        st.subheader("📊 Expense Breakdown")

        if "expenses" not in data:
            st.error("Invalid response from server")
            st.write(data)
            st.stop()

        expenses = data["expenses"]

        df = pd.DataFrame(list(expenses.items()), columns=["Category", "Amount"])

        fig1, ax1 = plt.subplots()
        ax1.pie(df["Amount"], labels=df["Category"], autopct='%1.1f%%')
        st.pyplot(fig1)

        fig2, ax2 = plt.subplots()
        ax2.bar(df["Category"], df["Amount"])
        st.pyplot(fig2)

        st.subheader("🤖 AI Insights")
        st.write(data["ai_insights"])

    except Exception as e:
        st.error(f"Upload error: {str(e)}")