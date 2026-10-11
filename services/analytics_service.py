"""
Analytics Service
Computes subject performance metrics, pass rates, grade distributions, and student risk flags.
"""
from typing import Any, Dict, List, Optional
import pandas as pd
from repositories.result_repository import ResultRepository
from repositories.faculty_repository import FacultyRepository
from repositories.student_repository import StudentRepository


class AnalyticsService:
    """Service providing aggregated analytics for dashboards and reporting."""

    def __init__(
        self,
        result_repo: Optional[ResultRepository] = None,
        faculty_repo: Optional[FacultyRepository] = None,
        student_repo: Optional[StudentRepository] = None
    ):
        self.result_repo = result_repo or ResultRepository()
        self.faculty_repo = faculty_repo or FacultyRepository()
        self.student_repo = student_repo or StudentRepository()

    def get_subject_kpis(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculates key performance indicators for a course:
        Pass rate, class average, high/low scores, evaluation progress.
        """
        if not results:
            return {
                "total_students": 0,
                "evaluated_count": 0,
                "passed_count": 0,
                "failed_count": 0,
                "pass_percentage": 0.0,
                "avg_internal": 0.0,
                "avg_external": 0.0,
                "avg_total": 0.0,
                "highest_total": 0.0,
                "lowest_total": 0.0,
                "published_count": 0,
                "unpublished_count": 0
            }

        df = pd.DataFrame(results)
        total = len(df)
        
        evaluated = df[df["grade"] != "PENDING"]
        eval_count = len(evaluated)
        
        if eval_count == 0:
            return {
                "total_students": total,
                "evaluated_count": 0,
                "passed_count": 0,
                "failed_count": 0,
                "pass_percentage": 0.0,
                "avg_internal": 0.0,
                "avg_external": 0.0,
                "avg_total": 0.0,
                "highest_total": 0.0,
                "lowest_total": 0.0,
                "published_count": int((df["is_published"] == 1).sum()),
                "unpublished_count": int((df["is_published"] == 0).sum())
            }

        passed = evaluated[evaluated["is_passed"] == 1]
        passed_count = len(passed)
        failed_count = eval_count - passed_count
        pass_pct = round((passed_count / eval_count) * 100.0, 1)

        avg_int = round(float(evaluated["internal_marks"].dropna().mean()), 1) if not evaluated["internal_marks"].dropna().empty else 0.0
        avg_ext = round(float(evaluated["external_marks"].dropna().mean()), 1) if not evaluated["external_marks"].dropna().empty else 0.0
        avg_tot = round(float(evaluated["total_marks"].dropna().mean()), 1) if not evaluated["total_marks"].dropna().empty else 0.0
        high_tot = round(float(evaluated["total_marks"].dropna().max()), 1) if not evaluated["total_marks"].dropna().empty else 0.0
        low_tot = round(float(evaluated["total_marks"].dropna().min()), 1) if not evaluated["total_marks"].dropna().empty else 0.0

        pub_count = int((df["is_published"] == 1).sum())
        unpub_count = total - pub_count

        return {
            "total_students": total,
            "evaluated_count": eval_count,
            "passed_count": passed_count,
            "failed_count": failed_count,
            "pass_percentage": pass_pct,
            "avg_internal": avg_int,
            "avg_external": avg_ext,
            "avg_total": avg_tot,
            "highest_total": high_tot,
            "lowest_total": low_tot,
            "published_count": pub_count,
            "unpublished_count": unpub_count
        }

    def get_grade_distribution(self, results: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculates frequency of each letter grade in the results set."""
        grades = ["O", "A+", "A", "B+", "B", "C", "P", "F", "PENDING"]
        dist = {g: 0 for g in grades}
        for r in results:
            g = r.get("grade", "PENDING")
            if g in dist:
                dist[g] += 1
            else:
                dist["PENDING"] += 1
        return dist

    def get_at_risk_students(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identifies students requiring academic intervention:
        - Failed students (is_passed == 0)
        - Low internals (< 50%)
        - High external variance (Internal >= 65% but External < 45%)
        """
        at_risk = []
        for r in results:
            if r.get("grade") == "PENDING":
                continue
            
            is_passed = r.get("is_passed", 0)
            int_marks = r.get("internal_marks", 0) or 0
            max_int = r.get("max_internal", 40) or 40
            ext_marks = r.get("external_marks", 0) or 0
            max_ext = r.get("max_external", 60) or 60

            int_pct = (int_marks / max_int * 100) if max_int > 0 else 0
            ext_pct = (ext_marks / max_ext * 100) if max_ext > 0 else 0

            reasons = []
            risk_level = "Support"

            if not is_passed or r.get("grade") == "F":
                risk_level = "High"
                reasons.append("Subject Not Cleared")
            elif int_pct < 45.0:
                risk_level = "High"
                reasons.append("Critical Low Internal (CIE < 45%)")
            elif int_pct < 50.0:
                risk_level = "Medium"
                reasons.append("Marginal Internal (CIE < 50%)")
            elif int_pct >= 65.0 and ext_pct < 45.0:
                risk_level = "Medium"
                reasons.append("High Internal-External Disparity")

            if reasons:
                at_risk.append({
                    "student_name": r.get("student_name", "Student"),
                    "usn": r.get("usn", "N/A"),
                    "section": r.get("section", "A"),
                    "internal_marks": int_marks,
                    "external_marks": ext_marks,
                    "total_marks": r.get("total_marks", 0),
                    "grade": r.get("grade", "F"),
                    "risk_level": risk_level,
                    "primary_issue": ", ".join(reasons)
                })

        priority_order = {"High": 0, "Medium": 1, "Support": 2}
        at_risk.sort(key=lambda x: priority_order.get(x["risk_level"], 3))
        return at_risk
