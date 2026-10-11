"""
Grading Service
Encapsulates configurable academic evaluation rules, grade calculations, SGPA, and CGPA metrics.
"""
from typing import Dict, List, Optional, Tuple, Any
from config import DEFAULT_GRADE_SCALE, DEFAULT_PASSING_RULES


class GradingService:
    """Service for computing subject grades, pass/fail status, and grade point averages."""

    def __init__(
        self,
        grade_scale: Optional[List[Tuple[str, float, int, str]]] = None,
        passing_rules: Optional[Dict[str, float]] = None
    ):
        self.grade_scale = grade_scale or DEFAULT_GRADE_SCALE
        self.passing_rules = passing_rules or DEFAULT_PASSING_RULES

    def evaluate_result(
        self,
        internal_marks: Optional[float],
        external_marks: Optional[float],
        max_internal: float = 40.0,
        max_external: float = 60.0,
        min_internal_pass: Optional[float] = None,
        min_external_pass: Optional[float] = None,
        min_total_pass: Optional[float] = None,
        is_absent: bool = False
    ) -> Dict[str, Any]:
        """
        Evaluates a student's marks and produces derived total, grade, grade points, and pass status.
        
        Args:
            internal_marks: Continuous assessment score (0 to max_internal)
            external_marks: Semester end exam score (0 to max_external)
            max_internal: Maximum internal marks for the course
            max_external: Maximum external marks for the course
            min_internal_pass: Subject-specific internal passing cutoff
            min_external_pass: Subject-specific external passing cutoff
            min_total_pass: Subject-specific total passing cutoff
            is_absent: Whether the student was absent for the exam
        """
        # Case 1: Student marked absent
        if is_absent:
            return {
                "total_marks": 0.0,
                "percentage": 0.0,
                "grade": "F",
                "grade_points": 0,
                "is_passed": 0,
                "is_absent": 1,
                "status_label": "Absent",
                "remarks": "Candidate was marked absent for the examination."
            }

        # Case 2: Incomplete or pending marks
        if internal_marks is None or external_marks is None:
            return {
                "total_marks": None,
                "percentage": None,
                "grade": "PENDING",
                "grade_points": 0,
                "is_passed": 0,
                "is_absent": 0,
                "status_label": "Pending",
                "remarks": "Evaluation in progress."
            }

        # Validate mark ranges
        if internal_marks < 0 or internal_marks > max_internal:
            raise ValueError(f"Internal marks {internal_marks} out of permitted range [0, {max_internal}]")
        if external_marks < 0 or external_marks > max_external:
            raise ValueError(f"External marks {external_marks} out of permitted range [0, {max_external}]")

        total_marks = round(internal_marks + external_marks, 2)
        max_total = max_internal + max_external
        percentage = round((total_marks / max_total) * 100.0, 2) if max_total > 0 else 0.0

        # Determine cutoff values (use subject specific if provided, else fallback to configurable rules)
        int_cutoff = min_internal_pass if min_internal_pass is not None else (self.passing_rules["min_internal_percentage"] * max_internal / 100.0)
        ext_cutoff = min_external_pass if min_external_pass is not None else (self.passing_rules["min_external_percentage"] * max_external / 100.0)
        tot_cutoff = min_total_pass if min_total_pass is not None else (self.passing_rules["min_total_percentage"] * max_total / 100.0)

        # Check all pass criteria
        passed_internal = internal_marks >= int_cutoff
        passed_external = external_marks >= ext_cutoff
        passed_total = total_marks >= tot_cutoff

        is_passed = 1 if (passed_internal and passed_external and passed_total) else 0

        # Assign letter grade and grade points
        if not is_passed:
            grade = "F"
            grade_points = 0
            fail_reasons = []
            if not passed_internal:
                fail_reasons.append(f"Internal marks ({internal_marks}) below minimum required ({int_cutoff})")
            if not passed_external:
                fail_reasons.append(f"External marks ({external_marks}) below minimum required ({ext_cutoff})")
            if not passed_total:
                fail_reasons.append(f"Total marks ({total_marks}) below minimum required ({tot_cutoff})")
            remarks = "Not Cleared: " + "; ".join(fail_reasons)
        else:
            grade = "P"
            grade_points = 4
            remarks = "Passed"
            for g_code, min_pct, points, desc in self.grade_scale:
                if percentage >= min_pct and g_code != "F":
                    grade = g_code
                    grade_points = points
                    remarks = desc
                    break

        return {
            "total_marks": total_marks,
            "percentage": percentage,
            "grade": grade,
            "grade_points": grade_points,
            "is_passed": is_passed,
            "is_absent": 0,
            "status_label": "Pass" if is_passed else "Fail",
            "remarks": remarks
        }

    @staticmethod
    def calculate_sgpa(results: List[Dict[str, Any]]) -> Optional[float]:
        """
        Calculates Semester Grade Point Average (SGPA).
        SGPA = Sum(Grade Points * Credits) / Sum(Credits)
        Returns None if no evaluated credits exist.
        """
        total_credit_points = 0.0
        total_credits = 0.0

        for r in results:
            if r.get("grade") == "PENDING" or r.get("grade") is None:
                continue
            credits = r.get("credits", 0)
            grade_points = r.get("grade_points", 0)
            if credits > 0:
                total_credit_points += (grade_points * credits)
                total_credits += credits

        if total_credits == 0:
            return None

        return round(total_credit_points / total_credits, 2)

    @staticmethod
    def calculate_cgpa(semester_sgpas: Dict[int, Tuple[float, int]]) -> Optional[float]:
        """
        Calculates Cumulative Grade Point Average (CGPA) across semesters.
        Input: dict of {semester: (sgpa, total_credits)}
        """
        total_weighted_sgpa = 0.0
        total_credits = 0

        for sem, (sgpa, credits) in semester_sgpas.items():
            if sgpa is not None and credits > 0:
                total_weighted_sgpa += (sgpa * credits)
                total_credits += credits

        if total_credits == 0:
            return None

        return round(total_weighted_sgpa / total_credits, 2)
