import cohere
import os
from dotenv import load_dotenv
from utils.finance import extract_income, calculate_budget
from services.rag_service import query_rag

load_dotenv()

co = cohere.Client(os.getenv("COHERE_API_KEY"))

# ---------------- 🚨 RULE-BASED OVERRIDE ---------------- #
def rule_based_override(user_input):
    text = user_input.lower()

    # RENT RULE
    if "rent" in text:
        if "45" in text or "50" in text:
            return """
1. Summary:
Spending above 40% of income on rent is risky.
It can reduce your ability to save.

2. Investment Suggestions:
- Reduce rent by moving or sharing
- Keep rent below 40% of income

3. Risk Level:
High. High rent limits savings.

4. Action Steps:
- Calculate rent-to-income ratio
- Look for cheaper housing options
- Cut unnecessary expenses

5. Follow-up Question:
What percentage of your income goes to rent?
"""

    # SAVING RULE
    if "saving 10%" in text:
        return """
1. Summary:
Saving 10% is below the recommended level.
You should aim for at least 20%.

2. Investment Suggestions:
- Increase savings gradually to 20%
- Automate monthly savings

3. Risk Level:
Medium. Low savings can affect future goals.

4. Action Steps:
- Track expenses
- Cut unnecessary spending
- Increase savings step by step

5. Follow-up Question:
Can you increase your savings to 15–20%?
"""

    return None


# ---------------- 🧹 HELPERS ---------------- #
def format_headings(text):
    text = text.replace("## Summary", "1. Summary")
    text = text.replace("## Investment Suggestions", "2. Investment Suggestions")
    text = text.replace("## Risk Level", "3. Risk Level")
    text = text.replace("## Action Steps", "4. Action Steps")
    text = text.replace("## Follow-up Question", "5. Follow-up Question")
    return text

def fix_risk_level(text):
    text = text.replace("Medium to High", "Medium")
    text = text.replace("Low to Medium", "Low")
    text = text.replace("High to Medium", "High")
    return text

def clean_spacing(text):
    return text.strip()


# ---------------- 🤖 MAIN FUNCTION ---------------- #
def get_ai_response(user_input, history=[]):

    # 🔥 STEP 1: RULE CHECK (MOST IMPORTANT)
    override = rule_based_override(user_input)
    if override:
        return override.strip()

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
        budget_section = ""

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

CRITICAL RULES (MUST FOLLOW):

- Rent > 40% → always say it is risky
- Saving < 20% → always say it is insufficient
- Emergency fund → always recommend 3–6 months
- SIP → good for beginners (long-term investing)

- Equity investments → Medium risk
- Debt instruments → Low risk
- Savings goals → Low risk

- If goal amount + timeline given → MUST calculate monthly savings
- NEVER assume new numbers if already provided
- ALWAYS use previous conversation data

- For budgeting:
  - Use 50/30/20 rule
  - Give at least 2 cost-cutting actions
  - Do NOT mix rent rules with general expenses

----------------------

Instructions:

- Be direct, practical, and concise
- Do NOT invent numbers
- Avoid vague suggestions

# 🔥 NEW (VERY IMPORTANT)
- If user provides a specific amount:
  - MUST give exact ₹ allocation (numbers required)
  - Allocation MUST sum to total amount
  - Example: ₹20,000 + ₹10,000 + ₹10,000 = ₹40,000

- NEVER say "a portion", "some amount", or "consider investing"
- ALWAYS include numbers when money is mentioned

- If savings:
  - Suggest allocation (e.g., 60/30/10 split)

- If goal:
  - Give monthly saving plan (₹/month + timeline)

- For short-term goals:
  - Prefer saving over investing

- Include simple calculations when relevant

----------------------

Output Format:

1. Summary:
(2 short lines)

2. Investment Suggestions:
- Must include ₹ amounts
- Suggestion 1
- Suggestion 2

3. Risk Level:
(Low/Medium/High + correct reason)

4. Action Steps:
- Include at least one numeric step (₹ or %)
- Step 1
- Step 2
- Step 3

5. Follow-up Question:

----------------------

Rules:

- Keep response under 100 words
- Use simple language
- Be specific and actionable
- NO generic explanations

----------------------

User Query:
{user_input}
"""

    # ---------------- 🤖 MODEL CALL ---------------- #
    response = co.chat(
        model="command-r-plus-08-2024",
        message=prompt,
        temperature=0.4
    )

    ai_text = response.text
    ai_text = format_headings(ai_text)
    ai_text = fix_risk_level(ai_text)
    ai_text = clean_spacing(ai_text)

    final_response = f"""
{budget_section}
{ai_text}
"""

    return final_response.strip()