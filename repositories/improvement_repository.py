"""
Improvement Repository
Handles persistence for structured improvement plans, weekly schedules, practice logs, and faculty feedback.
"""
from typing import Any, Dict, List, Optional
from repositories.base_repository import BaseRepository


class ImprovementRepository(BaseRepository):
    """Repository for student academic improvement plans and practice logs."""

    def create_plan(
        self,
        student_id: int,
        title: str,
        target_sgpa: Optional[float],
        recommendations_json: str,
        weekly_schedule_json: str,
        conn=None
    ) -> int:
        query = """
            INSERT INTO improvement_plans (
                student_id, title, target_sgpa, recommendations_json,
                weekly_schedule_json, status
            )
            VALUES (?, ?, ?, ?, ?, 'Active')
        """
        return self.execute_non_query(
            query,
            (student_id, title, target_sgpa, recommendations_json, weekly_schedule_json),
            conn=conn
        )

    def get_by_id(self, plan_id: int, conn=None) -> Optional[Dict[str, Any]]:
        query = """
            SELECT ip.*, s.usn, s.branch, s.semester, s.section,
                   u_st.full_name as student_name,
                   u_fa.full_name as faculty_reviewer_name
            FROM improvement_plans ip
            JOIN students s ON ip.student_id = s.id
            JOIN users u_st ON s.user_id = u_st.id
            LEFT JOIN users u_fa ON ip.reviewed_by_faculty_id = u_fa.id
            WHERE ip.id = ?
        """
        return self.execute_query_one(query, (plan_id,), conn=conn)

    def get_student_plans(self, student_id: int, conn=None) -> List[Dict[str, Any]]:
        query = """
            SELECT ip.*, u_fa.full_name as faculty_reviewer_name
            FROM improvement_plans ip
            LEFT JOIN users u_fa ON ip.reviewed_by_faculty_id = u_fa.id
            WHERE ip.student_id = ?
            ORDER BY ip.created_at DESC
        """
        return self.execute_query(query, (student_id,), conn=conn)

    def update_status(self, plan_id: int, status: str, conn=None) -> int:
        query = """
            UPDATE improvement_plans
            SET status = ?, updated_at = datetime('now', 'localtime')
            WHERE id = ?
        """
        return self.execute_non_query(query, (status, plan_id), conn=conn)

    def add_faculty_feedback(
        self,
        plan_id: int,
        faculty_user_id: int,
        feedback: str,
        status: str = "Faculty Reviewed",
        conn=None
    ) -> int:
        query = """
            UPDATE improvement_plans
            SET faculty_feedback = ?, reviewed_by_faculty_id = ?, status = ?,
                updated_at = datetime('now', 'localtime')
            WHERE id = ?
        """
        return self.execute_non_query(query, (feedback.strip(), faculty_user_id, status, plan_id), conn=conn)

    def add_practice_log(
        self,
        plan_id: int,
        student_id: int,
        subject_id: int,
        date_completed: str,
        practice_activity: str,
        duration_minutes: int,
        self_assessment_score: Optional[float] = None,
        notes: Optional[str] = None,
        conn=None
    ) -> int:
        query = """
            INSERT INTO practice_logs (
                plan_id, student_id, subject_id, date_completed,
                practice_activity, duration_minutes, self_assessment_score, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_non_query(
            query,
            (
                plan_id, student_id, subject_id, date_completed,
                practice_activity.strip(), duration_minutes,
                self_assessment_score, notes.strip() if notes else None
            ),
            conn=conn
        )

    def get_practice_logs(
        self,
        student_id: int,
        plan_id: Optional[int] = None,
        conn=None
    ) -> List[Dict[str, Any]]:
        query = """
            SELECT pl.*, sub.code as subject_code, sub.name as subject_name
            FROM practice_logs pl
            JOIN subjects sub ON pl.subject_id = sub.id
            WHERE pl.student_id = ?
        """
        params = [student_id]
        if plan_id is not None:
            query += " AND pl.plan_id = ?"
            params.append(plan_id)
        query += " ORDER BY pl.date_completed DESC, pl.id DESC"
        return self.execute_query(query, params, conn=conn)

    def list_all_plans_for_review(self, conn=None) -> List[Dict[str, Any]]:
        query = """
            SELECT ip.*, s.usn, s.section, s.semester, s.branch,
                   u_st.full_name as student_name,
                   u_fa.full_name as reviewer_name
            FROM improvement_plans ip
            JOIN students s ON ip.student_id = s.id
            JOIN users u_st ON s.user_id = u_st.id
            LEFT JOIN users u_fa ON ip.reviewed_by_faculty_id = u_fa.id
            ORDER BY ip.updated_at DESC
        """
        return self.execute_query(query, conn=conn)
