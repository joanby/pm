from backend.db.connection import get_connection


def find_user(username, path=None):
    conn = get_connection(path)
    cursor = conn.cursor()
    row = cursor.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None
