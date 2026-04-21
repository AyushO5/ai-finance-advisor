from flask import Blueprint, request, jsonify
from services.lm_service import get_ai_response

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/", methods=["POST"])
def chat():
    data = request.get_json()

    user_input = data.get("message")
    history = data.get("history", [])   # 🧠 NEW

    if not user_input:
        return jsonify({"error": "Message required"}), 400

    # 🔥 Handle short replies like "yes", "ok"
    if len(user_input.split()) <= 3:
        user_input = f"User said: '{user_input}'. Continue the previous conversation appropriately."

    reply = get_ai_response(user_input, history)   # 🧠 PASS HISTORY

    return jsonify({"reply": reply})