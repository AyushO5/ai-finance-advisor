import re

import re

def extract_income(text):
    text = text.lower()

    income_keywords = ["salary", "income", "earn", "per month", "monthly"]

    if not any(word in text for word in income_keywords):
        return None

    match = re.search(r'\d+', text)

    if match:
        return int(match.group())

    return None

def calculate_budget(income):
    # Splits income using the 50/30/20 rule: 50% needs, 30% wants, 20% savings
    needs = int(income * 0.5)
    wants = int(income * 0.3)
    savings = int(income * 0.2)

    return needs, wants, savings
