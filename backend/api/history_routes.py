"""
Scan History API Routes — View past scan results for authenticated users.
"""

import json
import logging
from flask import Blueprint, jsonify, g
from api.auth_routes import require_auth
from db import get_db

logger = logging.getLogger(__name__)

history_bp = Blueprint("history", __name__, url_prefix="/api")


def _parse_json_field(value, default):
    """Safely parse a JSON string field."""
    if not value:
        return default
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
        rows = db.execute(
            """SELECT id, url, score, grade, severity_counts, depth, created_at
               FROM scan_history
               WHERE user_id = ?
               ORDER BY created_at DESC
               LIMIT 50""",
            (g.user_id,),
        ).fetchall()

        history = []
        for row in rows:
            history.append({
                "id": row["id"],
                "url": row["url"],
                "score": row["score"],
                "grade": row["grade"],
                "severity_counts": _parse_json_field(row["severity_counts"], {}),
                "depth": row["depth"],
                "created_at": row["created_at"],
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
        row = db.execute(
            """SELECT * FROM scan_history
               WHERE id = ? AND user_id = ?""",
            (scan_id, g.user_id),
        ).fetchone()

        if not row:
            return jsonify({"error": "Scan not found"}), 404

        return jsonify({
            "id": row["id"],
            "url": row["url"],
            "score": row["score"],
            "grade": row["grade"],
            "severity_counts": _parse_json_field(row["severity_counts"], {}),
            "results": _parse_json_field(row["results"], []),
            "ai_analysis": _parse_json_field(row["ai_analysis"], {}),
            "crawl_info": _parse_json_field(row["crawl_info"], {}),
            "timing": _parse_json_field(row["timing"], {}),
            "scan_log": _parse_json_field(row["scan_log"], []),
            "depth": row["depth"],
            "created_at": row["created_at"],
        })

    except Exception as e:
        logger.error(f"Scan detail fetch failed: {e}")
        return jsonify({"error": "Failed to fetch scan details"}), 500
    finally:
        db.close()
