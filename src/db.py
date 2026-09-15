"""
Lightweight database layer using Python's built-in sqlite3 module — no
external dependencies required to run the core pipeline.

For production use with MySQL, swap get_connection() for a PyMySQL/
SQLAlchemy connection (see README "Switching to MySQL" section). The
SQL used throughout is plain ANSI SQL and needs only minor changes
(e.g. DATE(created_at) syntax) to run against MySQL.
"""

import os
import sqlite3
import config


def get_connection():
    os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_schema():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            amount REAL,
            quantity INTEGER,
            region TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()
