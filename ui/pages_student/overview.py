"""
Student Dashboard: Overview Page
Displays student profile summary, current semester standing, SGPA/CGPA, and quick action cards.
"""
import streamlit as st
from ui.components import render_page_header, render_metric_card
from services.result_service import ResultService
from services.grading_service import GradingService
from repositories.improvement_repository import ImprovementRepository


def render_student_overview(user: dict) -> None:
    """Renders the student home overview."""
    full_name = user.get("full_name", "Student")
    usn = user.get("usn", "N/A")
    sem = user.get("semester", 5)
    branch = user.get("branch", "Engineering")
    sec = user.get("section", "A")

    render_page_header(
        title=f"Welcome back, {full_name} 👋",
        subtitle=f"USN: {usn} | {branch} | Semester {sem} - Section {sec}"
    )

    result_service = ResultService()
    grading_service = GradingService()
    improvement_repo = ImprovementRepository()

    # Load published results
    results = result_service.get_student_results(user["id"])
    sem_results = [r for r in results if r["semester"] == sem]

    # Calculate metrics
    current_sgpa = grading_service.calculate_sgpa(sem_results) if sem_results else None
    
    # Calculate CGPA across all published semesters
    sems = sorted(list({r["semester"] for r in results}))
    sem_sgpa_map = {}
    for s in sems:
        s_res = [r for r in results if r["semester"] == s]
        s_gpa = grading_service.calculate_sgpa(s_res)
        s_cred = sum(r.get("credits", 0) for r in s_res)
        if s_gpa is not None:
            sem_sgpa_map[s] = (s_gpa, s_cred)
    cgpa = grading_service.calculate_cgpa(sem_sgpa_map)

    cleared_count = sum(1 for r in sem_results if r.get("is_passed") == 1)
    total_subjects = len(sem_results)
    pending_acks = sum(1 for r in sem_results if not r.get("ack_id"))

    # KPI Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card(
            title=f"Semester {sem} SGPA",
            value=f"{current_sgpa:.2f}" if current_sgpa else "N/A",
            subtitle="Out of 10.0"
        )
    with col2:
        render_metric_card(
            title="Cumulative CGPA",
            value=f"{cgpa:.2f}" if cgpa else "N/A",
            subtitle=f"Across {len(sems)} semesters"
        )
    with col3:
        render_metric_card(
            title="Courses Cleared",
            value=f"{cleared_count} / {total_subjects}",
            subtitle=f"{round((cleared_count/total_subjects*100) if total_subjects else 0)}% Clearance"
        )
    with col4:
        render_metric_card(
            title="Pending Acknowledgements",
            value=str(pending_acks),
            subtitle="Actions required" if pending_acks > 0 else "All viewed & confirmed"
        )

    st.markdown("### 📋 Quick Course Standing")
    if not sem_results:
        st.info("No published results available for the current semester yet.")
    else:
        # Display clean subject summary cards
        cols = st.columns(min(len(sem_results), 3))
        for idx, res in enumerate(sem_results):
            col_target = cols[idx % len(cols)]
            with col_target:
                grade_color = "#10B981" if res["is_passed"] == 1 else "#EF4444"
                status_txt = "CLEARED" if res["is_passed"] == 1 else "NEEDS RECOVERY"
                st.markdown(f"""
                    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 0.75rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-weight: 700; color: #1E3A8A; font-size: 0.95rem;">{res['subject_code']}</span>
                            <span style="font-weight: 800; color: {grade_color}; font-size: 1.1rem;">{res['grade']}</span>
                        </div>
                        <div style="font-size: 0.825rem; color: #64748B; margin-top: 0.2rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                            {res['subject_name']}
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-top: 0.6rem; color: #334155;">
                            <span>CIE: <b>{res['internal_marks'] or 0}/40</b></span>
                            <span>SEE: <b>{res['external_marks'] or 0}/60</b></span>
                            <span>Total: <b>{res['total_marks'] or 0}/100</b></span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    # Active improvement plan highlight
    student_plans = improvement_repo.get_student_plans(user.get("student_id", 0))
    if student_plans:
        latest_plan = student_plans[0]
        st.markdown("---")
        st.markdown("### 🎯 Active Academic Improvement Plan")
        st.success(f"**{latest_plan['title']}** (Target SGPA: {latest_plan['target_sgpa'] or 8.5}) is active. "
                   "Head to the **Improvement Plan** tab in the sidebar to review your weekly schedule and log practice sessions.")
