"""
AI Chatbot API for WebGuard
Uses Google Gemini to provide advanced web security assistance.
Restricted to web app and ecommerce security topics only.
"""

import os
import logging
from flask import Blueprint, request, jsonify
from google import genai

logger = logging.getLogger(__name__)

chat_bp = Blueprint("chat", __name__, url_prefix="/api")

# Gemini client
API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCVVpKGWb3hT-zqKzYJ4Qf8tgWBfp6R2YQ")
client = genai.Client(api_key=API_KEY)

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

        # Build conversation for Gemini
        contents = []

        # Add system prompt as first user message
        contents.append({
            "role": "user",
            "parts": [{"text": SYSTEM_PROMPT + "\n\nAcknowledge these instructions and wait for my question."}]
        })
        contents.append({
            "role": "model",
            "parts": [{"text": "Understood. I'm WebGuard AI, your web application and ecommerce security specialist. I'm ready to help you identify and fix security vulnerabilities. What would you like to know?"}]
        })

        # Add conversation history (last 10 messages to stay within context)
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
        logger.error(f"Chat error: {e}")
        return jsonify({"error": "AI service temporarily unavailable. Please try again."}), 500
