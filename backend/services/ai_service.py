"""
Smart Waste Segregation AI Service (Ollama Powered)
Fully offline, production-ready AI using local LLM
"""

import requests
import logging

logger = logging.getLogger("AI_SERVICE")

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

Responsibilities:
- Classify waste into categories:
  biodegradable, non_biodegradable, hazardous
- Suggest proper disposal methods
- Give recycling guidance
- Promote eco-friendly practices

Rules:
- Be clear, concise, and practical
- Do NOT provide medical or unrelated advice
- Always focus on environmental safety
- If unsure, suggest safe disposal practices
"""

# ----------------------------
# Intent Detection
# ----------------------------
def detect_intent(message: str):
    msg = message.lower()

    if any(word in msg for word in ["how to dispose", "waste", "trash", "garbage", "recycle"]):
        return "waste_query"

    if any(word in msg for word in ["plastic", "food", "battery", "glass", "paper"]):
        return "waste_identification"

    if any(word in msg for word in ["hello", "hi", "hey"]):
        return "greeting"

    return "general"


# ----------------------------
# Fallback Response
# ----------------------------
def fallback_response(intent):
    if intent == "greeting":
        return "Hello! Ask me anything about waste segregation and recycling."

    if intent in ["waste_query", "waste_identification"]:
        return "Please provide details about the waste item."

    return "Could you please describe the waste item?"


# ----------------------------
# Build Prompt
# ----------------------------
def build_prompt(message, history):
    prompt = SYSTEM_PROMPT + "\n\nConversation:\n"

    for msg in history[-5:]:
        role = "User" if msg["role"] == "user" else "Assistant"
        prompt += f"{role}: {msg.get('message', '')}\n"

    prompt += f"User: {message}\nAssistant:"

    return prompt


# ----------------------------
# Ollama Call
# ----------------------------
def generate_ollama_response(prompt):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.6,
                "top_p": 0.9,
                "num_predict": 250
            }
        },
        timeout=30
    )

    if response.status_code != 200:
        raise Exception(f"Ollama error: {response.text}")

    return response.json().get("response", "").strip()


# ----------------------------
# Main Function
# ----------------------------
def generate_ai_response(message: str, history=None):
    if history is None:
        history = []

    intent = detect_intent(message)
    logger.info(f"[AI] Intent: {intent}")

    try:
        prompt = build_prompt(message, history)
        return generate_ollama_response(prompt)

    except Exception as e:
        logger.error(f"Ollama failed: {e}")
        return fallback_response(intent)