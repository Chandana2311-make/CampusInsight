"""
User Repository
Handles data access for user accounts, credentials, and roles.
"""
from typing import Any, Dict, List, Optional
from repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    """Repository for user accounts."""

    def create_user(
        self,
        username: str,
        password_hash: str,
        salt: str,
        role: str,
        full_name: str,
        email: str,
        conn=None
    ) -> int:
        query = """
            INSERT INTO users (username, password_hash, salt, role, full_name, email)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        return self.execute_non_query(
            query,
            (username.strip(), password_hash, salt, role, full_name.strip(), email.strip()),
            conn=conn
        )

    def get_by_username(self, username: str, conn=None) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM users WHERE username = ? COLLATE NOCASE"
        return self.execute_query_one(query, (username.strip(),), conn=conn)

    def get_by_id(self, user_id: int, conn=None) -> Optional[Dict[str, Any]]:
        query = "SELECT id, username, role, full_name, email, created_at FROM users WHERE id = ?"
        return self.execute_query_one(query, (user_id,), conn=conn)

    def list_users(self, role: Optional[str] = None, conn=None) -> List[Dict[str, Any]]:
        if role:
            query = "SELECT id, username, role, full_name, email, created_at FROM users WHERE role = ? ORDER BY full_name"
            return self.execute_query(query, (role,), conn=conn)
        query = "SELECT id, username, role, full_name, email, created_at FROM users ORDER BY full_name"
        return self.execute_query(query, conn=conn)
