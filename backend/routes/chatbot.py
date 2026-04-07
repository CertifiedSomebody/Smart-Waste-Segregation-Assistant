import requests
from flask import Blueprint, request, jsonify

chatbot_bp = Blueprint("chatbot", __name__)

# ----------------------------
# Ollama Config
# ----------------------------
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:1b"

# ----------------------------
# System Prompt (UPDATED)
# ----------------------------
SYSTEM_PROMPT = """
You are an AI Smart Waste Segregation Assistant.

Your role:
- Classify waste into categories like:
  biodegradable, non-biodegradable, hazardous
- Help users understand how to dispose of waste properly
- Suggest recycling methods
- Guide users in a simple, clear, and eco-friendly way

Rules:
- Be concise and practical
- Ask 1 relevant follow-up question if needed
- Do NOT give medical or unrelated advice
- If unsure, suggest general safe disposal practices
- Focus on environmental impact and proper segregation
"""

# ----------------------------
# Chat Route
# ----------------------------
@chatbot_bp.route("/chat", methods=["POST", "OPTIONS"])
def chat():

    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        user_message = data.get("message", "").strip()
        history = data.get("history", [])

        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400

        # ----------------------------
        # Build conversation
        # ----------------------------
        conversation = SYSTEM_PROMPT + "\n\n"

        if isinstance(history, list):
            for msg in history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                conversation += f"{role}: {content}\n"

        conversation += f"user: {user_message}\nassistant:"

        # ----------------------------
        # Call Ollama
        # ----------------------------
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": conversation,
                "stream": False,
                "options": {
                    "temperature": 0.6,
                    "top_p": 0.9,
                    "num_predict": 250
                }
            },
            timeout=60
        )

        response.raise_for_status()
        result = response.json()

        ai_text = result.get("response") or result.get("message", {}).get("content", "")
        ai_text = ai_text.strip()

        if not ai_text:
            ai_text = "Sorry, I couldn't generate a response."

        return jsonify({
            "response": ai_text
        })

    # ----------------------------
    # Errors
    # ----------------------------
    except requests.exceptions.ConnectionError:
        return jsonify({
            "error": "Ollama not running. Start it with: ollama run llama3"
        }), 503

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "AI request timed out"
        }), 504

    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": "AI service unavailable",
            "details": str(e)
        }), 503

    except Exception as e:
        print(f"Backend Crash: {e}")
        return jsonify({
            "error": "Unexpected server error",
            "details": str(e)
        }), 500