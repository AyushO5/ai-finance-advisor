import re

def extract_income(text):
    # Grabs the first number found in the text — assumes income is mentioned early in the message
    match = re.search(r'\d+', text)
    return int(match.group()) if match else None


def calculate_budget(income):
    # Splits income using the 50/30/20 rule: 50% needs, 30% wants, 20% savings
    needs = int(income * 0.5)
    wants = int(income * 0.3)
    savings = int(income * 0.2)

    return needs, wants, savings
