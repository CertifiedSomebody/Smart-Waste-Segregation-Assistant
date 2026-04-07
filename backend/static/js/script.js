// Smart Waste Segregation Assistant - Frontend Logic
console.log("🚀 Waste Assistant script loaded successfully!");

// -----------------------------
// Config
// -----------------------------
const API_BASE = "http://127.0.0.1:5000/api/chatbot"; 
let sessionId = localStorage.getItem("session_id") || null;

// -----------------------------
// DOM Elements
// -----------------------------
const chatContainer = document.getElementById("chat-container");
const inputField = document.getElementById("user-input");
const sendButton = document.getElementById("send-btn") || document.querySelector("button");

// -----------------------------
// Utility: Add Message
// -----------------------------
function addMessage(text, sender) {
    const msg = document.createElement("div");
    msg.classList.add("message", sender);
    msg.innerText = text;
    chatContainer.appendChild(msg);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// -----------------------------
// Load History
// -----------------------------
async function loadHistory() {
    if (!sessionId) return;

    try {
        console.log(`Loading history for session: ${sessionId}`);

        const res = await fetch(`${API_BASE}/history/${sessionId}`);
        if (!res.ok) return;

        const data = await res.json();
        chatContainer.innerHTML = "";

        data.history.forEach(msg => {
            addMessage(msg.message, msg.role === "user" ? "user" : "bot");
        });

    } catch (err) {
        console.warn("History load failed:", err);
    }
}

// -----------------------------
// Send Message
// -----------------------------
async function sendMessage() {
    const message = inputField.value.trim();
    if (!message) return;

    addMessage(message, "user");
    inputField.value = "";

    try {
        console.log(`Sending message to: ${API_BASE}/chat`);

        const res = await fetch(`${API_BASE}/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId
            })
        });

        const data = await res.json();
        console.log("Server response:", data);

        if (!res.ok) {
            addMessage(`⚠️ Error: ${data.error || "Something went wrong"}`, "bot");
            return;
        }

        sessionId = data.session_id;
        localStorage.setItem("session_id", sessionId);

        addMessage(data.response, "bot");

    } catch (err) {
        console.error("Fetch failed:", err);

        addMessage(
            "⚠️ Network Error: Cannot connect to server. Make sure Flask is running.",
            "bot"
        );
    }
}

// -----------------------------
// Reset Chat
// -----------------------------
async function resetChat() {
    if (!sessionId) return;

    try {
        await fetch(`${API_BASE}/reset/${sessionId}`, {
            method: "POST"
        });

        localStorage.removeItem("session_id");
        sessionId = null;

        chatContainer.innerHTML = "";
        addMessage("Chat reset successfully. Ask me about waste disposal!", "bot");

    } catch (err) {
        console.error("Reset failed:", err);
        addMessage("⚠️ Failed to reset chat.", "bot");
    }
}

// -----------------------------
// Events
// -----------------------------

inputField.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
        e.preventDefault();
        sendMessage();
    }
});

if (sendButton) {
    sendButton.addEventListener("click", function (e) {
        e.preventDefault();
        sendMessage();
    });
}

// -----------------------------
// Init
// -----------------------------
window.onload = () => {
    loadHistory();

    if (!sessionId) {
        addMessage(
            "🌱 Hello! I am your Smart Waste Segregation Assistant. Ask me how to dispose or classify waste.",
            "bot"
        );
    }
};