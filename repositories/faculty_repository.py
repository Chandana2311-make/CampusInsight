"""
Faculty Repository
Handles faculty course assignments and verification of authorization over subjects/classes.
"""
from typing import Any, Dict, List, Optional
from repositories.base_repository import BaseRepository


class FacultyRepository(BaseRepository):
    """Repository for faculty assignments and course access."""

    def assign_faculty(
        self,
        faculty_user_id: int,
        subject_id: int,
        semester: int,
        section: str,
        conn=None
    ) -> int:
        query = """
            INSERT OR IGNORE INTO faculty_assignments (faculty_user_id, subject_id, semester, section)
            VALUES (?, ?, ?, ?)
        """
        return self.execute_non_query(
            query,
            (faculty_user_id, subject_id, semester, section.strip().upper()),
            conn=conn
        )

    def get_assigned_subjects(self, faculty_user_id: int, conn=None) -> List[Dict[str, Any]]:
        query = """
            SELECT fa.id as assignment_id, fa.semester, fa.section,
                   s.id as subject_id, s.code, s.name, s.branch, s.credits,
                   s.max_internal, s.max_external, s.min_internal_pass, s.min_external_pass, s.min_total_pass
            FROM faculty_assignments fa
            JOIN subjects s ON fa.subject_id = s.id
            WHERE fa.faculty_user_id = ?
            ORDER BY s.semester, s.code, fa.section
        """
        return self.execute_query(query, (faculty_user_id,), conn=conn)

    def is_faculty_assigned(
        self,
        faculty_user_id: int,
        subject_id: int,
        semester: Optional[int] = None,
        section: Optional[str] = None,
        conn=None
    ) -> bool:
        query = """
            SELECT 1 FROM faculty_assignments
            WHERE faculty_user_id = ? AND subject_id = ?
        """
        params = [faculty_user_id, subject_id]
        if semester is not None:
            query += " AND semester = ?"
            params.append(semester)
        if section is not None:
            query += " AND section = ?"
            params.append(section.strip().upper())
            
        res = self.execute_query_one(query, params, conn=conn)
        return res is not None

    def list_assignments(self, conn=None) -> List[Dict[str, Any]]:
        query = """
            SELECT fa.*, u.full_name as faculty_name, u.username as faculty_username,
                   s.code as subject_code, s.name as subject_name
            FROM faculty_assignments fa
            JOIN users u ON fa.faculty_user_id = u.id
            JOIN subjects s ON fa.subject_id = s.id
            ORDER BY s.code, fa.section
        """
        return self.execute_query(query, conn=conn)
