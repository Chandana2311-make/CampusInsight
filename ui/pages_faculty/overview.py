"""
Faculty Dashboard: Overview Page
Displays executive course indicators, assigned courses, overall clearance rate,
pending discrepancy queries, and students requiring academic support.
"""
import streamlit as st
from ui.components import render_page_header, render_metric_card
from repositories.faculty_repository import FacultyRepository
from repositories.result_repository import ResultRepository
from services.analytics_service import AnalyticsService
from services.query_service import QueryService


def render_faculty_overview(user: dict) -> None:
    """Renders the faculty home overview dashboard."""
    full_name = user.get("full_name", "Faculty Member")

    render_page_header(
        title=f"Welcome, {full_name} 👨‍🏫",
        subtitle="Department of Computer Science & Engineering | Academic Faculty Portal"
    )

    faculty_repo = FacultyRepository()
    result_repo = ResultRepository()
    analytics_service = AnalyticsService()
    query_service = QueryService()

    # Load courses assigned to this faculty member
    assignments = faculty_repo.get_assigned_subjects(user["id"])
    if not assignments:
        st.warning("No courses are currently assigned to your faculty profile.")
        return

    # Deduplicate subjects for dropdown/display
    unique_subjects = {a["subject_id"]: a for a in assignments}
    subject_ids = list(unique_subjects.keys())

    # Aggregate metrics across all assigned courses
    all_assigned_results = []
    for sub_id in subject_ids:
        all_assigned_results.extend(result_repo.get_subject_results(sub_id))

    kpis = analytics_service.get_subject_kpis(all_assigned_results)
    pending_queries = query_service.get_faculty_queries(user["id"], status="Submitted")
    at_risk_students = analytics_service.get_at_risk_students(all_assigned_results)

    # Top KPI Metrics Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card(
            title="Assigned Courses",
            value=str(len(subject_ids)),
            subtitle=f"{len(assignments)} Total Section Allocations"
        )
    with c2:
        render_metric_card(
            title="Overall Pass Rate",
            value=f"{kpis['pass_percentage']}%",
            subtitle=f"{kpis['passed_count']} of {kpis['evaluated_count']} Cleared"
        )
    with c3:
        render_metric_card(
            title="Pending Queries",
            value=str(len(pending_queries)),
            subtitle="Require faculty review" if pending_queries else "Inbox clear"
        )
    with c4:
        render_metric_card(
            title="Academic Support",
            value=str(len(at_risk_students)),
            subtitle="Students flagged for intervention"
        )

    # Assigned Courses Summary
    st.markdown("### 📚 Your Assigned Courses")
    cols = st.columns(min(len(unique_subjects), 2))
    for idx, (sub_id, sub_info) in enumerate(unique_subjects.items()):
        col = cols[idx % len(cols)]
        sub_results = [r for r in all_assigned_results if r["subject_id"] == sub_id]
        sub_kpis = analytics_service.get_subject_kpis(sub_results)

        with col:
            st.markdown(f"""
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 1.25rem 1.5rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 800; color: #1E3A8A; font-size: 1.15rem;">
                            {sub_info['code']}
                        </span>
                        <span style="background: #EFF6FF; color: #1D4ED8; font-weight: 700; font-size: 0.75rem; padding: 0.25rem 0.6rem; border-radius: 9999px;">
                            Sem {sub_info['semester']} • {sub_info['credits']} Credits
                        </span>
                    </div>
                    <div style="font-weight: 600; color: #334155; font-size: 0.95rem; margin-top: 0.25rem;">
                        {sub_info['name']}
                    </div>
                    <hr style="border: none; border-top: 1px solid #F1F5F9; margin: 0.75rem 0;" />
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: #475569;">
                        <span>Enrolled: <b>{sub_kpis['total_students']}</b></span>
                        <span>Pass Rate: <b>{sub_kpis['pass_percentage']}%</b></span>
                        <span>Class Avg: <b>{sub_kpis['avg_total']} / 100</b></span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #64748B; margin-top: 0.4rem;">
                        <span>Published: <b>{sub_kpis['published_count']}</b></span>
                        <span>Unpublished: <b>{sub_kpis['unpublished_count']}</b></span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
