"""
Student Dashboard: My Performance Page
Visual analytics, semester SGPA trends, internal vs external components, and course comparisons.
"""
import streamlit as st
from ui.components import render_page_header
from ui.charts import (
    build_semester_trend_chart,
    build_subject_breakdown_bar,
    build_pass_fail_donut
)
from services.result_service import ResultService
from services.grading_service import GradingService


def render_student_performance(user: dict) -> None:
    """Renders visual performance charts for the student."""
    render_page_header(
        title="Performance Analytics 📊",
        subtitle=f"Visual progress diagnostics for {user.get('full_name')} ({user.get('usn')})"
    )

    result_service = ResultService()
    grading_service = GradingService()

    all_results = result_service.get_student_results(user["id"])
    if not all_results:
        st.info("No published performance records to analyze yet.")
        return

    # Compute Historical SGPA Map
    sems = sorted(list({r["semester"] for r in all_results}))
    sgpa_map = {}
    for s in sems:
        sem_res = [r for r in all_results if r["semester"] == s]
        sgpa = grading_service.calculate_sgpa(sem_res)
        if sgpa is not None:
            sgpa_map[s] = sgpa

    # Row 1: Semester Trend Chart
    st.markdown("### 📈 Multi-Semester Progression")
    trend_fig = build_semester_trend_chart(sgpa_map)
    st.plotly_chart(trend_fig, use_container_width=True)

    # Row 2: Selected Semester Course Breakdown
    st.markdown("### 🔍 Course Component Breakdown")
    current_sem = user.get("semester", 5)
    selected_sem = st.selectbox(
        "Choose semester for component breakdown:",
        options=sems,
        index=len(sems) - 1
    )
    sem_results = [r for r in all_results if r["semester"] == selected_sem]

    col1, col2 = st.columns([2, 1])
    with col1:
        bar_fig = build_subject_breakdown_bar(sem_results)
        st.plotly_chart(bar_fig, use_container_width=True)

    with col2:
        pass_count = sum(1 for r in sem_results if r.get("is_passed") == 1)
        fail_count = len(sem_results) - pass_count
        donut_fig = build_pass_fail_donut(pass_count, fail_count)
        st.plotly_chart(donut_fig, use_container_width=True)
