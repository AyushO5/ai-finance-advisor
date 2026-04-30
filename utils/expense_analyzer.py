def analyze_expenses(expenses):
    total = sum(expenses.values())

    breakdown = []

    for category, amount in expenses.items():
        percentage = (amount / total) * 100
        breakdown.append(f"{category}: ₹{amount} ({percentage:.1f}%)")

    # 🔥 NO HARD DECISIONS HERE
    # just return clean data

    return breakdown