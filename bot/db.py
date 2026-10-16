import sqlite3
from contextlib import contextmanager

from bot.config import DB_PATH


@contextmanager
def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with _conn() as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                url TEXT NOT NULL,
                title TEXT,
                last_price REAL,
                UNIQUE(user_id, url)
            )
            """
        )


def add_item(user_id: int, url: str, title: str, price: float) -> bool:
    """Returns False if the user already tracks this URL."""
    try:
        with _conn() as c:
            c.execute(
                "INSERT INTO items (user_id, url, title, last_price) VALUES (?, ?, ?, ?)",
                (user_id, url, title, price),
            )
        return True
    except sqlite3.IntegrityError:
        return False


def list_items(user_id: int) -> list[sqlite3.Row]:
    with _conn() as c:
        return c.execute("SELECT * FROM items WHERE user_id = ?", (user_id,)).fetchall()


def all_items() -> list[sqlite3.Row]:
    with _conn() as c:
        return c.execute("SELECT * FROM items").fetchall()


def remove_item(user_id: int, item_id: int) -> bool:
    with _conn() as c:
        cur = c.execute(
            "DELETE FROM items WHERE id = ? AND user_id = ?", (item_id, user_id)
        )
        return cur.rowcount > 0


def update_price(item_id: int, price: float) -> None:
    with _conn() as c:
        c.execute("UPDATE items SET last_price = ? WHERE id = ?", (price, item_id))
