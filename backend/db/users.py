import uuid
from datetime import UTC, datetime

import bcrypt

from backend.db.connection import get_connection


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except ValueError:
        return False


def find_user(username, path=None):
    conn = get_connection(path)
    cursor = conn.cursor()
    row = cursor.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None


def find_user_by_id(user_id, path=None):
    conn = get_connection(path)
    cursor = conn.cursor()
    row = cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def list_users(path=None):
    conn = get_connection(path)
    cursor = conn.cursor()
    rows = cursor.execute("SELECT * FROM users ORDER BY created_at").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def create_user(username, password, display_name, role="member", path=None):
    conn = get_connection(path)
    cursor = conn.cursor()
    user_id = f"user-{uuid.uuid4().hex[:12]}"
    created_at = datetime.now(UTC).isoformat()
    cursor.execute(
        "INSERT INTO users (id, username, password_hash, display_name, role, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, username, hash_password(password), display_name, role, created_at),
    )
    conn.commit()
    conn.close()
    return find_user_by_id(user_id, path)


def update_user(user_id, display_name=None, role=None, password=None, path=None):
    fields = []
    values = []
    if display_name is not None:
        fields.append("display_name = ?")
        values.append(display_name)
    if role is not None:
        fields.append("role = ?")
        values.append(role)
    if password is not None:
        fields.append("password_hash = ?")
        values.append(hash_password(password))

    if fields:
        conn = get_connection(path)
        cursor = conn.cursor()
        values.append(user_id)
        cursor.execute(f"UPDATE users SET {', '.join(fields)} WHERE id = ?", values)
        conn.commit()
        conn.close()
    return find_user_by_id(user_id, path)


def delete_user(user_id, path=None):
    conn = get_connection(path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()


def count_admins(path=None):
    conn = get_connection(path)
    cursor = conn.cursor()
    row = cursor.execute("SELECT COUNT(*) AS count FROM users WHERE role = 'admin'").fetchone()
    conn.close()
    return row["count"]
