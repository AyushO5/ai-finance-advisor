import cohere
import os
from dotenv import load_dotenv
from utils.finance import extract_income, calculate_budget
from services.rag_service import query_rag

load_dotenv()
co = cohere.Client(os.getenv("COHERE_API_KEY"))


# ---------------- RULE-BASED OVERRIDE ---------------- #
def rule_based_override(user_input):
    text = user_input.lower()

    if "rent" in text and any(x in text for x in ["45", "50"]):
        return """
1. Summary:
Rent above 40% is risky.
It reduces savings potential.

2. Key Points:
- Recommended: ≤ 40% of income
- High rent → low savings

3. Risk Level:
High. Limits financial flexibility.

4. Action Steps:
- Calculate rent %
- Target below 40%
- Reduce or relocate

5. Follow-up Question:
What % of income goes to rent?
"""

    if "saving 10%" in text:
        return """
1. Summary:
Saving 10% is low.
Aim for at least 20%.

2. Key Points:
- Recommended: 20%+
- Low savings → weak future security

3. Risk Level:
Medium. Impacts long-term goals.

4. Action Steps:
- Increase to 15%
- Track expenses
- Cut 2 unnecessary costs

5. Follow-up Question:
Can you increase savings gradually?
"""

    return None


# ---------------- HELPERS ---------------- #
def format_headings(text):
    text = text.replace("## Summary", "1. Summary")
    text = text.replace("## Investment Suggestions", "2. Key Points")
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


# ---------------- MAIN FUNCTION ---------------- #
def get_ai_response(user_input, history=[], profile={}):

    # 🔥 1. RULE OVERRIDE
    override = rule_based_override(user_input)
    if override:
        return override.strip()

    # 🔥 2. HISTORY BUILD
    history_text = ""
    for msg in history[-5:]:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_text += f"{role}: {msg['content']}\n"

    # 🔥 3. PROFILE CONTEXT
    profile_text = f"""
User Profile:
- Income: {profile.get("income", "Unknown")}
- Goal: {profile.get("goal", "Not specified")}
"""

    # 🔥 4. BUDGET (ONLY IF NEW INCOME)
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

    # 🔥 5. SMART RAG (FIXED 🔥🔥)
    if len(user_input.split()) > 5:
        context = query_rag(user_input)
    else:
        # use last meaningful message
        last_msg = ""
        for msg in reversed(history):
            if msg["role"] == "user" and len(msg["content"].split()) > 3:
                last_msg = msg["content"]
                break
        context = query_rag(last_msg) if last_msg else ""

    print("RAG CONTEXT:", context)

    # 🔥 6. PROMPT
    prompt = f"""
{profile_text}

Previous Conversation:
{history_text}

You are a practical financial advisor.

----------------------
Financial Knowledge:
{context}
----------------------

CRITICAL RULES:

- Rent > 40% → risky
- Saving < 20% → insufficient
- Emergency fund → 3–6 months
- SIP → good for beginners

- Equity → Medium risk
- Debt → Low risk
- Savings goals → Low risk

- ALWAYS use previous context
- NEVER ignore user-provided numbers

----------------------

Instructions:

- Be short, direct, practical
- NO vague advice

- If amount given:
  → MUST give exact ₹ allocation
  → MUST sum correctly

- If goal:
  → give monthly saving plan

- If short reply:
  → continue previous topic

- For budgeting:
  → use 50/30/20 rule
  → give 2 cost-cutting actions

- For factual queries:
  → use exact numbers from context

----------------------

Output Format:

1. Summary:
(2 lines)

2. Key Points:
(Use numbers if possible)

3. Risk Level:
(reason)

4. Action Steps:
- Step 1
- Step 2
- Step 3

5. Follow-up Question:

----------------------

User Query:
{user_input}
"""

    # 🔥 7. MODEL CALL
    response = co.chat(
        model="command-r-plus-08-2024",
        message=prompt,
        temperature=0.3  # 🔥 more stable
    )

    ai_text = response.text
    ai_text = format_headings(ai_text)
    ai_text = fix_risk_level(ai_text)
    ai_text = clean_spacing(ai_text)

    return f"{budget_section}\n{ai_text}".strip()