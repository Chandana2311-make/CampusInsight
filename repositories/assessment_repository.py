"""
Assessment Repository
Stores topic-level and quiz assessments used as grounded evidence for the improvement engine.
"""
from typing import Any, Dict, List, Optional
from repositories.base_repository import BaseRepository


class AssessmentRepository(BaseRepository):
    """Repository for topic and quiz scores."""

    def add_score(
        self,
        student_id: int,
        subject_id: int,
        topic_name: str,
        score: float,
        max_score: float,
        assessment_type: str,
        conn=None
    ) -> int:
        query = """
            INSERT INTO topic_scores (student_id, subject_id, topic_name, score, max_score, assessment_type)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        return self.execute_non_query(
            query,
            (student_id, subject_id, topic_name.strip(), score, max_score, assessment_type.strip()),
            conn=conn
        )

    def get_by_student(
        self,
        student_id: int,
        subject_id: Optional[int] = None,
        conn=None
    ) -> List[Dict[str, Any]]:
        query = """
            SELECT ts.*, sub.code as subject_code, sub.name as subject_name
            FROM topic_scores ts
            JOIN subjects sub ON ts.subject_id = sub.id
            WHERE ts.student_id = ?
        """
        params = [student_id]
        if subject_id is not None:
            query += " AND ts.subject_id = ?"
            params.append(subject_id)
        query += " ORDER BY ts.recorded_date DESC, ts.topic_name ASC"
        return self.execute_query(query, params, conn=conn)

    def get_by_subject(self, subject_id: int, conn=None) -> List[Dict[str, Any]]:
        query = """
            SELECT ts.*, s.usn, u.full_name as student_name
            FROM topic_scores ts
            JOIN students s ON ts.student_id = s.id
            JOIN users u ON s.user_id = u.id
            WHERE ts.subject_id = ?
            ORDER BY ts.topic_name ASC
        """
        return self.execute_query(query, (subject_id,), conn=conn)
