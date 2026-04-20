def analyze_expenses(expenses):
    total = sum(expenses.values())

    insights = []
    breakdown = []

    for category, amount in expenses.items():
        percentage = (amount / total) * 100

        breakdown.append(f"{category}: ₹{amount} ({percentage:.1f}%)")

        if percentage > 40:
            insights.append(f"High spending on {category}")
        elif percentage < 10:
            insights.append(f"Low spending on {category}")
        else:
            insights.append(f"Moderate spending on {category}")

    return insights, breakdown