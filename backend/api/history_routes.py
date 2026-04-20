"""
Scan History API Routes — View past scan results for authenticated users.
Compatible with both PostgreSQL and SQLite.
"""

import json
import logging
from flask import Blueprint, jsonify, g
from api.auth_routes import require_auth
from db import get_db, USE_POSTGRES

logger = logging.getLogger(__name__)

history_bp = Blueprint("history", __name__, url_prefix="/api")


def _parse_json_field(value, default):
    """Safely parse a JSON string field. PostgreSQL JSONB returns dicts already."""
    if value is None:
        return default
    if isinstance(value, (dict, list)):
        return value  # Already parsed (PostgreSQL JSONB)
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return default


# -----------------------------------------------
# GET ALL SCAN HISTORY
# -----------------------------------------------
@history_bp.route("/history", methods=["GET"])
@require_auth
def get_history():
    db = get_db()
    try:
        placeholder = "%s" if USE_POSTGRES else "?"
        query = f"""SELECT id, url, scan_mode, score, grade, severity_counts, depth, created_at
               FROM scan_history
               WHERE user_id = {placeholder}
               ORDER BY created_at DESC
               LIMIT 50"""

        if USE_POSTGRES:
            import psycopg2.extras
            cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        else:
            cursor = db.cursor()

        cursor.execute(query, (g.user_id,))
        rows = cursor.fetchall()

        history = []
        for row in rows:
            r = dict(row)
            history.append({
                "id": r["id"],
                "url": r["url"],
                "scan_mode": r.get("scan_mode", "general"),
                "score": r["score"],
                "grade": r["grade"],
                "severity_counts": _parse_json_field(r["severity_counts"], {}),
                "depth": r["depth"],
                "created_at": str(r["created_at"]),
            })

        return jsonify({"history": history, "total": len(history)})

    except Exception as e:
        logger.error(f"History fetch failed: {e}")
        return jsonify({"error": "Failed to fetch history"}), 500
    finally:
        db.close()


# -----------------------------------------------
# GET SINGLE SCAN DETAIL
# -----------------------------------------------
@history_bp.route("/history/<int:scan_id>", methods=["GET"])
@require_auth
def get_scan_detail(scan_id):
    db = get_db()
    try:
        placeholder = "%s" if USE_POSTGRES else "?"
        query = f"""SELECT * FROM scan_history
               WHERE id = {placeholder} AND user_id = {placeholder}"""

        if USE_POSTGRES:
            import psycopg2.extras
            cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        else:
            cursor = db.cursor()

        cursor.execute(query, (scan_id, g.user_id))
        row = cursor.fetchone()

        if not row:
            return jsonify({"error": "Scan not found"}), 404

        r = dict(row)
        return jsonify({
            "id": r["id"],
            "url": r["url"],
            "scan_mode": r.get("scan_mode", "general"),
            "score": r["score"],
            "grade": r["grade"],
            "severity_counts": _parse_json_field(r["severity_counts"], {}),
            "results": _parse_json_field(r["results"], []),
            "ai_analysis": _parse_json_field(r["ai_analysis"], {}),
            "crawl_info": _parse_json_field(r["crawl_info"], {}),
            "timing": _parse_json_field(r["timing"], {}),
            "scan_log": _parse_json_field(r["scan_log"], []),
            "depth": r["depth"],
            "created_at": str(r["created_at"]),
        })

    except Exception as e:
        logger.error(f"Scan detail fetch failed: {e}")
        return jsonify({"error": "Failed to fetch scan details"}), 500
    finally:
        db.close()


# -----------------------------------------------
# DELETE SCAN FROM HISTORY
# -----------------------------------------------
@history_bp.route("/history/<int:scan_id>", methods=["DELETE"])
@require_auth
def delete_scan(scan_id):
    db = get_db()
    try:
        placeholder = "%s" if USE_POSTGRES else "?"
        query = f"DELETE FROM scan_history WHERE id = {placeholder} AND user_id = {placeholder}"

        cursor = db.cursor()
        cursor.execute(query, (scan_id, g.user_id))
        db.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Scan not found"}), 404

        return jsonify({"message": "Scan deleted"})

    except Exception as e:
        db.rollback()
        logger.error(f"Scan delete failed: {e}")
        return jsonify({"error": "Failed to delete scan"}), 500
    finally:
        db.close()
