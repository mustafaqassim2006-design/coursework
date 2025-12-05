# services/users_service.py

from typing import Optional, Dict, Any

from DB.db import DatabaseManager
from DB.crud import insert_user, get_user_by_username


class UserService:
    """
    Encapsulates all user-related operations.
    The Streamlit UI calls this, instead of working with the DB directly.
    """

    def __init__(self, db_manager_cls=DatabaseManager):
        self._db_manager_cls = db_manager_cls

    def _get_db(self):
        # Tiny helper so we can override db manager in tests if needed
        return self._db_manager_cls()

    def find_user(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Returns a dict representing the user row or None if not found.
        """
        with self._get_db() as db:
            row = get_user_by_username(db, username)

        if row is None:
            return None

        # sqlite3.Row is mapping-like; tuples used as fallback
        if hasattr(row, "keys"):
            return dict(row)

        # tuple fallback: assuming (id, username, password_hash, role)
        return {
            "id": row[0],
            "username": row[1],
            "password_hash": row[2],
            "role": row[3],
        }

    def register_user(self, username: str, password_hash: str, role: str = "general") -> None:
        """
        Simple wrapper around insert_user. You can extend with validation later.
        """
        with self._get_db() as db:
            insert_user(db, username, password_hash, role)
