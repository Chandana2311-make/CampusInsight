"""
Audit Repository
Provides persistent recording and querying of audit trail events.
"""
from typing import Any, Dict, List, Optional
from repositories.base_repository import BaseRepository


class AuditRepository(BaseRepository):
    """Repository for system audit trail."""

    def log_event(
        self,
        actor_user_id: int,
        action: str,
        entity_type: str,
        entity_id: int,
        old_value: Optional[str],
        new_value: Optional[str],
        reason: str,
        conn=None
    ) -> int:
        query = """
            INSERT INTO audit_events (
                actor_user_id, action, entity_type, entity_id,
                old_value, new_value, reason, timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
        """
        return self.execute_non_query(
            query,
            (
                actor_user_id, action.strip(), entity_type.strip(), entity_id,
                old_value, new_value, reason.strip()
            ),
            conn=conn
        )

    def list_events(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        actor_user_id: Optional[int] = None,
        limit: int = 200,
        conn=None
    ) -> List[Dict[str, Any]]:
        query = """
            SELECT a.*, u.username as actor_username, u.full_name as actor_name, u.role as actor_role
            FROM audit_events a
            JOIN users u ON a.actor_user_id = u.id
            WHERE 1=1
        """
        params = []
        if entity_type:
            query += " AND a.entity_type = ?"
            params.append(entity_type)
        if entity_id is not None:
            query += " AND a.entity_id = ?"
            params.append(entity_id)
        if actor_user_id is not None:
            query += " AND a.actor_user_id = ?"
            params.append(actor_user_id)
            
        query += " ORDER BY a.timestamp DESC, a.id DESC LIMIT ?"
        params.append(limit)
        return self.execute_query(query, params, conn=conn)
