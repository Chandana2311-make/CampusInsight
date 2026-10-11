"""
Result Repository
Handles database access for student marks, grades, publish status, and acknowledgements.
"""
from typing import Any, Dict, List, Optional
from repositories.base_repository import BaseRepository


class ResultRepository(BaseRepository):
    """Repository for student academic results and grades."""

    def upsert_result(
        self,
        student_id: int,
        subject_id: int,
        semester: int,
        internal_marks: Optional[float],
        external_marks: Optional[float],
        total_marks: Optional[float],
        grade: str,
        grade_points: int,
        is_passed: int,
        is_absent: int = 0,
        is_published: int = 0,
        conn=None
    ) -> int:
        query = """
            INSERT INTO results (
                student_id, subject_id, semester, internal_marks, external_marks,
                total_marks, grade, grade_points, is_passed, is_absent, is_published,
                published_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CASE WHEN ? = 1 THEN datetime('now', 'localtime') ELSE NULL END, datetime('now', 'localtime'))
            ON CONFLICT(student_id, subject_id, semester) DO UPDATE SET
                internal_marks = excluded.internal_marks,
                external_marks = excluded.external_marks,
                total_marks = excluded.total_marks,
                grade = excluded.grade,
                grade_points = excluded.grade_points,
                is_passed = excluded.is_passed,
                is_absent = excluded.is_absent,
                is_published = excluded.is_published,
                published_at = CASE WHEN excluded.is_published = 1 AND results.published_at IS NULL THEN datetime('now', 'localtime') ELSE results.published_at END,
                updated_at = datetime('now', 'localtime')
        """
        return self.execute_non_query(
            query,
            (
                student_id, subject_id, semester, internal_marks, external_marks,
                total_marks, grade, grade_points, is_passed, is_absent, is_published,
                is_published
            ),
            conn=conn
        )

    def get_by_id(self, result_id: int, conn=None) -> Optional[Dict[str, Any]]:
        query = """
            SELECT r.*, s.usn, u.full_name as student_name, sub.code as subject_code,
                   sub.name as subject_name, sub.credits, sub.max_internal, sub.max_external,
                   sub.min_internal_pass, sub.min_external_pass, sub.min_total_pass
            FROM results r
            JOIN students s ON r.student_id = s.id
            JOIN users u ON s.user_id = u.id
            JOIN subjects sub ON r.subject_id = sub.id
            WHERE r.id = ?
        """
        return self.execute_query_one(query, (result_id,), conn=conn)

    def get_student_results(
        self,
        student_id: int,
        semester: Optional[int] = None,
        only_published: bool = True,
        conn=None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves results for a specific student.
        Students can NEVER view unpublished results when only_published is True.
        """
        query = """
            SELECT r.*, sub.code as subject_code, sub.name as subject_name, sub.credits,
                   sub.max_internal, sub.max_external, sub.min_internal_pass, sub.min_external_pass, sub.min_total_pass,
                   ack.id as ack_id, ack.acknowledged_at
            FROM results r
            JOIN subjects sub ON r.subject_id = sub.id
            LEFT JOIN acknowledgements ack ON r.id = ack.result_id AND ack.student_id = r.student_id
            WHERE r.student_id = ?
        """
        params = [student_id]
        if only_published:
            query += " AND r.is_published = 1"
        if semester is not None:
            query += " AND r.semester = ?"
            params.append(semester)
            
        query += " ORDER BY r.semester ASC, sub.code ASC"
        return self.execute_query(query, params, conn=conn)

    def get_subject_results(
        self,
        subject_id: int,
        semester: Optional[int] = None,
        section: Optional[str] = None,
        conn=None
    ) -> List[Dict[str, Any]]:
        """Retrieves results for a specific subject (used by faculty)."""
        query = """
            SELECT r.*, s.usn, s.section, s.branch, u.full_name as student_name,
                   sub.code as subject_code, sub.name as subject_name, sub.credits,
                   sub.max_internal, sub.max_external, sub.min_internal_pass, sub.min_external_pass, sub.min_total_pass,
                   ack.acknowledged_at
            FROM results r
            JOIN students s ON r.student_id = s.id
            JOIN users u ON s.user_id = u.id
            JOIN subjects sub ON r.subject_id = sub.id
            LEFT JOIN acknowledgements ack ON r.id = ack.result_id
            WHERE r.subject_id = ?
        """
        params = [subject_id]
        if semester is not None:
            query += " AND r.semester = ?"
            params.append(semester)
        if section is not None:
            query += " AND s.section = ?"
            params.append(section.strip().upper())
            
        query += " ORDER BY s.usn ASC"
        return self.execute_query(query, params, conn=conn)

    def update_result_marks(
        self,
        result_id: int,
        internal_marks: Optional[float],
        external_marks: Optional[float],
        total_marks: Optional[float],
        grade: str,
        grade_points: int,
        is_passed: int,
        is_absent: int = 0,
        conn=None
    ) -> int:
        query = """
            UPDATE results
            SET internal_marks = ?, external_marks = ?, total_marks = ?,
                grade = ?, grade_points = ?, is_passed = ?, is_absent = ?,
                updated_at = datetime('now', 'localtime')
            WHERE id = ?
        """
        return self.execute_non_query(
            query,
            (internal_marks, external_marks, total_marks, grade, grade_points, is_passed, is_absent, result_id),
            conn=conn
        )

    def set_publish_status_by_subject(
        self,
        subject_id: int,
        semester: int,
        publish: bool,
        conn=None
    ) -> int:
        """Publishes or unpublishes results for a given subject and semester."""
        query = """
            UPDATE results
            SET is_published = ?,
                published_at = CASE WHEN ? = 1 THEN datetime('now', 'localtime') ELSE NULL END,
                updated_at = datetime('now', 'localtime')
            WHERE subject_id = ? AND semester = ?
        """
        is_pub = 1 if publish else 0
        return self.execute_non_query(query, (is_pub, is_pub, subject_id, semester), conn=conn)

    def acknowledge_result(
        self,
        result_id: int,
        student_id: int,
        comments: Optional[str] = None,
        conn=None
    ) -> int:
        query = """
            INSERT OR REPLACE INTO acknowledgements (result_id, student_id, comments, acknowledged_at)
            VALUES (?, ?, ?, datetime('now', 'localtime'))
        """
        return self.execute_non_query(query, (result_id, student_id, comments), conn=conn)

    def is_result_acknowledged(self, result_id: int, student_id: int, conn=None) -> bool:
        query = "SELECT 1 FROM acknowledgements WHERE result_id = ? AND student_id = ?"
        res = self.execute_query_one(query, (result_id, student_id), conn=conn)
        return res is not None
