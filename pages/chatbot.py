import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Finance Advisor", page_icon="💰")

# Custom CSS to pin the input bar to the bottom of the screen
st.markdown("""
<style>
            


.chat-input-container {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: #0e1117;
    padding: 10px 20px;
    border-top: 1px solid #333;
    z-index: 1000;
}

.main-content {
    padding-bottom: 120px;
}

[data-testid="stFileUploader"] small {
    display: none;
}


[data-testid="stFileUploader"] {
    margin-top: -10px;
}

.row-widget.stTextInput, 
.row-widget.stFileUploader, 
.row-widget.stButton {
    display: flex;
    align-items: center;
}

div[data-testid="column"] {
    padding: 0 !important;
}

[data-testid="stFileUploader"] small {
    display: none;
}


</style>
""", unsafe_allow_html=True)


st.markdown('<div class="main-content">', unsafe_allow_html=True)

st.title("💰 AI Financial Advisor")
st.subheader("💬 Chat with AI")

# Persist chat history across reruns using session state
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

st.markdown('</div>', unsafe_allow_html=True)



st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)

col1, col2, col3 = st.columns([5, 2, 1])

with col1:
    user_input = st.text_input(
        "",
        placeholder="Ask anything...",
        label_visibility="collapsed"
    )

with col2:
    uploaded_file = st.file_uploader(
        "",
        type=["csv"],
        label_visibility="collapsed"
    )

with col3:
    submit = st.button("Send")

st.markdown('</div>', unsafe_allow_html=True)



if submit:

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        try:
            res = requests.post(
                "http://127.0.0.1:5000/chat",
                json={"message": user_input}
            )
            data = res.json()
            bot_reply = data.get("reply", "Error")

        except:
            bot_reply = "Backend not reachable"

        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        st.rerun()  # Re-render the page so the new messages show up immediately


    if uploaded_file:
        files = {"file": uploaded_file}

        res = requests.post(
            "http://127.0.0.1:5000/upload/",
            files=files
        )

        data = res.json()

        st.subheader("📊 Expense Breakdown")

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
