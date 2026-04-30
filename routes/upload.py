from flask import Blueprint, request, jsonify
from utils.csv_parser import parse_csv
from utils.expense_analyzer import analyze_expenses
from services.expense_ai_service import generate_ai_insights

upload_bp = Blueprint("upload", __name__)

@upload_bp.route("/", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    try:
        expenses = parse_csv(file)

        breakdown = analyze_expenses(expenses)  # ✅ FIXED

        ai_response = generate_ai_insights(breakdown)  # ✅ FIXED

        return jsonify({
            "expenses": expenses,
            "breakdown": breakdown,
            "ai_insights": ai_response
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500