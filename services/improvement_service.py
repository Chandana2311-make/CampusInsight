"""
Improvement Service
Rule-based recommendation engine for student academic growth and supportive intervention.
Grounded strictly in recorded evidence; produces actionable study roadmaps without stigmatizing labels.
"""
import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional
from repositories.result_repository import ResultRepository
from repositories.student_repository import StudentRepository
from repositories.assessment_repository import AssessmentRepository
from repositories.improvement_repository import ImprovementRepository
from services.grading_service import GradingService


@dataclass
class Recommendation:
    """Structured academic guidance recommendation."""
    subject_code: str
    subject_name: str
    rule_applied: str
    priority: str          # 'High', 'Medium', 'Supportive'
    reason: str
    evidence: str
    suggested_action: str
    follow_up_measurement: str
    topic_evidence: Optional[List[Dict[str, Any]]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ImprovementService:
    """Testable rule-based academic improvement recommendation engine."""

    def __init__(
        self,
        student_repo: Optional[StudentRepository] = None,
        result_repo: Optional[ResultRepository] = None,
        assessment_repo: Optional[AssessmentRepository] = None,
        improvement_repo: Optional[ImprovementRepository] = None,
        grading_service: Optional[GradingService] = None
    ):
        self.student_repo = student_repo or StudentRepository()
        self.result_repo = result_repo or ResultRepository()
        self.assessment_repo = assessment_repo or AssessmentRepository()
        self.improvement_repo = improvement_repo or ImprovementRepository()
        self.grading_service = grading_service or GradingService()

    def generate_recommendations_for_results(
        self,
        results: List[Dict[str, Any]],
        historical_sgpas: Optional[Dict[int, float]] = None,
        topic_scores: Optional[List[Dict[str, Any]]] = None,
        target_sgpa: Optional[float] = None
    ) -> List[Recommendation]:
        """
        Pure rule-based evaluation of marks, passing criteria, trends, and topic assessments.
        Returns a list of structured Recommendation objects.
        """
        recommendations: List[Recommendation] = []
        topic_scores = topic_scores or []
        historical_sgpas = historical_sgpas or {}

        # Organize topic scores by subject_id
        topics_by_subject: Dict[int, List[Dict[str, Any]]] = {}
        for ts in topic_scores:
            sub_id = ts.get("subject_id")
            if sub_id:
                topics_by_subject.setdefault(sub_id, []).append(ts)

        for res in results:
            code = res.get("subject_code", "GEN")
            name = res.get("subject_name", "General Course")
            sub_id = res.get("subject_id", 0)
            is_published = res.get("is_published", 1)
            is_absent = res.get("is_absent", 0)
            is_passed = res.get("is_passed", 0)
            internal = res.get("internal_marks")
            external = res.get("external_marks")
            max_int = res.get("max_internal", 40.0)
            max_ext = res.get("max_external", 60.0)
            min_int = res.get("min_internal_pass", 16.0)
            min_ext = res.get("min_external_pass", 21.0)
            grade = res.get("grade", "PENDING")

            # RULE 5: Absent, missing or unpublished result
            if not is_published:
                recommendations.append(Recommendation(
                    subject_code=code,
                    subject_name=name,
                    rule_applied="Rule 5: Unpublished Result",
                    priority="Supportive",
                    reason="Official course marks have not been released by the department.",
                    evidence=f"Course {code} status is currently 'Unpublished'.",
                    suggested_action="Consult the department coordinator or faculty lead for evaluation publication timeline.",
                    follow_up_measurement="Verify grade publication status on portal in the next cycle."
                ))
                continue

            if is_absent or internal is None or external is None:
                recommendations.append(Recommendation(
                    subject_code=code,
                    subject_name=name,
                    rule_applied="Rule 5: Absent / Incomplete Record",
                    priority="High",
                    reason="Attendance or assessment submission is marked as absent or pending.",
                    evidence=f"Status: {'Absent' if is_absent else 'Pending evaluation'} on official record.",
                    suggested_action="Submit attendance proof or re-examination application to the academic dean's office for record resolution.",
                    follow_up_measurement="Obtain formal clearance and schedule make-up assessment."
                ))
                continue

            int_pct = (internal / max_int * 100.0) if max_int > 0 else 0.0
            ext_pct = (external / max_ext * 100.0) if max_ext > 0 else 0.0

            # Gather verified topic-level evidence if available
            subject_topics = topics_by_subject.get(sub_id, [])
            weak_topics_evidence = []
            for t in subject_topics:
                t_score = t.get("score", 0.0)
                t_max = t.get("max_score", 1.0)
                t_pct = (t_score / t_max * 100.0) if t_max > 0 else 0.0
                if t_pct < 60.0:
                    weak_topics_evidence.append({
                        "topic_name": t.get("topic_name"),
                        "score": t_score,
                        "max_score": t_max,
                        "percentage": round(t_pct, 1),
                        "assessment_type": t.get("assessment_type")
                    })

            # RULE 1: Failed subject
            if not is_passed or grade == "F":
                evidence_text = f"Internal: {internal}/{max_int} (Min required: {min_int}), External: {external}/{max_ext} (Min required: {min_ext})."
                suggested_act = "Enroll in supplementary tutorials, solve 5 previous year question papers under timed conditions, and review answer schemes with the course instructor."
                
                if weak_topics_evidence:
                    topic_names = ", ".join([f"{t['topic_name']} ({t['percentage']}%)" for t in weak_topics_evidence])
                    suggested_act += f" Specifically prioritize verified weak modules from assessments: {topic_names}."

                recommendations.append(Recommendation(
                    subject_code=code,
                    subject_name=name,
                    rule_applied="Rule 1: Subject Recovery Plan",
                    priority="High",
                    reason="Comprehensive recovery plan needed to clear credit requirements and rebuild core mastery.",
                    evidence=evidence_text,
                    suggested_action=suggested_act,
                    follow_up_measurement="Target scoring at least 65% in bi-weekly recovery mock tests.",
                    topic_evidence=weak_topics_evidence if weak_topics_evidence else None
                ))
                continue

            # RULE 2: Low internal score (e.g., CIE < 50% or near pass cutoff)
            if int_pct < 50.0:
                recommendations.append(Recommendation(
                    subject_code=code,
                    subject_name=name,
                    rule_applied="Rule 2: Foundational Internal Reinforcement",
                    priority="High" if int_pct < 45.0 else "Medium",
                    reason="Continuous internal assessment scores indicate opportunities to improve assignment rigor and periodic test consistency.",
                    evidence=f"Internal score is {internal}/{max_int} ({round(int_pct, 1)}%). Passing benchmark is {min_int}.",
                    suggested_action="Schedule weekly office hours with faculty, submit optional practice problem sets, and seek early review on internal assignments before deadlines.",
                    follow_up_measurement="Achieve >= 75% on upcoming mid-term unit quizzes."
                ))

            # RULE 3: Strong internal but weak external score (CIE >= 65% but SEE < 50%)
            if int_pct >= 65.0 and ext_pct < 50.0:
                recommendations.append(Recommendation(
                    subject_code=code,
                    subject_name=name,
                    rule_applied="Rule 3: Examination Technique & Time Management",
                    priority="Medium",
                    reason="Strong internal grasp is evident, but semester-end examination score was impacted by exam execution or time allocation.",
                    evidence=f"Internal mastery is high at {round(int_pct, 1)}%, but final exam score was {round(ext_pct, 1)}% ({external}/{max_ext}).",
                    suggested_action="Practice 3-hour timed exam simulations, construct bulleted answer frameworks with diagrams, and refine question selection strategy.",
                    follow_up_measurement="Complete 2 full-length timed mock tests with self-grading rubrics."
                ))

            # RULE 6: Passed but below target
            current_gp = res.get("grade_points", 0)
            target_gp = (target_sgpa or 8.0)
            if is_passed and current_gp < target_gp and not (int_pct < 50.0 or (int_pct >= 65.0 and ext_pct < 50.0)):
                recommendations.append(Recommendation(
                    subject_code=code,
                    subject_name=name,
                    rule_applied="Rule 6: Targeted Grade Elevation",
                    priority="Supportive",
                    reason="Solid foundational pass achieved; focused optimization can elevate overall grade points toward target.",
                    evidence=f"Current Grade: {grade} (Grade Point {current_gp}). Target SGPA benchmark is {target_gp}.",
                    suggested_action="Review high-weightage topics, practice advanced numericals/system designs, and participate in peer study circles.",
                    follow_up_measurement="Aim for an A+ or O grade (>= 80%) in following semester electives."
                ))

        # RULE 4: Declining semester trend
        if historical_sgpas and len(historical_sgpas) >= 2:
            sorted_sems = sorted(historical_sgpas.keys())
            recent_sem = sorted_sems[-1]
            prev_sem = sorted_sems[-2]
            recent_sgpa = historical_sgpas[recent_sem]
            prev_sgpa = historical_sgpas[prev_sem]

            if recent_sgpa < (prev_sgpa - 0.5):  # Noticeable drop
                recommendations.append(Recommendation(
                    subject_code="ALL-SEMS",
                    subject_name="Academic Trajectory",
                    rule_applied="Rule 4: Semester Trajectory Alignment",
                    priority="High",
                    reason="A downward SGPA trend across consecutive semesters signals study fatigue, balance shifts, or topic friction.",
                    evidence=f"Semester {prev_sem} SGPA ({prev_sgpa}) dropped to Semester {recent_sem} SGPA ({recent_sgpa}), a change of {round(recent_sgpa - prev_sgpa, 2)} points.",
                    suggested_action="Review daily study routine, audit extracurricular commitments, and schedule a 1-on-1 academic mentorship consultation.",
                    follow_up_measurement="Establish weekly milestones to recover at least +0.5 SGPA in the subsequent term."
                ))

        # Sort recommendations by priority (High -> Medium -> Supportive)
        priority_order = {"High": 0, "Medium": 1, "Supportive": 2}
        recommendations.sort(key=lambda r: priority_order.get(r.priority, 3))
        return recommendations

    def build_weekly_schedule(self, recommendations: List[Recommendation]) -> List[Dict[str, Any]]:
        """
        Creates a realistic, supportive weekly study schedule based on high-priority needs.
        """
        high_priority_subs = [r.subject_code for r in recommendations if r.priority == "High" and r.subject_code != "ALL-SEMS"]
        med_priority_subs = [r.subject_code for r in recommendations if r.priority in ("Medium", "Supportive") and r.subject_code != "ALL-SEMS"]

        p1 = high_priority_subs[0] if high_priority_subs else (med_priority_subs[0] if med_priority_subs else "Core Subject")
        p2 = high_priority_subs[1] if len(high_priority_subs) > 1 else (med_priority_subs[1] if len(med_priority_subs) > 1 else "Elective / Lab")

        schedule = [
            {"day": "Monday", "focus": f"{p1} - Fundamentals & Class Notes Review", "duration_minutes": 60, "target": "Review lecture slides and summarize 2 key concepts"},
            {"day": "Tuesday", "focus": f"{p2} - Problem Solving & Numerical Practice", "duration_minutes": 60, "target": "Solve 5 textbook end-of-chapter problems"},
            {"day": "Wednesday", "focus": f"{p1} - Topic Deep-Dive / Lab Rehearsal", "duration_minutes": 75, "target": "Code/diagram key mechanisms and note doubts for faculty"},
            {"day": "Thursday", "focus": f"{p2} - Assignment & Question Bank Practice", "duration_minutes": 60, "target": "Complete upcoming internal assignment questions early"},
            {"day": "Friday", "focus": "Weekly Doubt Clearing & Mentor Check-in", "duration_minutes": 45, "target": "Clarify challenging topics with peers or course instructor"},
            {"day": "Saturday", "focus": f"Timed Practice Mock Test ({p1} & {p2})", "duration_minutes": 90, "target": "Attempt 1 full past paper section under exam conditions"},
            {"day": "Sunday", "focus": "Rest & Next Week Planning", "duration_minutes": 30, "target": "Consolidate study log, reflect on weekly progress, and recharge"}
        ]
        return schedule

    def generate_and_save_plan(
        self,
        student_user_id: int,
        target_sgpa: Optional[float] = 8.5
    ) -> Dict[str, Any]:
        """
        Gathers student data, generates recommendations, builds weekly schedule,
        and saves the improvement plan persistently.
        """
        student = self.student_repo.get_by_user_id(student_user_id)
        if not student:
            raise ValueError("Student profile not found.")

        # Load published results
        results = self.result_repo.get_student_results(student["id"], only_published=True)
        
        # Load topic scores
        topic_scores = self.assessment_repo.get_by_student(student["id"])

        # Compute historical SGPA
        sems = sorted(list({r["semester"] for r in results}))
        historical_sgpas = {}
        for s in sems:
            sem_results = [r for r in results if r["semester"] == s]
            sgpa = self.grading_service.calculate_sgpa(sem_results)
            if sgpa is not None:
                historical_sgpas[s] = sgpa

        recs = self.generate_recommendations_for_results(
            results=results,
            historical_sgpas=historical_sgpas,
            topic_scores=topic_scores,
            target_sgpa=target_sgpa
        )

        schedule = self.build_weekly_schedule(recs)

        recs_dicts = [r.to_dict() for r in recs]
        title = f"Semester {student['semester']} Academic Improvement Roadmap"

        plan_id = self.improvement_repo.create_plan(
            student_id=student["id"],
            title=title,
            target_sgpa=target_sgpa,
            recommendations_json=json.dumps(recs_dicts),
            weekly_schedule_json=json.dumps(schedule)
        )

        return {
            "plan_id": plan_id,
            "title": title,
            "target_sgpa": target_sgpa,
            "recommendations": recs_dicts,
            "weekly_schedule": schedule
        }

    def log_student_practice(
        self,
        student_user_id: int,
        plan_id: int,
        subject_id: int,
        date_completed: str,
        practice_activity: str,
        duration_minutes: int,
        self_assessment_score: Optional[float] = None,
        notes: Optional[str] = None
    ) -> int:
        """Records student self-directed practice session against their improvement plan."""
        student = self.student_repo.get_by_user_id(student_user_id)
        if not student:
            raise PermissionError("Student profile not found.")

        plan = self.improvement_repo.get_by_id(plan_id)
        if not plan or plan["student_id"] != student["id"]:
            raise PermissionError("Access denied: You can only log progress on your own plan.")

        return self.improvement_repo.add_practice_log(
            plan_id=plan_id,
            student_id=student["id"],
            subject_id=subject_id,
            date_completed=date_completed,
            practice_activity=practice_activity,
            duration_minutes=duration_minutes,
            self_assessment_score=self_assessment_score,
            notes=notes
        )
