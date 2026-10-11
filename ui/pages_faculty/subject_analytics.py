"""
Faculty Dashboard: Subject Analytics Page
Deep-dive academic analytics, pass/fail ratios, grade distributions, and internal vs external correlation.
"""
import streamlit as st
from ui.components import render_page_header, render_metric_card
from ui.charts import (
    build_grade_distribution_chart,
    build_internal_vs_external_scatter,
    build_pass_fail_donut
)
from repositories.faculty_repository import FacultyRepository
from repositories.result_repository import ResultRepository
from services.analytics_service import AnalyticsService


def render_faculty_analytics(user: dict) -> None:
    """Renders visual course analytics for assigned faculty."""
    render_page_header(
        title="Subject Analytics & Grade Intelligence 📈",
        subtitle=f"Course Evaluation Diagnostics for {user.get('full_name')}"
    )

    faculty_repo = FacultyRepository()
    result_repo = ResultRepository()
    analytics_service = AnalyticsService()

    assignments = faculty_repo.get_assigned_subjects(user["id"])
    if not assignments:
        st.warning("No courses assigned to your account.")
        return

    unique_subjects = {f"{a['code']} - {a['name']} (Sem {a['semester']})": a for a in assignments}
    selected_label = st.selectbox("Select Course for Analytics:", list(unique_subjects.keys()))
    selected_course = unique_subjects[selected_label]
    subject_id = selected_course["subject_id"]
    semester = selected_course["semester"]

    results = result_repo.get_subject_results(subject_id=subject_id, semester=semester)
    if not results:
        st.info("No assessment records found for this course.")
        return

    kpis = analytics_service.get_subject_kpis(results)
    grade_dist = analytics_service.get_grade_distribution(results)

    # Top KPI Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Pass Rate", f"{kpis['pass_percentage']}%", f"{kpis['passed_count']} of {kpis['evaluated_count']} Cleared")
    with c2:
        render_metric_card("Class Average", f"{kpis['avg_total']} / 100", f"CIE Avg: {kpis['avg_internal']} | SEE Avg: {kpis['avg_external']}")
    with c3:
        render_metric_card("Highest Mark", f"{kpis['highest_total']} / 100", "Top Score")
    with c4:
        render_metric_card("Lowest Mark", f"{kpis['lowest_total']} / 100", "Needs Recovery")

    # Chart Row 1: Grade Distribution & Clearance Donut
    col_dist, col_donut = st.columns([2, 1])
    with col_dist:
        grade_fig = build_grade_distribution_chart(grade_dist)
        st.plotly_chart(grade_fig, use_container_width=True)
    with col_donut:
        donut_fig = build_pass_fail_donut(kpis["passed_count"], kpis["failed_count"])
        st.plotly_chart(donut_fig, use_container_width=True)

    # Chart Row 2: CIE vs SEE Correlation Scatter
    st.markdown("### 🔬 Continuous vs. Final Exam Correlation")
    st.caption("Identify students who demonstrate strong internal scores but underperformed in the final exam (or vice-versa).")
    scatter_fig = build_internal_vs_external_scatter(results)
    st.plotly_chart(scatter_fig, use_container_width=True)
