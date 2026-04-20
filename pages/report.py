import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    
    files = {"file": uploaded_file}

    res = requests.post(
        "http://127.0.0.1:5000/upload/",
        files=files
    )

    data = res.json()

    # 👇 now this works
    expenses = data["expenses"]

    df = pd.DataFrame(list(expenses.items()), columns=["Category", "Amount"])

    # 📊 Pie Chart
    st.subheader("📊 Expense Distribution")
    fig1, ax1 = plt.subplots()
    ax1.pie(df["Amount"], labels=df["Category"], autopct='%1.1f%%')
    st.pyplot(fig1)

    # 📊 Bar Chart
    st.subheader("📈 Category-wise Spending")
    fig2, ax2 = plt.subplots()
    ax2.bar(df["Category"], df["Amount"])
    st.pyplot(fig2)

    # 🤖 AI Insights
    st.subheader("🤖 AI Insights")
    st.write(data["ai_insights"])