import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from utils.memory import load_memory, save_memory, update_profile, get_current_chat, create_new_chat, delete_chat

st.set_page_config(page_title="Finance Advisor", page_icon="💰", layout="wide")

# ---------------- 🧠 LOAD MEMORY ---------------- #
memory = load_memory()

# 🔥 ensure at least one chat exists
if not memory.get("chats"):
    memory["chats"] = [{"id": 1, "messages": []}]
    memory["current_chat_id"] = 1
    save_memory(memory)

# 🔥 remove duplicates safely
seen = set()
unique_chats = []
for chat in memory["chats"]:
    if chat["id"] not in seen:
        unique_chats.append(chat)
        seen.add(chat["id"])

memory["chats"] = unique_chats
save_memory(memory)

current_chat = get_current_chat(memory)

# ---------------- SESSION INIT ---------------- #
if "messages" not in st.session_state:
    st.session_state.messages = current_chat.get("messages", [])

if "csv_uploaded" not in st.session_state:
    st.session_state["csv_uploaded"] = False

if "show_charts" not in st.session_state:
    st.session_state["show_charts"] = False

# ---------------- 🎨 UI ---------------- #
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

if st.sidebar.button("➕ New Chat", key="new_chat_btn"):
    memory = create_new_chat(memory)
    save_memory(memory)

    new_chat = get_current_chat(memory)
    st.session_state.messages = new_chat["messages"]
    st.rerun()

# 🔥 SINGLE CLEAN LOOP (NO DUPLICATES)
for idx, chat in enumerate(memory["chats"]):
    col1, col2 = st.sidebar.columns([4, 1])

    with col1:
        if st.button(f"Chat {chat['id']}", key=f"chat_btn_{idx}"):
            memory["current_chat_id"] = chat["id"]
            save_memory(memory)

            new_chat = get_current_chat(memory)
            st.session_state.messages = new_chat["messages"]
            st.rerun()

    with col2:
        if st.button("🗑️", key=f"delete_btn_{idx}"):
            memory = delete_chat(memory, chat["id"])
            save_memory(memory)

            new_chat = get_current_chat(memory)
            st.session_state.messages = new_chat["messages"]
            st.rerun()

# ---------------- HEADER ---------------- #
st.title("💰 AI Financial Advisor")
st.caption("Smart assistant for budgeting, savings, and investments")

# ---------------- CHAT ---------------- #
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------- CHARTS ---------------- #
if st.session_state.get("show_charts", False):
    df = st.session_state["last_expenses"]

    st.subheader("📊 Visual Breakdown")

    fig1, ax1 = plt.subplots()
    ax1.pie(df["Amount"], labels=df["Category"], autopct='%1.1f%%')
    st.pyplot(fig1)

    fig2, ax2 = plt.subplots()
    ax2.bar(df["Category"], df["Amount"])
    st.pyplot(fig2)

# ---------------- CSV ---------------- #
uploaded_file = st.file_uploader("Upload CSV for expense analysis", type=["csv"])

if uploaded_file and not st.session_state["csv_uploaded"]:
    try:
        files = {"file": uploaded_file}

        res = requests.post(
            "http://127.0.0.1:5000/upload/",
            files=files
        )

        data = res.json()

        if "expenses" not in data:
            st.error("Invalid response from server")
            st.write(data)
            st.stop()

        expenses = data["expenses"]

        df = pd.DataFrame(list(expenses.items()), columns=["Category", "Amount"])
        st.session_state["last_expenses"] = df
        st.session_state["show_charts"] = True

        csv_reply = "📊 **Expense Breakdown**\n\n"
        for k, v in expenses.items():
            csv_reply += f"- {k}: ₹{v}\n"

        csv_reply += f"\n🤖 **Insights:**\n{data['ai_insights']}"

        
        st.session_state["csv_insights"] = data["ai_insights"]

        st.session_state.messages.append({
            "role": "assistant",
            "content": csv_reply
        })

        st.session_state["csv_uploaded"] = True

        current_chat = get_current_chat(memory)
        current_chat["messages"] = st.session_state.messages
        save_memory(memory)

        st.rerun()

    except Exception as e:
        st.error(f"Upload error: {str(e)}")

# ---------------- INPUT ---------------- #
user_input = st.chat_input("Ask about saving, investing, budgeting...")

if user_input:
    # 🔥 hide charts after question
    st.session_state["show_charts"] = False

    st.session_state.messages.append({"role": "user", "content": user_input})

    memory["profile"] = update_profile(user_input, memory.get("profile", {}))

    try:
        res = requests.post(
            "http://127.0.0.1:5000/chat",
            json={
                "message": user_input,
                "history": st.session_state.messages,
                "profile": memory["profile"],
                "insights": st.session_state.get("csv_insights", "")
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