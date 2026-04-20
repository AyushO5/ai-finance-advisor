from flask import Blueprint, request, jsonify
from services.lm_service import get_ai_response

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message")

    if not user_input:
        return jsonify({"error": "Message required"}), 400

    reply = get_ai_response(user_input)

    return jsonify({"reply": reply})