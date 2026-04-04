"""
AI Chatbot API for WebGuard
Uses Google Gemini to provide advanced web security assistance.
Restricted to web app and ecommerce security topics only.
"""

import os
import logging
from flask import Blueprint, request, jsonify

logger = logging.getLogger(__name__)

chat_bp = Blueprint("chat", __name__, url_prefix="/api")

# Lazy-initialized Gemini client (avoids crash at import time)
_client = None
_init_error = None

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCVVpKGWb3hT-zqKzYJ4Qf8tgWBfp6R2YQ")

def get_client():
    """Lazy-init the Gemini client. Returns (client, error_string)."""
    global _client, _init_error
    if _client is not None:
        return _client, None
    if _init_error is not None:
        return None, _init_error
    try:
        from google import genai
        _client = genai.Client(api_key=GEMINI_API_KEY)
        logger.info("[CHAT] Gemini client initialized successfully")
        return _client, None
    except Exception as e:
        _init_error = str(e)
        logger.error(f"[CHAT] Failed to init Gemini: {e}")
        return None, _init_error


SYSTEM_PROMPT = """You are WebGuard AI — an advanced cybersecurity assistant specializing in web application and ecommerce website security.

YOUR ROLE:
- Help users fix security vulnerabilities in their web applications and ecommerce stores
- Provide exact commands, code snippets, configurations, and step-by-step instructions
- Give advanced-level technical guidance (server configs, WAF rules, secure coding patterns)
- Explain OWASP Top 10 vulnerabilities and how to remediate them
- Help with: SQL Injection, XSS, CSRF, SSRF, authentication flaws, session management, API security, payment security, SSL/TLS, security headers, access control, input validation, output encoding, rate limiting, CORS, CSP, HSTS, and all web security topics

RESPONSE STYLE:
- Be direct and technical — give actual commands and code, not just theory
- Use code blocks for commands and configs
- Structure answers with clear sections when needed
- If a fix involves multiple steps, number them clearly
- Always mention the security impact of the issue
- Suggest both quick fixes and long-term solutions

STRICT RESTRICTIONS:
- ONLY answer questions related to web application security, ecommerce security, website fixes, server configuration, and related technical topics
- If someone asks about anything NOT related to web/ecommerce security (e.g., general coding, personal questions, math, other topics), politely decline and say: "I'm specialized in web application and ecommerce security only. Please ask me about website vulnerabilities, security fixes, server hardening, or ecommerce protection."
- Never provide information that could be used for malicious hacking — only defensive security guidance
- Never generate malware, exploits, or attack tools"""


@chat_bp.route("/chat", methods=["POST"])
def chat():
    """Handle chat messages. Expects { message, history[] }"""
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()
        history = data.get("history", [])

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        if len(user_message) > 2000:
            return jsonify({"error": "Message too long (max 2000 chars)"}), 400

        # Get or init the Gemini client
        client, init_err = get_client()
        if client is None:
            logger.error(f"[CHAT] Client unavailable: {init_err}")
            return jsonify({"error": f"AI engine failed to initialize. Error: {init_err}"}), 500

        # Build conversation for Gemini
        contents = []

        # System prompt as first exchange
        contents.append({
            "role": "user",
            "parts": [{"text": SYSTEM_PROMPT + "\n\nAcknowledge these instructions and wait for my question."}]
        })
        contents.append({
            "role": "model",
            "parts": [{"text": "Understood. I'm WebGuard AI, ready to help with web and ecommerce security. What's your question?"}]
        })

        # Add conversation history (last 10 messages)
        for msg in history[-10:]:
            role = "user" if msg.get("role") == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg.get("content", "")}]
            })

        # Add current message
        contents.append({
            "role": "user",
            "parts": [{"text": user_message}]
        })

        # Call Gemini
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
        )

        reply = response.text.strip() if response.text else "I couldn't generate a response. Please try again."

        return jsonify({"reply": reply})

    except Exception as e:
        logger.error(f"[CHAT] Error: {e}")
        return jsonify({"error": f"AI error: {str(e)[:200]}"}), 500
