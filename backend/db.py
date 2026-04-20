"""
Database module — PostgreSQL for production, SQLite for local development.
Auto-detects DATABASE_URL env var; falls back to SQLite if not set.
"""

import os
import json
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL", "")

# Determine if we're using PostgreSQL (production) or SQLite (local dev)
USE_POSTGRES = DATABASE_URL.startswith("postgres")


def get_db():
    """Get a database connection."""
    if USE_POSTGRES:
        import psycopg2
        import psycopg2.extras
        # Render provides postgres:// but psycopg2 needs postgresql://
        db_url = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        conn = psycopg2.connect(db_url)
        conn.autocommit = False
        return conn
    else:
        import sqlite3
        DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "websec.db")
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn


def _dict_from_row(row, cursor_description):
    """Convert a database row to a dict (works for both pg and sqlite)."""
    if row is None:
        return None
    if isinstance(row, dict):
        return row
    if hasattr(row, 'keys'):
        return dict(row)
    # psycopg2 tuple row
    columns = [desc[0] for desc in cursor_description]
    return dict(zip(columns, row))


def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """
    Execute a query with automatic placeholder conversion.
    SQLite uses ?, PostgreSQL uses %s.
    Returns: dict row, list of dict rows, lastrowid, or None.
    """
    conn = get_db()
    try:
        if USE_POSTGRES:
            # Convert ? placeholders to %s for PostgreSQL
            query = query.replace("?", "%s")
            import psycopg2.extras
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        else:
            cursor = conn.cursor()

        cursor.execute(query, params or ())

        if fetch_one:
            row = cursor.fetchone()
            conn.commit()
            if USE_POSTGRES:
                return dict(row) if row else None
            else:
                return dict(row) if row else None
        elif fetch_all:
            rows = cursor.fetchall()
            conn.commit()
            if USE_POSTGRES:
                return [dict(r) for r in rows]
            else:
                return [dict(r) for r in rows]
        else:
            conn.commit()
            if USE_POSTGRES:
                # Try to get lastrowid via RETURNING
                try:
                    row = cursor.fetchone()
                    return row.get("id") if row else None
                except Exception:
                    return None
            else:
                return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_db():
    """Create tables if they don't exist."""
    conn = get_db()
    cursor = conn.cursor()

    if USE_POSTGRES:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                password_hash TEXT,
                auth_provider TEXT DEFAULT 'local',
                google_id TEXT,
                avatar_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scan_history (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                url TEXT NOT NULL,
                scan_mode TEXT DEFAULT 'general',
                score INTEGER DEFAULT 0,
                grade TEXT DEFAULT 'F',
                severity_counts JSONB DEFAULT '{}',
                results JSONB DEFAULT '[]',
                ai_analysis JSONB DEFAULT '{}',
                crawl_info JSONB DEFAULT '{}',
                timing JSONB DEFAULT '{}',
                scan_log JSONB DEFAULT '[]',
                depth TEXT DEFAULT 'standard',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_scan_history_user
            ON scan_history(user_id, created_at DESC)
        """)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                password_hash TEXT,
                auth_provider TEXT DEFAULT 'local',
                google_id TEXT,
                avatar_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                url TEXT NOT NULL,
                scan_mode TEXT DEFAULT 'general',
                score INTEGER DEFAULT 0,
                grade TEXT DEFAULT 'F',
                severity_counts TEXT DEFAULT '{}',
                results TEXT DEFAULT '[]',
                ai_analysis TEXT DEFAULT '{}',
                crawl_info TEXT DEFAULT '{}',
                timing TEXT DEFAULT '{}',
                scan_log TEXT DEFAULT '[]',
                depth TEXT DEFAULT 'standard',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_scan_history_user
            ON scan_history(user_id, created_at DESC)
        """)

    conn.commit()
    conn.close()
    db_type = "PostgreSQL" if USE_POSTGRES else "SQLite"
    logger.info(f"Database initialized ({db_type})")
