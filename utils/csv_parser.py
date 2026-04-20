import pandas as pd

def parse_csv(file):
    df = pd.read_csv(file)

    # Ensure correct columns
    if not {"category", "amount"}.issubset(df.columns):
        raise ValueError("CSV must have 'category' and 'amount' columns")

    expenses = {}

    for _, row in df.iterrows():
        category = row["category"]
        amount = row["amount"]

        expenses[category] = expenses.get(category, 0) + amount

    return expenses