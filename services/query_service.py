"""
Query Service
Orchestrates the discrepancy query lifecycle: Submitted -> Under Review -> Resolved / Rejected.
Enforces role boundaries: student isolation and faculty course-assignment authorization.
"""
from typing import Any, Dict, List, Optional
from repositories.query_repository import QueryRepository
from repositories.student_repository import StudentRepository
from repositories.faculty_repository import FacultyRepository
from repositories.subject_repository import SubjectRepository
from repositories.audit_repository import AuditRepository


class QueryService:
    """Service managing student queries and faculty responses."""

    VALID_STATUS_TRANSITIONS = {
        "Submitted": ["Under Review", "Resolved", "Rejected"],
        "Under Review": ["Resolved", "Rejected", "Submitted"],
        "Resolved": ["Under Review"],  # Re-open if necessary
        "Rejected": ["Under Review"]   # Re-open if necessary
    }

    def __init__(
        self,
        query_repo: Optional[QueryRepository] = None,
        student_repo: Optional[StudentRepository] = None,
        faculty_repo: Optional[FacultyRepository] = None,
        subject_repo: Optional[SubjectRepository] = None,
        audit_repo: Optional[AuditRepository] = None
    ):
        self.query_repo = query_repo or QueryRepository()
        self.student_repo = student_repo or StudentRepository()
        self.faculty_repo = faculty_repo or FacultyRepository()
        self.subject_repo = subject_repo or SubjectRepository()
        self.audit_repo = audit_repo or AuditRepository()

    def submit_query(
        self,
        student_user_id: int,
        subject_id: int,
        category: str,
        description: str
    ) -> int:
        """
        Submits a new result discrepancy query from a student.
        """
        student = self.student_repo.get_by_user_id(student_user_id)
        if not student:
            raise PermissionError("Only enrolled students can raise discrepancy queries.")

        if not description or len(description.strip()) < 10:
            raise ValueError("Query description must be at least 10 characters long explaining the concern.")

        valid_categories = (
            "Internal Marks Discrepancy",
            "External Marks Re-evaluation",
            "Total/Grade Calculation Error",
            "Attendance/Assessment Record",
            "Other"
        )
        if category not in valid_categories:
            raise ValueError(f"Invalid category '{category}'. Must be one of: {', '.join(valid_categories)}")

        query_id = self.query_repo.create_query(
            student_id=student["id"],
            subject_id=subject_id,
            category=category,
            description=description.strip()
        )

        return query_id

    def get_student_queries(self, student_user_id: int) -> List[Dict[str, Any]]:
        """Returns queries filed strictly by the requesting student."""
        student = self.student_repo.get_by_user_id(student_user_id)
        if not student:
            return []
        return self.query_repo.get_student_queries(student["id"])

    def get_faculty_queries(
        self,
        faculty_user_id: int,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Returns queries for courses assigned to the faculty member."""
        return self.query_repo.get_faculty_queries(faculty_user_id, status=status)

    def update_query_status(
        self,
        faculty_user_id: int,
        query_id: int,
        new_status: str,
        faculty_response: Optional[str]
    ) -> bool:
        """
        Updates query status and response.
        Enforces that only faculty assigned to the subject can respond.
        """
        query = self.query_repo.get_by_id(query_id)
        if not query:
            raise ValueError(f"Query ID {query_id} does not exist.")

        # Authorization check
        if not self.faculty_repo.is_faculty_assigned(faculty_user_id, query["subject_id"]):
            raise PermissionError("Access denied: You are not authorized to review queries for this course.")

        current_status = query["status"]
        allowed = self.VALID_STATUS_TRANSITIONS.get(current_status, [])
        if new_status != current_status and new_status not in allowed:
            raise ValueError(f"Invalid transition from '{current_status}' to '{new_status}'. Allowed: {allowed}")

        if new_status in ("Resolved", "Rejected") and (not faculty_response or len(faculty_response.strip()) < 5):
            raise ValueError("A detailed faculty response is required when resolving or rejecting a query.")

        self.query_repo.update_status(
            query_id=query_id,
            status=new_status,
            faculty_response=faculty_response,
            faculty_user_id=faculty_user_id
        )

        # Audit event
        self.audit_repo.log_event(
            actor_user_id=faculty_user_id,
            action="UPDATE_QUERY_STATUS",
            entity_type="query",
            entity_id=query_id,
            old_value=f"Status: {current_status}",
            new_value=f"Status: {new_status} | Response: {faculty_response}",
            reason=f"Faculty resolution update"
        )

        return True
