import os
import sys
import subprocess
import logging
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ----------------------------
# Logging Setup
# ----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger("MAIN")

# ----------------------------
# Config
# ----------------------------
PORT = os.getenv("PORT", "5000")
DEBUG = os.getenv("DEBUG", "False") == "True"

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")

BACKEND_PATH = "backend/app.py"

# ----------------------------
# Debug startup
# ----------------------------
print("🔥 main.py started")

# ----------------------------
# Check Ollama
# ----------------------------
def check_ollama():
    try:
        res = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if res.status_code == 200:
            models = res.json().get("models", [])
            model_names = [m.get("name") for m in models]

            if OLLAMA_MODEL in model_names:
                return True
            else:
                logger.warning(f"⚠️ Model '{OLLAMA_MODEL}' not found in Ollama")
                logger.warning(f"👉 Available models: {model_names}")
                return False

        return False

    except Exception as e:
        logger.warning(f"Ollama check failed: {e}")
        return False

# ----------------------------
# Validate backend file
# ----------------------------
def check_backend_exists():
    if not os.path.exists(BACKEND_PATH):
        logger.error(f"❌ Backend file not found: {BACKEND_PATH}")
        sys.exit(1)

# ----------------------------
# Start backend
# ----------------------------
def start_backend():
    logger.info("🚀 Starting Smart Waste Segregation Assistant backend...")

    try:
        subprocess.run(
            [sys.executable, BACKEND_PATH],
            check=True
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Backend crashed: {e}")
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")

# ----------------------------
# Main
# ----------------------------
def main():
    print("🚀 main() is running")

    logger.info("===================================")
    logger.info(" 🌱 Smart Waste Segregation Assistant")
    logger.info("===================================")

    # Check backend
    check_backend_exists()

    # Check Ollama
    if check_ollama():
        logger.info("✅ Ollama is running")
        logger.info(f"🧠 Model: {OLLAMA_MODEL}")
    else:
        logger.warning("⚠️ Ollama NOT ready or model missing")
        logger.warning("👉 Run: ollama pull llama3.2:1b")

    logger.info(f"🌐 Server will run at: http://localhost:{PORT}")

    # Start backend
    start_backend()

# ----------------------------
# Entry
# ----------------------------
if __name__ == "__main__":
    main()