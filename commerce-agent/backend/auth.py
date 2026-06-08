"""用户认证模块 — SQLite + PBKDF2 密码哈希"""
import sqlite3, hashlib, os, secrets
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "data" / "users.db"

def get_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    # Seed admin if not exists
    try:
        create_user("admin", "admin123", "admin")
    except ValueError:
        pass  # already exists
    conn.close()

def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    if salt is None:
        salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200000)
    return dk.hex(), salt

def create_user(username: str, password: str, role: str = "user") -> dict:
    conn = get_db()
    existing = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
    if existing:
        conn.close()
        raise ValueError("用户名已存在")
    pw_hash, salt = hash_password(password)
    now = datetime.now().isoformat()
    conn.execute(
        "INSERT INTO users (username, password_hash, salt, role, created_at) VALUES (?, ?, ?, ?, ?)",
        (username, pw_hash, salt, role, now)
    )
    conn.commit()
    user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return {"id": user_id, "username": username, "role": role}

def verify_user(username: str, password: str) -> dict | None:
    conn = get_db()
    row = conn.execute(
        "SELECT id, username, password_hash, salt, role FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    conn.close()
    if not row:
        return None
    pw_hash, _ = hash_password(password, row["salt"])
    if pw_hash == row["password_hash"]:
        return {"id": row["id"], "username": row["username"], "role": row["role"]}
    return None
