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



def get_ai_response(user_input):

    
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
        budget_section = "Budget Breakdown: Not enough data provided."

    # Pull relevant financial knowledge from ChromaDB to ground the response
    context = query_rag(user_input)

    prompt = f"""
You are an intelligent financial advisor helping users manage their money.

You MUST follow this workflow internally:
1. Understand the user's financial situation
2. Use the provided financial knowledge if relevant
3. Apply practical reasoning
4. Give clear, actionable advice

----------------------
📚 Financial Knowledge:
{context}
----------------------

🎯 Instructions:
- Use the financial knowledge wherever relevant
- Do NOT include phrases like "Not enough data provided" or system messages.
- Do NOT assume user financial details unless explicitly given.
- Use conditional language like "If your rent exceeds 40%..."
- When a financial rule is known, state it directly and confidently. 
- Avoid unrealistic or uncommon solutions like government programs unless highly relevant.
- Prefer practical, common actions.
- If user income/expenses are unclear, make reasonable assumptions.
- If financial knowledge contains a rule (like percentage limits), you MUST include it clearly in the answer.
- Avoid generic phrases like "common challenge" or "important to balance".
- Be direct and specific.
- Always provide specific actions like "reduce", "track", "cut expenses" for budgeting questions.
- Personalize the advice based on the user's situation
- Be practical, not theoretical
- Avoid generic statements. 
- Avoid suggesting high-risk or speculative investments unless explicitly asked.

📦 Output Format (STRICT):

1. Summary (2 short lines, very clear)

2. Investment Suggestions:
- Bullet point 1
- Bullet point 2

3. Risk Level:
Low / Medium / High (with 1 line reason)

4. Action Steps:
- Step 1
- Step 2
- Step 3

5. Follow-up Question:
(Ask something meaningful to continue conversation)

⚠️ Rules:
- Keep response under 120 words
- Use simple, conversational language
- Do NOT repeat the question
- Do NOT add unnecessary explanations

User Query:{user_input}
"""
    
    print("RAG CONTEXT:", context)

    response = co.chat(
        model="command-r-plus-08-2024", 
        message=prompt,
        temperature=0.5 # Slightly higher than expense_ai_service to allow more varied phrasing
    )

    ai_text = response.text
    ai_text = format_headings(ai_text)
    ai_text = fix_risk_level(ai_text)
    ai_text = clean_spacing(ai_text)

    final_response = f"""
{budget_section}

{ai_text}
"""

    return final_response
