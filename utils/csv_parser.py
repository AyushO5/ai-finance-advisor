import pandas as pd

def parse_csv(file):
    df = pd.read_csv(file)

    # 🔥 FIX: normalize column names
    df.columns = df.columns.str.lower()

    if "category" not in df.columns or "amount" not in df.columns:
        raise Exception("CSV must have 'category' and 'amount' columns")

    expenses = {}

    for _, row in df.iterrows():
        category = row["category"]
        amount = float(row["amount"])

        if category in expenses:
            expenses[category] += amount
        else:
            expenses[category] = amount

    return expenses
