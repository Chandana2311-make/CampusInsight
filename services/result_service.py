"""
Result Service
Handles result upload, validation, publishing, mark modifications with mandatory audit trails,
and strictly enforces role-based student and faculty data isolation.
"""
import io
import csv
from typing import Any, Dict, List, Optional, Tuple, Union
from repositories.result_repository import ResultRepository
from repositories.subject_repository import SubjectRepository
from repositories.student_repository import StudentRepository
from repositories.faculty_repository import FacultyRepository
from repositories.audit_repository import AuditRepository
from services.grading_service import GradingService


class ResultService:
    """Service orchestrating mark calculations, validation, publishing, and audit logging."""

    def __init__(
        self,
        result_repo: Optional[ResultRepository] = None,
        subject_repo: Optional[SubjectRepository] = None,
        student_repo: Optional[StudentRepository] = None,
        faculty_repo: Optional[FacultyRepository] = None,
        audit_repo: Optional[AuditRepository] = None,
        grading_service: Optional[GradingService] = None
    ):
        self.result_repo = result_repo or ResultRepository()
        self.subject_repo = subject_repo or SubjectRepository()
        self.student_repo = student_repo or StudentRepository()
        self.faculty_repo = faculty_repo or FacultyRepository()
        self.audit_repo = audit_repo or AuditRepository()
        self.grading_service = grading_service or GradingService()

    def get_student_results(
        self,
        student_user_id: int,
        semester: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves results exclusively for the authenticated student.
        Strictly enforces that ONLY published results are visible.
        """
        student = self.student_repo.get_by_user_id(student_user_id)
        if not student:
            return []
        
        # Security: only_published is hardcoded to True for student queries
        return self.result_repo.get_student_results(
            student_id=student["id"],
            semester=semester,
            only_published=True
        )

    def get_faculty_subject_results(
        self,
        faculty_user_id: int,
        subject_id: int,
        semester: Optional[int] = None,
        section: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves subject results for faculty.
        Enforces authorization: faculty must be assigned to this subject.
        """
        if not self.faculty_repo.is_faculty_assigned(faculty_user_id, subject_id, semester=semester, section=section):
            raise PermissionError("Access denied: You are not authorized to view results for this subject/section.")
            
        return self.result_repo.get_subject_results(
            subject_id=subject_id,
            semester=semester,
            section=section
        )

    def validate_csv_content(
        self,
        csv_text_or_bytes: Union[str, bytes],
        subject_id: int,
        semester: int
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Validates CSV rows for mark import.
        Expected headers: USN, Internal, External, Is_Absent (optional)
        Returns: (valid_rows, error_rows)
        """
        subject = self.subject_repo.get_by_id(subject_id)
        if not subject:
            raise ValueError(f"Subject ID {subject_id} does not exist.")

        if isinstance(csv_text_or_bytes, bytes):
            content = csv_text_or_bytes.decode("utf-8-sig", errors="replace")
        else:
            content = csv_text_or_bytes

        reader = csv.DictReader(io.StringIO(content))
        if not reader.fieldnames:
            return [], [{"row_number": 1, "usn": "", "error": "CSV file is empty or missing headers."}]

        # Normalize headers flexibly: strip spaces, underscores, hyphens and lower-case
        norm_map = {}
        for col in reader.fieldnames:
            clean_key = col.strip().lower().replace("_", "").replace("-", "").replace(" ", "")
            norm_map[clean_key] = col

        # Aliases for USN / Roll number
        usn_aliases = [
            "usn", "studentusn", "regno", "registrationno", "registrationnumber",
            "rollno", "rollnumber", "studentid", "studentregno", "candidateno"
        ]
        usn_col = next((norm_map[a] for a in usn_aliases if a in norm_map), None)

        # Aliases for Internal / CIE marks
        int_aliases = [
            "internal", "internalmarks", "cie", "theorycie", "iamarks", "ciemarks",
            "internalmark", "continuousassessment", "internals"
        ]
        int_col = next((norm_map[a] for a in int_aliases if a in norm_map), None)

        # Aliases for External / SEE marks
        ext_aliases = [
            "external", "externalmarks", "see", "theorysee", "universitymarks",
            "seemarks", "semesterendexam", "externalmark", "externals"
        ]
        ext_col = next((norm_map[a] for a in ext_aliases if a in norm_map), None)

        # Aliases for Absent flag
        absent_aliases = ["isabsent", "absent", "attendance", "status", "ab", "abstatus"]
        absent_col = next((norm_map[a] for a in absent_aliases if a in norm_map), None)

        if not usn_col or not int_col or not ext_col:
            return [], [{
                "row_number": 1,
                "usn": "",
                "error": f"Missing required headers in college CSV. Expected columns for Student ID (USN/RollNo), Internal (CIE), and External (SEE). Found: {list(reader.fieldnames)}"
            }]

        valid_rows: List[Dict[str, Any]] = []
        error_rows: List[Dict[str, Any]] = []
        seen_usns = set()

        for idx, row in enumerate(reader, start=2):
            raw_usn = row.get(usn_col, "").strip().upper()
            raw_int = row.get(int_col, "").strip()
            raw_ext = row.get(ext_col, "").strip()
            raw_absent = row.get(absent_col, "0").strip().lower() if absent_col else "0"

            if not raw_usn:
                error_rows.append({"row_number": idx, "usn": "", "error": "USN/Roll No cannot be empty."})
                continue

            if raw_usn in seen_usns:
                error_rows.append({"row_number": idx, "usn": raw_usn, "error": f"Duplicate record for '{raw_usn}' in upload."})
                continue
            seen_usns.add(raw_usn)

            student = self.student_repo.get_by_usn(raw_usn)
            if not student:
                error_rows.append({
                    "row_number": idx,
                    "usn": raw_usn,
                    "error": f"Student with USN '{raw_usn}' is not registered in the institutional database."
                })
                continue

            is_absent = 1 if raw_absent in ("1", "true", "yes", "ab", "absent") else 0

            # If absent, marks can be 0 or empty
            int_marks: Optional[float] = None
            ext_marks: Optional[float] = None

            if is_absent:
                int_marks = 0.0
                ext_marks = 0.0
            else:
                try:
                    int_marks = float(raw_int)
                except ValueError:
                    error_rows.append({"row_number": idx, "usn": raw_usn, "error": f"Invalid internal mark '{raw_int}': must be numeric."})
                    continue

                try:
                    ext_marks = float(raw_ext)
                except ValueError:
                    error_rows.append({"row_number": idx, "usn": raw_usn, "error": f"Invalid external mark '{raw_ext}': must be numeric."})
                    continue

                if int_marks < 0 or int_marks > subject["max_internal"]:
                    error_rows.append({
                        "row_number": idx,
                        "usn": raw_usn,
                        "error": f"Internal mark {int_marks} exceeds range [0, {subject['max_internal']}]."
                    })
                    continue

                if ext_marks < 0 or ext_marks > subject["max_external"]:
                    error_rows.append({
                        "row_number": idx,
                        "usn": raw_usn,
                        "error": f"External mark {ext_marks} exceeds range [0, {subject['max_external']}]."
                    })
                    continue

            # Evaluate derived values
            eval_result = self.grading_service.evaluate_result(
                internal_marks=int_marks,
                external_marks=ext_marks,
                max_internal=subject["max_internal"],
                max_external=subject["max_external"],
                min_internal_pass=subject["min_internal_pass"],
                min_external_pass=subject["min_external_pass"],
                min_total_pass=subject["min_total_pass"],
                is_absent=bool(is_absent)
            )

            valid_rows.append({
                "student_id": student["id"],
                "usn": raw_usn,
                "student_name": student["full_name"],
                "subject_id": subject_id,
                "semester": semester,
                "internal_marks": int_marks,
                "external_marks": ext_marks,
                "total_marks": eval_result["total_marks"],
                "grade": eval_result["grade"],
                "grade_points": eval_result["grade_points"],
                "is_passed": eval_result["is_passed"],
                "is_absent": is_absent
            })

        return valid_rows, error_rows

    def import_marks(
        self,
        faculty_user_id: int,
        subject_id: int,
        semester: int,
        valid_rows: List[Dict[str, Any]]
    ) -> int:
        """
        Imports validated rows into the database.
        IMPORTANT: Imported results are NOT published automatically.
        Enforces faculty authorization.
        """
        if not self.faculty_repo.is_faculty_assigned(faculty_user_id, subject_id, semester=semester):
            raise PermissionError("Access denied: You are not authorized to import marks for this course.")

        imported_count = 0
        for row in valid_rows:
            self.result_repo.upsert_result(
                student_id=row["student_id"],
                subject_id=subject_id,
                semester=semester,
                internal_marks=row["internal_marks"],
                external_marks=row["external_marks"],
                total_marks=row["total_marks"],
                grade=row["grade"],
                grade_points=row["grade_points"],
                is_passed=row["is_passed"],
                is_absent=row.get("is_absent", 0),
                is_published=0  # Deliberately saved as UNPUBLISHED
            )
            imported_count += 1

        # Audit trail
        self.audit_repo.log_event(
            actor_user_id=faculty_user_id,
            action="IMPORT_MARKS_CSV",
            entity_type="subject",
            entity_id=subject_id,
            old_value=None,
            new_value=f"Imported {imported_count} student marks (unpublished)",
            reason=f"Faculty CSV upload for semester {semester}"
        )

        return imported_count

    def update_result_mark(
        self,
        faculty_user_id: int,
        result_id: int,
        internal_marks: Optional[float],
        external_marks: Optional[float],
        reason: str,
        is_absent: bool = False
    ) -> Dict[str, Any]:
        """
        Updates a student's marks with mandatory reason and full audit logging.
        Enforces faculty assignment authorization.
        """
        if not reason or len(reason.strip()) < 5:
            raise ValueError("A clear, valid justification reason (at least 5 characters) is required for mark modifications.")

        current = self.result_repo.get_by_id(result_id)
        if not current:
            raise ValueError(f"Result ID {result_id} not found.")

        # Check authorization
        if not self.faculty_repo.is_faculty_assigned(faculty_user_id, current["subject_id"]):
            raise PermissionError("Access denied: You are not authorized to modify results for this subject.")

        old_snapshot = f"Internal={current['internal_marks']}, External={current['external_marks']}, Total={current['total_marks']}, Grade={current['grade']}"

        # Evaluate new grade
        eval_res = self.grading_service.evaluate_result(
            internal_marks=internal_marks,
            external_marks=external_marks,
            max_internal=current["max_internal"],
            max_external=current["max_external"],
            min_internal_pass=current["min_internal_pass"],
            min_external_pass=current["min_external_pass"],
            min_total_pass=current["min_total_pass"],
            is_absent=is_absent
        )

        self.result_repo.update_result_marks(
            result_id=result_id,
            internal_marks=internal_marks,
            external_marks=external_marks,
            total_marks=eval_res["total_marks"],
            grade=eval_res["grade"],
            grade_points=eval_res["grade_points"],
            is_passed=eval_res["is_passed"],
            is_absent=1 if is_absent else 0
        )

        new_snapshot = f"Internal={internal_marks}, External={external_marks}, Total={eval_res['total_marks']}, Grade={eval_res['grade']}"

        # Audit Event Logging
        self.audit_repo.log_event(
            actor_user_id=faculty_user_id,
            action="UPDATE_STUDENT_MARKS",
            entity_type="result",
            entity_id=result_id,
            old_value=old_snapshot,
            new_value=new_snapshot,
            reason=reason.strip()
        )

        return eval_res

    def set_publish_status(
        self,
        faculty_user_id: int,
        subject_id: int,
        semester: int,
        publish: bool,
        reason: str
    ) -> int:
        """
        Explicitly publishes or unpublishes marks for a subject and semester.
        Enforces faculty authorization and records an audit event.
        """
        if not self.faculty_repo.is_faculty_assigned(faculty_user_id, subject_id, semester=semester):
            raise PermissionError("Access denied: You are not authorized to publish results for this subject.")

        if not reason or len(reason.strip()) < 3:
            raise ValueError("A reason is required when changing result publication status.")

        count = self.result_repo.set_publish_status_by_subject(subject_id, semester, publish)

        action_name = "PUBLISH_RESULTS" if publish else "UNPUBLISH_RESULTS"
        self.audit_repo.log_event(
            actor_user_id=faculty_user_id,
            action=action_name,
            entity_type="subject",
            entity_id=subject_id,
            old_value="Unpublished" if publish else "Published",
            new_value="Published" if publish else "Unpublished",
            reason=reason.strip()
        )
        return count

    def acknowledge_result(
        self,
        student_user_id: int,
        result_id: int,
        comments: Optional[str] = None
    ) -> bool:
        """
        Records student acknowledgement that they have viewed the result.
        Enforces that students can acknowledge only their own results.
        Acknowledgement does not waive their right to raise queries.
        """
        student = self.student_repo.get_by_user_id(student_user_id)
        if not student:
            raise PermissionError("Student profile not found.")

        result = self.result_repo.get_by_id(result_id)
        if not result:
            raise ValueError("Result record not found.")

        if result["student_id"] != student["id"]:
            raise PermissionError("Access denied: You cannot acknowledge another student's result.")

        self.result_repo.acknowledge_result(
            result_id=result_id,
            student_id=student["id"],
            comments=comments
        )
        return True
