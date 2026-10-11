"""
Query Repository
Handles discrepancy queries raised by students and responses/resolutions from authorized faculty.
"""
from typing import Any, Dict, List, Optional
from repositories.base_repository import BaseRepository


class QueryRepository(BaseRepository):
    """Repository for student result discrepancy queries."""

    def create_query(
        self,
        student_id: int,
        subject_id: int,
        category: str,
        description: str,
        conn=None
    ) -> int:
        query = """
            INSERT INTO result_queries (student_id, subject_id, category, description, status)
            VALUES (?, ?, ?, ?, 'Submitted')
        """
        return self.execute_non_query(
            query,
            (student_id, subject_id, category, description.strip()),
            conn=conn
        )

    def get_by_id(self, query_id: int, conn=None) -> Optional[Dict[str, Any]]:
        query = """
            SELECT q.*, s.usn, u_st.full_name as student_name,
                   sub.code as subject_code, sub.name as subject_name,
                   u_fa.full_name as faculty_name
            FROM result_queries q
            JOIN students s ON q.student_id = s.id
            JOIN users u_st ON s.user_id = u_st.id
            JOIN subjects sub ON q.subject_id = sub.id
            LEFT JOIN users u_fa ON q.faculty_user_id = u_fa.id
            WHERE q.id = ?
        """
        return self.execute_query_one(query, (query_id,), conn=conn)

    def get_student_queries(self, student_id: int, conn=None) -> List[Dict[str, Any]]:
        query = """
            SELECT q.*, sub.code as subject_code, sub.name as subject_name,
                   u_fa.full_name as faculty_name
            FROM result_queries q
            JOIN subjects sub ON q.subject_id = sub.id
            LEFT JOIN users u_fa ON q.faculty_user_id = u_fa.id
            WHERE q.student_id = ?
            ORDER BY q.created_at DESC
        """
        return self.execute_query(query, (student_id,), conn=conn)

    def get_faculty_queries(
        self,
        faculty_user_id: int,
        status: Optional[str] = None,
        conn=None
    ) -> List[Dict[str, Any]]:
        """Returns queries for all subjects assigned to this faculty member."""
        query = """
            SELECT DISTINCT q.*, s.usn, s.section, u_st.full_name as student_name,
                   sub.code as subject_code, sub.name as subject_name,
                   u_fa.full_name as reviewer_name
            FROM result_queries q
            JOIN students s ON q.student_id = s.id
            JOIN users u_st ON s.user_id = u_st.id
            JOIN subjects sub ON q.subject_id = sub.id
            JOIN faculty_assignments fa ON fa.subject_id = sub.id AND fa.faculty_user_id = ?
            LEFT JOIN users u_fa ON q.faculty_user_id = u_fa.id
            WHERE 1=1
        """
        params = [faculty_user_id]
        if status:
            query += " AND q.status = ?"
            params.append(status)
            
        query += " ORDER BY q.created_at DESC"
        return self.execute_query(query, params, conn=conn)

    def update_status(
        self,
        query_id: int,
        status: str,
        faculty_response: Optional[str],
        faculty_user_id: int,
        conn=None
    ) -> int:
        query = """
            UPDATE result_queries
            SET status = ?, faculty_response = ?, faculty_user_id = ?, updated_at = datetime('now', 'localtime')
            WHERE id = ?
        """
        return self.execute_non_query(
            query,
            (status, faculty_response.strip() if faculty_response else None, faculty_user_id, query_id),
            conn=conn
        )
