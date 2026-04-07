"""
Smart Waste Segregation Assistant - Main Flask App (Enhanced)
Production-grade Flask server with monitoring, logging, and resilience
"""

import os
import time
import logging
import requests
from flask import Flask, jsonify, request, render_template
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables
load_dotenv()

# Internal imports
from backend.database.db import init_db, check_db_health
from backend.routes.chatbot import chatbot_bp

# ----------------------------
# Logging Setup
# ----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger("APP")

# ----------------------------
# Config
# ----------------------------
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_HEALTH_URL = f"{OLLAMA_BASE_URL}/api/tags"

# ----------------------------
# Ollama Check
# ----------------------------
def check_ollama():
    try:
        res = requests.get(OLLAMA_HEALTH_URL, timeout=3)
        return res.status_code == 200
    except Exception as e:
        logger.warning(f"Ollama check failed: {e}")
        return False

# ----------------------------
# App Factory
# ----------------------------
def create_app():
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )

    # Config
    app.config["JSON_SORT_KEYS"] = False
    app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

    # CORS
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Request Timing Middleware
    @app.before_request
    def start_timer():
        request.start_time = time.time()

    @app.after_request
    def log_response(response):
        duration = time.time() - request.start_time
        logger.info(f"{request.method} {request.path} - {response.status_code} ({duration:.3f}s)")
        return response

    # Register Blueprint
    app.register_blueprint(chatbot_bp, url_prefix="/api/chatbot")

    # Root → UI
    @app.route("/")
    def home():
        return render_template("index.html")

    # Health Check
    @app.route("/health")
    def health():
        db_status = check_db_health()
        ollama_status = check_ollama()

        return jsonify({
            "status": "ok" if db_status and ollama_status else "degraded",
            "database": "connected" if db_status else "disconnected",
            "ai_service": "running" if ollama_status else "offline"
        })

    # Readiness Check
    @app.route("/ready")
    def ready():
        return jsonify({
            "ready": True,
            "services": {
                "database": check_db_health(),
                "ollama": check_ollama()
            }
        })

    # Debug Routes
    @app.route("/routes")
    def list_routes():
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                "endpoint": rule.endpoint,
                "methods": list(rule.methods),
                "route": str(rule)
            })
        return jsonify(routes)

    # Global Error Handler
    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled Exception: {e}")
        return jsonify({
            "error": "Something went wrong",
            "details": str(e)
        }), 500

    # 404 Handler
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "error": "Route not found",
            "path": request.path
        }), 404

    return app

# ----------------------------
# Entry Point
# ----------------------------
if __name__ == "__main__":
    logger.info("🚀 Starting Smart Waste Segregation Assistant...")

    # Initialize Database
    try:
        init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database init failed: {e}")

    # Check Ollama
    if check_ollama():
        logger.info("✅ AI service detected (Ollama running)")
    else:
        logger.warning("⚠️ AI service not running (fallback enabled)")

    app = create_app()

    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("DEBUG", "True") == "True"

    logger.info(f"🌐 Server running at: http://localhost:{PORT}")

    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=DEBUG
    )