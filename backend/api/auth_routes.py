"""
Authentication API Routes — Register, Login, Google OAuth, Profile
Uses JWT tokens with 7-day expiry. Passwords hashed with werkzeug.
Supports Google OAuth sign-in via ID token verification.
"""

import jwt
import re
import datetime
import logging
from functools import wraps
from flask import Blueprint, request, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db, execute_query, USE_POSTGRES

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

import os
JWT_SECRET = os.environ.get("JWT_SECRET", "websec-ai-secret-key-change-in-production")
JWT_EXPIRY_DAYS = 7
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")


# -----------------------------------------------
# EMAIL VALIDATION
# -----------------------------------------------
def _is_valid_email(email):
    """Validate email format with strict regex."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False

    # Block disposable/fake email domains
    disposable_domains = [
        "mailinator.com", "guerrillamail.com", "tempmail.com", "throwaway.email",
        "yopmail.com", "sharklasers.com", "guerrillamailblock.com", "grr.la",
        "dispostable.com", "trashmail.com", "fakeinbox.com", "temp-mail.org",
        "10minutemail.com", "maildrop.cc",
    ]
    domain = email.split("@")[1].lower()
    if domain in disposable_domains:
        return False

    # Must have at least 2-char TLD
    tld = domain.split(".")[-1]
    if len(tld) < 2:
        return False

    return True


# -----------------------------------------------
# JWT HELPERS
# -----------------------------------------------
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

    if not _is_valid_email(email):
        return jsonify({"error": "Please enter a valid email address"}), 400

    db = get_db()
    try:
        if USE_POSTGRES:
            import psycopg2.extras
            cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        else:
            cursor = db.cursor()
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))

        existing = cursor.fetchone()
        if existing:
            return jsonify({"error": "Email already registered"}), 409

        password_hash = generate_password_hash(password)

        if USE_POSTGRES:
            cursor.execute(
                "INSERT INTO users (email, name, password_hash, auth_provider) VALUES (%s, %s, %s, %s) RETURNING id",
                (email, name, password_hash, "local"),
            )
            user_id = cursor.fetchone()["id"]
        else:
            cursor.execute(
                "INSERT INTO users (email, name, password_hash, auth_provider) VALUES (?, ?, ?, ?)",
                (email, name, password_hash, "local"),
            )
            user_id = cursor.lastrowid

        db.commit()
        token = create_token(user_id, email, name)

        return jsonify({
            "token": token,
            "user": {"id": user_id, "email": email, "name": name},
        }), 201

    except Exception as e:
        db.rollback()
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
        if USE_POSTGRES:
            import psycopg2.extras
            cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(
                "SELECT id, email, name, password_hash FROM users WHERE email = %s",
                (email,),
            )
        else:
            cursor = db.cursor()
            cursor.execute(
                "SELECT id, email, name, password_hash FROM users WHERE email = ?",
                (email,),
            )

        user = cursor.fetchone()
        if user:
            user = dict(user)

        if not user or not user.get("password_hash"):
            return jsonify({"error": "Invalid email or password"}), 401

        if not check_password_hash(user["password_hash"], password):
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
# GOOGLE OAUTH
# -----------------------------------------------
@auth_bp.route("/google", methods=["POST"])
def google_auth():
    """Verify Google ID token and create/login user."""
    data = request.get_json()
    id_token_str = data.get("credential") or data.get("id_token") or ""

    if not id_token_str:
        return jsonify({"error": "Google credential is required"}), 400

    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests

        # Verify the ID token with Google
        idinfo = id_token.verify_oauth2_token(
            id_token_str,
            google_requests.Request(),
            GOOGLE_CLIENT_ID,
        )

        google_id = idinfo.get("sub")
        email = idinfo.get("email", "").lower()
        name = idinfo.get("name", email.split("@")[0])
        avatar_url = idinfo.get("picture", "")

        if not email:
            return jsonify({"error": "Could not get email from Google"}), 400

    except ValueError as e:
        logger.error(f"Google token verification failed: {e}")
        return jsonify({"error": "Invalid Google token"}), 401
    except Exception as e:
        logger.error(f"Google auth error: {e}")
        return jsonify({"error": "Google authentication failed"}), 500

    # Find or create user
    db = get_db()
    try:
        if USE_POSTGRES:
            import psycopg2.extras
            cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT id, email, name FROM users WHERE email = %s", (email,))
        else:
            cursor = db.cursor()
            cursor.execute("SELECT id, email, name FROM users WHERE email = ?", (email,))

        user = cursor.fetchone()
        if user:
            user = dict(user)

        if user:
            # Existing user — update google_id and avatar if needed
            if USE_POSTGRES:
                cursor.execute(
                    "UPDATE users SET google_id = %s, avatar_url = %s, auth_provider = %s WHERE id = %s",
                    (google_id, avatar_url, "google", user["id"]),
                )
            else:
                cursor.execute(
                    "UPDATE users SET google_id = ?, avatar_url = ?, auth_provider = ? WHERE id = ?",
                    (google_id, avatar_url, "google", user["id"]),
                )
            db.commit()
            token = create_token(user["id"], user["email"], user["name"])
            return jsonify({
                "token": token,
                "user": {"id": user["id"], "email": user["email"], "name": user["name"]},
            })
        else:
            # New user — create account (no password for Google users)
            if USE_POSTGRES:
                cursor.execute(
                    "INSERT INTO users (email, name, auth_provider, google_id, avatar_url) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                    (email, name, "google", google_id, avatar_url),
                )
                user_id = cursor.fetchone()["id"]
            else:
                cursor.execute(
                    "INSERT INTO users (email, name, auth_provider, google_id, avatar_url) VALUES (?, ?, ?, ?, ?)",
                    (email, name, "google", google_id, avatar_url),
                )
                user_id = cursor.lastrowid

            db.commit()
            token = create_token(user_id, email, name)
            return jsonify({
                "token": token,
                "user": {"id": user_id, "email": email, "name": name},
            }), 201

    except Exception as e:
        db.rollback()
        logger.error(f"Google auth DB error: {e}")
        return jsonify({"error": "Authentication failed"}), 500
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
