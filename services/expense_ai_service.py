import cohere
import os
from dotenv import load_dotenv

load_dotenv()

co = cohere.Client(os.getenv("COHERE_API_KEY"))


def generate_ai_insights(breakdown):

    prompt = f"""
You are a financial advisor analyzing expenses.

----------------------
Expense Breakdown:
{chr(10).join(breakdown)}

----------------------

Instructions:

- Use numerical reasoning (percentages or proportions)
- If any category is high (like rent), mention rule (e.g., 40%)
- Avoid vague phrases like "significant" or "moderate"
- Be specific and actionable
- Do NOT give generic advice

----------------------

Output Format:

1. Insights:
- Include numbers or percentages

2. Suggestions:
- Practical and specific actions

3. Warning:
- If any category exceeds safe limits
- Otherwise: None

----------------------

Rules:

- Keep under 100 words
- Be direct and specific

"""
# chr(10) is used instead of \n inside the f-string to avoid syntax issues with backslashes
    response = co.chat(
        model="command-r-plus-08-2024",
        message=prompt,
        temperature=0.4 # Low temperature for more consistent, structured output
    )

    return response.text.strip()
