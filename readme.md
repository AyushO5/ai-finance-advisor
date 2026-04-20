# 💰 AI Financial Advisor

An AI-powered financial assistant that analyzes expenses, provides budgeting advice, and generates personalized financial insights using LLMs and RAG (Retrieval-Augmented Generation).

---

## Features

- Chat-based financial advisor
- CSV expense analysis with charts
- AI-generated insights
- RAG-based financial knowledge
-  File upload + chat in one interface
-  Evaluation system (accuracy + hallucination)

---

## Tech Stack

- **Frontend:** Streamlit  
- **Backend:** Flask  
- **AI Model:** Cohere  
- **Embeddings:** Sentence Transformers  
- **Vector DB:** ChromaDB  
- **Language:** Python  

---

## How it Works

1. User asks a question or uploads CSV  
2. Backend processes input  
3. RAG retrieves financial rules  
4. LLM generates structured advice  
5. Output shown with insights + charts  

---

## 📂 Project Structure

finance-bot/
│── app.py
│── routes/
│── services/
│ ├── lm_service.py
│ ├── rag_service.py
│ ├── expense_ai_service.py
│── utils/
│── pages/
│── data/
│── evaluate.py
│── README.md


---

## ⚙️ Setup

```bash
git clone https://github.com/YOUR_USERNAME/ai-finance-advisor.git
cd ai-finance-advisor
pip install -r requirements.txt