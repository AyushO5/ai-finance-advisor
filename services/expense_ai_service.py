import cohere
import os
from dotenv import load_dotenv

load_dotenv()

co = cohere.Client(os.getenv("COHERE_API_KEY"))


def generate_ai_insights(insights, breakdown):

    prompt = f"""
You are a financial advisor.

Analyze the user's expenses and provide structured insights.

-------------------------
Expense Breakdown:
{chr(10).join(breakdown)}

Detected Patterns:
{chr(10).join(insights)}
-------------------------

Follow STRICT format:

1. Insights:
- Insight 1
- Insight 2
- Insight 3

2. Suggestions:
- Suggestion 1
- Suggestion 2
- Suggestion 3

3. Warning:
- Only include if overspending is detected
- Otherwise write: None

Rules:
- Keep it under 100 words
- Be practical and direct
- Avoid generic statements
- Do NOT add extra headings

"""

    response = co.chat(
        model="command-r-plus-08-2024",
        message=prompt,
        temperature=0.4
    )

    return response.text.strip()