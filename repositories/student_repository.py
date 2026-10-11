"""
Student Repository
Handles access and persistence for student profiles and academic details.
"""
from typing import Any, Dict, List, Optional
from repositories.base_repository import BaseRepository


class StudentRepository(BaseRepository):
    """Repository for students."""

    def create_student(
        self,
        user_id: int,
        usn: str,
        branch: str,
        semester: int,
        section: str,
        batch_year: int = 2022,
        conn=None
    ) -> int:
        query = """
            INSERT INTO students (user_id, usn, branch, semester, section, batch_year)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        return self.execute_non_query(
            query,
            (user_id, usn.strip().upper(), branch.strip(), semester, section.strip().upper(), batch_year),
            conn=conn
        )

    def get_by_user_id(self, user_id: int, conn=None) -> Optional[Dict[str, Any]]:
        query = """
            SELECT s.*, u.username, u.full_name, u.email
            FROM students s
            JOIN users u ON s.user_id = u.id
            WHERE s.user_id = ?
        """
        return self.execute_query_one(query, (user_id,), conn=conn)

    def get_by_id(self, student_id: int, conn=None) -> Optional[Dict[str, Any]]:
        query = """
            SELECT s.*, u.username, u.full_name, u.email
            FROM students s
            JOIN users u ON s.user_id = u.id
            WHERE s.id = ?
        """
        return self.execute_query_one(query, (student_id,), conn=conn)

    def get_by_usn(self, usn: str, conn=None) -> Optional[Dict[str, Any]]:
        query = """
            SELECT s.*, u.username, u.full_name, u.email
            FROM students s
            JOIN users u ON s.user_id = u.id
            WHERE s.usn = ? COLLATE NOCASE
        """
        return self.execute_query_one(query, (usn.strip().upper(),), conn=conn)

    def list_students(
        self,
        semester: Optional[int] = None,
        branch: Optional[str] = None,
        section: Optional[str] = None,
        conn=None
    ) -> List[Dict[str, Any]]:
        query = """
            SELECT s.*, u.username, u.full_name, u.email
            FROM students s
            JOIN users u ON s.user_id = u.id
            WHERE 1=1
        """
        params = []
        if semester is not None:
            query += " AND s.semester = ?"
            params.append(semester)
        if branch is not None:
            query += " AND s.branch = ?"
            params.append(branch)
        if section is not None:
            query += " AND s.section = ?"
            params.append(section)
            
        query += " ORDER BY s.usn ASC"
        return self.execute_query(query, params, conn=conn)
