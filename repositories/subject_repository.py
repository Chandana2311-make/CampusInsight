"""
Subject Repository
Handles persistence and queries for academic courses and grading limits.
"""
from typing import Any, Dict, List, Optional
from repositories.base_repository import BaseRepository


class SubjectRepository(BaseRepository):
    """Repository for academic subjects/courses."""

    def create_subject(
        self,
        code: str,
        name: str,
        semester: int,
        branch: str,
        max_internal: float = 40.0,
        max_external: float = 60.0,
        min_internal_pass: float = 16.0,
        min_external_pass: float = 21.0,
        min_total_pass: float = 40.0,
        credits: int = 4,
        conn=None
    ) -> int:
        query = """
            INSERT INTO subjects (
                code, name, semester, branch, max_internal, max_external,
                min_internal_pass, min_external_pass, min_total_pass, credits
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_non_query(
            query,
            (
                code.strip().upper(), name.strip(), semester, branch.strip(),
                max_internal, max_external, min_internal_pass, min_external_pass,
                min_total_pass, credits
            ),
            conn=conn
        )

    def get_by_id(self, subject_id: int, conn=None) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM subjects WHERE id = ?"
        return self.execute_query_one(query, (subject_id,), conn=conn)

    def get_by_code(self, code: str, conn=None) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM subjects WHERE code = ? COLLATE NOCASE"
        return self.execute_query_one(query, (code.strip().upper(),), conn=conn)

    def list_subjects(
        self,
        semester: Optional[int] = None,
        branch: Optional[str] = None,
        conn=None
    ) -> List[Dict[str, Any]]:
        query = "SELECT * FROM subjects WHERE 1=1"
        params = []
        if semester is not None:
            query += " AND semester = ?"
            params.append(semester)
        if branch is not None:
            query += " AND branch = ?"
            params.append(branch)
        query += " ORDER BY semester ASC, code ASC"
        return self.execute_query(query, params, conn=conn)

    def update_rules(
        self,
        subject_id: int,
        min_internal_pass: float,
        min_external_pass: float,
        min_total_pass: float,
        conn=None
    ) -> int:
        query = """
            UPDATE subjects
            SET min_internal_pass = ?, min_external_pass = ?, min_total_pass = ?
            WHERE id = ?
        """
        return self.execute_non_query(
            query,
            (min_internal_pass, min_external_pass, min_total_pass, subject_id),
            conn=conn
        )
