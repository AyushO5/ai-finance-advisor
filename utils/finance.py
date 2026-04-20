import re

def extract_income(text):
    match = re.search(r'\d+', text)
    return int(match.group()) if match else None


def calculate_budget(income):
    needs = int(income * 0.5)
    wants = int(income * 0.3)
    savings = int(income * 0.2)

    return needs, wants, savings
