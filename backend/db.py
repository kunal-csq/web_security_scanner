"""
Database module — SQLite setup for users and scan history.
Auto-creates tables on first run. Zero config needed.
"""

import sqlite3
import os
import logging

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "websec.db")


def get_db():
    """Get a database connection with row_factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            url TEXT NOT NULL,
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
    logger.info(f"Database initialized at {DB_PATH}")
