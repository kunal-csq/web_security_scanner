"""
Authentication API Routes — Register, Login, Profile
Uses JWT tokens with 7-day expiry. Passwords hashed with werkzeug.
"""

import jwt
import datetime
import logging
from functools import wraps
from flask import Blueprint, request, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# Secret key for JWT — in production, use env var
import os
JWT_SECRET = os.environ.get("JWT_SECRET", "websec-ai-secret-key-change-in-production")
JWT_EXPIRY_DAYS = 7


def create_token(user_id, email, name):
    """Create a JWT token."""
    payload = {
        "user_id": user_id,
        "email": email,
        "name": name,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=JWT_EXPIRY_DAYS),
        "iat": datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def decode_token(token):
    """Decode and validate a JWT token."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def require_auth(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization", "")

        if auth_header.startswith("Bearer "):
            token = auth_header[7:]

        if not token:
            return jsonify({"error": "Authentication required"}), 401

        payload = decode_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401

        g.user_id = payload["user_id"]
        g.user_email = payload["email"]
        g.user_name = payload["name"]

        return f(*args, **kwargs)
    return decorated


def get_optional_user():
    """Try to extract user from token, return None if not authenticated."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        payload = decode_token(auth_header[7:])
        if payload:
            return payload
    return None


# -----------------------------------------------
# REGISTER
# -----------------------------------------------
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    email = (data.get("email") or "").strip().lower()
    name = (data.get("name") or "").strip()
    password = data.get("password") or ""

    if not email or not name or not password:
        return jsonify({"error": "Email, name, and password are required"}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    if "@" not in email:
        return jsonify({"error": "Invalid email format"}), 400

    db = get_db()
    try:
        # Check if email exists
        existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            return jsonify({"error": "Email already registered"}), 409

        # Create user
        password_hash = generate_password_hash(password)
        cursor = db.execute(
            "INSERT INTO users (email, name, password_hash) VALUES (?, ?, ?)",
            (email, name, password_hash),
        )
        db.commit()

        user_id = cursor.lastrowid
        token = create_token(user_id, email, name)

        return jsonify({
            "token": token,
            "user": {"id": user_id, "email": email, "name": name},
        }), 201

    except Exception as e:
        logger.error(f"Registration failed: {e}")
        return jsonify({"error": "Registration failed"}), 500
    finally:
        db.close()


# -----------------------------------------------
# LOGIN
# -----------------------------------------------
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    db = get_db()
    try:
        user = db.execute(
            "SELECT id, email, name, password_hash FROM users WHERE email = ?",
            (email,),
        ).fetchone()

        if not user or not check_password_hash(user["password_hash"], password):
            return jsonify({"error": "Invalid email or password"}), 401

        token = create_token(user["id"], user["email"], user["name"])

        return jsonify({
            "token": token,
            "user": {"id": user["id"], "email": user["email"], "name": user["name"]},
        })

    except Exception as e:
        logger.error(f"Login failed: {e}")
        return jsonify({"error": "Login failed"}), 500
    finally:
        db.close()


# -----------------------------------------------
# GET CURRENT USER (PROTECTED)
# -----------------------------------------------
@auth_bp.route("/me", methods=["GET"])
@require_auth
def me():
    return jsonify({
        "user": {
            "id": g.user_id,
            "email": g.user_email,
            "name": g.user_name,
        }
    })
