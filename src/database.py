import sqlite3
import os
from contextlib import closing


DATABASE_URL = os.getenv("DATABASE_URL", "data/transactions.db")

def connect_db(db_path: str) -> sqlite3.Connection:
    """Connect to the SQLite database."""

    dirName = os.path.dirname(db_path)
    if dirName:
        os.makedirs(dirName, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    try:
        conn = connect_db(DATABASE_URL)
        with closing(conn), conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    type TEXT NOT NULL,
                    value INTEGER NOT NULL,
                    description TEXT
                )
                """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_user_id
                ON transactions (user_id);
                """
            )

    except sqlite3.Error as e:
        print(f"ERROR: {e}")


def create_transaction(user_id: int, transactions_type: str, value: int, description: str) -> None:
    try:
        conn = connect_db(DATABASE_URL)
        with closing(conn), conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO transactions (user_id, type, value, description)
                VALUES(?, ?, ?, ?);
                """,
                (user_id, transactions_type, value, description)
            )


    except sqlite3.Error as e:
        print(f"ERROR: {e}")


def get_transactions(user_id: int, limit: int = 20) -> list[sqlite3.Row]:
    try:
        conn = connect_db(DATABASE_URL)
        with closing(conn), conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, timestamp, type, value, description
                FROM transactions
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?;
                """,
                (user_id, limit)
            )
            return cursor.fetchall()

    except sqlite3.Error as e:
        print(f"ERROR: {e}")
        return []


def get_balance(user_id: int) -> int:
    try:
        conn = connect_db(DATABASE_URL)
        with closing(conn), conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT COALESCE(SUM(CASE WHEN type = 'RECEITA' THEN value ELSE -value END),0) as balance
                FROM transactions
                WHERE user_id = ?
                """,
                (user_id,)
            )
            row = cursor.fetchone()
            return row["balance"] if row else 0

    except sqlite3.Error as e:
        print(f"ERROR: {e}")
        return 0


def update_transaction(transaction_id: int, user_id: int, transaction_type: str, value: int, description: str) -> bool:
    try:
        conn = connect_db(DATABASE_URL)
        with closing(conn), conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE transactions
                SET type = ?, value = ?, description =?
                WHERE id = ? AND user_id = ?;
                """,
                (transaction_type, value, description, transaction_id, user_id)
            )
            return cursor.rowcount > 0

    except sqlite3.Error as e:
        print(f"ERROR: {e}")
        return False


def delete_transaction(transaction_id: int, user_id: int) -> bool:
    try:
        conn = connect_db(DATABASE_URL)
        with closing(conn), conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                DELETE FROM transactions
                WHERE id = ? AND user_id = ?;
                """,
                (transaction_id, user_id)
            )
            return cursor.rowcount > 0

    except sqlite3.Error as e:
        print(f"ERROR: {e}")
        return False