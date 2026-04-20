import requests
import time

# ================= CONFIG ================= #

API_URL = "http://127.0.0.1:5000/chat"
DELAY = 1  # seconds (avoid rate limit)

# ================= TEST DATASET ================= #

test_data = [

    # -------- RENT -------- #
    {"question": "Is spending 50% of income on rent risky?", "keywords": ["40%", "rent", "risky"], "category": "rent"},
    {"question": "Should I move if my rent is too high?", "keywords": ["reduce", "rent", "cost"], "category": "rent"},
    {"question": "What is a safe rent percentage?", "keywords": ["40%", "rent"], "category": "rent"},
    {"question": "Is 45% rent okay?", "keywords": ["40%", "risky"], "category": "rent"},
    {"question": "How to reduce rent expenses?", "keywords": ["share", "move", "reduce"], "category": "rent"},

    # -------- SAVINGS -------- #
    {"question": "How much should I save monthly?", "keywords": ["20%", "saving"], "category": "saving"},
    {"question": "Is saving 10% enough?", "keywords": ["20%", "increase"], "category": "saving"},
    {"question": "Why is saving important?", "keywords": ["emergency", "future"], "category": "saving"},
    {"question": "How to build an emergency fund?", "keywords": ["3", "months", "emergency"], "category": "saving"},
    {"question": "What is a good saving strategy?", "keywords": ["budget", "saving"], "category": "saving"},

    # -------- BUDGET -------- #
    {"question": "How to manage my expenses?", "keywords": ["budget", "track"], "category": "budget"},
    {"question": "How to reduce spending?", "keywords": ["cut", "reduce"], "category": "budget"},
    {"question": "What is budgeting?", "keywords": ["plan", "expenses"], "category": "budget"},
    {"question": "Why am I overspending?", "keywords": ["track", "expenses"], "category": "budget"},
    {"question": "How to control unnecessary expenses?", "keywords": ["limit", "cut"], "category": "budget"},

    # -------- INVESTMENT -------- #
    {"question": "Should I invest or save first?", "keywords": ["emergency", "saving"], "category": "investment"},
    {"question": "Is SIP good for beginners?", "keywords": ["long-term", "investment"], "category": "investment"},
    {"question": "Where should I invest money?", "keywords": ["mutual", "fund"], "category": "investment"},
    {"question": "Is stock market risky?", "keywords": ["risk", "volatile"], "category": "investment"},
    {"question": "Best investment options?", "keywords": ["diversify", "portfolio"], "category": "investment"},
]

# ================= FUNCTIONS ================= #

def get_response(question):
    try:
        res = requests.post(API_URL, json={"message": question})
        data = res.json()
        return data.get("reply", "").lower()
    except:
        return ""

def check_correctness(response, keywords):
    matches = sum(1 for kw in keywords if kw.lower() in response)
    return matches >= (len(keywords) // 2 + 1)

def check_hallucination(response, keywords):
    return not any(kw.lower() in response for kw in keywords)

# ================= EVALUATION ================= #

total = len(test_data)
correct = 0
hallucinated = 0

category_scores = {}

print("\n🚀 Running Evaluation...\n")

for i, item in enumerate(test_data, 1):

    print(f"🔄 Processing {i}/{total}...")

    question = item["question"]
    keywords = item["keywords"]
    category = item["category"]

    response = get_response(question)

    is_correct = check_correctness(response, keywords)
    is_hallucinated = check_hallucination(response, keywords)

    # overall
    if is_correct:
        correct += 1
    if is_hallucinated:
        hallucinated += 1

    # category tracking
    if category not in category_scores:
        category_scores[category] = {"total": 0, "correct": 0}

    category_scores[category]["total"] += 1
    if is_correct:
        category_scores[category]["correct"] += 1

    print(f"Q{i}: {question}")
    print(f"Correct: {'✅' if is_correct else '❌'}")
    print(f"Hallucination: {'⚠️ YES' if is_hallucinated else 'NO'}")
    print("-" * 50)

    time.sleep(DELAY)

# ================= RESULTS ================= #

accuracy = (correct / total) * 100
hallucination_rate = (hallucinated / total) * 100

print("\n📊 FINAL RESULTS")
print(f"Total Questions: {total}")
print(f"Correct Responses: {correct}")
print(f"Accuracy: {accuracy:.2f}%")
print(f"Hallucination Rate: {hallucination_rate:.2f}%")

# ================= CATEGORY RESULTS ================= #

print("\n📊 Category-wise Accuracy:")
for cat, data in category_scores.items():
    acc = (data["correct"] / data["total"]) * 100
    print(f"{cat}: {acc:.2f}%")