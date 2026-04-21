import cohere
import os
from dotenv import load_dotenv
from utils.finance import extract_income, calculate_budget
from services.rag_service import query_rag

load_dotenv()

co = cohere.Client(os.getenv("COHERE_API_KEY"))

def format_headings(text):
    # Cohere sometimes returns markdown-style headings (##); normalize them to numbered format
    text = text.replace("## Summary", "1. Summary")
    text = text.replace("## Investment Suggestions", "2. Investment Suggestions")
    text = text.replace("## Risk Level", "3. Risk Level")
    text = text.replace("## Action Steps", "4. Action Steps")
    text = text.replace("## Follow-up Question", "5. Follow-up Question")

    return text

def fix_risk_level(text):
    # Cohere occasionally returns compound labels; reduce them to single-word values
    text = text.replace("Medium to High", "Medium")
    text = text.replace("Low to Medium", "Low")
    text = text.replace("High to Medium", "High")
    return text

def clean_spacing(text):
    return text.strip()



def get_ai_response(user_input, history=[]):

    # ---------------- 🧠 BUILD HISTORY ---------------- #
    history_text = ""
    for msg in history[-5:]:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_text += f"{role}: {msg['content']}\n"

    # ---------------- 💰 BUDGET LOGIC ---------------- #
    income = extract_income(user_input)

    if income:
        needs, wants, savings = calculate_budget(income)
        budget_section = f"""
Budget Breakdown:
- Needs: ₹{needs}
- Wants: ₹{wants}
- Savings: ₹{savings}
"""
    else:
        budget_section = ""   # 🔥 removed annoying message

    # ---------------- 📚 RAG CONTROL ---------------- #
    if len(user_input.split()) > 5:
        context = query_rag(user_input)
    else:
        context = ""

    print("RAG CONTEXT:", context)

    # ---------------- 🧠 PROMPT ---------------- #
    prompt = f"""
Previous Conversation:
{history_text}

You are a practical financial advisor.

----------------------
Financial Knowledge:
{context}
----------------------

Instructions:

- Use relevant financial rules if helpful
- Do NOT invent numbers
- If data is missing, use conditional advice
- If input is short (yes/no), continue conversation naturally
- Avoid textbook-style explanations
- Use short, conversational sentences
- Sound like a real human advisor, not a report
- Be concise and practical
- When the user provides a specific amount, suggest a clear allocation (₹ distribution)
- Avoid vague phrases like "small investment"
- Ensure Risk Level is consistent with the investment type
- Avoid generic advice like "research more" or "consider options"
- Give specific, actionable suggestions (numbers if possible)
- If the user mentions a goal amount (e.g., buying something), break it into a simple savings plan
- Show monthly saving options (e.g., ₹5000/month → X months)
- Prefer simple saving strategies over investments for short-term goals
- Avoid suggesting investments like mutual funds or FD for goals under 1 year
- Include simple calculations when helpful
- Always use information from previous conversation if available (income, savings, goals)
- Do NOT ignore previously mentioned numbers
- If goal amount and timeline are known, calculate exact monthly savings
- NEVER assume a new number if it was already provided earlier
- If goal amount + timeline are given → MUST calculate monthly saving required
- For savings goals → Risk Level = Low (no market risk)

- When mentioning investments:
  - Clearly specify type (equity, debt, index fund)
  - Assign correct risk (Low/Medium/High based on type)

----------------------

Output Format:

1. Summary:
(2 short lines)

2. Investment Suggestions:
- Suggestion 1
- Suggestion 2

3. Risk Level:
(MUST match the suggested investment type)

4. Action Steps:
- Step 1
- Step 2
- Step 3

5. Follow-up Question:
(Ask something useful)

----------------------

Rules:

- Keep response under 100 words
- Use simple language
- Be direct and specific

----------------------

User Query:
{user_input}
"""

    # ---------------- 🤖 MODEL CALL ---------------- #
    response = co.chat(
        model="command-r-plus-08-2024",
        message=prompt,
        temperature=0.4   # 🔥 more stable
    )

    ai_text = response.text
    ai_text = format_headings(ai_text)
    ai_text = fix_risk_level(ai_text)
    ai_text = clean_spacing(ai_text)

    # ---------------- 🎯 FINAL RESPONSE ---------------- #
    final_response = f"""
{budget_section}
{ai_text}
"""

    return final_response.strip()
